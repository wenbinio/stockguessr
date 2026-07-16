"""Fetch daily closes from Yahoo Finance for all portfolio tickers + the bootstrap
universe + SPY.

Writes two CSVs (date x ticker matrices): prices.csv (adjusted closes — dividends
reinvested) and prices_raw.csv (unadjusted closes — for isolating the dividend
component when applying dividend tax). Tickers that repeatedly fail are skipped and
recorded in failed_tickers.json rather than aborting the run.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
PERIOD1 = 1767225600  # 2026-01-01
PERIOD2 = 1784332800  # 2026-07-18 (exclusive upper bound)
UA = "Mozilla/5.0"


def normalize(ticker: str) -> str:
    return ticker.strip().upper().replace(".", "-")


def fetch_ticker(ticker: str, retries: int = 4):
    """Returns (adjusted_series, raw_series) or None."""
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1={PERIOD1}&period2={PERIOD2}&interval=1d"
    )
    for attempt in range(retries):
        try:
            out = subprocess.run(
                ["curl", "-sS", "--max-time", "30", "-A", UA, url],
                capture_output=True, text=True, check=True,
            ).stdout
            result = json.loads(out)["chart"]["result"][0]
            ts = result["timestamp"]
            ind = result["indicators"]
            raw = ind["quote"][0]["close"]
            adj = ind.get("adjclose", [{}])[0].get("adjclose") or raw
            dates = pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York").date
            idx = pd.to_datetime(dates)
            s_adj = pd.Series(adj, index=idx, name=ticker).dropna()
            s_raw = pd.Series(raw, index=idx, name=ticker).dropna()
            if s_adj.empty:
                raise ValueError("empty series")
            return s_adj, s_raw
        except Exception as e:  # noqa: BLE001
            wait = 2 ** attempt
            print(f"  {ticker}: attempt {attempt + 1} failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    return None


def main() -> int:
    tickers = {"SPY"}
    for pf in sorted((HERE / "portfolios").glob("*.json")):
        tickers.update(normalize(t) for t in json.loads(pf.read_text())["tickers"])
    tickers.update(normalize(t) for t in json.loads((HERE / "universe.json").read_text())["tickers"])

    print(f"Fetching {len(tickers)} tickers...")
    adj_series, raw_series, failed = [], [], []
    for t in sorted(tickers):
        got = fetch_ticker(t)
        if got is None:
            print(f"  {t}: FAILED — skipping")
            failed.append(t)
            continue
        adj_series.append(got[0])
        raw_series.append(got[1])
        time.sleep(0.4)  # be polite to the API

    for frame, fname in ((adj_series, "prices.csv"), (raw_series, "prices_raw.csv")):
        df = pd.concat(frame, axis=1).sort_index()
        df.index.name = "date"
        df.to_csv(HERE / fname)
        print(f"Wrote {fname}: {df.shape[0]} days x {df.shape[1]} tickers")
    (HERE / "failed_tickers.json").write_text(json.dumps(sorted(failed)))
    if failed:
        print(f"Skipped {len(failed)} unfetchable tickers: {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
