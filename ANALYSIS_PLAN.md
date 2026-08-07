# Pre-registered analysis plan (committed before Round-3 entry and before forward outcomes accrue)

Adopted from the independent Fable methodology review of 2026-07-16. This plan
binds the final report; deviations must be disclosed as post-hoc.

## Primary endpoint

**Daily-return CAPM alpha** vs SPY (two-factor SPY+BTC for multi-asset Round-2/3
books), estimated by daily regression with Newey-West (HAC) standard errors.
Raw NAV / total return is a secondary, descriptive endpoint. Rankings are
reported in flat dollars and percent, but *inference* uses alpha.

## Luck discipline

- Bootstrap null baskets get per-basket beta and alpha; luck percentiles are
  reported on **alpha**, not raw return.
- Per-book significance uses family-wise correction across all books
  (max-statistic / Romano-Wolf stepdown against the bootstrap null).
- Already-known result under this standard: only the top Round-1 book clears
  the max-of-28 unlevered null (95th pct of max ≈ +51.5%); books 2-4 do not
  (p ≈ 0.08-0.12). This is disclosed rather than hidden.

## Dependence handling

- Tier comparisons use spread portfolios of **daily returns** (mean of tier A
  books minus tier B), tested with HAC errors or stationary block bootstrap —
  absorbing cross-book correlation from shared holdings (e.g. AVGO in 11/28
  R1 books).
- Reports include average pairwise correlation of book returns and an
  effective-number-of-bets estimate; headline counts like "16 of 28 beat SPY"
  carry that context.
- Sonnet-vs-Haiku uses the paired-by-mandate design; the R1 result
  (Haiku wins 7/10 pairs, sign-test p ≈ 0.34) is reported as within noise.

## Tier inference

No classical test at n=3 (Fable). Tier means are reported with bootstrap CIs
and no p-values unless/until the Round-3 factorial arms and replicate variance
permit a hierarchical model (book ~ tier + tooling + mandate + noise).

## Known confounds (disclosed in every report)

Tier x tooling x backtest-procedure x mandate confound (partially broken by
R3 factorial arms); experimenter-is-participant (orchestrator wrote rules,
engine, context packs, and competes); curated-context herding in fleet legs
(mitigated from R3 by mechanical context packs); tournament incentive favors
variance; H2-leg same-close fill convention vs R2/R3 next-close convention;
single price source (Yahoo); daily-close granularity favoring high leverage;
dropped-ticker renormalization in R1.

---

# Amendment 2 — epoch-2 endpoint (pre-registered 2026-08-07)

Adopted from the independent Fable design critique of 2026-08-07
(`experiments/reviews/design_critique_2026-08-07.md`). Committed **before** the
outcomes it governs have accrued: at the time of writing, prices run through
the 2026-08-06 close and epoch 2 is five sessions old.

## Why this amendment exists

The original confirmatory endpoint scores Round 2 over its whole life,
2026-07-16 to 2026-12-31. On 2026-07-30 every agent simultaneously received
free internet, own-account visibility and unrestricted position sizing. The
rules themselves (`experiments/round2/RULES.md`, "Consequences for the
experimental design") forbid pooling across that boundary. The original
endpoint therefore pools exactly what the rules say cannot be pooled, and it
cannot be repaired after the fact by any statistical adjustment.

## The endpoint, restated

1. **Confirmatory endpoint (epoch 2 only)**: daily-return CAPM alpha vs SPY
   over **2026-08-03 to 2026-12-31** — the first full session after the
   epoch-2 books filled (2026-07-31) through final scoring. HAC (Newey-West)
   standard errors, family-wise Romano-Wolf stepdown across all books in the
   round. This is the only window on which an inferential claim may be made.
2. **Epoch 1 (2026-07-16/17 to 2026-07-30)** is reported separately and
   **descriptively only**. Eleven sessions cannot support inference and will
   not be asked to.
3. **The full-window ranking is demoted to descriptive.** It may be shown as a
   tournament result — it is what actually happened to the money — but no
   p-value, significance claim, or tier inference may be attached to it.

## What this amendment concedes, permanently

The treatment hit all 46 agents at once, so there is **no control arm**: the
effect of free information and free sizing is confounded with whatever the
market did after 2026-07-30, and no re-registration recovers it. The Round-3
factorial tooling arm (5 Sonnet-with-tools vs 5 Opus-without-tools) measured a
contrast that no longer exists; its pre-2026-07-30 data remains valid for that
contrast and nothing after does. Cross-agent blinding ended on 2026-07-30 and
is not reinstated, since the results are published continuously to a public
hub; any post-epoch-2 herding is therefore uncontrolled and must be disclosed.

## Binding procedural commitments

- **Every interim statistical run is logged**, whether or not its result is
  reported, in `experiments/reviews/analysis_runs.jsonl`: timestamp, script,
  window, what was computed, and the result. Selective reporting is prevented
  by making the unreported runs part of the record.
- **Both directions of every persistence test are reported.** The 2026-08-07
  critique found that R1→R2 rank correlation had been reported repeatedly
  (rho = -0.049) while R1→R3 had never been computed (rho = +0.470). Any
  persistence claim must state every pairing tested.
- **Inference runs only from `tracker/stats.py`**, which implements this plan.
  Ad-hoc t-statistics computed in a shell are descriptive only and must be
  labelled as such. The 2026-08-07 critique found the orchestrator reporting
  OLS t-statistics while citing this plan's HAC requirement; under HAC the
  count of Round-2 books clearing |t| > 1.96 falls from 1 to 0.
- **The desk is audited by an independent agent before December scoring**, in
  the manner of the Round-1 forensic audit, covering repair discretion,
  validation gaps and rule-amendment authorship.
