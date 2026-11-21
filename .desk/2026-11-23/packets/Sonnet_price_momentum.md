# Account packet — Sonnet price momentum
as of the 2026-11-20 close  |  next trading date: 2026-11-23

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$843.77** from $1,000 → **-15.62%**  (SPY -7.89%, BTC -7.82%)
- max drawdown -19.25%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 63.6517 | 60.5100 | -4.94 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.0383 | 168.0600 | -12.03 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 447.7300 (CLOSED STOP_LOSS 2026-11-05) | -17.93 realized | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 140.1800 | -9.08 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.2179 | 81.4500 | -1.54 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.2617 | 107.5200 (CLOSED STOP_LOSS 2026-11-04) | -11.70 realized | -10.0% | +20.0% |

- cash: 5%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

- lifetime standing-order fills on this book: 2 (SMH, XHB)

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$933.69** from $1,000 → **-6.63%**  (SPY -6.97%, BTC -7.98%)
- max drawdown -12.94%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9019 | 163.7100 (CLOSED TAKE_PROFIT 2026-10-02) | +57.56 realized | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | 76150.3203 | 58798.9805 (CLOSED STOP_LOSS 2026-11-20) | -22.79 realized | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.1013 | 34.6000 | -24.95 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.0184 | 42.6900 | -4.08 | -10.0% | +20.0% |

- cash: 20%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

**Standing orders that FIRED since the last poll:**
  - 2026-11-20 STOP_LOSS BTC-USD (long) at 58798.9805

- lifetime standing-order fills on this book: 4 (BTC-USD, GDX, SOXL)
