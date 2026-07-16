"""Score each portfolio against the S&P 500 (SPY) from the 2026-01-02 entry close.

Each portfolio is equal-weighted at the 2026-01-02 close and held with no
rebalancing. Outputs:
  - results.json: per-portfolio daily index series (base 100) + summary stats
  - a printed ranking table
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ENTRY = "2026-01-02"


def portfolio_index(prices: pd.DataFrame, tickers: list[str]) -> pd.Series:
    px = prices[tickers].loc[ENTRY:]
    # forward-fill occasional missing days so a single gap doesn't distort the basket
    px = px.ffill().dropna()
    shares = 1.0 / px.iloc[0]  # equal dollar weight at entry close
    value = (px * shares).sum(axis=1) / len(tickers)
    return value / value.iloc[0] * 100


def max_drawdown(idx: pd.Series) -> float:
    return float(((idx / idx.cummax()) - 1).min() * 100)


def main() -> int:
    prices = pd.read_csv(HERE / "prices.csv", index_col="date", parse_dates=True)

    portfolios = {}
    for pf in sorted((HERE / "portfolios").glob("*.json")):
        spec = json.loads(pf.read_text())
        portfolios[spec["name"]] = spec["tickers"]

    out = {"entry_date": ENTRY, "series": {}, "summary": []}
    spy = portfolio_index(prices, ["SPY"])
    out["series"]["S&P 500 (SPY)"] = {d.strftime("%Y-%m-%d"): round(v, 3) for d, v in spy.items()}

    rows = [{
        "name": "S&P 500 (SPY)", "benchmark": True,
        "total_return_pct": round(float(spy.iloc[-1] - 100), 2),
        "max_drawdown_pct": round(max_drawdown(spy), 2),
        "alpha_vs_spy_pct": 0.0,
    }]
    for name, tickers in portfolios.items():
        idx = portfolio_index(prices, tickers)
        out["series"][name] = {d.strftime("%Y-%m-%d"): round(v, 3) for d, v in idx.items()}
        rows.append({
            "name": name, "benchmark": False,
            "total_return_pct": round(float(idx.iloc[-1] - 100), 2),
            "max_drawdown_pct": round(max_drawdown(idx), 2),
            "alpha_vs_spy_pct": round(float(idx.iloc[-1] - spy.iloc[-1]), 2),
        })

    rows.sort(key=lambda r: r["total_return_pct"], reverse=True)
    out["summary"] = rows
    out["as_of"] = prices.index[-1].strftime("%Y-%m-%d")
    (HERE / "results.json").write_text(json.dumps(out, indent=2))

    print(f"\nRanking ({ENTRY} close -> {out['as_of']} close, equal weight, no rebalance)\n")
    print(f"{'#':>2}  {'Portfolio':<28} {'Return':>8} {'MaxDD':>8} {'vs SPY':>8}")
    for i, r in enumerate(rows, 1):
        tag = " (benchmark)" if r["benchmark"] else ""
        print(f"{i:>2}  {r['name']:<28} {r['total_return_pct']:>7.2f}% "
              f"{r['max_drawdown_pct']:>7.2f}% {r['alpha_vs_spy_pct']:>+7.2f}%{tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
