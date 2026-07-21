# Info Desk protocol (adopted 2026-07-21, week 2)

Replaces the week-1 protocol in which all 37 managers received a full
mechanical context pack (complete market table + own NAV/book) every week.

## The change

1. **Collection.** Each week a single **Sonnet collector agent** gathers the
   market data (Yahoo daily closes, point-in-time: data through the most
   recent completed US session only) and compiles **10 discrete, numbered,
   facts-only info items**, ranked by materiality. No recommendations, no
   narrative. Stored under `collected/<date>.json`. The collected file is
   **embargoed** — managers never see it whole.

2. **Release — one item at a time.** Each week the desk releases exactly
   **one** info item (the next unreleased item by rank) into
   `released/`. Managers making their weekly stock plays receive ONLY:
   - their own current book (positions + theses), and
   - the cumulative list of *released* items to date.

   They do **not** receive their NAV, performance, the full market table,
   or the unreleased items. This controls the information channel: we can
   attribute week-on-week plays to specific released facts.

3. **Weekly plays.** Managers may HOLD or REBALANCE as before; the same
   validation rules apply (weights+cash=100, max 40%, shorts ≤50%, min 5
   positions, perp leverage 2–10, R3 novelty <50% overlap vs the R2 book).
   Accepted books go to `experiments/<round>/weeks/<entry-date>/` and fill
   at the next session close via the deterministic engine, unchanged.

4. **Full update at year-end only.** The complete update of all agents —
   full performance collation, full market history, NAV disclosure —
   happens at the end of 2026 (executed with the Jan 2, 2027 final-scoring
   run, which uses the Dec 31, 2026 close). Until then the weekly channel
   is drip-only.

## Directory layout

- `collected/<date>.json` — the Sonnet collector's full 10-item file (embargoed)
- `released/<date>_item<N>.json` — the single item released that week
- `released/index.json` — cumulative list of released items (what managers see)

## Rationale

Week 1 showed broad, simultaneous capitulation when every momentum manager
saw the same full table. Drip release (a) cuts the weekly cost of 37
full-context reassessments to one collector run, (b) turns information
itself into a controlled variable, and (c) prevents the weekly NAV feedback
loop from steering the books until the year-end collation.
