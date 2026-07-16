"""Round-2 execution desk + NAV engine.

Deterministic broker for the $1,000 full-toolkit accounts:
  - executes every allocation as fills at precise official closes
    (16:00 America/New_York on the effective date; crypto priced at the same
    timestamp), writing them to experiments/round2/fills.jsonl
  - values every book daily: long/short equities & ETFs (10bps/side,
    3% APR borrow on shorts), crypto spot (25bps/side), crypto perps
    (margin x leverage exposure, 25bps/side on notional, 10% APR funding,
    liquidation to zero when loss >= 95% of margin), cash at 4% APY
  - chains weekly rebalances: allocation files in
    experiments/round2/allocations/ (initial) and weeks/<date>/ (reassessments)
  - writes experiments/round2/results.json, docs/api/round2.json and refreshes
    the FALLBACK snapshot in docs/round2.html

Also supports --backtest <entry> <end> <allocation.json> to validate a
construction (and this engine) on a historical window.
"""

import json
import sys
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R2 = ROOT / "experiments" / "round2"
DOCS = ROOT / "docs"

CAPITAL = 1000.0
ENTRY = "2026-07-16"
PERIOD1 = 1704067200  # 2024-01-01, deep enough for backtests
UA = "Mozilla/5.0"
COST = {"equity": 0.0010, "crypto": 0.0025, "perp": 0.0025}
BORROW_APR, FUNDING_APR, CASH_APY = 0.03, 0.10, 0.04
LIQ_THRESHOLD = 0.05  # perp liquidated when value <= 5% of margin
ALIASES = {"FI": "FISV", "SQ": "XYZ"}


def normalize(sym: str) -> str:
    s = sym.strip().upper().replace(".", "-")
    return ALIASES.get(s, s)


def fetch(symbol: str, retries: int = 4) -> pd.Series | None:
    period2 = int(time.time()) + 86400
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1={PERIOD1}&period2={period2}&interval=1d")
    for attempt in range(retries):
        try:
            out = subprocess.run(["curl", "-sS", "--max-time", "30", "-A", UA, url],
                                 capture_output=True, text=True, check=True).stdout
            r = json.loads(out)["chart"]["result"][0]
            ind = r["indicators"]
            closes = ind.get("adjclose", [{}])[0].get("adjclose") or ind["quote"][0]["close"]
            dates = pd.to_datetime(r["timestamp"], unit="s", utc=True) \
                      .tz_convert("America/New_York").date
            s = pd.Series(closes, index=pd.to_datetime(list(dates)), name=symbol).dropna()
            # crypto has intraday "today" rows; keep one row per date (last)
            s = s.groupby(s.index).last()
            return s if not s.empty else None
        except Exception:  # noqa: BLE001
            time.sleep(2 ** attempt)
    return None


def load_price_matrix(symbols: set[str]) -> pd.DataFrame:
    series = []
    for sym in sorted(symbols):
        s = fetch(sym)
        if s is not None:
            series.append(s)
        time.sleep(0.35)
    px = pd.concat(series, axis=1).sort_index()
    return px.ffill()


