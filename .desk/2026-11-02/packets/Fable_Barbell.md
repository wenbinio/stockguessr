# Account packet — Fable Barbell
as of the 2026-10-30 close  |  next trading date: 2026-11-02

## Round 2 book (`fable_barbell.json`)
- NAV **$1,027.53** from $1,000 → **+2.75%**  (SPY +0.92%, BTC +21.02%)
- max drawdown -2.91%  |  gross exposure 60%  |  cash 40%  |  8 positions
- strategy of record: Risk-balanced barbell for a Fed on hold but a 5.3% ten-year and $100 oil: 25% aggressive AI-infra compounders (NVDA/AVGO/ANET) with stops ratcheted up to the new fill and take-profits attached, against 35% rate-resilient ballast (Berkshire, energy, gold, pharma) and 40% yielding cash.
- current leg entered 2026-10-05 (leg 6 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| NVDA | equity | long |  | 12 | 238.9000 | 204.6400 | -14.34 | -18.0% | +40.0% |
| AVGO | equity | long |  | 8 | 362.5100 | 326.0800 | -10.05 | -18.0% | +40.0% |
| ANET | equity | long |  | 5 | 206.9000 | 168.8600 (CLOSED STOP_LOSS 2026-10-30) | -18.39 realized | -18.0% | +40.0% |
| BRK-B | equity | long |  | 14 | 504.2600 | 542.4900 | +7.58 | — | — |
| XLE | equity | long |  | 8 | 63.4500 | 70.0200 | +10.35 | -15.0% | +25.0% |
| GLD | equity | long |  | 5 | 379.5500 | 355.7800 | -6.26 | — | — |
| MRK | equity | long |  | 4 | 139.5400 | 149.5200 | +7.15 | — | — |
| JNJ | equity | long |  | 4 | 252.9300 | 273.2000 | +8.01 | — | — |

- cash: 40%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

**Standing orders that FIRED since the last poll:**
  - 2026-10-30 STOP_LOSS ANET (long) at 168.86

- lifetime standing-order fills on this book: 2 (ANET, BTC-USD)

## Round 3 book (`fable_barbell.json`)
- NAV **$972.63** from $1,000 → **-2.74%**  (SPY +1.92%, BTC +20.81%)
- max drawdown -4.53%  |  gross exposure 60%  |  cash 40%  |  7 positions
- strategy of record: Cross-sectional sector-momentum long/short re-ranked on the tape through 10-16 with Brent at $110, a 5.1% ten-year and a Fed holding in October ahead of a December hike: long energy, consumer staples and health care versus short the bottom of the cross-section in real estate, industrials, consumer discretionary and communication services, correlation-deduped with hard stops and take-profits and 40% yielding cash.
- current leg entered 2026-10-19 (leg 11 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 12 | 67.8000 | 70.0200 | +3.27 | -12.0% | +20.0% |
| XLP | equity | long |  | 12 | 87.2100 | 89.4200 | +2.53 | -12.0% | +20.0% |
| XLV | equity | long |  | 10 | 175.6500 | 184.8700 | +5.25 | -12.0% | +20.0% |
| XLRE | equity | short |  | 7 | 41.6700 | 43.1700 | -3.60 | -10.0% | +20.0% |
| XLI | equity | short |  | 7 | 166.6800 | 167.4000 | -0.43 | -10.0% | +20.0% |
| XLY | equity | short |  | 7 | 114.4600 | 115.3800 | -0.80 | -10.0% | +20.0% |
| XLC | equity | short |  | 5 | 110.0900 | 99.9000 | +9.26 | -10.0% | +20.0% |

- cash: 40%

- lifetime standing-order fills on this book: 3 (GDXJ, SLV, URNM)
