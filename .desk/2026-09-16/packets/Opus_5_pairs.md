# Account packet — Opus 5 pairs
as of the 2026-09-14 close  |  next trading date: 2026-09-16

## Round 3 book (`opus5_pairs.json`)
- NAV **$1,004.58** from $1,000 → **+0.46%**  (SPY +2.37%, BTC +22.32%)
- max drawdown -1.07%  |  gross exposure 90.0%  |  cash 10%  |  10 positions
- strategy of record: Five market-neutral relative-value pairs (XLI/VTV, ITA/RSP, MTUM/XLK, STLD/NUE, IJR/IWD) chosen from a 279-symbol, 3,000-pair screen for a 250-day log-spread z-score of 2.2-3.4 sigma AND hard evidence of stationarity - 17 to 32 crossings of the spread's own mean in the past year, under 20% two-year drift, daily-return correlation above 0.57 and a mean-reversion half-life of 10-26 trading days - then filtered by hand to remove every pair whose dislocation was caused by a fresh fundamental catalyst on the leg being faded, with each pair sized to cancel its long and short SPY betas (short/long ratio capped at 1.35 so the position still tracks the measured 1:1 log spread), leaving a regression-measured net SPY beta of +3.0% of NAV.
- current leg entered 2026-09-08 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLI | equity | long |  | 9.8 | 174.4200 | 169.8250 | -2.63 | — | — |
| VTV | equity | short |  | 13.2 | 224.6400 | 222.6300 | +0.89 | — | — |
| ITA | equity | long |  | 8.8 | 223.5300 | 216.2600 | -3.25 | — | — |
| RSP | equity | short |  | 11.8 | 216.7300 | 214.2600 | +1.14 | — | — |
| MTUM | equity | long |  | 9.3 | 308.6900 | 300.8000 | -2.56 | — | — |
| XLK | equity | short |  | 8.3 | 187.8700 | 185.0700 | +1.49 | — | — |
| STLD | equity | long |  | 6.8 | 240.3100 | 236.7150 | -1.50 | — | — |
| NUE | equity | short |  | 8.3 | 256.4000 | 256.2900 | +0.04 | — | — |
| IJR | equity | long |  | 5.9 | 144.2500 | 140.3700 | -2.69 | — | — |
| IWD | equity | short |  | 7.8 | 255.5300 | 253.7400 | +0.70 | — | — |

- cash: 10%