def simulate(alloc: dict, px: pd.DataFrame, entry: str, end: str | None = None,
             capital: float = CAPITAL, fills: list | None = None):
    """Daily NAV for one allocation, buy-and-hold from entry close. Returns
    (nav_series, position_state) or None if entry prices are missing."""
    dates = px.loc[entry:end].index
    if len(dates) == 0:
        return None
    t0 = dates[0]
    positions = []
    for p in alloc["positions"]:
        sym = normalize(p["symbol"])
        if p["kind"] in ("crypto", "perp") and not sym.endswith("-USD"):
            sym += "-USD"
        if sym not in px.columns or pd.isna(px.loc[t0, sym]):
            return None
        margin = p["weight_pct"] / 100 * capital
        lev = float(p.get("leverage", 1)) if p["kind"] == "perp" else 1.0
        notional = margin * lev
        entry_cost = notional * COST[p["kind"]]
        if fills is not None:
            fills.append({"ts": t0.strftime("%Y-%m-%d") + "T16:00:00-04:00",
                          "agent": alloc["name"], "action": "OPEN", "symbol": sym,
                          "kind": p["kind"], "side": p["side"], "weight_pct": p["weight_pct"],
                          "leverage": lev if p["kind"] == "perp" else None,
                          "fill_price": round(float(px.loc[t0, sym]), 4),
                          "notional_usd": round(notional, 2),
                          "entry_cost_usd": round(entry_cost, 2)})
        positions.append({"sym": sym, "kind": p["kind"],
                          "side": 1 if p["side"] == "long" else -1,
                          "margin": margin - entry_cost, "lev": lev,
                          "p0": float(px.loc[t0, sym]), "dead": False})
    cash0 = alloc["cash_pct"] / 100 * capital
    nav = {}
    for d in dates:
        t = (d - t0).days / 365.0
        total = cash0 * (1 + CASH_APY * t)
        for pos in positions:
            if pos["dead"]:
                continue
            ret = float(px.loc[d, pos["sym"]]) / pos["p0"] - 1
            if pos["kind"] == "perp":
                v = pos["margin"] * (1 + pos["lev"] * pos["side"] * ret
                                     - pos["lev"] * FUNDING_APR * t)
                if v <= pos["margin"] * LIQ_THRESHOLD:
                    pos["dead"] = True
                    v = 0.0
            elif pos["side"] == -1:  # equity/crypto short
                v = pos["margin"] * (1 - ret - BORROW_APR * t)
                v = max(v, 0.0)
            else:
                v = pos["margin"] * (1 + ret)
            pos["value"] = v
            total += v
        nav[d] = total
    return pd.Series(nav), positions


