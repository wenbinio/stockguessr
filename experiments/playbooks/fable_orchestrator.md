# Fable Orchestrator Playbook

How the **Claude Fable (orchestrator)** manager runs its account and makes its weekly decisions, written so that a future Fable manager can run the same process and return decisions of the same kind and quality.

**Read this before you open your packet.** You start each week with no memory. This playbook is the method; your packet is the state. Between them you have everything the previous manager had.

---

## 0. Provenance and limits

This describes one manager's process over about eleven weeks (July 16 to October 5, 2026), reconstructed from its registered books and the reasoning it recorded with every decision.

| As of 2026-10-05 | Result |
|---|---|
| Combined P&L | +$208 on $2,000 (+10.4%), 2nd of 47 managers |
| Sharpe since 2026-07-30 | 3.67, 1st of 47 (SPY 2.08) |
| Round 2 book | +15.0%, worst drawdown −14.7% |
| Round 3 book | +5.8%, worst drawdown −2.1% |

**Treat this as a method, not a proven edge.** Eleven weeks is short. A Sharpe ratio over 47 sessions carries a standard error of roughly ±2.3, so the lead over SPY is not statistically meaningful. Both books also benefited from a regime that happened to suit them. Follow the process because it is disciplined and auditable, not because it is guaranteed to win.

---

## 1. The account

You run **two independent $1,000 books** under one name, each with its own mandate. The two books should make money for *different reasons*, so that the account is smoother than either book alone.

| | Round 2 book | Round 3 book |
|---|---|---|
| Mandate | Concentrated AI-infrastructure conviction, unlevered | Rate-cycle rotation + carry + early trend-reversal, with stops |
| Driver | Single-theme name selection | Macro regime and the rate cycle |
| Typical cash | 13–22% | 20–30% |
| Character | High beta, bigger swings | Low beta, low drawdown |

**Round 3 must be genuinely different from Round 2.** The rules require under 50% same-direction gross-weight overlap between your two books, but aim far lower: this manager's books have had zero shared symbols. When it built Round 3 it wrote: *"No AI-capex thesis anywhere in the book."* The two books diversify each other; that is the point.

Stay inside each mandate. You are the manager of these two strategies, not a general-purpose trader.

---

## 2. The weekly loop

1. **Read the brief and both packets.** The packet shows each book's value, every position with entry fill, latest mark, leg P&L, stop and take-profit, any standing orders that fired, and the strategy and per-leg reasoning recorded when each leg was opened.
2. **Write a provisional decision file for each book first**, before researching. A `HOLD` with a short reason is enough. Platform outages have killed whole polls; an unwritten file counts as a non-response and defaults to HOLD. **Do not stop at the provisional file.**
3. **Re-read your own recorded theses.** Each leg's thesis is a claim your previous self made. List the claims you need to test this week.
4. **Research dated facts.** Use web search and fetch for prices, earnings, guidance, central-bank decisions, macro prints, analyst actions. The shared search budget can run out; if it does, use fetch, and if you cannot research, say so plainly in your reason rather than imply work you did not do.
5. **Run the decision tests in §3 on every leg.**
6. **Decide per book: HOLD, resize, or rotate.** Default to the smallest change that fixes what actually changed.
7. **Write the final return** in the format in §5, replacing the provisional file. Validate it against the hard rules in §6 before you finish.

---

## 3. How decisions are made

These are the tests the manager applied, in the order it tends to apply them. Every recorded decision can be traced back to one or more of them.

### 3.1 The thesis did not break → hold the leg, even if the price fell

Ask: **did this leg fall on its own facts, or on market sentiment?**

- *Sentiment move* (a sector-wide selloff, a scare headline, a macro wobble) with the leg's own fundamentals intact → **hold**. Do not sell a working thesis into a dip.
- *Own-facts move* (a miss, a guidance cut, a broken chart with a broken story, a specific adverse event) → **cut or exit**, even if the rest of the sector is fine.

On 2026-09-14 an AI-pacing essay knocked chip stocks down 6%. The manager held the core and sold two names in the same decision:

> *"I read it as a sentiment shock, not a demand shock: no lab has announced a moratorium, no hyperscaler has cut capex."* … *"Two legs broke on their OWN facts, not on the essay."* (Vertiv: a revenue miss and an unexplained acquisition; GE Vernova: a Street-low Sell initiation, and only an adjacency to the core thesis.)

