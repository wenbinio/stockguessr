"""Score each portfolio against the S&P 500 (SPY) from the 2026-01-02 entry close.

Each portfolio is equal-weighted at the entry close and held with no rebalancing.
Two return figures per portfolio:

  gross    — paper return on adjusted closes (frictionless dividend reinvestment)
  friction — deducts trading costs (COST_BPS per side on entry and exit) and taxes
             the dividend component of return at DIV_TAX (dividends isolated as
             adjusted-close factor / raw-close factor per ticker)

Also reported: max drawdown, realized beta vs SPY (daily returns), CAPM alpha for
the window (risk-free RF_ANNUAL prorated), and a bootstrap percentile — where the
gross return lands among N_BOOT random equal-weight 10-stock baskets drawn from
universe.json (the "luck" distribution).

Outputs results.json (flagship daily series + full summary + bootstrap histogram)
and prints the ranking table.
"""

import json
import random
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
ENTRY = "2026-01-02"
COST_BPS = 10        # per side, entry + exit
DIV_TAX = 0.15       # tax rate applied to the dividend component of total return
RF_ANNUAL = 0.04     # T-bill proxy for CAPM alpha
N_BOOT = 2000
BOOT_SIZE = 10
MIN_TICKERS = 7      # skip a portfolio if fewer than this many tickers have data


def basket_factors(adj: pd.DataFrame, tickers: list[str]) -> pd.Series:
    """Per-ticker total-return factors (adjusted close) over the window."""
    px = adj[tickers].loc[ENTRY:].ffill().dropna()
    return px.iloc[-1] / px.iloc[0]


def portfolio_index(adj: pd.DataFrame, tickers: list[str]) -> pd.Series:
    px = adj[tickers].loc[ENTRY:].ffill().dropna()
    shares = 1.0 / px.iloc[0]
    value = (px * shares).sum(axis=1) / len(tickers)
    return value / value.iloc[0] * 100


def friction_return(adj: pd.DataFrame, raw: pd.DataFrame, tickers: list[str]) -> float:
    """Net return after trading costs and dividend tax, as a percentage."""
    f_adj = basket_factors(adj, tickers)
    rw = raw[tickers].loc[ENTRY:].ffill().dropna()
    f_raw = rw.iloc[-1] / rw.iloc[0]
    div_factor = f_adj / f_raw                      # growth attributable to dividends
    net = f_raw * (1 + (1 - DIV_TAX) * (div_factor - 1))
    cost = (1 - COST_BPS / 1e4) ** 2                # entry + exit
    return float((net.mean() * cost - 1) * 100)


def max_drawdown(idx: pd.Series) -> float:
    return float(((idx / idx.cummax()) - 1).min() * 100)


def beta_and_alpha(idx: pd.Series, spy: pd.Series) -> tuple[float, float]:
    rp, rm = idx.pct_change().dropna(), spy.pct_change().dropna()
    common = rp.index.intersection(rm.index)
    rp, rm = rp[common], rm[common]
    beta = float(rp.cov(rm) / rm.var())
    days = (idx.index[-1] - idx.index[0]).days
    rf = RF_ANNUAL * days / 365
    r_p = idx.iloc[-1] / 100 - 1
    r_m = spy.iloc[-1] / 100 - 1
    alpha = (r_p - (rf + beta * (r_m - rf))) * 100
    return beta, float(alpha)


