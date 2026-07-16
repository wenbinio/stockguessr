# Round 3 — novel strategies, $1,000 accounts

Round 3 opens at the **2026-07-17 US close**. Same account mechanics as Round 2
(see `../round2/RULES.md`: $1,000 virtual capital, long/short US equities & ETFs
including leveraged, crypto spot, crypto perps 2–10x with funding and
liquidation, weekly Friday reassessment, NAV scoring vs $1,000-in-SPY and
$1,000-in-BTC, engine `tracker/round2.py --round 3`), with **one new rule**:

## The novelty requirement

Every agent must deploy a strategy **materially different from both its
Round-1 mandate and its Round-2 construction**:

- A different return *driver* (not just different tickers for the same thesis).
  An agent whose R1/R2 books were long AI-momentum may not submit long
  AI-momentum with new names; it must find a different edge hypothesis
  (e.g. carry, pairs/relative value, event-driven, seasonality, vol-regime
  switching, cross-asset rotation, dispersion...).
- Each allocation must include a `novelty` field: 2-3 sentences stating the
  edge hypothesis and how it differs from that agent's previous two books.
- Flagship agents must backtest the novel construction before registering it
  (same standard as Round 2); the orchestrator's backtest runs through the
  engine itself.
- The Execution Desk validates novelty at registration: an R3 book sharing
  more than 50% of its gross weight with the same-direction positions of that
  agent's R2 book is rejected and re-requested.

## What this tests

Rounds 1-2 measured how well agents ride their assigned/natural strategies.
Round 3 measures **inventiveness under constraint**: does forcing a new edge
hypothesis destroy performance (strategies were load-bearing) or preserve it
(the model's judgment generalizes)? Scored in flat dollars earned, like
everything else.

## Reporting

Results feed `docs/api/round3.json` and the Round-3 tab of the hub, including
the novelty statements and a divergence panel (R3 vs R2 book overlap per
agent — expected to be near zero by construction).