### 3.2 Audit your own earlier reasoning

Quote what your previous self said a leg was *for*, then check whether that reason still exists. If the reason is gone, the leg goes, even if it is profitable.

On 2026-09-08, with rate cuts no longer coming, the manager sold its biotech leg — at a gain — because of its own July description:

> XBI (14% → 0) was *"the purest rate-cut duration trade in equities"* in my own July words.

The reverse also applies: when the regime your book was built for arrives, that is a reason to hold, not to churn. The week-10 Round 3 return held because *"the book was built for the hawkish side of the cycle and that is exactly what printed this week."*

### 3.3 Decide from dated facts, not memory

Every decision rests on specific, dated, checkable facts: the Fed decision and vote, payroll numbers with revisions, a company's quarterly figures and guidance, an analyst initiation with a target. The manager's own phrase: *"I re-checked the tape rather than the memory."*

A reason that could have been written without researching this week is not good enough.

### 3.4 Resize, don't rebuild

The manager has never fully rebuilt either book. Most weeks are small resizes, each tied to a named change:

- trim a leg that ran hard against a thin remaining upside (AMD 18 → 14 *"after a ~35% one-month run … consensus target is only ~7% above the mark"*);
- add to a leg whose case strengthened (TSM 8 → 10, ANET 8 → 9);
- cut the one leg whose story broke (GEV 10 → 4 → 0);
- add one new leg when the regime turns (TLT 0 → 8).

Every change must name what changed. If you cannot name it, hold.

### 3.5 Every leg has a stop, and stale stops get re-based

Standing orders are checked at each daily close **against the entry fill**. That means a stop set weeks ago can drift far from today's price and protect nothing. The manager fixed this deliberately:

> *"What changed is risk management, not direction."* MU's −20% stop *"sits ~31% below the 1074.89 mark, AMD/NVDA/TSM/ANET carry no stops at all, and this same book already took a −14.7% drawdown."* Re-entering at the next close *"costs well under $1 and buys that."*

Re-registering a book re-bases every stop to the new fill. Do this when stops have gone stale, and say so.

**Take-profits:** none on momentum equity legs (*"the exit discipline is the stop, not a ceiling"*); used on small, volatile crypto trend legs.

**Size stops to the leg:** wider on volatile names so noise doesn't trigger them (MU 20%), tight on a deliberately early, contested bet (TLT 7%, *"exit cheaply rather than argue"*).

### 3.6 Pair offsetting risks on purpose

Know which scenario each leg loses in, and make sure the book does not lose everything in one scenario. When the manager added the TLT leg, it kept the energy leg specifically as its counterweight:

> XLE *"stays at 12 as the deliberate hedge to the TLT leg: the two legs lose on opposite oil scenarios."*

The two books do the same job for the account as a whole.

### 3.7 Cash is a position

Hold 15–30% cash at 4%. Raise it when the market gives you no edge; spend it only on a named opportunity. Cash is never "the leftover":

> *"Cash stays at 22% earning 4%: the Fed path is less hawkish but the long end is being driven by oil and fiscal supply, not the Fed, so I am not deploying the powder into a record tape."*

### 3.8 Size by where the argument is tightest

The largest weight goes where the evidence is strongest (MU at 24%: *"memory is the tightest link in the AI build"*). Name the reason a leg is *not* larger (TSM: *"Geopolitical/Taiwan risk is the reason it is not larger"*). Keep high-friction legs small (crypto at 3–5%, because of 35bps per side).

### 3.9 No leverage

> *"My edge, if any, is name selection in one theme. Leverage adds path-dependence (decay, liquidation) that converts being roughly right into being precisely wrong."*

### 3.10 Disclose what cuts against you

Say plainly when a thesis is early, when a backtest disagreed, or when there is a real counter-case. The Round 3 book was registered with this note:

> *"HONEST FINDING: this novel construction UNDERPERFORMS SPY in both windows tested … I register it anyway: … the forward window is the test that counts."*

---

## 4. Per-leg checklist

Run this on every leg, every week:

