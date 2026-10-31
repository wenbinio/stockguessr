# Account packet — Sonnet price momentum
as of the 2026-10-30 close  |  next trading date: 2026-11-02

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$943.33** from $1,000 → **-5.67%**  (SPY +0.92%, BTC +21.02%)
- max drawdown -12.65%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 63.6517 | 70.0200 | +10.00 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.0383 | 203.7600 | +6.66 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 522.4900 | -4.23 | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 155.9800 | +1.17 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.5556 | 81.8400 | -1.59 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.2617 | 100.9700 | -4.89 | -10.0% | +20.0% |

- cash: 5%

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$1,055.64** from $1,000 → **+5.56%**  (SPY +1.92%, BTC +20.81%)
- max drawdown -8.22%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9019 | 163.7100 (CLOSED TAKE_PROFIT 2026-10-02) | +57.56 realized | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | 76150.3203 | 77198.2109 | +1.38 | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.1013 | 51.5800 | +11.88 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.0184 | 43.4300 | -5.88 | -10.0% | +20.0% |

- cash: 20%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

- lifetime standing-order fills on this book: 3 (GDX, SOXL)
