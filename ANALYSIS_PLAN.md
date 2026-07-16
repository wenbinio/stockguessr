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
