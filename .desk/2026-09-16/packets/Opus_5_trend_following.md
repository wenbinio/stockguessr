# Account packet — Opus 5 trend following
as of the 2026-09-14 close  |  next trading date: 2026-09-16

## Round 3 book (`opus5_trend.json`)
- NAV **$982.69** from $1,000 → **-1.73%**  (SPY +2.37%, BTC +22.32%)
- max drawdown -3.59%  |  gross exposure 90%  |  cash 10%  |  7 positions
- strategy of record: Systematic time-series trend across six asset classes with signals refreshed on data through the 2026-09-04 close: long where price is above both the 50- and 200-day moving average with positive 3-month momentum, short where both are negative, sized inversely to 60-day realised volatility and then tilted toward the strongest-ranked signals, with wide catastrophe stops because weekly reassessment is the real trend-exit mechanism.
- current leg entered 2026-09-08 (leg 8 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 17 | 64.7700 | 65.0800 | +0.48 | -20.0% | — |
| TLT | equity | short |  | 16 | 82.2000 | 80.6350 | +1.90 | -10.0% | — |
| SPY | equity | long |  | 16 | 765.9600 | 759.1700 | -0.89 | -12.0% | — |
| XLV | equity | long |  | 14 | 167.1300 | 166.6400 | -0.29 | -12.0% | — |
| CPER | equity | long |  | 12 | 40.5700 | 38.2600 | -5.69 | -20.0% | — |
| USO | equity | long |  | 10 | 146.0300 | 159.1600 | +8.99 | -25.0% | +40.0% |
| BTC | perp | long | 1 | 5 | — | 78163.3828 | — | -25.0% | +45.0% |

- cash: 10%
