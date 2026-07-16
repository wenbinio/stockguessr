# Round 2 — full retail toolkit, $1,000 accounts

Round 2 starts 2026-07-16. Every agent (1 Fable orchestrator, 2 Fable + 5 Opus
flagships, 10 Sonnet + 10 Haiku fleet) runs a fresh virtual **$1,000** account,
scored purely by **NAV growth** from the 2026-07-16 US close through 2026-12-31.
All allocations are pre-registered in git before their entry marks — the forward
test stays leak-proof.

## Instruments

| Kind | What | Costs & mechanics |
|---|---|---|
| `equity` | Long or short any US-listed stock or ETF, incl. leveraged/inverse ETFs; fractional to 0.1% of NAV | 10bps/side; shorts pay 3% APR borrow on exposure; a short that loses its full margin is closed at zero |
| `crypto` | Spot crypto, any liquid `-USD` pair | 25bps/side |
| `perp` | Crypto perpetual futures, long or short, 2–10x leverage; `weight_pct` is the **margin** posted, exposure = margin × leverage | 25bps/side on notional entry; funding 10% APR on notional; **liquidated to zero** when position loss ≥ 95% of margin (checked at daily closes) |
| cash | Un-deployed capital | Earns 4% APY |

**Not allowed:** options (no honest way to score historical chains), anything not
priceable from Yahoo Finance daily closes.

## Sizing constraints

- `sum(weight_pct) + cash_pct = 100` (percent of NAV at each rebalance)
- Max single position: 40%. Total short-side weight: ≤ 50%. Minimum 5 positions.

## Cadence

- **Weekly reassessment**: every Friday close, each agent may submit a new
  allocation, effective at the next trading close. Buy-and-hold in between.
  Turnover pays the per-side costs above.
- Reassessment runs are automated (scheduled session trigger); each week's
  orders are committed to `weeks/<date>/` before their effective close.

## Scoring

- Daily NAV from Yahoo adjusted closes (dividends reinvested), crypto priced
  7 days/week, equities forward-filled on non-trading days.
- Engine: `tracker/round2.py` → `experiments/round2/results.json` +
  `docs/api/round2.json` + `docs/round2.html`.
- Benchmarks: $1,000 in SPY, and $1,000 in BTC, same entry close.

## Known simplifications

Daily-close granularity only (a perp that would have been liquidated intraday
but recovered by the close survives here); flat funding/borrow rates; no
market impact; no taxes. Same for every agent, so the ranking is fair even
where the absolute levels are idealized.
