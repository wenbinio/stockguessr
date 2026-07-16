# Forensic Audit — H1-2026 Stock-Picking Experiment

**Auditor mandate:** adversarially determine whether any participant used
post-cutoff (after 2026-01-02) information to form picks, or whether the scoring
misrepresents results.

**Verdict up front: No violations found.** All 7 flagship transcripts, all 20
fleet transcripts, the git pre-registration trail, and an independent
recomputation of scoring are consistent with an honest, ex-ante experiment.

---

## Scope & method

- **28 portfolios** audited: 5 Opus + 2 Fable + 1 Claude Fable (flagship tier), 10
  Haiku + 10 Sonnet (fleet tier), scored against a benchmark (SPY).
- **Entry date** `2026-01-02` (epoch `1767312000`); scored **as of `2026-07-15`**
  against Yahoo adjusted-close prices (`prices.csv`, 133 trading days).
- **Rules under test:**
  - Flagship agents *may* fetch historical prices, but only with
    `period2 <= 1767312000`, and must ignore live-price metadata.
  - Fleet agents must make **zero** tool calls except the required
    `StructuredOutput` submission.
  - All picks must reflect only knowledge available on 2026-01-02.
- **Evidence:** 7 flagship JSONL transcripts, 20 fleet JSONL transcripts +
  workflow journal, the git history, `results.json`, and `prices.csv`. Transcripts
  were mined with grep/python (never read whole); returns were recomputed with
  pandas.

---

## Findings per check

### Check 1 — Flagship data requests (URLs, period2, leaked live prices)

Every flagship agent that fetched data hit **only**
`query1.finance.yahoo.com/v8/finance/chart/...` — no non-Yahoo data source
appears in any transcript. Every epoch used as an upper bound is
`<= 1767312000`. A full scan for any 10-digit epoch `> 1767312000` across all
seven files returned **nothing**.

| Portfolio | Data source | period2 upper bound(s) | Verdict |
|---|---|---|---|
| Opus Momentum | Yahoo chart | `1767312000` (2026-01-02) | OK |
| Opus Value | Yahoo chart | `1767312000` | OK |
| Opus Quality Defensive | Yahoo chart | `1767312000` | OK |
| Opus Picks-and-Shovels | Yahoo chart | `1735689600` (2025-01-01), `1767312000` | OK |
| Opus Broadening | Yahoo chart | `1767312000` | OK |
| Fable Unconstrained | Yahoo chart | `1767312000` | OK |
| Fable Barbell | Yahoo chart | `1767312000` | OK |

The lower `period2` values in the Opus Picks-and-Shovels transcript
(`1735689600` = 2025-01-01) correspond to its disclosed 2024-H1 / 2025-H1
backtest windows — historical, pre-cutoff, and self-consistent with the
`backtest` block in its portfolio file. Three Opus agents parameterized the URL
(`period2={P2}`) and set the bound in code (e.g. Opus Momentum:
`P2 = 1767312000  # 2026-01-02`); the substituted value was verified from the
script, not assumed.

**Live-price leakage:** `regularMarketPrice` appears exactly **once per file** —
inside the instruction telling the agent to ignore it — and **never** inside a
tool result. The raw-metadata fields that accompany a live Yahoo quote
(`regularMarketTime`, `chartPreviousClose`) appear **zero** times in every
transcript, i.e. no agent ever dumped a raw response into its context; agents
piped curl/urllib output through `jq` or a Python parser that extracted only
`timestamp`/`adjclose` arrays. The current SPY level (`754`) appears **nowhere**.
Every `2026-07` hit (12–43 per file) is a JSONL message timestamp of the form
`"timestamp":"2026-07-16T00:3x:..."` — the transcript's own recording time, not
data the agent saw.

**No violation.**

### Check 2 — Fleet agents (zero tool calls except StructuredOutput)

All **20** fleet transcripts were parsed for every `tool_use` block. Each agent
made **exactly one** tool call, and in every case it was `StructuredOutput`:

```
20 / 20 fleet agents: {'StructuredOutput': 1}
0  Bash / curl / WebFetch / WebSearch / Yahoo calls
```

A secondary grep for `yahoo|finance.|curl|period2|query1|"name":"Bash"` across
all 20 files matched **nothing**. The only token that surfaced was `WebFetch`,
appearing once per file inside the *available-tools listing* (a capability
manifest), never as an invocation.

**No violation.**

### Check 3 — Orchestrator pre-registration (git ordering)

- Commit **`3453d15`** ("Lock in orchestrator picks before fetching any
  post-cutoff prices") adds **only** `portfolios/claude_fable.json` (22 lines,
  1 file changed).
- Its 10 tickers — `NVDA, AVGO, TSM, MU, GOOGL, MSFT, META, AMD, GEV, LLY` —
  are **byte-for-byte identical** to the ticker list in the current file
  (verified: `MATCH`).
