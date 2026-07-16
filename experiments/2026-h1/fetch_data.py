"""Fetch daily closes from Yahoo Finance for all portfolio tickers + SPY.

Writes one CSV (date x ticker matrix of adjusted closes) to prices.csv.
Evaluation window: 2026-01-02 (entry close) through the latest available close.
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


def fetch_ticker(ticker: str, retries: int = 4) -> pd.Series | None:
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
            closes = ind.get("adjclose", [{}])[0].get("adjclose") or ind["quote"][0]["close"]
            dates = pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York").date
            s = pd.Series(closes, index=pd.to_datetime(dates), name=ticker).dropna()
            if s.empty:
                raise ValueError("empty series")
            return s
        except Exception as e:  # noqa: BLE001
            wait = 2 ** attempt
            print(f"  {ticker}: attempt {attempt + 1} failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    print(f"  {ticker}: FAILED after {retries} attempts")
    return None


def main() -> int:
    tickers = {"SPY"}
    for pf in sorted((HERE / "portfolios").glob("*.json")):
        tickers.update(json.loads(pf.read_text())["tickers"])

    print(f"Fetching {len(tickers)} tickers...")
    series = []
    for t in sorted(tickers):
        print(f"  {t}")
        s = fetch_ticker(t)
        if s is None:
            return 1
        series.append(s)
        time.sleep(0.4)  # be polite to the API

    prices = pd.concat(series, axis=1).sort_index()
    prices.index.name = "date"
    prices.to_csv(HERE / "prices.csv")
    print(f"Wrote prices.csv: {prices.shape[0]} days x {prices.shape[1]} tickers "
          f"({prices.index[0].date()} -> {prices.index[-1].date()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
