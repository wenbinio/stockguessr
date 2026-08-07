# Forensic audit — the Round-2 / Round-3 Execution Desk

**Auditor mandate:** determine, from the files and the git history, whether the
orchestrator — who writes the rules, authors the prompts, runs the desk that
validates and repairs competitors' books, writes the analysis, and competes in
the tournament as `claude_fable` — actually abused any of the four discretionary
channels the 2026-08-07 methodology critique
(`experiments/reviews/design_critique_2026-08-07.md`) identified as
uncontrolled: repair discretion, prompt authorship, rule-amendment authorship,
reporting discretion.

**Auditor holds no book.** Scope: everything in the tree at commit `919ea0d`,
plus the full git history. Standard: the Round-1 forensic audit
(`experiments/2026-h1/AUDIT.md`) — every claim tied to a file, a commit or a
recomputed value, and every "clean" finding stated together with the test that
could have failed it.

---

## Verdict: **QUALIFIED**

The channels that the critique judged *controlled* are controlled, and I
verified them harder than the critique did. There is **no evidence that the
orchestrator favoured its own books**: it registered first, not last; it took no
repair, no exemption and no lower bar on registration; its books are scored by
the same code with no per-agent branching; and its one contested reasoning gap is
honestly declared and the underlying record genuinely pre-existed. On the
mechanics — fill convention, registration fidelity, rule compliance — the desk is
the cleanest part of the experiment: **1,381 of 1,381 fills** trace to a file
committed before that date's close, and **all 172 registered books** pass the
rules.

The qualification rests on four findings, none of which is self-dealing but two
of which are materially wrong:

1. **Ten registered books hold a live equity position the manager intended as
   cash** (Finding B1). `CASH` is Pathward Financial, Inc. (NasdaqGS); `USDC` is
   USDATA Corp. at $0.0012. The desk's repair machinery scaled these as if they
   were securities and the engine filled them. All ten are Haiku. This is an
   economics-changing outcome of accept-and-repair that no note in the repo
   discloses.
2. **The repair rule was not the same each time.** At week 2 the desk *deleted*
   seven negative stop-losses; five days later it adopted the opposite
   convention (*convert to magnitude*) and disclosed it. The week-2 handling is
   recorded nowhere (Finding B2).
3. **`check_reasoning.py` grades the orchestrator on a looser rule than everyone
   else** — a one-line fallback lets a single blended reason satisfy two separate
   round decisions, which no competitor is allowed (Finding A3).
4. **Amendment 2 was pre-registered by a competing participant four sessions
   after the window it governs had opened**, and it moves the drafter's own books
   from 17/28 → 6/28 (R2) and 14/47 → 6/47 (R3) (Finding G1). It is disclosed,
   defensible, and demonstrably *not* the most self-serving choice available —
   but it was not a blind call and it should not have been the drafter's to make.

Nothing found rises to fraud, concealment, or a rigged score. Findings 1 and 2
are process failures with a tier-differential incidence; findings 3 and 4 are
exactly the conflicts the critique named, caught operating at low amplitude.

---

## Q1 — Did the orchestrator's own books receive favourable treatment?

**Finding: no. Clean on every test I could construct.**

`claude_fable` runs one book per round: `experiments/round2/allocations/claude_fable.json`
(entry 2026-07-16), one reassessment `experiments/round2/weeks/2026-07-20/claude_fable.json`,
and `experiments/round3/allocations/claude_fable.json` (entry 2026-07-17, never
rebalanced).

### A1 — Registration ordering: the orchestrator locked in *first*, not last

The test that could have failed: if the orchestrator's week-1 book had been
committed *after* the 35 rival books, it could have front-run or copied them.

| commit | time (UTC) | contents |
|---|---|---|
| `1f9fc62` | 2026-07-18 **12:13:21** | **only** `round2/weeks/2026-07-20/claude_fable.json` (1 file, 89 lines) |
| `d3760c5` | 2026-07-18 **12:36:34** | the desk log + all 5 rival week-1 books |

The orchestrator committed its own book **23 minutes before** the field's. Same
for the opening books: `claude_fable` R2 sits inside `3a3e1bc` alongside the
other seven flagships (no separate, later commit), and `claude_fable` R3 sits
inside `7cc1a50` alongside 16 other books. It never registered after seeing a
rival's registration.

