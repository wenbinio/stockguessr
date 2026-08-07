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
DOCS = ROOT / "docs"

ROUNDS = {
    "2": {"dir": "round2", "entry": "2026-07-16", "api": "round2.json",
          "pages": [("round2.html", "FALLBACK"), ("index.html", "R2FALLBACK")]},
    "3": {"dir": "round3", "entry": "2026-07-17", "api": "round3.json",
          "pages": [("index.html", "R3FALLBACK")]},
}
_round = sys.argv[sys.argv.index("--round") + 1] if "--round" in sys.argv else "2"
CFG = ROUNDS[_round]
R2 = ROOT / "experiments" / CFG["dir"]

CAPITAL = 1000.0
ENTRY = CFG["entry"]
PERIOD1 = 1704067200  # 2024-01-01, deep enough for backtests
UA = "Mozilla/5.0"
BORROW_APR, FUNDING_APR, CASH_APY = 0.03, 0.10, 0.04
LIQ_THRESHOLD = 0.05  # perp liquidated when value <= 5% of margin
PERP_MAX_LEV = 100.0  # venue maximum on majors (unrestricted-retail rules, 2026-07-30)
CASH_LIKE = {"CASH", "USDC", "USD", "MONEY", "CASHX"}  # tickers that are NOT cash
ALIASES = {"FI": "FISV", "SQ": "XYZ"}

# Realistic retail fee schedule (per side, fraction of notional)
LEVERAGED_ETFS = {"TQQQ", "SQQQ", "SOXL", "SOXS", "TNA", "TZA", "UPRO", "SPXU",
                  "UDOW", "SDOW", "LABU", "LABD", "FNGU", "TECL", "TECS", "YINN"}
SEC_TAF_SELL = 0.000031  # SEC fee + FINRA TAF, sell side only


def fee_rate(kind: str, sym: str, price: float, is_close: bool) -> float:
    if kind == "perp":
        return 0.00075                     # taker fee + spread on notional
    if kind == "crypto":
        return 0.0035                      # retail taker + spread
    base = 0.0005 if sym in LEVERAGED_ETFS else (0.0012 if price < 15 else 0.0002)
    return base + (SEC_TAF_SELL if is_close else 0.0)


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


def registered_notionals(alloc: dict) -> dict:
    """Map (sym, side, kind) -> notional weight (weight x leverage), registered terms."""
    out = {}
    for p in alloc["positions"]:
        sym = normalize(p["symbol"])
        if p["kind"] in ("crypto", "perp") and not sym.endswith("-USD"):
            sym += "-USD"
        lev = float(p.get("leverage", 1)) if p["kind"] == "perp" else 1.0
        key = (sym, p["side"], p["kind"])
        out[key] = out.get(key, 0.0) + p["weight_pct"] * lev
    return out


