# Account packet — Haiku deep value
as of the 2026-11-20 close  |  next trading date: 2026-11-23

## Round 2 book (`fleet_haiku_deep_value.json`)
- NAV **$970.46** from $1,000 → **-2.95%**  (SPY -7.89%, BTC -7.82%)
- max drawdown -12.31%  |  gross exposure 83%  |  cash 17%  |  9 positions
- strategy of record: Core value exposure (SPY/VTV) with tactical plays on beaten-down software (ADBE/CRM), defensive dividend anchors (JPM/KO), small tech hedges (SQQQ short), crypto capitulation (BTC spot 4%), tactical GLD short, 17% cash for rebalancing.
- current leg entered 2026-07-16 (leg 1 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| SPY | equity | long |  | 18 | 748.8604 | 689.8100 | -7.89 | — | — |
| VTV | equity | long |  | 15 | 217.8520 | 214.2200 | -1.67 | — | — |
| ADBE | equity | long |  | 12 | 235.3100 | 217.7100 | -7.48 | — | — |
| CRM | equity | long |  | 10 | 172.3767 | 180.6200 | +4.78 | — | — |
| JPM | equity | long |  | 10 | 341.4465 | 310.5300 | -9.05 | — | — |
| KO | equity | long |  | 7 | 84.4163 | 96.9900 | +14.89 | — | — |
| GLD | equity | short |  | 4 | 364.9600 | 322.8700 | +11.53 | — | — |
| SQQQ | equity | short |  | 3 | 40.3173 | 57.5900 | -42.84 | — | — |
| BTC-USD | crypto | long |  | 4 | 63789.2812 | 58798.9805 | -7.82 | — | — |

- cash: 17%

## Round 3 book (`fleet_haiku_deep_value.json`)
- NAV **$993.81** from $1,000 → **-0.62%**  (SPY -6.97%, BTC -7.98%)
- max drawdown -5.08%  |  gross exposure 59%  |  cash 41%  |  4 positions
- strategy of record: Rate-regime rotation: long energy and financials, a small bitcoin spot sleeve, and a short on QQQ as a semiconductor and rate-hike hedge, with 41% cash.
- current leg entered 2026-10-19 (leg 5 of this book's history)

| symbol | kind | side | lev | wt% | entry fill | mark | leg P&L% | stop | TP |
|---|---|---|---|---|---|---|---|---|---|
| XLE | equity | long |  | 30 | 67.8000 | 60.5100 | -10.75 | -12.0% | +25.0% |
| XLF | equity | long |  | 15 | 55.0600 | 54.5700 | -0.89 | -10.0% | +18.0% |
| BTC-USD | crypto | long |  | 4 | 81853.5391 | 68249.2734 (CLOSED STOP_LOSS 2026-11-13) | -16.62 realized | -15.0% | +40.0% |
| QQQ | equity | short |  | 10 | 718.3600 | 608.4500 (CLOSED TAKE_PROFIT 2026-11-20) | +15.30 realized | -8.0% | +15.0% |

- cash: 41%
- note: weights, gross exposure and cash are as registered at entry; a leg marked CLOSED has been sold and its proceeds are now cash.

**Standing orders that FIRED since the last poll:**
  - 2026-11-20 TAKE_PROFIT QQQ (short) at 608.45

- lifetime standing-order fills on this book: 3 (BTC-USD, QQQ)
