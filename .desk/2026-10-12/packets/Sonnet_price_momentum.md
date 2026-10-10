# Account packet — Sonnet price momentum
as of the 2026-10-09 close  |  next trading date: 2026-10-12

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$947.95** from $1,000 → **-5.20%**  (SPY +3.97%, BTC +29.41%)
- max drawdown -12.65%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 63.6517 | 65.0800 | +2.24 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.0383 | 191.5200 | +0.25 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 603.3300 | +10.59 | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 153.7700 | -0.27 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.5556 | 77.9800 | +3.20 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.2617 | 94.7700 | +1.55 | -10.0% | +20.0% |

- cash: 5%

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$1,055.26** from $1,000 → **+5.53%**  (SPY +5.01%, BTC +29.18%)
- max drawdown -8.22%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9019 | 163.7100 (CLOSED TAKE_PROFIT 2026-10-02) | +57.56 realized | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | — | 82546.3203 | — | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.1013 | 45.9500 | -0.33 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.0184 | 41.4100 | -0.95 | -10.0% | +20.0% |

- cash: 20%

- lifetime standing-order fills on this book: 3 (GDX, SOXL)