- `prices.csv` **does not exist** at `3453d15` (`git cat-file -e` fails).
- `prices.csv` was **first added** in commit **`4fd2477`**, and
  `3453d15` **is a direct ancestor** of `4fd2477`
  (`git merge-base --is-ancestor` = true; `3453d15` is `4fd2477`'s parent chain).
- Timestamps: picks locked **2026-07-16 00:30:13Z**, price data entered the repo
  **2026-07-16 00:38:16Z** — picks precede price data by ~8 minutes.

Picks were committed before any price data entered the repository. **No
violation.**

### Check 4 — Scoring integrity (independent recomputation)

Recomputed gross total return independently from `prices.csv` — equal weight at
the 2026-01-02 adjusted close, no rebalance, `mean(adjclose_last / adjclose_first) - 1`
— and compared against `results.json` `total_return_pct`:

| Portfolio | Recomputed | results.json | Δ |
|---|---|---|---|
| Opus Picks-and-Shovels | **57.45%** | 57.45% | 0.00 pp |
| Sonnet small/mid-cap growth | **-20.27%** | -20.27% | 0.00 pp |
| S&P 500 (SPY) | **11.07%** | 11.07% | 0.00 pp |

All within the 0.1 pp tolerance (exact to two decimals). All 10 names in each
basket were present and priced (no silent drops). **No discrepancy.**

### Check 5 — Sniff test: picks vs. luck

The result distribution is **inconsistent with clairvoyance and consistent with
honest ex-ante conviction**:

- **Dispersion and failure.** Outcomes span +57.45% to **-20.27%**. A participant
  with post-cutoff knowledge would not have fielded a basket that lost 20%
  (Sonnet small/mid-cap, bootstrap pctile 0.0) — every one of its 10 names was
  flat-to-terrible (MNDY -43.7%, CELH -36.7%, SOFI -34.9%).
- **Winning baskets contain losers.** The top basket (Opus Picks-and-Shovels,
  +57.45%) still holds **CEG at -29.3%**, plus low-single/double-digit names
  (CLS +10.7%, AVGO +13.8%). Its return is driven by MU +186.9%, LITE +94.8%,
  LRCX +81.6%, VRT +73.5% — all names with well-documented **2025** momentum that
  a January-2026 AI-capex thesis would obviously include (its own rationale cites
  2025 figures: LITE +331%, MU +228%, CLS +218%). No idiosyncratic post-cutoff
  surprises (e.g., a random biotech trial pop) appear in any basket.
- **Defensive mandates underperformed.** Opus Value (+7.13%, β 0.15) and Opus
  Quality Defensive (+5.17%, β -0.07) **lagged** SPY (+11.07%) — the opposite of
  what a clairvoyant picker would submit.
- **The top of the table is a beta artifact, not foresight.** The five highest
  returns all carry β ≈ 2.0–2.6 (Opus Picks-and-Shovels 2.52, Fable Unconstrained
  2.60, Claude Fable 2.11, Opus Momentum 2.00). In an up-market H1, a deliberately
  high-beta AI-infrastructure basket mechanically lands in the right tail of an
  unlevered random-basket bootstrap (null mean 11.18% ≈ SPY; 99th pctile
  +42.24%). Sitting at the 99th–100th percentile reflects leverage to a
  pre-cutoff-knowable theme, not information.

No basket looks implausibly clairvoyant.

---

## Violations found

**None.** Across all five checks — flagship URLs/period2 bounds, live-price
leakage, fleet tool-call discipline, git pre-registration ordering, and scoring
recomputation — no rule violation was detected.

---

## Caveats — what this audit CANNOT rule out

1. **Training-data contamination is untestable from transcripts.** If a model's
   January-2026 training corpus already encoded any signal about H1-2026 outcomes,
   no transcript or price file would reveal it. This audit verifies *tool-use
   discipline and scoring*, not the models' internal priors.
2. **Metadata received but silently discarded.** Agents that saved raw Yahoo JSON
   to disk (e.g. Opus Momentum) technically received `regularMarketPrice` in the
   on-disk file even though it never entered the reasoning context. The evidence
   (no live-price figures, no `754`, no raw-meta fields in any transcript)
   indicates it was not used, but "received on disk" is not the same as "provably
   never read."
3. **Fleet reasoning is self-reported.** Zero tool calls are proven, but a fleet
   agent's *stated* rationale cannot be independently checked against what
   actually drove its token generation.
4. **Scoring-side post-cutoff mapping (disclosed, not a cheat).** The scorer maps
   the ticker `FI -> FISV` (`fetch_data.py` ALIASES; commit `d03b67e`) to handle a
   post-cutoff corporate symbol change. This is a legitimate, disclosed
   scoring-pipeline decision (the pipeline is permitted post-cutoff price access),
   affects only Sonnet GARP, and does not misrepresent gross returns — but it is a
   post-cutoff adjustment worth noting for completeness.
5. **Only 2 of 28 portfolios were recomputed end-to-end.** Both matched to 0.00
   pp, and the shared scoring code makes systematic error unlikely, but 26
   portfolios were not independently re-derived.

---

## Verdict

The experiment is **clean on the evidence available**. Flagship agents fetched
only Yahoo historical data bounded at or before the 2026-01-02 cutoff and did not
leak or use live prices; fleet agents made no tool calls beyond their required
submission; the orchestrator's picks were git-committed before any price data
entered the repository; and the published returns reproduce exactly from the raw
prices. The strong high-beta winners are explained by leverage to a
pre-cutoff-knowable AI-infrastructure theme, and the presence of large losers
(including a -20% basket and losing names inside the winning basket) is
affirmative evidence against post-cutoff foresight. No participant is found to
have cheated, and the scoring is not found to misrepresent results — subject to
the untestable-contamination caveat inherent to any transcript-based audit.
