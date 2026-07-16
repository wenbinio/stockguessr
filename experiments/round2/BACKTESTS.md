# Round 2 — pre-registration backtests

Before any Round-2 capital was (virtually) deployed, every flagship agent was
required to backtest its construction — including any leverage, short, or
crypto element — on historical windows, using the same cost model the live
engine charges. The orchestrator's backtest was run through the engine itself
(`tracker/round2.py --backtest`), which doubles as the engine's validation.
Fleet (Sonnet/Haiku) agents run tools-disabled and therefore allocate from
knowledge + provided context without their own backtests.

These blocks are extracted verbatim from the pre-registered allocation files
in `allocations/` (see git history for the pre-entry timestamps). Note what
the process caught: several constructions were **rejected by their own
backtests** before registration — details in each agent's notes.

---

## Claude Fable (orchestrator)  (fable)

**Round-2 strategy:** Concentrated AI-infrastructure conviction, unlevered, with a small contrarian BTC spot leg and dry powder for weekly dip-buying

**Book:** 8 positions, 78% gross exposure, 0% short, 22% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2026H1 | +61.1% | +11.1% |
| 2025H2 | +33.9% | +9.9% |

**Max drawdown:** 2026H1 -11.9%, 2025H2 -12.8%

**Method & honest caveats:** Run through the round-2 engine itself (tracker/round2.py --backtest) with full costs — this validates both the construction and the engine. Honest caveats: the 2026H1 window is heavily in-sample (these are the H1 winners I already knew); the BTC spot leg LOST money in both windows (-29% and -26%) — it is a contrarian entry at today's price, not a backtest-supported signal.

---

## Fable Unconstrained  (fable)

**Round-2 strategy:** Dual-momentum: long 6m leaders that are NOT in sharp 1m correction (cyber-tilted), small unlevered BTC mean-reversion, no leverage, fat cash at 4%

**Book:** 7 positions, 77% gross exposure, 0% short, 23% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2024H2 | +7.1% | +7.5% |
| 2025H1 | +9.7% | +5.7% |
| 2025H2 | +22.1% | +10.4% |
| 2026H1 | +72.4% | +10.5% |

**Method & honest caveats:** Rule = rank universe by trailing 6m return, exclude anything down >12% in trailing 1m, hold top 6 + cash. Beat/matched SPY 4/4 windows. REJECTED after testing: SOXL sleeve (-50.7% in 2024H2 stress) and 2x ETH perp short (2025H2 adverse move = 202% of margin = liquidation). Caveats: 42% cyber concentration is the main risk; momentum matched but did not beat SPY in the crash window.

---

## Fable Barbell  (fable)

**Round-2 strategy:** Risk-balanced barbell: 46% aggressive AI-infra compounders plus a small 2x contrarian BTC perp, against 38% defensive ballast (quality/staples/gold/utilities plus a 3% SOXL short as convexity hedge) and 18% yielding cash.

**Book:** 12 positions, 85% gross exposure, 3% short, 18% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2025H1 | +13.2% | +5.7% |
| 2026H1 | +5.4% | +9.3% |
| 2025_tariff_stress | -2.2% | -9.0% |
| 2026_april_stress | +5.6% | +11.6% |

**Method & honest caveats:** Barbell max drawdown -15.8%/-7.6% vs -40%/-15% for the aggressive sleeve alone - ballast cut DD by ~50-60%. The 3% BTC perp backtests negative by construction (the crash IS the entry thesis); the SOXL short cost 3-7pts in the 2026H1 semi bull and only pays in a correction.

---

## Opus Momentum  (opus)

**Round-2 strategy:** Leveraged long US semis/Nasdaq momentum (TQQQ/SOXL/SMH/AMD/MU/AVGO) funded partly by short crypto perps riding the persistent BTC/ETH/SOL downtrend, weekly-reassessed with a cash buffer.

**Book:** 8 positions, 113% gross exposure, 14% short, 15% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2025H2 | +35.8% | +9.9% |
| 2026H1 | +90.9% | +11.1% |
| 2024H2_adverse | -16.9% | +4.4% |

**Method & honest caveats:** 6mo buy-and-hold sim with real engine costs. Beat SPY by +26pp and +80pp in the two recent windows. Leverage-decay verified: leveraged ETFs reward trend persistence and punish reversal. Perp shorts printed +60-98% on margin as crypto fell, but a >32% adverse move at 3x approaches liquidation. Honest caveat: the -16.9% adverse window shows the whole book is one correlated momentum bet; weekly reassessment is the mitigation.

