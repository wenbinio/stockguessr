"""Refresh the live performance data for the StockGuessr experiments.

Reads every H1 portfolio (experiments/2026-h1/portfolios/*.json) and every H2
order sheet (experiments/2026-h2/orders/*.json), fetches daily raw + adjusted
closes from Yahoo Finance, and writes:

  docs/api/performance.json  — compact summary + flagship H2 series (stable API)
  docs/api/agents.json       — full per-agent detail: trade ledger, positions,
                               per-position contributions, per-leg beta/CAPM
                               alpha, daily series for both legs
  docs/index.html, docs/agents.html — refreshes the inline snapshot between the
                               FALLBACK-START/END markers so both pages work
                               without a server

Run by .github/workflows/performance-tracker.yml after each US market close;
safe to run manually any time.
"""

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
H1_DIR = ROOT / "experiments" / "2026-h1"
H2_DIR = ROOT / "experiments" / "2026-h2"
DOCS = ROOT / "docs"

H1_ENTRY = "2026-01-02"
H2_ENTRY = "2026-07-15"   # order marks: 2026-07-15 close
PERIOD1 = 1767225600      # 2026-01-01
UA = "Mozilla/5.0"
RF_ANNUAL = 0.04
ALIASES = {"FI": "FISV", "SQ": "XYZ"}  # post-cutoff ticker changes (same company)


def normalize(t: str) -> str:
    t = t.strip().upper().replace(".", "-")
    return ALIASES.get(t, t)


def fetch(ticker: str, retries: int = 4):
    """Returns (adjusted, raw) daily close series or None."""
    period2 = int(time.time()) + 86400
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={PERIOD1}&period2={period2}&interval=1d")
    for attempt in range(retries):
        try:
            out = subprocess.run(["curl", "-sS", "--max-time", "30", "-A", UA, url],
                                 capture_output=True, text=True, check=True).stdout
            result = json.loads(out)["chart"]["result"][0]
            ind = result["indicators"]
            raw = ind["quote"][0]["close"]
            adj = ind.get("adjclose", [{}])[0].get("adjclose") or raw
            dates = pd.to_datetime(result["timestamp"], unit="s", utc=True) \
                      .tz_convert("America/New_York").date
            idx = pd.to_datetime(list(dates))
            s_adj = pd.Series(adj, index=idx, name=ticker).dropna()
            s_raw = pd.Series(raw, index=idx, name=ticker).dropna()
            return (s_adj, s_raw) if not s_adj.empty else None
        except Exception:  # noqa: BLE001
            time.sleep(2 ** attempt)
    return None


def leg_stats(adj: pd.DataFrame, tickers: list[str], entry: str, spy_idx: pd.Series):
    """Equal-weight buy-hold stats for one leg. Returns dict or None."""
    usable = [t for t in tickers if t in adj.columns]
    if len(usable) < min(7, len(tickers)):
        return None
    px = adj[usable].loc[entry:].ffill().dropna()
    if px.empty:
        return None
    factors = px.iloc[-1] / px.iloc[0]
    idx = (px / px.iloc[0]).mean(axis=1) * 100
    ret = float(idx.iloc[-1] - 100)
    beta = alpha = None
    rp = idx.pct_change().dropna()
    rm = spy_idx.pct_change().dropna()
    common = rp.index.intersection(rm.index)
    if len(common) >= 6 and float(rm[common].var()) > 0:
        beta = float(rp[common].cov(rm[common]) / rm[common].var())
        days = (idx.index[-1] - idx.index[0]).days
        rf = RF_ANNUAL * days / 365
        r_m = float(spy_idx.loc[idx.index[-1]] / spy_idx.loc[idx.index[0]] - 1)
        alpha = (ret / 100 - (rf + beta * (r_m - rf))) * 100
    return {
        "return_pct": round(ret, 2),
        "beta": None if beta is None else round(beta, 2),
        "capm_alpha_pct": None if alpha is None else round(alpha, 2),
        "market_component_pct": None if alpha is None else round(ret - alpha, 2),
        "series": {d.strftime("%Y-%m-%d"): round(v, 2) for d, v in idx.items()},
        "contributions": {t: round((float(factors[t]) - 1) / len(usable) * 100, 2)
                          for t in usable},
        "position_returns": {t: round((float(factors[t]) - 1) * 100, 2) for t in usable},
        "book": usable,
    }


