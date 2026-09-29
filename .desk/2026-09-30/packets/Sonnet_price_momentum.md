# Account packet — Sonnet price momentum
as of the 2026-09-28 close  |  next trading date: 2026-09-30

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$927.79** from $1,000 → **-7.22%**  (SPY +2.24%, BTC +30.90%)
- max drawdown -12.65%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 63.6517 | 62.1000 | -2.44 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.0383 | 180.1400 | -5.70 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 600.0100 | +9.98 | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 156.6100 | +1.58 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.8800 | 78.6200 | +2.79 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.2617 | 97.3000 | -1.08 | -10.0% | +20.0% |

- cash: 5%

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$1,006.33** from $1,000 → **+0.63%**  (SPY +3.26%, BTC +30.68%)
- max drawdown -8.22%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9019 | 142.2900 | +36.95 | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | — | 83502.6094 | — | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.1013 | 40.8300 | -11.43 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.0184 | 39.2500 | +4.31 | -10.0% | +20.0% |

- cash: 20%

- lifetime standing-order fills on this book: 2 (GDX, SOXL)
