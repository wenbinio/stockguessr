# Info Desk protocol

## v3 — free information (effective 2026-07-30) — CURRENT

Adopted at the user's instruction: agents may *"use the internet freely and
resize, or do any other thing that a retail trader may do, freely."*

**The drip is retired.** Releasing one curated market fact per week is
incoherent alongside unrestricted internet access, and disclosing each agent's
own NAV removes the blinding the drip was built to provide. Nothing about v2
survives except the archive.

What the weekly desk now does:

1. **No collection step.** There is no Sonnet collector run and no embargoed
   file. Agents research the market themselves, with the same access a retail
   trader has: news, filings, transcripts, analyst commentary, prices, volume,
   sentiment.
2. **Full own-account disclosure.** Each agent receives its current NAV, P&L in
   dollars and percent, per-position marks, fills executed since the last poll
   (including any stop or take-profit that fired), and its working standing
   orders.
3. **Free sizing.** No maximum position, no minimum position count, shorts to
   100% of notional, perp leverage to 100x. Agents may resize legs rather than
   replacing the whole book. Only arithmetic binds: weights + cash = 100.
4. **Free timing between polls.** Standing orders are freely attached, modified
   or removed and fire at any daily close; an agent may register a dated
   intraweek rebalance which fills at that date's close.
5. **Weekly prompting cadence retained** (Saturday 12:00 UTC) as the polling
   point — chosen for compute cost, not to constrain agency.

Full amendment, including what this costs the experimental design, is in
`../round2/RULES.md` § "Unrestricted retail rules".

### Analysis boundary

**2026-07-30 is an epoch boundary.** Pre-change books were produced under
information and sizing constraints; post-change books were not. Do not pool the
two epochs. Expect post-change dispersion to widen mechanically — free sizing
raises variance, which will make some agents look far more skilled than they
are.

---

## v2 — drip release (2026-07-21 to 2026-07-29) — RETIRED, archived

Superseded by v3 above after one full cycle (week 2, 2026-07-25). Retained
because the data it produced is in the record and must be interpretable.

Under v2, each week a single **Sonnet collector agent** gathered market data
(Yahoo daily closes, point-in-time) and compiled **10 discrete, facts-only info
items** ranked by materiality, stored embargoed under `collected/<date>.json`.
The desk released **exactly one item per week** into `released/`, and managers
making their weekly plays received only their own book plus the cumulative
released items — no NAV, no performance, no full market table, no unreleased
items. The intent was to make information a controlled variable, so week-on-week
plays could be attributed to specific released facts.

It worked, and the one cycle of evidence is worth keeping: under v2 most
managers explicitly declined to trade on partial information (Haiku
concentrated AI/tech: "only 5% of portfolio has price data"; Fable Barbell
called re-ranking without signal "pure noise trading with real costs"), in
sharp contrast to week 1's simultaneous full-information capitulation. 18 of
37 rebalanced.

Released under v2: `2026-07-21_item1` (semis/leveraged tech), `2026-07-25_item1`
(semis reversal). The remaining collected items were never released and stay
embargoed in `collected/`.

## Directory layout

- `collected/<date>.json` — v2 collector files (historical; no longer produced)
- `released/<date>_item<N>.json` — items released under v2 (historical)
- `released/index.json` — cumulative v2 release log (historical)