Corroborating evidence that it did not copy: at week 1 the field rotated *out* of
semis (Opus Momentum "rotating to current leaders", Sonnet price momentum "long
financials/healthcare, short SOXL/TQQQ"); `claude_fable` did the opposite,
deploying 9 points of cash *into* MU/AMD/NVDA. That trade then lost — its H2 curve
in `docs/api/performance.json` bottoms at **88.14** on 2026-07-29.

### A2 — Conventions, validation and repairs: identical, and it needed no help

- **Fill convention.** R2 book committed 2026-07-16 05:05:44 UTC, fills at the
  2026-07-16 close; R3 committed 2026-07-16 11:33:16 UTC, fills at the 2026-07-17
  close; week-1 rebalance committed 2026-07-18 12:13:21, fills at the 2026-07-20
  close. `experiments/round{2,3}/fills.jsonl` show 8 / 9 / 8 OPEN legs at exactly
  those closes and nothing else. Same convention as every other agent (Q5).
- **Arithmetic.** All three books sum to exactly 100 as submitted
  (78+22, 80+20, 87+13). **It never took a repair** — there is no
  `registration_note` on any orchestrator file.
- **Rule compliance.** Under the old caps: max single position 18%, zero shorts,
  8–9 positions, no perps. Comfortably inside every guardrail it wrote.
- **Novelty rule.** Recomputed same-direction gross-weight overlap between its R3
  and R2 books: **0.0%** — the strictest score in the field (compare Sonnet deep
  value 21.1%, Haiku contrarian turnarounds 19.3%; limit is 50%). It applied its
  own rule to itself at full force and its R3 book abandoned the AI-infra thesis
  entirely.
- **Backtest honesty.** `round3/allocations/claude_fable.json` `backtest.notes`
  records "HONEST FINDING: this novel construction UNDERPERFORMS SPY in both
  windows tested" and registers it anyway; the R2 block volunteers "the 2026H1
  window is heavily in-sample (these are the H1 winners I already knew)".
- **Scoring code.** `grep` for `Fable|orchestrator|claude_fable` across
  `tracker/round2.py`, `tracker/stats.py`, `tracker/make_performance_page.py`,
  `tracker/make_ledger.py` returns **no per-agent branching** — only a docstring
  and a tier label dict. There is no code path that treats its book differently.

### A3 — Where the standard *is* lower (two real asymmetries)

**(i) The reasoning checker has an orchestrator-only fallback.**
`tracker/check_reasoning.py:95` reads

```python
r = orc.get(f"{k}_reason") or orc.get("reason")
```

For every one of the 46 competing managers, `check_desk` (line 71) requires a
`reason` **on each round's decision object** with no fallback. For the
orchestrator, a single blended `reason` satisfies *both* the round-2 and round-3
checks. It used that latitude twice:

- `experiments/desk/week2_2026-07-25.json` `orchestrator`: one `reason` for two
  HOLDs.
- `experiments/desk/unrestricted_resize_2026-07-30.json` `orchestrator`: one
  `reason` for two HOLDs — and the text is **entirely about the R2 book**
  ("My R2 book is -10% and concentrated in exactly the AI-infra complex the tape
  is unwinding"). The Round-3 HOLD at the largest desk event of the round has no
  round-specific reason. Any competitor submitting that would have been flagged.

This was corrected by conduct at week 3 (`week3_2026-08-01.json` carries
`round2_reason` and `round3_reason` separately) but not by code — the fallback is
still in the file.

**(ii) The orchestrator files no `research_notes`.** At the two free-internet
events, all 46 managers carry a `research_notes` field (46/46 in both logs);
the `orchestrator` block carries none, in any log. Under rules whose central
change is *what information an agent went and got*, the one participant who
cannot be audited on that dimension is the participant who wrote the rules. Both
its decisions were HOLD, so the stakes are low, but the record is not to the same
standard.

**(iii) Structural, not fixable.** The orchestrator is the only participant that
necessarily reads every other book — it collects and commits them. Round-3
context hygiene (`round3/RULES.md:126-127`) forbids agents from reading
`allocations/`, `results.json`, desk logs and `docs/`; the orchestrator does all
of that by construction. I found no *use* of that access (A1 above is affirmative
evidence against it), but no artefact in the repo could rule it out.

### A4 — Did it ever trade on information others did not have?

No trade in the R2/R3 record supports that. Its only reassessment cites SOXL
-29.5% for the week ending 2026-07-17 — the same figure quoted by six other
managers in the same log. Scanning all 280 desk decisions plus 92
`research_notes` blobs for date references later than the desk-run date returned
**34 hits, every one prospective** (scheduled earnings — "NVDA earnings 8/26",
"CRSP 8/3" — or seasonality window labels like "8/10 last decade"). The
orchestrator's two hits are its own retroactive-note date stamps. **No hindsight
leakage found in any agent's reasoning, including the orchestrator's.**

---

## Q2 — Were the 16 desk repairs applied even-handedly?

**Finding: the *rule* was applied even-handedly and mechanically, and the
14-of-16 Haiku concentration is an agent property, not a desk property. But the
rule changed once without disclosure, and in ten books it produced an outcome
that is not "fixing arithmetic".**

### B0 — The 16 repairs, and the rule actually applied

All 16 `registration_note` files (12 at `weeks/2026-07-31/`, 4 at
`round3/allocations/`): 14 Haiku, 2 Opus (`opus_broadening` R2,
`opus5_trend` R3).

The stated rule is "scale positions proportionally, preserve declared cash". I
recomputed the implied scale factor `k = sum(registered weights) / sum(submitted
weights)` from the desk log's as-submitted numbers against every registered file,
and compared it to `(100 − declared cash) / sum(submitted weights)`:

| book | submitted W + C | registered W + C | implied k | rule k |
|---|---|---|---|---|
| Haiku concentrated AI/tech R2 | 100 + 17 | 83.0 + 17 | 0.8300 | 0.8300 |
| Haiku concentrated AI/tech R3 | 100 + 19 | 81.0 + 19 | 0.8100 | 0.8100 |
| Haiku dividend growth R2 | 100 + 23 | 77.0 + 23 | 0.7700 | 0.7700 |
| Haiku dividend growth R3 | 100 + 8 | 92.0 + 8 | 0.9200 | 0.9200 |
| Haiku global diversification R2 | 100 + 39 | 61.0 + 39 | 0.6100 | 0.6100 |
| Haiku macro/sector rotation R2 | 100 + 39 | 61.0 + 39 | 0.6100 | 0.6100 |
| Haiku small/mid growth R2 | 100 + 5 | 95.0 + 5 | 0.9500 | 0.9500 |
| Haiku small/mid growth R3 | 100 + 32 | 68.0 + 32 | 0.6800 | 0.6800 |
| Haiku contrarian turnarounds R2/R3 | 100 + *(omitted)* | 100 + 0 | 1.0000 | 1.0000 |
| **Opus 5 trend following R3** | 99 + 3 | 97.0 + 3 | 0.9798 | 0.9798 |
| **Opus Broadening R2** | 96 + 3 | 97.0 + 3 | **1.0104** | 1.0104 |

**Every factor matches the rule to four decimal places, for Haiku and Opus
alike, and in both directions** — `opus_broadening` was scaled *up* 1.0104,
increasing an Opus book's market exposure. There is no case where the desk chose
the reading that helped or hurt a particular tier. Every repaired book sums to
100 afterwards.

### B1 (material) — Ten books hold Pathward Financial and a sub-penny shell where the manager meant cash

This is the finding that changes economics beyond arithmetic.

Ten registered books at the 2026-07-31 fill contain a position whose *symbol is a
word for cash*, typed as `kind: "equity", side: "long"`:

| file | symbol | registered weight | thesis (verbatim, abridged) |
|---|---|---|---|
| `round2/weeks/2026-07-31/fleet_haiku_macro_sector_rotation.json` | `CASH` | 23.79% | "preserving 39% post-earnings **dry powder**" |
| `round2/weeks/2026-07-31/fleet_haiku_global_diversification_….json` | `USDC` | 23.79% | "Increased **cash buffer** from 30% to 39%" |
| `round2/weeks/2026-07-31/fleet_haiku_dividend_growth_and_income.json` | `CASH` | 17.71% | "**4% APY on cash** provides portfolio yield" |
| `round2/weeks/2026-07-31/fleet_haiku_concentrated_ai_technology.json` | `cash` | 14.11% | "**Dry powder** for post-earnings volatility management" |
| `round2/weeks/2026-07-31/fleet_haiku_contrarian_turnarounds.json` | `CASH` | 15% | "retain 15% for **dry powder**" |
| `round2/weeks/2026-07-31/fleet_haiku_small_mid_cap_growth.json` | `CASH` | 4.75% | "**Dry powder** for tactical moves" |
| `round3/weeks/2026-07-31/fleet_haiku_contrarian_turnarounds.json` | `CASH` | 27% | "raise **dry powder** given macro surprise" |
| `round3/weeks/2026-07-31/fleet_haiku_small_mid_cap_growth.json` | `CASH` | 21.76% | "Elevated **cash** raised for Fed policy uncertainty" |
| `round3/weeks/2026-07-31/fleet_haiku_concentrated_ai_technology.json` | `cash` | 15.39% | "Increased from 6% to 19% for defensive positioning" |
| `round3/weeks/2026-07-31/fleet_haiku_dividend_growth_and_income.json` | `CASH` | 7.36% | "Conservative **cash buffer**" |

The engine filled all ten (`fills.jsonl`, ts `2026-07-31T16:00:00-04:00`):

```
CASH  fill_price 88.24    notional $45.24 – $275.40
USDC  fill_price 0.0012   notional $231.99
```

Resolved against the same data source the engine uses
(`query1.finance.yahoo.com/v8/finance/chart/…`):

- **`CASH` = Pathward Financial, Inc.**, `instrumentType: EQUITY`, NasdaqGS — a
  bank holding company.
- **`USDC` = USDATA Corp.**, `instrumentType: EQUITY`, trading at $0.0001–$0.0012
  — a sub-penny shell, not the USD Coin stablecoin and not cash.

So `Haiku global diversification` has **23.79% of a $1,000 book — $231.99
notional — long a $0.0012 shell stock**, registered under a thesis that says
"cash buffer … reduces forced leverage exposure". In eight of the ten the cash is
additionally **double-counted**: e.g. `fleet_haiku_macro_sector_rotation` R2 has
`cash_pct: 39` *and* a 23.79% `CASH` position, so 62.8% of the book is nominally
cash-like and 23.79% of it is a regional bank.

The desk did not invent these tickers — the managers wrote them. But three desk
acts converted a manager's notation error into a live position:

1. The desk **chose accept-and-repair** rather than bounce-and-repoll.
2. The repair **arithmetically scaled the cash placeholder as a security**
   (0.6100 × 39 = 23.79) — the desk's own hand is on the number.
3. For `fleet_haiku_contrarian_turnarounds` the repair explicitly *relied* on the
   placeholder: "cash_pct omitted by the manager; set to 0 = 100 − sum(weights)",
   where 15% (R2) / 27% (R3) of "sum(weights)" **is** the `CASH` position. That
   book's declared cash is 0.0 and 15–27% of it is Pathward Financial.

The check that should have caught this ran and *validated* it: commit `355771d`
states "all 183 symbols verified priceable". `CASH` and `USDC` passed **because**
they are real tickers. Nothing in `tracker/round2.py`'s `validate()` (lines
268-291) or `check_reasoning.py` tests symbol semantics, and no
`registration_note`, desk log entry or commit message anywhere in the repo
mentions it. All ten books are still live and are published on the hub
(`docs/api/ledger.json` carries the CASH/USDC fills).

**All ten are Haiku.** This is the sharpest form of the critique's Finding 5
tier-differential concern, and it is worse than the critique described: the
transfer is not merely "from what Haiku's orders would do toward what Haiku
meant", it is *away from both*.

### B2 (material) — The repair rule changed once, silently

Comparing every desk-log position object against its registered file across all
four events:

| event | negative stop → magnitude | negative stop → **deleted** | leverage key stripped from non-perp | disclosed? |
|---|---|---|---|---|
| week 1 (2026-07-18) | 0 | 0 | 0 | n/a |
| week 2 (2026-07-25) | 0 | **7** | 1 | **no** |
| resize (2026-07-30) | **77** | 0 | 10 | yes — `355771d` |
| week 3 (2026-08-01) | **45** | 0 | 0 | **no** |

- At week 2 the desk deleted seven `stop_loss_pct` values (-10, -12, -10, -10,
  -8, -8, -12) from `round3/weeks/2026-07-27/fleet_haiku_dividend_growth_and_income.json`
  — comparing it to its own record in `experiments/desk/week2_2026-07-25.json`.
  It **kept** the positive `take_profit_pct: 20` on the same TNA leg. So the
  favourable trigger survived and every protective trigger was deleted. The file
  has no `registration_note`; commit `020fb6e` says only "0 rejected — every book
  passed weights/cash, max-position, short, position-count and perp-leverage
  checks".
- Five days later, `355771d` adopted the opposite convention and gave the reason
  the week-2 handling contradicts: negatives were "converted to magnitudes rather
  than dropped, which would have silently deleted risk controls."
- `tracker/round2.py:189-191` applies `abs()` to stops at evaluation, so
  *converting* is a no-op and *deleting* is the only choice with consequences.
  The week-2 deletion was the one intervention that could change a book's
  behaviour, and it is the one that was not recorded.

Materiality, ex post: that book ran only 2026-07-27 → 2026-07-31 and no stop
fired for it in `round3/fills.jsonl`, so the deletion cost nothing in the event.
The desk could not have known that when it deleted them.

The 07-30 commit's own numbers, by contrast, **verify exactly**: I count 77
negative stop conversions (the message says 77) and 10 leverage strips on
non-perp legs (the message says 10). Week 3's 45 conversions are undisclosed;
`4ce8273` reports "0 arithmetic repairs" (true) and is silent on sanitization.

Leverage strips are economically inert — `simulate()` honours `leverage` only for
`kind == "perp"` (lines 111, 134) — but they do lower the published
`gross_exposure_pct` (line 345 multiplies by `leverage` for every kind), so a
stripped `TQQQ leverage: 3` understates that book's stated exposure on the hub.

### B3 — Did repairs systematically advantage or disadvantage anyone?

Recomputed from `docs/api/round{2,3}.json` NAV series, 2026-07-31 → 2026-08-06
(SPY +3.51% over the same window):

| | repaired | not repaired |
|---|---|---|
| R2 all books | +3.49% (n=7) | +1.93% (n=21) |
| R2 Haiku only | +4.06% (n=6) | +3.01% (n=4) |
| R3 all books | +0.37% (n=5) | +0.61% (n=42) |
| R3 Haiku only | +1.17% (n=4) | +0.92% (n=6) |

No consistent sign across rounds, n ≤ 7 per cell, and the within-tier gaps are
smaller than the between-tier ones. **No systematic advantage or disadvantage is
detectable.** What *is* structural: the desk's convention (preserve declared
cash, scale positions) removed a mean of **22.8 points of gross exposure** from
the eight "weights = 100 with cash on top" books, versus the alternative reading
(cash is the error, scale cash to zero). In a +3.5% tape that is a drag; in a
falling one it would be a cushion. It is a real economic choice made case-by-case
by a competitor, and it is not reported as a sensitivity anywhere.

