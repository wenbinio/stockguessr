# Account packet — Sonnet price momentum
as of the 2026-11-06 close  |  next trading date: 2026-11-09

## Round 2 book (`fleet_sonnet_price_momentum.json`)
- NAV **$862.87** from $1,000 → **-13.71%**  (SPY -1.81%, BTC +18.75%)
- max drawdown -17.73%  |  gross exposure 95%  |  cash 5%  |  6 positions
- strategy of record: Broad long/short sector-ETF momentum: own the sectors whose uptrend is confirming and accelerating (energy, E&P beta, semis, biotech) and short the rate-sensitive sectors whose downtrend is confirming ahead of tomorrow's FOMC (long-duration Treasuries, homebuilders), holding a small cash buffer.
- current leg entered 2026-09-16 (leg 7 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 25 | 63.6517 | 61.6200 | -3.19 | -12.0% | +30.0% |
| XOP | equity | long |  | 15 | 191.0383 | 173.7700 | -9.04 | -15.0% | +35.0% |
| SMH | equity | long |  | 15 | 545.5600 | 447.7300 (CLOSED STOP_LOSS 2026-11-05) | -17.93 realized | -15.0% | +35.0% |
| XBI | equity | long |  | 15 | 154.1800 | 152.2100 | -1.28 | -12.0% | +28.0% |
| TLT | equity | short |  | 15 | 80.8800 | 81.9200 | -1.29 | -8.0% | +15.0% |
| XHB | equity | short |  | 10 | 96.2617 | 107.5200 (CLOSED STOP_LOSS 2026-11-04) | -11.70 realized | -10.0% | +20.0% |

- cash: 5%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

**Standing orders that FIRED since the last poll:**
  - 2026-11-04 STOP_LOSS XHB (short) at 107.52
  - 2026-11-05 STOP_LOSS SMH (long) at 447.73

- lifetime standing-order fills on this book: 2 (SMH, XHB)

## Round 3 book (`fleet_sonnet_price_momentum.json`)
- NAV **$994.68** from $1,000 → **-0.53%**  (SPY -0.83%, BTC +18.54%)
- max drawdown -8.22%  |  gross exposure 80%  |  cash 20%  |  4 positions
- strategy of record: Concentrated, leveraged expression of the same price-momentum mandate as the Round 2 book: leveraged semiconductors and BTC spot as the highest-conviction uptrends, a leveraged oil & gas E&P vehicle for beta-heavy energy exposure, and a utilities short as the cleanest confirmed negative-momentum trend on the board - zero symbol overlap with the Round 2 book.
- current leg entered 2026-09-16 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SOXL | equity | long |  | 20 | 103.9019 | 163.7100 (CLOSED TAKE_PROFIT 2026-10-02) | +57.56 realized | -20.0% | +50.0% |
| BTC | crypto | long |  | 25 | 76150.3203 | 75746.9297 | -0.53 | -20.0% | +50.0% |
| GUSH | equity | long |  | 20 | 46.1013 | 37.2500 | -19.20 | -25.0% | +50.0% |
| XLU | equity | short |  | 15 | 41.0184 | 43.1300 | -5.15 | -10.0% | +20.0% |

- cash: 20%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

- lifetime standing-order fills on this book: 3 (GDX, SOXL)
