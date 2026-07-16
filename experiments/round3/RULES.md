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

## Fee schedule (amended 2026-07-16, applies to all fills both rounds)

Per side, fraction of notional:
- Equities/ETFs: 2bps half-spread (large-cap/major ETF), 5bps leveraged ETFs,
  12bps names under $15; sells add SEC + FINRA TAF (0.31bps); $0 commission.
- Crypto spot: 35bps (retail taker fee + spread).
- Crypto perps: 7.5bps on notional (taker + spread); funding 10% APR unchanged.
- Short borrow 3% APR and cash 4% APY unchanged.

## Standing orders ("act throughout")

At any reassessment, an agent may attach `stop_loss_pct` and/or
`take_profit_pct` to any position. The engine evaluates them at every daily
close between reassessments and executes at that close (timestamped fill,
exit fees charged, proceeds earn cash yield from that date). This gives agents
intraweek agency without daily prompting.

## Point-in-time data discipline

An agent acting on date D — at entry, a weekly reassessment, or in any
backtest — may consult price data through D and nothing later. Live forward
legs enforce this by physics; backtests and replays enforce it by rule, and
desk prompts state it explicitly.

## Factorial arms (methodology-review adoption, 2026-07-16)

Beyond the 28 main agents, Round 3 adds 10 factorial accounts to break the
tier/tooling/backtest confound. These run WITHOUT the novelty rule, on five
standard fleet mandates (deep value, price momentum, quality compounders,
dividend growth, small/mid growth):

- 5 x Sonnet WITH flagship treatment (data tools + mandatory backtest)
- 5 x Opus WITHOUT tools (fleet treatment: knowledge + mechanical context only)

Tagged `group: "factorial"`; scored identically; excluded from the novelty
divergence panel.

## Context hygiene (binding)

- Tools-disabled agents receive a MECHANICALLY GENERATED context pack
  (script-emitted return tables, no authored narrative), identical across
  agents, committed pre-entry (`context_pack.txt`).
- R3 agents must not be shown Round-2 allocations, leaderboards, other agents'
  output, or BACKTESTS.md. Tool-enabled agents are instructed to fetch market
  data only (no repo reads); compliance is transcript-auditable.
- Point-in-time rule applies: acting on date D means data through D only.

## Fill convention (unified)

Decisions are committed strictly before the fill close; all R3 fills occur at
the first close after commitment (2026-07-17 for the opening book). The
Round-1 H2 leg's same-close marking is documented as a known inconsistency.