---

## Opus Value  (opus)

**Round-2 strategy:** Contrarian mean-reversion: buy deeply oversold crypto and depressed value/quality names, hedge with gold, modest short of frothy 3x-leveraged semis; prudent sizing after backtests showed momentum-shorting is a portfolio killer.

**Book:** 10 positions, 87% gross exposure, 7% short, 17% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2024H2 | +16.9% | +7.5% |
| 2025H1 | -6.1% | +5.4% |
| 2025H2 | -5.2% | +10.4% |

**Method & honest caveats:** Strongly regime-dependent: beat SPY only when crypto rallied and semis crashed (2024H2), lagged when momentum persisted. Shorting momentum leaders was catastrophic in tests, so shorts cut to one small survivable SOXL leg.

---

## Opus Quality Defensive  (opus)

**Round-2 strategy:** Low-beta quality/defensive core (healthcare, quality factor, min-vol, staples) with a small gold diversifier and a disciplined 8% short on semis to express 'AI-infra overextended' without dominating the book.

**Book:** 7 positions, 88% gross exposure, 8% short, 12% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2025_tariff_crash | -5.2% | -19.0% |
| 2025_recovery | +3.1% | +24.5% |
| april_2026_drawdown | -3.6% | -9.1% |
| 2026_recovery | +0.9% | +19.4% |

**Method & honest caveats:** Hedge genuinely defends (captured ~25-40% of downside in both crashes) but the book lags rising markets hard. Inverse leveraged ETFs rejected: SOXS lost 98% in the 2026 recovery; a plain 8% SMH short is the disciplined insurance.

---

## Opus Picks-and-Shovels  (opus)

**Round-2 strategy:** Long diversified AI-infra suppliers (power + semi-cap + custom silicon) with a contained 15% 3x-semis leverage kicker and a small laggard short; leverage capped so the April-dip-style drawdown stays ~-14%, not -44%.

**Book:** 9 positions, 94% gross exposure, 5% short, 6% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| YTD_2026 | +87.6% | +11.1% |
| Q2_2026 | +75.6% | +15.5% |
| last_3M | +34.6% | +9.0% |
| april_dip_max_drawdown | -14.0% | -8.9% |

**Method & honest caveats:** SOXL decay check: daily compounding HELPED in the H1 uptrend (+294% actual vs +254% naive) but drove -43.5% peak-to-trough in the Feb-Mar dip. Capping SOXL at 15% cut basket drawdown to -14%. HONEST: in-sample basket of known H1 winners; short-term momentum has rolled over; a sideways H2 bleeds SOXL.

---

## Opus Broadening  (opus)

**Round-2 strategy:** Long-heavy breadth basket (small-cap + equal-weight + cyclical sectors, TNA-amplified) with a small anti-concentration QQQ short and a speculative crypto tail

**Book:** 10 positions, 96% gross exposure, 9% short, 4% cash

| Window | Strategy | Benchmark (SPY) |
|---|---|---|
| 2024 | +7.9% | +24.0% |
| 2024H2 | +7.1% | +7.5% |
| 2025 | +8.7% | +16.6% |
| 2025H2 | +14.1% | +10.4% |
| 2026H1 | +16.1% | +10.5% |

**Method & honest caveats:** Beats SPY only in breadth-leading regimes (2025H2, 2026H1); lags badly when megacaps reassert (2024). Never posted a losing window. Short overlays underperformed long-only breadth in EVERY window - the 9% QQQ short is thesis expression, not backtest-supported.

---

## Reading these honestly

- **2026H1 numbers are heavily in-sample.** Any window ending 2026-07-15 tests a
  book chosen with knowledge of that window's winners. The 2024/2025 windows and
  the stress zooms are the meaningful ones.
- **The rejections are the best evidence the process worked:** Fable
  Unconstrained dropped its SOXL sleeve (-50.7% in the 2024H2 stress) and a 2x
  ETH perp short (adverse move = 202% of margin = liquidation); Opus Value cut
  its shorts to one small leg after momentum-shorting proved "catastrophic";
  Opus Quality rejected inverse leveraged ETFs (SOXS -98% through a recovery).
- **The real test is forward:** all of this was registered before the
  2026-07-16 entry close, and the weekly Execution Desk scores what happens
  next. Backtest quality is a hypothesis, not a result.
