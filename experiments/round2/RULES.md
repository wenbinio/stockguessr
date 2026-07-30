# Round 2 — full retail toolkit, $1,000 accounts

Round 2 starts 2026-07-16. Every agent (1 Fable orchestrator, 2 Fable + 5 Opus
flagships, 10 Sonnet + 10 Haiku fleet) runs a fresh virtual **$1,000** account,
scored purely by **NAV growth** from the 2026-07-16 US close through 2026-12-31.
All allocations are pre-registered in git before their entry marks — the forward
test stays leak-proof.

## Instruments

| Kind | What | Costs & mechanics |
|---|---|---|
| `equity` | Long or short any US-listed stock or ETF, incl. leveraged/inverse ETFs; fractional to 0.1% of NAV | 10bps/side; shorts pay 3% APR borrow on exposure; a short that loses its full margin is closed at zero |
| `crypto` | Spot crypto, any liquid `-USD` pair | 25bps/side |
| `perp` | Crypto perpetual futures, long or short, 2–10x leverage; `weight_pct` is the **margin** posted, exposure = margin × leverage | 25bps/side on notional entry; funding 10% APR on notional; **liquidated to zero** when position loss ≥ 95% of margin (checked at daily closes) |
| cash | Un-deployed capital | Earns 4% APY |

**Not allowed:** options (no honest way to score historical chains), anything not
priceable from Yahoo Finance daily closes.

## Sizing constraints

- `sum(weight_pct) + cash_pct = 100` (percent of NAV at each rebalance)
- Max single position: 40%. Total short-side weight: ≤ 50%. Minimum 5 positions.

## Cadence

- **Weekly reassessment**: every Friday close, each agent may submit a new
  allocation, effective at the next trading close. Buy-and-hold in between.
  Turnover pays the per-side costs above.
- Reassessment runs are automated (scheduled session trigger); each week's
  orders are committed to `weeks/<date>/` before their effective close.

## Scoring

- Daily NAV from Yahoo adjusted closes (dividends reinvested), crypto priced
  7 days/week, equities forward-filled on non-trading days.
- Engine: `tracker/round2.py` → `experiments/round2/results.json` +
  `docs/api/round2.json` + `docs/round2.html`.
- Benchmarks: $1,000 in SPY, and $1,000 in BTC, same entry close.

## Known simplifications

Daily-close granularity only (a perp that would have been liquidated intraday
but recovered by the close survives here); flat funding/borrow rates; no
market impact; no taxes. Same for every agent, so the ranking is fair even
where the absolute levels are idealized.

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

---

# Unrestricted retail rules (effective 2026-07-30)

Adopted at the user's instruction: *"Ask all agents to use the internet freely
and resize, or do any other thing that a retail trader may do, freely."*
Everything below supersedes the corresponding earlier section for any book
registered on or after **2026-07-30**. Books registered before that date were
built under the old constraints and stay as-is; nothing is re-registered.

## 1. Free information

Every agent — flagship, fleet, factorial and Opus 5 field alike — now has
**unrestricted internet access**: news, filings, earnings transcripts, analyst
commentary, price and volume data, social sentiment, anything a retail trader
could read. The distinction between "tools-enabled" and "mechanical context
pack" agents is abolished.

Agents also now see **their own account**, as any retail trader does: current
NAV, profit and loss in dollars and percent, per-position marks, realised
fills, and the standing orders they have working.

## 2. Free sizing

No concentration guardrails remain:

- **no maximum position size** (a single name may be 100% of the account)
- **no minimum number of positions** (a one-line book is legal)
- **short side may use the entire notional** (shorts up to 100%)
- **perp leverage up to 100x**, the venue maximum on majors

Agents may resize freely — add to, trim, or exit any leg at a reassessment
rather than replacing the whole book. What survives is arithmetic and venue
reality: position weights plus cash must equal exactly 100% of the account,
weights are non-negative (use `side: "short"` for the short side), and cash
cannot go negative.

Equity margin is **not** enabled: gross equity exposure is still capped at the
account value, because modelling a margin debit would require an interest
model the engine does not have. Leverage is available through perps and
leveraged ETFs. This is the one retail affordance still missing, and it is a
modelling gap, not a rule.

## 3. Free timing, weekly prompting

Agents are polled at the Saturday desk, and between polls they act through
standing orders they control: `stop_loss_pct` and `take_profit_pct` on any
position, freely attached, modified or removed at each poll, evaluated at every
daily close. An agent may also **register a dated intraweek rebalance** by
naming a future trading date, which the engine fills at that date's close.

## 4. What still binds, and why

- **Point-in-time discipline.** An agent acting on date D may consult
  information through D and nothing later. For live forward legs this is
  physics. For **backtests it is now materially harder to enforce** — an agent
  with free internet can trivially read what happened in a historical window
  it is "testing". Backtests registered from 2026-07-30 must state what was
  looked up; they are transcript-auditable and should be read as construction
  checks, not evidence.
- **Fees, funding, borrow and liquidation** are unchanged and apply to every
  fill. At high leverage the 5%-of-margin liquidation floor bites quickly: a
  50x perp is liquidated by a ~2% adverse move.
- **Arithmetic**: weights + cash = 100.

## 5. Consequences for the experimental design (recorded, not hidden)

This is a **treatment change mid-experiment** and it costs three things:

1. **The factorial tooling arm is dissolved.** Round 3's 5 Sonnet-with-tools
   vs 5 Opus-without-tools arm existed to break the tier x tooling confound.
   With both arms on free internet the tooling contrast is gone; what remains
   is a clean same-treatment model comparison, which answers a narrower
   question. The arm keeps its `factorial` tag and its pre-2026-07-30 history
   is still valid for the original contrast.
2. **The Info Desk drip protocol is retired** (see
   `experiments/info_desk/PROTOCOL.md`). Releasing one market fact per week is
   incoherent alongside unrestricted internet, and NAV disclosure removes the
   blinding it was built to provide.
3. **Pre- and post-2026-07-30 data must not be pooled naively.** Everything
   before this date was produced under information and sizing constraints;
   everything after was not. Treat 2026-07-30 as an **epoch boundary** in the
   analysis, report the two epochs separately, and expect post-change books to
   show wider dispersion — free sizing mechanically increases variance, which
   will make some agents look far more skilled than they are.

The exchange is deliberate: less internal validity, much more realism. The
question shifts from "can a constrained model pick stocks" to "what does a
model do with the freedom an actual retail trader has."
