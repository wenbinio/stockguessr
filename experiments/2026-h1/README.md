# H1 2026 experiment: 28 Claude portfolios vs the S&P 500

A live run of the StockGuessr idea at portfolio scale. Portfolios were formed with
knowledge frozen at the January 2026 model cutoff, virtually bought at the 2026-01-02
close (equal weight, no rebalancing), and scored against real market prices through
2026-07-15.

## Contestants

**Flagship tier (8)** — one portfolio each, with a mandatory pre-cutoff backtest:

| Portfolio | Picked by | Strategy |
|---|---|---|
| Claude Fable (orchestrator) | claude-fable-5 | Concentrated AI-infrastructure conviction basket |
| Fable Unconstrained | fable subagent | Unconstrained best ideas |
| Fable Barbell | fable subagent | Risk-balanced barbell (5 aggressive + 5 ballast) |
| Opus Momentum | opus subagent | 12-1 cross-sectional momentum |
| Opus Value | opus subagent | Value / contrarian mean-reversion |
| Opus Quality Defensive | opus subagent | Quality / low-volatility defensive |
| Opus Picks-and-Shovels | opus subagent | AI infrastructure suppliers, Mag-7 forbidden |
| Opus Broadening | opus subagent | Anti-concentration / breadth catch-up |

**Fleet tier (20)** — 10 Sonnet + 10 Haiku agents, one style mandate each (GARP, deep
value, momentum, quality, dividend, small/mid growth, macro rotation, AI/tech,
contrarian, global). Fleet agents ran with tools disabled: pure cutoff-knowledge picks,
no data access at all.

## Result (2026-01-02 → 2026-07-15, gross)

Flagship ranking:

| # | Portfolio | Gross | Net* | Beta | CAPM α | Luck pctile** |
|---|---|---|---|---|---|---|
| 1 | Opus Picks-and-Shovels | +57.45% | +57.12% | 2.52 | +32.78% | 100.0 |
| 2 | Fable Unconstrained | +47.94% | +47.61% | 2.60 | +22.57% | 99.7 |
| 3 | Claude Fable (orchestrator) | +45.19% | +44.86% | 2.11 | +24.21% | 99.6 |
| 4 | Opus Momentum | +45.18% | +44.86% | 2.00 | +25.14% | 99.6 |
| 5 | Fable Barbell | +32.82% | +32.52% | 1.35 | +18.60% | 96.2 |
| 6 | Opus Broadening | +11.31% | +10.95% | 1.01 | +0.12% | 54.4 |
| — | **S&P 500 (SPY)** | **+11.07%** | **+10.76%** | 1.00 | — | 53.7 |
| 7 | Opus Value | +7.13% | +6.59% | 0.15 | +3.64% | 40.1 |
| 8 | Opus Quality Defensive | +5.17% | +4.79% | −0.07 | +3.67% | 33.5 |

\* Net of 10bps/side trading costs and 15% tax on the dividend component of return.
\*\* Share of 2,000 random equal-weight 10-stock baskets (drawn from the ~100 largest
S&P names) that the portfolio beat.

Average gross return by model tier: **Fable +42.0%** (3 portfolios) > **Opus +25.2%**
(5) > **Haiku +15.1%** (10) > **Sonnet +6.5%** (10) > SPY +11.1% sits between the two
fleets. 16 of 28 portfolios beat the index; the spread ran from +57.5% (Opus
Picks-and-Shovels) to −20.3% (Sonnet small/mid-cap growth). Full table in
`results.json` and `chart.html`.

The AI-infrastructure trade kept working in H1 2026, so portfolios that leaned into it
won, and the CAPM alphas show the caveat that matters: high-beta baskets get a lot of
their raw excess return from amplified market exposure. Even so, the top four flagship
books cleared 99%+ of random baskets — hard to attribute to luck alone within this
window.

## Friction model (what "Net" removes)

- Trading costs: 10bps per side (entry + exit) on every position — spread + impact proxy.
- Dividend tax: 15% of the dividend component, isolated per ticker as the ratio of the
  adjusted-close factor to the raw-close factor over the window.
- Still ignored (would further shrink real-world results): market impact at size,
  capital-gains tax on exit, cash drag, borrow/financing, and any rebalancing.
- CAPM α uses realized daily beta vs SPY and a 4% annualized risk-free rate.

## Files

- `portfolios/*.json` — every contestant's picks, rationale, and (flagship) backtest
- `universe.json` — the ~100-name universe the bootstrap null draws from
- `fetch_data.py` — pulls daily adjusted + raw closes (Yahoo Finance) for all tickers
- `evaluate.py` — gross/net returns, drawdown, beta, CAPM α, bootstrap percentiles
- `make_chart.py` — renders `chart.html` (self-contained, light/dark, interactive)
- `prices.csv`, `prices_raw.csv`, `results.json`, `chart.html` — data and outputs

Reproduce/update with:

```bash
python3 fetch_data.py && python3 evaluate.py && python3 make_chart.py
```

## Honesty caveats

- The orchestrator's picks were committed to git *before* any post-cutoff prices were
  fetched (see commit history); flagship agents were instructed never to request data
  past 2026-01-02; fleet agents had no tool access at all. But model training data may
  overlap early-January 2026 market levels, so treat the first days as potentially
  contaminated.
- One 6.5-month window in a strong tape; several unfetchable fleet tickers were dropped
  from their baskets (recorded in `failed_tickers.json` / `results.json`).
- Running 28 portfolios and celebrating the winners is itself selection bias — that is
  exactly what the bootstrap percentile column is there to discipline.
- Research/educational demo — not investment advice.
