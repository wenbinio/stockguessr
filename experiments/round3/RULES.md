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

## The Opus 5 field (added 2026-07-26, entry 2026-07-27)

A dedicated single-model cohort: **8 accounts, all Opus 5, all tool-enabled,
all mandatorily backtested**. Tagged `group: "opus5"`, stems `opus5_*`.

Where the factorial arms hold the mandate fixed and vary the model, this
cohort holds the **model fixed and varies the return driver**, so the spread
within it is attributable to strategy selection rather than tier. Each account
is assigned a distinct, pre-registered edge hypothesis, none of which is
long-AI-momentum (the driver that dominates the R1/R2/R3 field):

1. `opus5_carry` — cross-asset carry: perp funding, cash yield, borrow spreads
2. `opus5_pairs` — market-neutral relative value / statistical pairs
3. `opus5_meanrev` — cross-sectional short-horizon mean reversion (buy losers)
4. `opus5_trend` — multi-asset trend following (managed-futures style)
5. `opus5_volregime` — volatility-regime switching and vol targeting
6. `opus5_dispersion` — dispersion: long idiosyncratic names vs short index
7. `opus5_seasonality` — calendar/flow effects and month-end positioning
8. `opus5_eventdriven` — catalyst/event-driven and corporate-action driven

Binding conditions:

- **Point-in-time**: data through the **2026-07-24** close only (the last
  completed session before registration). Books are committed before the
  2026-07-27 fill close.
- **Mandatory backtest**: every account backtests its own construction through
  the engine itself (`tracker/round2.py --backtest <entry> <end> <file>`) over
  **at least two windows**, one of which must end before 2026-01-01, and
  records the result verbatim in a `backtest` block. Costs, funding,
  liquidation and standing orders are therefore applied by the same code that
  scores the live round.
- **Cross-cohort distinctness**: no two Opus 5 books may share more than 50%
  of gross weight in the same direction; the desk checks this pairwise at
  registration (the field's analogue of the per-agent novelty rule, which
  cannot apply here because these accounts have no R1/R2 history).
- **Context hygiene**: these agents fetch market data only. They may read the
  rules and the engine source; they may not read any `allocations/`,
  `results.json`, `fills.jsonl`, desk logs, `docs/`, or another agent's output.
- **Later entry is disclosed**: this cohort enters at the 2026-07-27 close,
  seven sessions after the 2026-07-17 Round-3 field. Absolute NAV is therefore
  not directly comparable to the original field; the cohort is scored against
  SPY over its own window, and the hub labels the entry date.

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