### B4 — Does 14-of-16-Haiku reflect the desk or the agents?

**The agents, decisively.** Failure is defined mechanically (`|sum(weights) +
cash − 100| > 0.05`) and I applied it myself to the as-submitted numbers in the
desk logs, independent of whether the desk repaired anything. Result: the set of
books that fail arithmetic and the set that carry a `registration_note` are
**identical — zero disagreements in either direction across all four desk
events**. The desk did not repair a book that did not need it, and did not let a
failing book through unrepaired.

Submission-failure rate at the 2026-07-30 resize:

| model | failed / submitted |
|---|---|
| **haiku** | **10 / 11 (91%)** |
| opus | 2 / 24 (8%) |
| sonnet | 0 / 23 (0%) |
| fable | 0 / 4 (0%) |

And the failure mode is one repeated convention error ("weights expressed as
percent of *invested* capital with cash on top"), not random slips. At week 2 and
week 3 the failure count was 0/18 and 0/11. The concentration is a property of
what Haiku submitted.

---

## Q3 — Do the registered books match what the agents actually returned?

**Finding: yes — after accounting for two disclosed transformations, every
registered book matches the desk record. 96 rebalances and 5 position-echoing
HOLDs cross-checked; 2 divergences found, both documentation-level.**

Method: for all four desk logs I mapped every decision to its file under
`experiments/round{2,3}/weeks/<effective_entry>/` and compared symbol, side,
kind, `weight_pct`, `stop_loss_pct`, `take_profit_pct`, `leverage`, `cash_pct`,
`reason` vs `reassessment_note`, and `novelty`.

**Reasons.** 96 of 96 match: 5 byte-identical, 91 identical after stripping a
desk-added prefix of the form `"Week 1 desk (2026-07-18): "`. No reason was
rewritten, softened or invented. `novelty` matched in all 37 cases.

**Positions and cash.** Every difference is accounted for by exactly one of:
(a) an arithmetic repair carrying a `registration_note` (B0), (b) a negative-stop
sign conversion (B2), (c) a leverage strip on a non-perp leg (B2). **No book was
registered with a symbol, side, kind, or a weight ratio the agent did not
submit.** No REBALANCE decision is missing its file; no week file exists without
a corresponding desk record — except one, noted below.

**Divergence 1 (documentation).** `experiments/desk/week3_2026-08-01.json`,
Opus Quality Defensive R3 HOLD: the log echoes DBMF, PDBC and XLE **without**
stops, while the registered
`round3/weeks/2026-07-31/opus_quality_defensive.json` carries
`stop_loss_pct` 10 / 12 / 13 and `take_profit_pct` 30 on all three. The
*registered* book (the one that trades) preserves the agent's risk controls; the
log's echo is incomplete. Direction is harmless; fidelity is not.

**Divergence 2 (structural).** `experiments/round2/weeks/2026-07-20/claude_fable.json`
is the **only** registered book in the entire corpus with no corresponding entry
in any desk log's `decisions` array. The orchestrator's decisions live in a
separate `orchestrator` block that records action + reason but **never
positions**. Its books are therefore the only ones whose registered contents
cannot be cross-checked against an independent record of what was submitted. In
this case author and submitter are the same entity so nothing is falsifiable
either way — but it means the single most important integrity check in this
section is the one check that structurally cannot be run on the auditor's own
account.

**Silver lining worth recording:** because the desk logs preserve the
*as-submitted* values (negative stops, unrepaired weights, leverage keys), they
already function as the `_as_submitted` provenance record the critique's Finding
5(c) asked for. It is not adjacent to the position object, but it exists and it
is machine-readable. That is how B1 and B2 were found.

---

## Q4 — Are the prompts even-handed across tiers?

**Finding: unverifiable from the repository. No prompt text is archived
anywhere.**

The test I wanted to run — diff the prompt sent to Haiku against the prompt sent
to Opus 5 — cannot be run. `grep -rIl "prompt"` across `experiments/`, `tracker/`
and `docs/` returns five files, none containing a verbatim prompt. What exists:

- **Descriptions of packet contents**, which are tier-neutral by construction:
  `experiments/info_desk/PROTOCOL.md` v2 (own book + cumulative released items,
  no NAV, no market table — same for all 37) and v3 (own account + free internet
  — same for all 46). No tier appears anywhere in either specification.
- **`experiments/round3/context_pack.txt`**, the mechanically generated pack for
  tools-disabled agents. It exists and is committed in `7093a64`
  (2026-07-16 11:23:00 UTC), **before** the 2026-07-17 R3 entry close — the rules'
  claim (`round3/RULES.md:145-147`) that it was "committed pre-entry" and
  "identical across agents" verifies on the first half and is a single shared
  file on the second.
- **One documented steer**, disclosed by the desk itself:
  `week3_2026-08-01.json` `note` — managers "were told that 'nothing material has
  changed' is a valid HOLD reason". This went to all 46 and its author held both
  its books that week. That coincidence is worth stating plainly, and the desk
  states it plainly. What I can say from the outcome: the steer produced 62 HOLDs
  and 11 REBALANCEs, and **all 11 rebalances came from Opus agents** — i.e. the
  tiers responded to the identical instruction very differently, which is
  consistent with a uniform prompt and inconsistent with a tier-specific one, but
  is not proof.

**Indirect evidence of even-handedness:** the released Info Desk items were, in
both cycles, the collection's **rank-1 item by materiality** — `item 1` of 10 in
both `collected/2026-07-21.json` and `collected/2026-07-25.json`, matching
`released/*_item1.json` byte-for-byte. No cherry-picking of which fact to
release. (Both releases were the semis theme, which is the theme of the
orchestrator's own concentrated book; rank-1 selection is mechanical and both
were genuinely the largest moves, so I record this as coincidence, not finding.)

**Unresolved.** "Transcript-auditable" (`round2/RULES.md:130-132`) remains an
unfunded promise: the Round-1 audit had 27 JSONL transcripts to mine; this desk
archives none. Prompt even-handedness, tool-use discipline, and whether any
free-internet agent read the public hub to see rivals' books are all
unfalsifiable from this repository.

---

## Q5 — Fill-convention integrity

**Finding: clean, exhaustively. Not a sample — every fill.**

The mandate asked for at least 12 books. I ran the check over all **1,381 OPEN
fills** in `experiments/round{2,3}/fills.jsonl`: for each, resolve the registered
file whose `entry` equals the fill date, take `git log --format=%aI` for that
file (both first and last commit), and require the commit to precede
`<fill date>T16:00:00-04:00`.

```
OPEN fills traced to a file committed strictly before that date's 16:00 ET close: 1381
violations: 0
fills with no matching registered file: 0
```

Every one of the 172 registered books was committed **exactly once** and has
never been amended (`git log | wc -l == 1` for all of them), so there is no
"registered then quietly edited after the close" path.

Margins by desk event:

| effective fill close | commit | commit time (UTC) | margin before close | books |
|---|---|---|---|---|
| 2026-07-20 (Mon) | `1f9fc62` / `d3760c5` | 07-18 12:13 / 12:36 | ~2 d 8 h | 6 |
| 2026-07-27 (Mon) | `020fb6e` | 07-25 12:45 | ~2 d 7 h | 18 |
| 2026-07-31 (Fri) | `355771d` | 07-30 02:38 | ~1 d 17 h | 62 |
| 2026-08-03 (Mon) | `4ce8273` | 08-01 13:06 | ~2 d 7 h | 11 |
| 2026-07-16 R2 entry | `3a3e1bc` / `8d05e1a` | 07-16 05:05 / 05:15 | ~15 h | 28 |
| 2026-07-17 R3 entry | `7cc1a50` … `b682455` | 07-16 11:33–11:41 | ~1 d 8 h | 38 |
| 2026-07-27 Opus 5 entry | `32fec97` … `f1caede` | 07-26 03:34–04:05 | ~1 d 16 h | 9 |

The 2026-07-30 resize is the strongest case, not the weakest: books were
committed at 02:38 UTC on 07-30 (= 22:38 ET on 07-29), so the managers saw the
07-29 close and **neither the 07-30 nor the 07-31 close** — yet the fill is at the
07-31 close, two full sessions later. Corroborated from the other side: the
`research_notes` reference 07-29 closes and after-hours ("MSFT +7% AH",
"AAPL/AMZN tonight"), never 07-30 or 07-31 outcomes. The convention is applied
conservatively against the agents, including the orchestrator.

`fills.jsonl` shows OPEN fills on **only** the six legitimate dates (2026-07-16,
-17, -20, -27, -31, 08-03) and stop/TP fills only at daily closes in between,
each traceable to a `stop_loss_pct` / `take_profit_pct` in a book registered
before it.

**One inherited exception, out of desk scope but load-bearing (see G2):** the
Round-1 **H2 leg** uses `H2_ENTRY = "2026-07-15"` (`tracker/track.py:34`) while
`experiments/2026-h2/orders/*.json` were committed on 2026-07-16 at 03:30–03:48
UTC — i.e. marked at a close that had already printed when the books were
written. `round3/RULES.md:157` discloses this as a "known inconsistency".

---

## Q6 — Did the reasoning backfill overstep?

**Finding: no. It is the most scrupulous thing in the repository.**

`experiments/desk/week1_2026-07-18.json` has exactly two commits: `d3760c5`
(2026-07-18) and `d2c60b3` (2026-07-30). `git diff d3760c5 d2c60b3` on that file
changes **28 lines** and touches exactly three things: the two default-HOLD
entries (bare strings → objects with desk-authored reasoning and
`reason_source: "desk, not the agent"`), the `orchestrator` block, and the
addition of `reasoning_invariant`. **The 35 competing managers' 60 decisions are
untouched** — no rival's reason was retrofitted, improved, or edited while the
orchestrator's was being written.

**The Round-2 reason genuinely pre-existed.** The desk log's `round2_reason` is
**byte-for-byte identical** (271 chars, verified by string equality in Python) to
the `reassessment_note` in `git show 1f9fc62:experiments/round2/weeks/2026-07-20/claude_fable.json`
— committed 2026-07-18 12:13:21, twelve days before the backfill. That file has
never been modified (`old == cur` → `True`). The `round2_reason_source` names
that exact path. This is a citation, not a reconstruction.

**The Round-3 entry is honestly marked.** It carries
`round3_reason_unavailable: true`, opens "NO CONTEMPORANEOUS REASON WAS
RECORDED", labels the note "written 2026-07-30, NOT the reasoning used at the
time", states "This is a reconstruction of the situation, not a record of the
decision", and signs `round3_reason_source: "retroactive reconstruction by the
orchestrator, 2026-07-30"`. It satisfies every clause of the rule at
`round2/RULES.md:190-194` and asserts nothing about what the agent thought.

**What was replaced is itself the indictment.** The pre-backfill value was
`"round2": "REBALANCE (deployed 9pts cash into MU/AMD/NVDA)"` — precisely the
"action string as a reason" that `round2/RULES.md:185-186` now calls
unacceptable. The orchestrator's own record is the worked example of the failure
mode its new rule prohibits, and it says so in the rules
(`round2/RULES.md:201-205`, "Known backfill").

**One caveat inherited from the critique, confirmed:** the rule text claims the
checker "rejects" action strings. It does not — `_thin()` tests only
`len(s.strip()) < 25` (`check_reasoning.py:29-33`), and the original 47-character
string would have passed. The enforcement is against blankness, not vacuousness,
and the rules still overstate it. `check_reasoning.py` currently passes on 172
books and 280 desk decisions.

---

## Q7 — Anything else

### G1 (material) — Amendment 2 was pre-registered by a participant after the outcomes had started printing, and it materially improves that participant's rank

`ANALYSIS_PLAN.md` § "Amendment 2" (commit `162375e`, 2026-08-07 21:36 UTC)
re-registers the confirmatory endpoint as **2026-08-03 → 2026-12-31**. The
amendment discloses its own timing — "epoch 2 is five sessions old" — and the
data through 2026-08-06 was already in `docs/api/` and already analysed.

Recomputed rank of `Claude Fable (orchestrator)` under each candidate window
(NAV series from `docs/api/round{2,3}.json`, all books ranked by return over the
window):

| window start | R2 rank | R3 rank |
|---|---|---|
| 2026-07-16/17 (original endpoint) | **17 / 28** | **14 / 47** |
| 2026-07-31 (the critique's recommendation) | 4 / 28 | 10 / 47 |
| **2026-08-03 (adopted)** | **6 / 28** | **6 / 47** |

The amendment moves the drafter's own books from below to well above median in
both rounds. The drafter could see that when writing it.

Three things argue against reading this as self-dealing, and I record them
because they are load-bearing:

1. **The date was not free.** 2026-08-03 is mechanically defined ("the first full
   session after the epoch-2 books filled"), and the amendment adopts a critique
   the orchestrator did not write.
2. **It is not the best available choice for the drafter.** The critique
   *recommended* 2026-07-31; that date gives `claude_fable` R2 rank **4/28**
   versus 6/28 under the date actually adopted. The orchestrator chose the
   less-flattering of the two defensible dates for its stronger book.
3. **No claim has been made from it.** `tracker/stats.py` refuses to infer at
   n = 4 ("insufficient observations", logged in `analysis_runs.jsonl`).

Nevertheless: a competing participant re-selected the endpoint that will decide
the tournament, after seeing four sessions of results under it, and the new
endpoint erases an epoch in which its own books were among the worst
(`claude_fable` H2 curve bottomed at 88.14 on 2026-07-29). The amendment's own
remedy list (line 110) says the desk should be independently audited; the
endpoint choice should have been made by that same third party, not ratified by
it afterwards.

**Genuine remediation, recorded:** the same commit pair also implements what the
critique said was missing — `tracker/stats.py` (HAC alpha, Romano-Wolf stepdown
over a block-bootstrapped residual *matrix*, effective-bets), a mandatory run log
(`experiments/reviews/analysis_runs.jsonl`), and a binding commitment to report
**all five** persistence pairings. The first logged run duly reports the
unflattering ones alongside the flattering: R1H1→R2 −0.049, R1H1→R3 **+0.470**,
R1H2→R2 **+0.487**, R1H2→R3 −0.245, R1H1→R1H2 −0.279. The selective-reporting
problem the critique documented is, on this evidence, fixed.

### G2 — Two of the five newly-mandated persistence figures rest on the one leg with a compromised fill convention

`tracker/stats.py:231` pairs both `R1-H1` **and** `R1-H2` against R2 and R3.
`R1H2 → R2 = +0.487` is the largest positive persistence number in the set — and
the R1-H2 leg is the one marked at a close that had already printed when its
books were written (Q5, `track.py:34` vs commit `d95d833`). The "report every
pairing" rule is right, but it now surfaces a number whose provenance is weaker
than the other four, unlabelled. Any persistence claim should carry that flag.

### G3 — Two numeric claims in commit messages are not reproducible from the artefacts they describe

Instructed not to take commit messages at face value, I checked them. Most
verify exactly (`355771d`'s "77" and "10" are exactly right; `4ce8273`'s "62
HOLD, 11 REBALANCE, 0 rejected, 0 arithmetic repairs" is exactly right — I count
11 files under `weeks/2026-08-03/` and no `registration_note`). Two do not:

- `919ea0d` claims "Effective independent books: **4.4** of 28 and 7.3 of 47".
  `analysis_runs.jsonl`, written by the code in that same commit, records
  `round2.effective_bets = **18.95**` (residual correlation 0.0177) and
  `round3.effective_bets = 7.26`. The R3 figure matches; the R2 figure quoted is
  the **critique's** number, computed on raw NAV returns, not the new code's.
- Same commit: "best p_RW: **0.464** and 0.185". The R3 minimum is 0.1848 ✓; the
  R2 minimum in the log is **0.4313** (Haiku growth at a reasonable price,
  |t| = 1.886, first in the stepdown order), not 0.464.

Neither error is self-serving — 4.4 is the *more* conservative figure — but a
commit message that reports a number the committed code did not produce is a
provenance failure in a repo whose spine is provenance. Separately, the two
"effective bets" figures now in circulation (0.0177/18.95 on residuals vs
0.201/4.4 on raw returns) are different statistics; whichever is published needs
its definition attached, or the hub will carry a 4× discrepancy with the critique.

### G4 — The critique's Finding 5(b) and Finding 3 presentation remedies are still open

- Repaired books carry prose, not a machine-readable flag. `grep` for
  `registration_note` across `docs/api/*.json`: `ledger.json` 10,
  `performance.json` 0, `round2.json` 0, `round3.json` 0. No tier comparison can
  currently be produced "with and without repaired books" from the published API.
- The orchestrator's accounts are **not flagged as conflicted** on any published
  page; `docs/performance.html` contains no marker beyond the word
  "(orchestrator)" inside the account name. They appear as ordinary rows.

### G5 — Positive controls that passed

Stated so the "clean" findings above are legible as tests:

- **All 172 registered books** pass the current `validate()` (weights + cash =
  100 ± 0.05, no negative weights, cash ≥ 0, shorts ≤ 100, perp leverage in
  (0,100]). Zero violations.
- **All 99 books registered before 2026-07-30** also pass the *old* caps in force
  at their registration (max single position ≤ 40%, shorts ≤ 50%, ≥ 5 positions,
  perp leverage 2–10x). Zero violations. No book was let through under a rule
  that was later loosened for it.
- **`check_reasoning.py` passes**: 172 books, 280 desk decisions, no gaps.
- **No hindsight** in any of the 280 reasons or 92 research notes (Q1 A4).
- **No per-agent branching** anywhere in the scoring or reporting pipeline.

---

## Unresolved / not verifiable from this repository

1. **Prompt texts.** None are archived. Tier even-handedness of the actual
   prompts is asserted by the rules and by the protocol descriptions and cannot
   be checked. The one disclosed steer (week-3 HOLD legitimation) is documented
   but its verbatim wording is not.
2. **Transcripts.** `round2/RULES.md:130-132` calls backtests
   "transcript-auditable"; no transcript exists in the repo. Tool-use discipline,
   whether any free-internet agent read `docs/` to see rivals' books, and the
   914 / 468 tool-call counts in `355771d` and `4ce8273` are all unverifiable.
3. **Whether the orchestrator's private reasoning used cross-agent information.**
   Structurally unfalsifiable: it reads every book by construction. Commit
   ordering (A1) shows it could not have registered *after* seeing rivals'
   registrations, which is the strongest available proxy, and it is clean.
4. **Ex-post impact of the CASH / USDC mis-registration (B1).** I confirmed the
   ticker identities against the live data source and the fill notionals from
   `fills.jsonl`, but I could not decompose the affected books' NAV series to
   isolate the contribution, because no price matrix is committed. Ten live books
   are affected; the largest single exposure is 27% (`fleet_haiku_contrarian_turnarounds`
   R3, `CASH` = Pathward Financial).
5. **The counterfactual repair.** I did not re-run the engine under the
   alternative reading (scale cash to zero, keep weights) for the 8 affected
   books, so the 22.8-point mean exposure delta is arithmetic, not a simulated
   NAV difference.
6. **Round-1 H2 leg.** Its same-close marking is disclosed and out of this
   audit's scope, but it feeds two of the five persistence statistics now
   mandated for publication (G2).

---

## Recommendations, in priority order

1. **Fix B1 before December.** Ten live books hold Pathward Financial and USDATA
   Corp. where the manager wrote "dry powder". Decide and disclose: reclassify to
   cash with a dated correction note, or leave them and label the exposure
   explicitly on the hub. Add a symbol-semantics guard to `validate()` — reject
   any position whose symbol matches `^(CASH|USD|USDC|USDT|MONEY|MMF)$` — so the
   priceability check stops laundering a notation error into a fill.
2. **Backfill the week-2 and week-3 sanitization records** (B2) into
   `experiments/desk/*.json` or per-file notes, dated and labelled as
   retroactive, to the same standard the reasoning backfill met (Q6). Then adopt
   one written sanitization rule and never change it silently again.
3. **Remove the `or orc.get("reason")` fallback** at `check_reasoning.py:95`.
   The referee's account should be graded by the strictest branch in the file,
   not the only lenient one. Require `research_notes` on the orchestrator block.
4. **Record the orchestrator's positions in the desk log** like every other
   manager's, so its books are cross-checkable (Q3, divergence 2).
5. **Hand the endpoint decision to the auditor.** Amendment 2 is defensible and
   was not the drafter's best option — but it is still a participant choosing the
   scoring window with four sessions of its own results visible. Any further
   endpoint change should be ratified by a party holding no book, before it is
   committed.
6. **Tag repaired books machine-readably** in `docs/api/*.json` and pre-commit to
   reporting every tier comparison with and without them; flag the orchestrator's
   rows as conflicted on the published tables.
7. **Archive one desk transcript per event**, or drop "transcript-auditable"
   from the rules.

---

*Every value in this report was recomputed by the auditor from the repository at
commit `919ea0d` — desk logs cross-checked against `experiments/round{2,3}/weeks/`
in Python, commit timestamps from `git log --format=%aI` per file, fills from
`experiments/round{2,3}/fills.jsonl`, returns from `docs/api/round{2,3}.json`
NAV series, and the `CASH` / `USDC` ticker identities from
`query1.finance.yahoo.com/v8/finance/chart/` (the same endpoint
`tracker/round2.py:73` uses). No claim in a commit message is relied on except
where this report states it was checked against the tree.*
