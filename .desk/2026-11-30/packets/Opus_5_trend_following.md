# Account packet — Opus 5 trend following
as of the 2026-11-27 close  |  next trading date: 2026-11-30

## Round 3 book (`opus5_trend.json`)
- NAV **$965.12** from $1,000 → **-3.49%**  (SPY -1.77%, BTC -6.31%)
- max drawdown -6.56%  |  gross exposure 82.0%  |  cash 18%  |  14 positions
- strategy of record: Systematic time-series trend on signals refreshed through the 2026-11-20 close: long where price is above both the 50- and 200-day MAs with positive 3-month momentum (healthcare XLV, staples XLP, dollar UUP), short where both are broken with negative 3-month momentum (XLC, GLD, SLV, COPX, URA, EEM, XLK, SMH, IWM, XLI, DBA), sized inversely to 20-day realized volatility, with the rest in cash.
- current leg entered 2026-11-23 (leg 16 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLV | equity | long |  | 7 | 179.4200 | 184.2000 | +2.66 | -7.0% | — |
| XLP | equity | long |  | 9 | 90.3800 | 92.6800 | +2.54 | -7.0% | — |
| UUP | equity | long |  | 10 | 29.7800 | 29.7200 | -0.20 | -4.0% | — |
| XLC | equity | short |  | 8 | 103.6000 | 107.4800 | -3.75 | -9.0% | — |
| GLD | equity | short |  | 6 | 333.0200 | 334.4000 | -0.41 | -10.0% | — |
| SLV | equity | short |  | 4 | 38.9100 | 39.4000 | -1.26 | -14.0% | — |
| COPX | equity | short |  | 3.5 | 60.1500 | 61.3400 | -1.98 | -16.0% | — |
| URA | equity | short |  | 3.5 | 28.3700 | 29.1700 | -2.82 | -16.0% | — |
| EEM | equity | short |  | 5 | 57.8300 | 58.1000 | -0.47 | -11.0% | — |
| XLK | equity | short |  | 4 | 162.3800 | 160.1500 | +1.37 | -15.0% | — |
| SMH | equity | short |  | 3 | 460.1800 | 440.0600 | +4.37 | -20.0% | — |
| IWM | equity | short |  | 7 | 265.7400 | 273.7900 | -3.03 | -9.0% | — |
| XLI | equity | short |  | 7 | 162.4700 | 165.5600 | -1.90 | -9.0% | — |
| DBA | equity | short |  | 5 | 26.2400 | 26.7500 | -1.94 | -8.0% | — |

- cash: 18%
