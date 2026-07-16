# H1 2026 experiment: Claude & five Opus agents vs the S&P 500

A live run of the StockGuessr idea at portfolio scale. Six model-picked portfolios were
formed with knowledge frozen at the January 2026 model cutoff, virtually bought at the
2026-01-02 close (equal weight, no rebalancing), and scored against real market prices
through 2026-07-15.

## Contestants

| Portfolio | Picked by | Strategy |
|---|---|---|
| Claude Fable (orchestrator) | claude-fable-5 | Concentrated AI-infrastructure conviction basket |
| Opus Momentum | claude-opus subagent | 12-1 cross-sectional momentum |
| Opus Value | claude-opus subagent | Value / contrarian mean-reversion |
| Opus Quality Defensive | claude-opus subagent | Quality / low-volatility defensive |
| Opus Picks-and-Shovels | claude-opus subagent | AI infrastructure suppliers, Mag-7 forbidden |
| Opus Broadening | claude-opus subagent | Anti-concentration / breadth catch-up |

Each Opus agent was required to backtest its strategy rule on pre-cutoff data
(2024-H1 and 2025-H1 holding windows) before committing to picks, and was forbidden
from requesting any price data after 2026-01-02. Backtest numbers are recorded in each
portfolio JSON.

## Result (2026-01-02 → 2026-07-15)

| # | Portfolio | Return | Max drawdown | Alpha vs SPY |
|---|---|---|---|---|
| 1 | Opus Picks-and-Shovels | +57.45% | -15.63% | +46.38% |
| 2 | Claude Fable (orchestrator) | +45.19% | -14.81% | +34.11% |
| 3 | Opus Momentum | +45.18% | -12.41% | +34.11% |
| 4 | Opus Broadening | +11.31% | -10.43% | +0.24% |
| 5 | **S&P 500 (SPY)** | **+11.07%** | **-8.88%** | benchmark |
| 6 | Opus Value | +7.13% | -5.36% | -3.94% |
| 7 | Opus Quality Defensive | +5.17% | -10.81% | -5.91% |

Four of six portfolios beat the index. The AI-infrastructure trade kept working in
H1 2026: the ex-Mag7 suppliers basket won by a wide margin, and both the orchestrator's
conviction basket and the mechanical momentum screen (which converged on 5 of 10 names)
finished in a near-exact tie. The defensive and value books did what they usually do in
a melt-up: less drawdown-adjusted pain in the April dip, less upside overall.

## Files

- `portfolios/*.json` — each contestant's picks, rationale, and pre-cutoff backtest
- `fetch_data.py` — pulls daily adjusted closes (Yahoo Finance) for all tickers + SPY
- `evaluate.py` — builds equal-weight index series (base 100) and the ranking table
- `make_chart.py` — renders `chart.html` (self-contained, light/dark, interactive)
- `prices.csv`, `results.json`, `chart.html` — data and outputs as of 2026-07-15

Reproduce/update with:

```bash
python3 fetch_data.py && python3 evaluate.py && python3 make_chart.py
```

## Honesty caveats

- The orchestrator's picks were committed to git *before* any post-cutoff prices were
  fetched (see commit history), and agents were instructed never to request data past
  2026-01-02 — but model training data may overlap early-January 2026 market levels,
  so treat the first days as potentially contaminated.
- Survivorship of the experiment itself: this is one 6.5-month window in a strong tape;
  a basket that wins by riding one theme is not evidence of durable skill.
- Research/educational demo — not investment advice.
