# Account packet — Opus 5 trend following
as of the 2026-11-06 close  |  next trading date: 2026-11-09

## Round 3 book (`opus5_trend.json`)
- NAV **$948.77** from $1,000 → **-5.12%**  (SPY -0.83%, BTC +18.54%)
- max drawdown -5.50%  |  gross exposure 87%  |  cash 13%  |  11 positions
- strategy of record: Systematic time-series trend on signals refreshed through the 2026-10-30 close: long where price is above both the 50- and 200-day MAs with positive 3-month momentum (energy XLE/USO, dollar UUP, healthcare XLV, staples XLP), short where both MAs are broken with negative momentum (communication services XLC, gold GLD, silver SLV, copper miners COPX, uranium URA, emerging markets EEM), vol-scaled with the rest in cash.
- current leg entered 2026-11-02 (leg 14 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 20 | 67.2500 | 61.6200 | -8.37 | -18.0% | — |
| USO | equity | long |  | 9 | 156.8700 | 148.4100 | -5.39 | -15.0% | +35.0% |
| UUP | equity | long |  | 6 | 28.9600 | 29.1300 | +0.59 | -6.0% | — |
| XLV | equity | long |  | 12 | 184.6000 | 184.8000 | +0.11 | -10.0% | — |
| XLP | equity | long |  | 8 | 90.8300 | 90.0800 | -0.83 | -8.0% | — |
| XLC | equity | short |  | 8 | 100.2600 | 104.7900 | -4.52 | -10.0% | — |
| GLD | equity | short |  | 7 | 361.6500 | 372.5200 | -3.01 | -10.0% | — |
| SLV | equity | short |  | 4 | 45.5700 | 46.8700 | -2.85 | -15.0% | — |
| COPX | equity | short |  | 4 | 72.8400 | 71.2500 | +2.18 | -14.0% | — |
| URA | equity | short |  | 3 | 32.9300 | 32.3400 | +1.79 | -15.0% | — |
| EEM | equity | short |  | 6 | 61.1100 | 59.3300 | +2.91 | -9.0% | — |

- cash: 13%