def main() -> None:
    h1_specs, h2_specs = {}, {}
    for p in sorted((H1_DIR / "portfolios").glob("*.json")):
        d = json.loads(p.read_text())
        d["tickers"] = [normalize(t) for t in d["tickers"]]
        h1_specs[d["name"]] = d
    for p in sorted((H2_DIR / "orders").glob("*.json")):
        d = json.loads(p.read_text())
        for o in d["orders"]:
            o["ticker"] = normalize(o["ticker"])
        d["resulting_portfolio"] = [normalize(t) for t in d["resulting_portfolio"]]
        h2_specs[d["name"]] = d

    tickers = {"SPY"}
    for d in h1_specs.values():
        tickers.update(d["tickers"])
    for d in h2_specs.values():
        tickers.update(d["resulting_portfolio"])

    adj_s, raw_s = [], []
    for t in sorted(tickers):
        got = fetch(t)
        if got is not None:
            adj_s.append(got[0])
            raw_s.append(got[1])
        time.sleep(0.35)
    adj = pd.concat(adj_s, axis=1).sort_index()
    raw = pd.concat(raw_s, axis=1).sort_index().ffill()

    spy_h1 = (adj["SPY"].loc[H1_ENTRY:] / adj["SPY"].loc[H1_ENTRY:].iloc[0]) * 100
    spy_h2 = (adj["SPY"].loc[H2_ENTRY:] / adj["SPY"].loc[H2_ENTRY:].iloc[0]) * 100
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    as_of = adj.index[-1].strftime("%Y-%m-%d")

    def fill(ticker, date):
        try:
            return round(float(raw[ticker].loc[date]), 2)
        except KeyError:
            return None

    agents = {}
    for name in sorted(set(h1_specs) | set(h2_specs)):
        s1, s2 = h1_specs.get(name), h2_specs.get(name)
        meta = s1 or s2
        h1 = leg_stats(adj, s1["tickers"], H1_ENTRY, spy_h1) if s1 else None
        h2 = h2_hold = None
        if s2:
            h2 = leg_stats(adj, s2["resulting_portfolio"], H2_ENTRY, spy_h2)
            if s1:
                cf = leg_stats(adj, s1["tickers"], H2_ENTRY, spy_h2)
                h2_hold = cf["return_pct"] if cf else None

        # trade ledger: H1 entry buys, then H2 sells/buys with reasons + realized P&L
        ledger = []
        if s1:
            for t in s1["tickers"]:
                ledger.append({"leg": "H1", "date": H1_ENTRY, "action": "BUY", "ticker": t,
                               "fill": fill(t, H1_ENTRY)})
        if s2:
            h1_pos = (h1 or {}).get("position_returns", {})
            for o in s2["orders"]:
                row = {"leg": "H2", "date": s2["order_date"], "action": o["action"],
                       "ticker": o["ticker"], "fill": fill(o["ticker"], H2_ENTRY),
                       "reason": o["reason"]}
                if o["action"] == "SELL":
                    # realized total return over H1 leg (adjusted) if it was held
                    row["realized_pct"] = h1_pos.get(o["ticker"])
                ledger.append(row)

        # current positions with entry leg, fills and live P&L
        positions = []
        if s2 and h2:
            held_from_h1 = set(s2["holds"]) if s1 else set()
            for t in h2["book"]:
                entry_date = H1_ENTRY if t in held_from_h1 else H2_ENTRY
                e_adj = adj[t].loc[entry_date:].ffill().dropna()
                positions.append({
                    "ticker": t,
                    "entry_date": entry_date,
                    "entry_fill": fill(t, entry_date),
                    "last_close": fill(t, as_of),
                    "since_entry_pct": round(float(e_adj.iloc[-1] / e_adj.iloc[0] - 1) * 100, 2),
                    "h2_contribution_pct": h2["contributions"].get(t),
                })

        agents[name] = {"model": meta["model"], "group": meta["group"],
                        "strategy": meta["strategy"], "h1": h1, "h2": h2,
                        "h2_hold_counterfactual_pct": h2_hold,
                        "ledger": ledger, "positions": positions}

    agents_payload = {
        "updated_utc": stamp, "as_of_close": as_of,
        "h1_entry": H1_ENTRY, "h2_entry": H2_ENTRY, "rf_annual": RF_ANNUAL,
        "spy": {
            "h1_return_pct": round(float(spy_h1.iloc[-1] - 100), 2),
            "h2_return_pct": round(float(spy_h2.iloc[-1] - 100), 2),
            "h1_series": {d.strftime("%Y-%m-%d"): round(v, 2) for d, v in spy_h1.items()},
            "h2_series": {d.strftime("%Y-%m-%d"): round(v, 2) for d, v in spy_h2.items()},
        },
        "agents": agents,
    }

    # compact summary endpoint (stable shape for the overview page)
    perf_payload = {
        "updated_utc": stamp, "as_of_close": as_of,
        "h1_entry": H1_ENTRY, "h2_entry": H2_ENTRY,
        "spy": {"h1_to_date_pct": agents_payload["spy"]["h1_return_pct"],
                "h2_to_date_pct": agents_payload["spy"]["h2_return_pct"]},
        "agents": [{
            "name": n, "model": a["model"], "group": a["group"], "strategy": a["strategy"],
            "h1_return_pct": a["h1"]["return_pct"] if a["h1"] else None,
            "h2_return_pct": a["h2"]["return_pct"] if a["h2"] else None,
            "h2_hold_counterfactual_pct": a["h2_hold_counterfactual_pct"],
        } for n, a in agents.items()],
        "h2_series": {"S&P 500 (SPY)": agents_payload["spy"]["h2_series"],
                      **{n: a["h2"]["series"] for n, a in agents.items()
                         if a["h2"] and a["group"] == "flagship"}},
    }

    (DOCS / "api").mkdir(parents=True, exist_ok=True)
    for fname, payload in (("performance.json", perf_payload), ("agents.json", agents_payload)):
        (DOCS / "api" / fname).write_text(json.dumps(payload, separators=(",", ":")))

    for page, payload in (("index.html", perf_payload), ("agents.html", agents_payload)):
        f = DOCS / page
        if f.exists():
            blob = json.dumps(payload, separators=(",", ":"))
            f.write_text(re.sub(r"(/\*FALLBACK-START\*/).*?(/\*FALLBACK-END\*/)",
                                lambda m: m.group(1) + blob + m.group(2),
                                f.read_text(), flags=re.S))
    print(f"refreshed: {len(agents)} agents, as of {as_of} close")


if __name__ == "__main__":
    main()