- [ ] What was this leg *for*, in my recorded thesis?
- [ ] Is that reason still true, based on facts dated this week?
- [ ] If the price moved, was it the leg's own facts or the market's mood?
- [ ] Is the leg closed already? (A row marked `CLOSED <action> <date>` is gone; its cash is yours.)
- [ ] Is the stop still close enough to the price to mean something?
- [ ] Does this leg offset another leg's risk, or duplicate it?
- [ ] Is the size justified by the strength of the evidence, and is there a named reason it isn't bigger?
- [ ] Is there a dated catalyst inside the holding window (earnings, a central-bank meeting, an election)?

And on the book:

- [ ] What single scenario hurts this book most, and is that acceptable?
- [ ] Is cash at a level I can defend in one sentence?
- [ ] Round 3 only: is overlap with my Round 2 book well under 50%?

---

## 5. Writing the return

One JSON file per book, written to the exact path in your dispatch message.

**To hold:**

```json
{"decision": "HOLD", "reason": "<why holding beats trading, with this week's dated facts>"}
```

**To trade**, the complete replacement book:

```json
{
  "name": "Claude Fable (orchestrator)",
  "strategy": "<one sentence describing the book as it now stands>",
  "entry": "<next trading date>",
  "capital_usd": 1000,
  "cash_pct": 25,
  "reassessment_note": "<see structure below>",
  "positions": [
    {"symbol": "TLT", "kind": "equity", "side": "long", "weight_pct": 8,
     "stop_loss_pct": 7.0,
     "thesis": "<specific reasoning for THIS leg at THIS size>"}
  ]
}
```

### The reassessment note

The manager's notes follow the same structure every week. Use it:

1. **Status in one line:** the book's result and drawdown against SPY, and whether the thesis held.
2. **What changed this week:** dated facts only.
3. **What did not change**, and why that matters.
4. **Numbered changes**, each with its reason: `(1) New 8% leg in TLT …`, `(2) XLF cut from 10 to 7 …`.
5. **Cash:** the level and why.
6. **Stops:** whether they were re-based, and the cost.
7. **Round 3 only:** the overlap with Round 2.

### A leg thesis

Each thesis answers four things: **why this name, why this size, what the catalyst is, and why the stop is where it is.** For example:

> **TLT, long 8%, stop 7%.** New early trend-reversal leg. The 10-year touched 5.34% this week, the highest since 2002, and then September payrolls came in at +29k vs ~85k expected with July revised negative; October-hike odds fell from ~70% to ~14%. A 5.5%+ 30-year coupon pays to wait, and the asymmetry at a 24-year high in yields with a cracking labor market is what this mandate exists to catch. The counter-case (oil near $100, record fiscal supply, a Fed that still leans hawkish) is why the stop is a tight 7%: if yields make a new high, exit cheaply rather than argue. Deliberately paired against the XLE leg.

---

## 6. Hard rules

A book that breaks any of these is rejected whole and your previous book stands.

1. `sum(weight_pct) + cash_pct == 100` (±0.05). Every weight ≥ 0; `cash_pct` ≥ 0.
2. Short weights total ≤ 100. Perp `leverage` must be in (0, 100], and `leverage` appears **only** on `kind: "perp"`.
3. `kind` is `equity`, `crypto` or `perp`. `side` is `long` or `short`.
4. Crypto and perp symbols are the bare ticker (`BTC`) or the `-USD` form (`BTC-USD`).
5. `CASH`, `USDC`, `USD`, `MONEY` and `CASHX` are real listed securities, **not cash**. Hold cash through `cash_pct`.
6. `stop_loss_pct` and `take_profit_pct` are positive magnitudes (a 15% stop is `15.0`). Omit them rather than passing 0.
7. Every position needs a real `thesis`, and every traded book a real `reassessment_note`.
8. **Every symbol must be a real, currently listed instrument.** Verify it against a live quote. Never infer a ticker from a fund's name — a book was rejected for an invented one.
9. **Round 3 novelty:** under 50% same-direction gross-weight overlap with your own live Round 2 book. If your Round 2 return is a HOLD, the live Round 2 book is the one already registered — measure against that.

**Frictions you pay:** equities 2bps per side (5bps leveraged ETFs, 12bps under $15/share, plus 0.31bps on sells); crypto spot 35bps; perps 7.5bps of notional plus 10% APR funding on longs; short borrow 3% APR. Idle cash earns 4% APY. Small resizes are cheap; full rebuilds and crypto churn are not.

**Process rules:** write only to your own directory; do not read other managers' packets, decisions or notes.

---

## 7. Worked decisions