def simulate(alloc: dict, px: pd.DataFrame, entry: str, end: str | None = None,
             capital: float = CAPITAL, fills: list | None = None,
             prev_alloc: dict | None = None):
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
        prev_n = 0.0
        if prev_alloc is not None:
            key = (sym, p["side"], p["kind"])
            prev_n = registered_notionals(prev_alloc).get(key, 0.0) / 100 * capital
        traded = max(notional - prev_n, 0.0)  # only the increment trades
        entry_cost = traded * fee_rate(p["kind"], sym, float(px.loc[t0, sym]), False)
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
                          "p0": float(px.loc[t0, sym]), "dead": False,
                          "stop": p.get("stop_loss_pct"), "tp": p.get("take_profit_pct")})
    # exit costs on positions closed or reduced vs the prior registered book
    exit_costs = 0.0
    if prev_alloc is not None:
        new_n = registered_notionals(alloc)
        for key, prev_w in registered_notionals(prev_alloc).items():
            reduced_w = max(prev_w - new_n.get(key, 0.0), 0.0)
            if reduced_w > 0 and key[0] in px.columns and not pd.isna(px.loc[t0, key[0]]):
                exit_costs += (reduced_w / 100 * capital) * fee_rate(
                    key[2], key[0], float(px.loc[t0, key[0]]), True)
    # cash tracked as dated events so stop/TP proceeds earn yield from close date
    cash_events = [(t0, alloc["cash_pct"] / 100 * capital - exit_costs)]
    nav = {}
    for d in dates:
        t = (d - t0).days / 365.0
        total = sum(amt * (1 + CASH_APY * (d - dt).days / 365.0) for dt, amt in cash_events)
        for pos in positions:
            if pos["dead"]:
                continue
            ret = float(px.loc[d, pos["sym"]]) / pos["p0"] - 1
            if pos["kind"] == "perp":
                funding = FUNDING_APR * t if pos["side"] > 0 else 0.0  # longs pay; shorts approximated flat
                v = pos["margin"] * (1 + pos["lev"] * pos["side"] * ret
                                     - pos["lev"] * funding)
                if v <= pos["margin"] * LIQ_THRESHOLD:
                    pos["dead"] = True
                    v = 0.0
            elif pos["side"] == -1:  # equity/crypto short
                v = pos["margin"] * (1 - ret - BORROW_APR * t)
                v = max(v, 0.0)
            else:
                v = pos["margin"] * (1 + ret)
            # standing orders: position-level P&L vs margin, evaluated at daily closes
            pnl_pct = (v / pos["margin"] - 1) * 100 if pos["margin"] > 0 else 0.0
            trigger = None
            if not pos["dead"] and pos.get("stop") is not None and pnl_pct <= -abs(pos["stop"]):
                trigger = "STOP_LOSS"
            elif not pos["dead"] and pos.get("tp") is not None and pnl_pct >= abs(pos["tp"]):
                trigger = "TAKE_PROFIT"
            if trigger:
                exit_cost = v * pos["lev"] * fee_rate(pos["kind"], pos["sym"],
                                                      float(px.loc[d, pos["sym"]]), True)
                proceeds = max(v - exit_cost, 0.0)
                cash_events.append((d, proceeds))
                pos["dead"] = True
                pos["value"] = 0.0
                if fills is not None:
                    fills.append({"ts": d.strftime("%Y-%m-%d") + "T16:00:00-04:00",
                                  "agent": alloc["name"], "action": trigger,
                                  "symbol": pos["sym"], "kind": pos["kind"],
                                  "side": "long" if pos["side"] > 0 else "short",
                                  "fill_price": round(float(px.loc[d, pos["sym"]]), 4),
                                  "proceeds_usd": round(proceeds, 2),
                                  "exit_cost_usd": round(exit_cost, 2)})
                total += proceeds
                continue
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
        if pd.Timestamp(spec["entry"]) > px.index[-1]:
            # registered rebalance whose entry close hasn't printed yet: the
            # prior book keeps running until the new leg becomes priceable
            break
        end = specs[i + 1]["entry"] if i + 1 < len(specs) else None
        res = simulate(spec, px, spec["entry"], end, capital, fills,
                       prev_alloc=specs[i - 1] if i > 0 else None)
        if res is None:
            missing = [normalize(q["symbol"]) for q in spec["positions"]
                       if normalize(q["symbol"]) not in px.columns]
            print(f"DATA ERROR {spec['name']}: leg {spec['entry']} unpriceable "
                  f"(missing: {missing or 'entry date beyond data'})")
            return None, specs[0]
        leg, _ = res
        if not curve.empty:
            leg = leg.iloc[1:]  # avoid double-counting the rebalance close
        curve = pd.concat([curve, leg])
        capital = float(leg.iloc[-1]) if len(leg) else capital
        live = spec
    return curve, (live if not curve.empty else specs[-1])


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

    def validate(spec, fname):
        """Unrestricted-retail rules (effective 2026-07-30).

        Concentration guardrails are gone: no maximum position size, no minimum
        position count, and the short side may use the whole notional. What
        remains is arithmetic (a book must allocate exactly 100% of the
        account) plus venue realism on perp leverage. Books registered before
        2026-07-30 were built under the old caps; see round2/RULES.md.
        """
        w = sum(q["weight_pct"] for q in spec["positions"]) + spec["cash_pct"]
        shorts = sum(q["weight_pct"] for q in spec["positions"] if q["side"] == "short")
        probs = []
        # Cash is `cash_pct`, never a position. CASH and USDC are real listed
        # securities (Pathward Financial; USDATA Corp, a sub-penny OTC shell),
        # so a manager writing "CASH" for dry powder silently bought a bank —
        # and a symbol-priceability check passes them precisely because they
        # are genuine tickers. Ten books were filled this way on 2026-07-31.
        for q in spec["positions"]:
            if q["symbol"].upper() in CASH_LIKE:
                probs.append(f"'{q['symbol']}' is a listed security, not cash — use cash_pct")
        if abs(w - 100) > 0.05: probs.append(f"weights+cash={w:.1f}")
        if not spec["positions"]: probs.append("no positions")
        if any(q["weight_pct"] < 0 for q in spec["positions"]):
            probs.append("negative weight (use side=short instead)")
        if spec["cash_pct"] < 0: probs.append(f"negative cash={spec['cash_pct']:.1f}")
        if shorts > 100: probs.append(f"shorts={shorts:.0f}%")
        for q in spec["positions"]:
            if q["kind"] == "perp" and not 0 < float(q.get("leverage", 0)) <= PERP_MAX_LEV:
                probs.append(f"perp leverage {q.get('leverage')} (venue max {PERP_MAX_LEV}x)")
        if probs:
            print(f"RULES VIOLATION {fname}: {'; '.join(probs)}")
        return not probs

    alloc_files = {}
    bad = []
    for f in sorted((R2 / "allocations").glob("*.json")):
        if not validate(json.loads(f.read_text()), f.name):
            bad.append(str(f.relative_to(R2.parent.parent)))
        alloc_files.setdefault(f.stem, []).append(f)
    for wk in sorted(R2.glob("weeks/*/")):
        for f in sorted(wk.glob("*.json")):
            # weekly rebalances go through the SAME gate as opening books. Until
            # 2026-08-07 they were never validated here at all: validate() ran
            # only over allocations/ and its return value was discarded, so a
            # malformed reassessment would have been simulated silently.
            if not validate(json.loads(f.read_text()), str(Path(wk.name) / f.name)):
                bad.append(str(f.relative_to(R2.parent.parent)))
            alloc_files.setdefault(f.stem, []).append(f)
    if bad:
        print(f"REFUSING TO SCORE: {len(bad)} book(s) violate the rules — "
              f"fix or withdraw them, do not publish a ranking that includes them:")
        for b in bad:
            print(f"  {b}")
        return 1

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
    (DOCS / "api" / CFG["api"]).write_text(blob)
    import re
    for page_name, marker in CFG["pages"]:
        page = DOCS / page_name
        if page.exists() and f"/*{marker}-START*/" in page.read_text():
            page.write_text(re.sub(
                rf"(/\*{marker}-START\*/).*?(/\*{marker}-END\*/)",
                lambda m: m.group(1) + blob + m.group(2),
                page.read_text(), flags=re.S))
    print(f"round{_round}: {len(out['agents'])} agents valued, {len(fills)} fills recorded, "
          f"as of {out['as_of']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