def run_agent(files: list[Path], px: pd.DataFrame, fills: list):
    """Chain an agent's allocation history (sorted by entry date) into one NAV curve."""
    specs = sorted((json.loads(f.read_text()) for f in files), key=lambda s: s["entry"])
    curve = pd.Series(dtype=float)
    capital = CAPITAL
    for i, spec in enumerate(specs):
        end = specs[i + 1]["entry"] if i + 1 < len(specs) else None
        res = simulate(spec, px, spec["entry"], end, capital, fills if i == 0 or True else None)
        if res is None:
            return None, specs[0]
        leg, _ = res
        if not curve.empty:
            leg = leg.iloc[1:]  # avoid double-counting the rebalance close
        curve = pd.concat([curve, leg])
        capital = float(leg.iloc[-1]) if len(leg) else capital
    return curve, specs[-1]


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--backtest":
        entry, end, path = sys.argv[2], sys.argv[3], sys.argv[4]
        alloc = json.loads(Path(path).read_text())
        syms = {normalize(p["symbol"]) + ("-USD" if p["kind"] in ("crypto", "perp")
                and not normalize(p["symbol"]).endswith("-USD") else "")
                for p in alloc["positions"]} | {"SPY", "BTC-USD"}
        px = load_price_matrix(syms)
        res = simulate(alloc, px, entry, end)
        if res is None:
            print("missing entry prices")
            return 1
        nav, positions = res
        spy = px["SPY"].loc[entry:end].dropna()
        print(f"{alloc['name']}  {entry} -> {nav.index[-1].date()}")
        print(f"  NAV: ${CAPITAL:.0f} -> ${nav.iloc[-1]:.2f} ({(nav.iloc[-1]/CAPITAL-1)*100:+.2f}%)")
        print(f"  max drawdown: {((nav/nav.cummax())-1).min()*100:.2f}%")
        print(f"  SPY same window: {(spy.iloc[-1]/spy.iloc[0]-1)*100:+.2f}%")
        for pos in positions:
            tag = " LIQUIDATED" if pos["dead"] else ""
            print(f"    {pos['sym']:<9} {'S' if pos['side']<0 else 'L'}"
                  f"{pos['lev']:.0f}x  ${pos.get('value', 0):8.2f}{tag}")
        return 0

    alloc_files = {}
    for f in sorted((R2 / "allocations").glob("*.json")):
        alloc_files.setdefault(f.stem, []).append(f)
    for wk in sorted(R2.glob("weeks/*/")):
        for f in sorted(wk.glob("*.json")):
            alloc_files.setdefault(f.stem, []).append(f)

    symbols = {"SPY", "BTC-USD"}
    for files in alloc_files.values():
        for f in files:
            for p in json.loads(f.read_text())["positions"]:
                s = normalize(p["symbol"])
                if p["kind"] in ("crypto", "perp") and not s.endswith("-USD"):
                    s += "-USD"
                symbols.add(s)
    px = load_price_matrix(symbols)
    # crypto trades 24/7 and returns an intraday row for "today"; official fills
    # happen at the US close, so truncate to the last completed equity session
    px = px.loc[:px["SPY"].dropna().index[-1]]

    fills = []
    out = {"updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "entry": ENTRY, "capital_usd": CAPITAL, "as_of": px.index[-1].strftime("%Y-%m-%d"),
           "benchmarks": {}, "agents": {}}
    for bench, sym in (("SPY ($1000)", "SPY"), ("BTC ($1000)", "BTC-USD")):
        s = px[sym].loc[ENTRY:].dropna()
        if len(s):
            curve = s / s.iloc[0] * CAPITAL
            out["benchmarks"][bench] = {
                "nav": round(float(curve.iloc[-1]), 2),
                "series": {d.strftime("%Y-%m-%d"): round(v, 2) for d, v in curve.items()}}

    for stem, files in sorted(alloc_files.items()):
        curve, spec = run_agent(files, px, fills)
        if curve is None or curve.empty:
            # pre-entry (the entry close hasn't printed yet): show the book at par
            spec = json.loads(files[0].read_text())
            gross = sum(p["weight_pct"] * p.get("leverage", 1) for p in spec["positions"])
            out["agents"][spec["name"]] = {
                "model": spec["model"], "group": spec["group"], "strategy": spec["strategy"],
                "nav": CAPITAL, "growth_pct": 0.0, "max_drawdown_pct": 0.0,
                "gross_exposure_pct": round(gross, 1), "n_positions": len(spec["positions"]),
                "cash_pct": spec["cash_pct"], "positions": spec["positions"], "series": {},
            }
            continue
        gross = sum(p["weight_pct"] * p.get("leverage", 1) for p in spec["positions"])
        out["agents"][spec["name"]] = {
            "model": spec["model"], "group": spec["group"], "strategy": spec["strategy"],
            "nav": round(float(curve.iloc[-1]), 2),
            "growth_pct": round((float(curve.iloc[-1]) / CAPITAL - 1) * 100, 2),
            "max_drawdown_pct": round(float(((curve / curve.cummax()) - 1).min() * 100), 2),
            "gross_exposure_pct": round(gross, 1),
            "n_positions": len(spec["positions"]),
            "cash_pct": spec["cash_pct"],
            "positions": spec["positions"],
            "series": {d.strftime("%Y-%m-%d"): round(v, 2) for d, v in curve.items()},
        }

    (R2 / "fills.jsonl").write_text("\n".join(json.dumps(f) for f in fills) + "\n")
    (R2 / "results.json").write_text(json.dumps(out, indent=1))
    (DOCS / "api").mkdir(parents=True, exist_ok=True)
    blob = json.dumps(out, separators=(",", ":"))
    (DOCS / "api" / "round2.json").write_text(blob)
    import re
    for page, marker in ((DOCS / "round2.html", "FALLBACK"),
                         (DOCS / "index.html", "R2FALLBACK")):
        if page.exists() and f"/*{marker}-START*/" in page.read_text():
            page.write_text(re.sub(
                rf"(/\*{marker}-START\*/).*?(/\*{marker}-END\*/)",
                lambda m: m.group(1) + blob + m.group(2),
                page.read_text(), flags=re.S))
    print(f"round2: {len(out['agents'])} agents valued, {len(fills)} fills recorded, "
          f"as of {out['as_of']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