def main() -> int:
    adj = pd.read_csv(HERE / "prices.csv", index_col="date", parse_dates=True)
    raw = pd.read_csv(HERE / "prices_raw.csv", index_col="date", parse_dates=True)
    have = set(adj.columns)

    # --- bootstrap null: random baskets from the universe -----------------
    universe = [t for t in json.loads((HERE / "universe.json").read_text())["tickers"]
                if t in have]
    rng = random.Random(20260102)  # deterministic
    factors = basket_factors(adj, universe)
    boot = sorted(
        float((sum(factors[t] for t in rng.sample(universe, BOOT_SIZE)) / BOOT_SIZE - 1) * 100)
        for _ in range(N_BOOT)
    )

    def percentile(ret: float) -> float:
        below = sum(1 for b in boot if b < ret)
        return round(below / len(boot) * 100, 1)

    # --- score portfolios --------------------------------------------------
    spy = portfolio_index(adj, ["SPY"])
    out = {"entry_date": ENTRY, "as_of": adj.index[-1].strftime("%Y-%m-%d"),
           "friction_model": {"cost_bps_per_side": COST_BPS, "dividend_tax": DIV_TAX,
                              "rf_annual": RF_ANNUAL},
           "series": {}, "summary": [], "bootstrap": {}}
    out["series"]["S&P 500 (SPY)"] = {d.strftime("%Y-%m-%d"): round(v, 3) for d, v in spy.items()}

    rows = [{
        "name": "S&P 500 (SPY)", "model": "benchmark", "group": "benchmark", "benchmark": True,
        "strategy": "the index",
        "total_return_pct": round(float(spy.iloc[-1] - 100), 2),
        "friction_return_pct": round(friction_return(adj, raw, ["SPY"]), 2),
        "max_drawdown_pct": round(max_drawdown(spy), 2),
        "beta": 1.0, "capm_alpha_pct": 0.0, "alpha_vs_spy_pct": 0.0,
        "bootstrap_pctile": percentile(float(spy.iloc[-1] - 100)),
    }]

    for pf in sorted((HERE / "portfolios").glob("*.json")):
        spec = json.loads(pf.read_text())
        tickers = [t.strip().upper().replace(".", "-") for t in spec["tickers"]]
        usable = [t for t in tickers if t in have]
        dropped = sorted(set(tickers) - set(usable))
        if len(usable) < MIN_TICKERS:
            print(f"SKIPPING {spec['name']}: only {len(usable)} tickers with data")
            continue
        idx = portfolio_index(adj, usable)
        beta, capm_alpha = beta_and_alpha(idx, spy)
        gross = float(idx.iloc[-1] - 100)
        row = {
            "name": spec["name"], "model": spec.get("model", "unknown"),
            "group": spec.get("group", "fleet"), "benchmark": False,
            "strategy": spec["strategy"],
            "total_return_pct": round(gross, 2),
            "friction_return_pct": round(friction_return(adj, raw, usable), 2),
            "max_drawdown_pct": round(max_drawdown(idx), 2),
            "beta": round(beta, 2), "capm_alpha_pct": round(capm_alpha, 2),
            "alpha_vs_spy_pct": round(gross - float(spy.iloc[-1] - 100), 2),
            "bootstrap_pctile": percentile(gross),
        }
        if dropped:
            row["dropped_tickers"] = dropped
        rows.append(row)
        if spec.get("group") == "flagship":
            out["series"][spec["name"]] = {d.strftime("%Y-%m-%d"): round(v, 3)
                                           for d, v in idx.items()}

    rows.sort(key=lambda r: r["total_return_pct"], reverse=True)
    out["summary"] = rows

    # store the null distribution (deciles + histogram for the chart)
    out["bootstrap"] = {
        "n": N_BOOT, "basket_size": BOOT_SIZE, "universe_size": len(universe),
        "mean": round(sum(boot) / len(boot), 2),
        "quantiles": {q: round(boot[int(q / 100 * (len(boot) - 1))], 2)
                      for q in (1, 5, 10, 25, 50, 75, 90, 95, 99)},
        "returns": [round(b, 2) for b in boot],
    }

    (HERE / "results.json").write_text(json.dumps(out, indent=1))

    print(f"\nRanking ({ENTRY} close -> {out['as_of']} close, equal weight, no rebalance)")
    print(f"Friction model: {COST_BPS}bps/side costs, {int(DIV_TAX*100)}% dividend tax; "
          f"bootstrap = {N_BOOT} random {BOOT_SIZE}-stock baskets\n")
    print(f"{'#':>2}  {'Portfolio':<28} {'Model':<7} {'Gross':>8} {'Net':>8} "
          f"{'Beta':>5} {'CAPM a':>8} {'Pctile':>7}")
    for i, r in enumerate(rows, 1):
        print(f"{i:>2}  {r['name']:<28} {r['model']:<7} {r['total_return_pct']:>7.2f}% "
              f"{r['friction_return_pct']:>7.2f}% {r['beta']:>5.2f} "
              f"{r['capm_alpha_pct']:>+7.2f}% {r['bootstrap_pctile']:>6.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
