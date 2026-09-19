# Account packet — Sonnet price momentum
as of the 2026-09-18 close  |  next trading date: 2026-09-21

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$931.72** from $1,000 → **-6.83%**  (SPY +1.71%, BTC +26.83%)
- max drawdown -12.65%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 64.0300 | 64.3100 | +0.44 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.8000 | 190.6100 | -0.62 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 573.0000 | +5.03 | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 156.7200 | +1.65 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.8800 | 81.2500 | -0.46 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.8000 | 96.3900 | +0.42 | -10.0% | +20.0% |

- cash: 5%

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$978.59** from $1,000 → **-2.14%**  (SPY +2.73%, BTC +26.61%)
- max drawdown -8.22%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9700 | 123.6700 | +18.95 | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | — | 80901.4609 | — | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.2600 | 45.7100 | -1.19 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.3200 | 41.1000 | +0.53 | -10.0% | +20.0% |

- cash: 20%

- lifetime standing-order fills on this book: 2 (GDX, SOXL)