### Hold the core, sell the broken legs (2026-09-15, Round 2)

**Situation:** chip stocks fell 6% in a day on an AI-pacing essay. The book was down.
**Test applied:** sentiment vs own facts (§3.1).
**Decision:** kept MU, AMD, NVDA, TSM and ANET; raised MU to 24%; sold Vertiv and GE Vernova; cash to 21%.
**Why:** the core's demand data was the opposite of weak (memory prices at records, HBM sold out). Vertiv and GE Vernova had their own problems unrelated to the essay.

### Exit a winner whose reason expired (2026-09-08, Round 3)

**Situation:** the book was built for a rate-cutting cycle. Payrolls beat, the 10-year hit 4.82%, and markets began pricing a hike.
**Test applied:** audit your own thesis (§3.2).
**Decision:** sold XBI (14% → 0) at a gain, cut KRE, added XLE 12% as the new regime's lead.
**Why:** XBI's own recorded reason was the rate-cut trade, and that trade was gone.

### Change risk, not direction (2026-10-05, Round 2)

**Situation:** the book was up ~15%, every thesis intact, AI stocks at records.
**Test applied:** stale stops (§3.5) and trim after a run (§3.4).
**Decision:** same names; AMD 18 → 14; TSM and ANET up; every stop re-based to the new fill.
**Why:** *"What changed is risk management, not direction."* Most legs had no stop at all, though this same book had fallen 14.7% from its peak in July.

### Catch the turn early, with a cheap exit (2026-10-05, Round 3)

**Situation:** the 10-year hit a 24-year high, then payrolls missed badly and hike odds collapsed.
**Test applied:** early trend-reversal (the mandate), paired risk (§3.6).
**Decision:** new TLT 8% with a 7% stop; XLF cut 10 → 7 into bank earnings; XLE kept as TLT's offset.
**Why:** the asymmetry at a multi-decade yield high is what this mandate exists for, and the tight stop keeps being early cheap.

---

## 8. Anti-patterns

- **Selling a working thesis into a sentiment dip.**
- **Holding a leg after the reason for owning it has gone**, because it is profitable or because you don't want to admit the change.
- **Rebuilding the whole book** when one leg changed.
- **Changes with no named cause.** "Felt like rotating" is not a reason.
- **Stops far below the market**, or no stops at all.
- **Two legs that lose in the same scenario** without that being a deliberate choice.
- **Deploying cash because it is there.**
- **Leverage.**
- **Reasons that could have been written from memory.**
- **Inferring a ticker from a fund's name.**
- **Claiming research you did not do.**

---

## Appendix: book history

### Round 2

| Entry | Cash | Book |
|---|---|---|
| 2026-07-16 | 22% | MU 15, AMD 12, NVDA 12, GEV 10, TSM 8, VRT 8, ANET 8, BTC 5 |
| 2026-07-20 | 13% | MU 18, AMD 15, NVDA 15, GEV 10, TSM 8, VRT 8, ANET 8, BTC 5 |
| 2026-09-08 | 15% | MU 18, AMD 18, NVDA 16, GEV 4, TSM 8, VRT 8, ANET 8, BTC 5 |
| 2026-09-16 | 21% | MU 24, AMD 18, NVDA 16, TSM 8, ANET 8, BTC 5 |
| 2026-10-05 | 22% | MU 24, AMD 14, NVDA 16, TSM 10, ANET 9, BTC 5 |

### Round 3

| Entry | Cash | Book |
|---|---|---|
| 2026-07-17 | 20% | XBI 14, KRE 12, XLF 10, XLV 10, JEPQ 10, IWD 8, EWJ 8, ETH 5, SOL 3 |
| 2026-09-08 | 26% | XLE 12, IWD 12, XLF 10, EWJ 10, JEPQ 10, XLV 8, KRE 4, ETH 5, SOL 3 |
| 2026-09-16 | 30% | XLE 12, IWD 12, XLF 10, EWJ 10, JEPQ 10, XLV 8, ETH 5, SOL 3 |
| 2026-10-05 | 25% | XLE 12, IWD 12, XLF 7, EWJ 10, JEPQ 10, XLV 8, TLT 8, ETH 5, SOL 3 |

The account could not be polled the week of 2026-09-28, so both books held by default that week.

Full reasoning for every decision is in `experiments/desk/week*.json` under the name `Claude Fable (orchestrator)`.
