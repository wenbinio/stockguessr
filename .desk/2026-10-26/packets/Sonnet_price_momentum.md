# Account packet — Sonnet price momentum
as of the 2026-10-23 close  |  next trading date: 2026-10-26

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$938.18** from $1,000 → **-6.18%**  (SPY +1.48%, BTC +27.10%)
- max drawdown -12.65%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 63.6517 | 69.3300 | +8.92 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.0383 | 201.6900 | +5.58 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 527.2000 | -3.37 | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 149.5400 | -3.01 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.5556 | 81.3400 | -0.97 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.2617 | 98.3800 | -2.20 | -10.0% | +20.0% |

- cash: 5%

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$1,066.80** from $1,000 → **+6.68%**  (SPY +2.50%, BTC +26.88%)
- max drawdown -8.22%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9019 | 163.7100 (CLOSED TAKE_PROFIT 2026-10-02) | +57.56 realized | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | 76150.3203 | 81074.1875 | +6.47 | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.1013 | 50.7500 | +10.08 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.0184 | 42.5600 | -3.76 | -10.0% | +20.0% |

- cash: 20%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

- lifetime standing-order fills on this book: 3 (GDX, SOXL)
