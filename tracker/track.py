"""Refresh the live performance JSON for the StockGuessr experiments.

Reads every H1 portfolio (experiments/2026-h1/portfolios/*.json) and every H2
order sheet (experiments/2026-h2/orders/*.json), fetches daily adjusted closes
from Yahoo Finance, and writes:

  docs/api/performance.json   — the "API endpoint" (summary + flagship series)
  docs/index.html             — refreshes the inline snapshot between the
                                FALLBACK-START/END markers so the page also
                                works without a server

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
ALIASES = {"FI": "FISV", "SQ": "XYZ"}  # post-cutoff ticker changes (same company)


def normalize(t: str) -> str:
    t = t.strip().upper().replace(".", "-")
    return ALIASES.get(t, t)


def fetch(ticker: str, retries: int = 4) -> pd.Series | None:
    period2 = int(time.time()) + 86400
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={PERIOD1}&period2={period2}&interval=1d")
    for attempt in range(retries):
        try:
            out = subprocess.run(["curl", "-sS", "--max-time", "30", "-A", UA, url],
                                 capture_output=True, text=True, check=True).stdout
            result = json.loads(out)["chart"]["result"][0]
            ind = result["indicators"]
            closes = ind.get("adjclose", [{}])[0].get("adjclose") or ind["quote"][0]["close"]
            dates = pd.to_datetime(result["timestamp"], unit="s", utc=True) \
                      .tz_convert("America/New_York").date
            s = pd.Series(closes, index=pd.to_datetime(dates), name=ticker).dropna()
            return s if not s.empty else None
        except Exception:  # noqa: BLE001
            time.sleep(2 ** attempt)
    return None


def basket_return(prices: pd.DataFrame, tickers: list[str], entry: str) -> float | None:
    usable = [t for t in tickers if t in prices.columns]
    if len(usable) < min(7, len(tickers)):
        return None
    px = prices[usable].loc[entry:].ffill().dropna()
    if px.empty:
        return None
    return round(float((px.iloc[-1] / px.iloc[0]).mean() - 1) * 100, 2)


def basket_series(prices: pd.DataFrame, tickers: list[str], entry: str) -> dict:
    usable = [t for t in tickers if t in prices.columns]
    px = prices[usable].loc[entry:].ffill().dropna()
    idx = (px / px.iloc[0]).mean(axis=1) * 100
    return {d.strftime("%Y-%m-%d"): round(v, 3) for d, v in idx.items()}


def main() -> None:
    h1_books, h2_books, meta = {}, {}, {}
    for p in sorted((H1_DIR / "portfolios").glob("*.json")):
        d = json.loads(p.read_text())
        h1_books[d["name"]] = [normalize(t) for t in d["tickers"]]
        meta[d["name"]] = {"model": d["model"], "group": d["group"], "strategy": d["strategy"]}
    for p in sorted((H2_DIR / "orders").glob("*.json")):
        d = json.loads(p.read_text())
        h2_books[d["name"]] = [normalize(t) for t in d["resulting_portfolio"]]
        meta.setdefault(d["name"], {"model": d["model"], "group": d["group"],
                                    "strategy": d.get("strategy", "")})

    tickers = {"SPY"}
    for book in list(h1_books.values()) + list(h2_books.values()):
        tickers.update(book)

    series = []
    for t in sorted(tickers):
        s = fetch(t)
        if s is not None:
            series.append(s)
        time.sleep(0.35)
    prices = pd.concat(series, axis=1).sort_index()

    out = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "as_of_close": prices.index[-1].strftime("%Y-%m-%d"),
        "h1_entry": H1_ENTRY, "h2_entry": H2_ENTRY,
        "spy": {"h1_to_date_pct": basket_return(prices, ["SPY"], H1_ENTRY),
                "h2_to_date_pct": basket_return(prices, ["SPY"], H2_ENTRY)},
        "agents": [], "h2_series": {},
    }
    for name in sorted(set(h1_books) | set(h2_books)):
        m = meta[name]
        row = {"name": name, "model": m["model"], "group": m["group"], "strategy": m["strategy"],
               "h1_return_pct": basket_return(prices, h1_books[name], H1_ENTRY) if name in h1_books else None,
               "h2_return_pct": basket_return(prices, h2_books[name], H2_ENTRY) if name in h2_books else None}
        if name in h1_books:
            # counterfactual: the H1 book left untouched over the H2 window
            row["h2_hold_counterfactual_pct"] = basket_return(prices, h1_books[name], H2_ENTRY)
        out["agents"].append(row)

    out["h2_series"]["S&P 500 (SPY)"] = basket_series(prices, ["SPY"], H2_ENTRY)
    for name, book in h2_books.items():
        if meta[name]["group"] == "flagship":
            out["h2_series"][name] = basket_series(prices, book, H2_ENTRY)

    (DOCS / "api").mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, separators=(",", ":"))
    (DOCS / "api" / "performance.json").write_text(payload)

    index = DOCS / "index.html"
    if index.exists():
        html = index.read_text()
        html = re.sub(r"(/\*FALLBACK-START\*/).*?(/\*FALLBACK-END\*/)",
                      lambda m: m.group(1) + payload + m.group(2), html, flags=re.S)
        index.write_text(html)
    print(f"performance.json updated: {len(out['agents'])} agents, "
          f"as of {out['as_of_close']} close, {len(payload)} bytes")


if __name__ == "__main__":
    main()
