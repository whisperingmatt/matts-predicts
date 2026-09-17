project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S6 (GROWTH-002): 12-month labels, two new features, decile ranks, build-window single-feature tables and composite
status: COMPLETE — everything in S6 built and verified; no feature passes on win_50 in its declared direction; composite is the unconfirmed top-3 fallback. Holdout not opened.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1.5 hours

---

## What Was Built or Changed

The spec was placed at specs/GROWTH-002-decile-retest.md. Its section 2 names six raw values "from features.parquet" that S3 never wrote: rev_growth_accel, op_margin_delta, pe_vs_5y_median, dist_above_30w_sma, atr_contraction, share_count_change_8q. They were intermediates inside features.py. The ruling (decisions.md, Chunk 4b) was to append them as new columns by extending features.py and to prove every pre-existing column unchanged. The proof found a pre-existing nondeterminism instead: the 13F share sum was a floating-point sum in duckdb's arbitrary parallel order, so inst_pct differed by up to 2e-13 between runs and 14 sponsorship flags flipped where a quarter tied its predecessor. The sum is now exact decimal; two consecutive builds are identical across all 56 columns; against the S3 file, 2 flags differ, both in the holdout, and the S5 report moves by one row in two cells with no verdict change. The regenerated S5 files are committed.

src/labels12.py builds the 12-month labels (E1) exactly as labels.py builds the 24-month ones; labels.parquet is untouched and supplies launch_300 as the reference. src/decile.py computes the 22 raw values (two of them new: pegy and shareholder_yield per E3), ranks each within (month_end, lag) among non-null rows with a tie rule that never splits equal values (decile 10 always the maximum), writes deciles.parquet for every month, and on the build window produces per-decile lift tables for win_50, win_100, and launch_300 at four lags, overall and by regime bucket, the declared-extreme-cell table with Spearman rho, build-window verdicts, and the section 4 composite. The report reports/decile_build_results.md embeds reports/decile_build_reading.md. Ordering is deterministic.

## Files Touched [MANDATORY]

- specs/GROWTH-002-decile-retest.md (new; the uploaded spec, verbatim)
- strategies/02-growth/src/features.py (six raw columns appended; exact 13F sum)
- strategies/02-growth/src/labels12.py (new)
- strategies/02-growth/src/decile.py (new)
- strategies/02-growth/reports/decile_build_results.md, decile_build_reading.md (new; committed)
- strategies/02-growth/reports/s6_decile_cells.csv, s6_extreme_cells.csv, s6_composite.csv (new; committed)
- strategies/02-growth/reports/holdout_results.md, s5_single_signal.csv (regenerated: one row moved in two h10 cells)
- decisions.md (Chunk 4b section: spec placement, feature extension and definitions, labels, decile tie rule, pass reading, composite; determinism fix)
- BACKLOG.md (Chunk 4b section: S6 DONE, S7 TODO)
- docs/wrapits/WRAPIT_2026-09-17-1810_s6-decile-build.md (this file)
- data/processed/features.parquet (56 columns), labels12.parquet, deciles.parquet (gitignored, regenerable)

## Environment Variables [MANDATORY]

None used. No network access this session.

## Services and Integrations Touched [MANDATORY]

None.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. features.py extension: `python -m src.features` → `RESULT: PASS — features written, point-in-time clean`, 56 columns (50 + 6). Column-by-column comparison with the S3 file: only inst_pct, inst_pct_prev (≤ 2.3e-13) and h10_sponsorship (2 rows, both holdout) differ; all other 47 columns identical on all 2,353,204 rows. Two consecutive runs after the exact-sum fix: 0 differing rows across all 56 columns.

2. Regression on S4/S5 with the new file: `python -m src.stats` → build report and CSVs unchanged; `python -m src.holdout` → holdout_results.md differs in two h10 rows (rows_true 7,693→7,692 and 7,618→7,617; rate 1.75%→1.76%, 3.08%→3.09%), verdicts unchanged.

3. `python -m src.labels12`: 588,301 rows, 563,218 with a 12m return, last observable month end 2025-08-31; build window win_50 46,046 (11.70%), win_100 10,731 (2.73%), 0 unlabeled; `RESULT: PASS — win_50 base rate inside [3%, 25%]`. Hand recomputation with pandas from the price table for AAPL 2006-01-31 (0.1355), a delisted row ABI1 2008-06-30 (−0.1684, terminal 2008-11-21), and a doubler A 2009-03-31 (1.2374): all matched to 1e-9 with the right flags.

4. `python -m src.decile`: `deciles.parquet: 2,353,204 rows, 22 features`; win_50 base 11.70%; `RESULT: PASS — build-window decile report written`, 26 seconds. Decile sizes at lag 0: continuous features 10.0% per decile; insider_buy_count_90d decile 1 = 79.2% (zeros) and deciles 7–10 = 1.4% to 7.6%; dividend_yield decile 1 = 48.8% (zero yield).

5. Verdicts on win_50: 22 of 22 FAIL in declared direction. Best extreme cells: inst_pct_delta_qoq 1.48 [1.42, 1.53] lag 0; ret_12m_skip1 1.38 lag 6 (rho −0.04); dist_above_30w_sma 1.34; ret_6m_skip1 1.33 (rho −0.12); pe_vs_5y_median 1.35 (rho −0.41); marketcap 1.31 (rho −1.00); pegy 1.31 (rho −0.89); dividend_yield 1.30 (rho −0.79); peg 1.29 (rho −0.93). Backward with monotone curves: pct_from_52w_high 0.79 (rho +1.00), share_count_change_8q 0.93 (rho +0.83), shareholder_yield 0.91 (rho −0.83). PASS-build on win_100: peg (all lags, 1.78 [1.63]), pegy (all lags, 1.83 [1.68]), marketcap (all lags, 2.03 [1.95], rho −1.00), dividend_yield (lags 6, 12, 1.56). PASS-build on launch_300: marketcap (all lags, 2.32 [2.14], rho −0.98). None regime-dependent.

6. Composite: fewer than 3 pass on win_50 → UNCONFIRMED top-3 by extreme-decile lift: ret_12m_skip1, pe_vs_5y_median, inst_pct_delta_qoq. Coverage 29.2% at lag 0; decile 10 = 2.4% of universe rows, deciles 8–10 = 7.5%; win_50 lift 1.12 [1.05, 1.20] (771 events) and 1.12; win_100 decile 10 1.72 [1.47, 2.01] (154), 1.91 at lag 12; launch_300 decile 10 42 events, insufficient. Every regime bucket beyond 10% drawdown is empty for the composite.

State: S6 BUILT and VERIFIED.

## How to Verify This Is Working Right Now

Warning first: a fresh cloud session has no data; steps 2 to 3 take about twelve minutes and the key must be in the environment.

1. New session, branch claude/nice-dijkstra-801d68 (or main once merged): `cd strategies/02-growth`
2. `python -m src.fetch_bulk && python -m src.ingest`
3. `python -m src.universe && python -m src.labels && python -m src.regime && python -m src.features && python -m src.labels12`
4. `python -m src.decile` — expect `win_50 base 11.70%`, a verdict table with 22 FAIL rows on win_50, `composite members (UNCONFIRMED top-3): ['ret_12m_skip1', 'pe_vs_5y_median', 'inst_pct_delta_qoq']`, `RESULT: PASS`.
5. `git diff --stat reports/` — no change unless Sharadar restated history after 2026-09-17.

## What Breaks and How to Fix It

- `STOP: win_50 base rate outside [3%, 25%]`: labels12 or the universe changed; do not proceed; report.
- A raw column missing (`Binder Error ... not found`): features.parquet predates the S6 extension; rerun `python -m src.features`.
- Composite decile 10 empty or tiny after a data refresh: the tie rule on a mean of few integer deciles; the pool share is reported, not tuned. If S7 needs a larger pool the recipe change goes through decisions.md.
- rho `n/a` with a PASS-looking lift: fewer than 5 deciles met D8 (rare labels); the feature cannot pass by section 3 as read; the CSV carries every decile's counts.

## Environment Facts Learned [MANDATORY]

- duckdb floating-point sums are order-dependent across runs; any sum feeding a committed number must be exact (decimal) or sorted. Added to decisions.md; worth a CLAUDE.md line if a third instance appears.
- percent_rank with ties-low makes a mass point at the minimum collapse into decile 1 (dividend yield 49%, insider count 79%). Reported beside every cell; recorded in decisions.md.
- The full S6 pipeline (labels12 + decile) runs in about 35 seconds.

## Ephemeral Outputs Not Yet Saved

None. All tables are committed; parquet is regenerable.

## Plain English Summary for Matt

The retest fixed the two problems it was built for: the 12-month label happens one time in nine, so every cell is readable, and ranking into deciles removed the ceiling that capped the majority flags. What it found is that nothing passes on the main label in the direction we declared. Momentum's curve is a U: the worst decile a year earlier wins 50% as often as the best, and the middle loses. Three of our declared directions are the reverse of the data, cleanly and monotonically: stocks far from their highs, heavy share issuers, and negative shareholder yield win more, the same lesson the binary flags taught in S4. The one clean declared-direction result is size: the smallest decile wins monotonically, at 1.3 times on the 50% label and 2 to 2.3 times on the rarer 100% and 300% labels, where cheap PEG stocks and non-payers also pass the build half. The composite, built from the top three because none passed, adds nothing on the 50% label and covers 2.4% of stock-months. S7 runs the holdout on all of this for the record; with no build-window pass on win_50, no feature can meet the full section 3 criterion on that label.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| Spec at root specs/ | CLAUDE.md layout | The spec header's strategies/02-growth/specs/ |
| Six raw values appended to features.parquet; existing columns proven unchanged | Spec expects them there; "do not rebuild" honored in substance | Separate computation duplicating features.py |
| 13F sum made exact decimal | Run-to-run reproducibility; 14 flag flips from float order | Leave as is |
| Decile = min(10, floor(10·percent_rank)+1), ties-low | Ties never split; decile 10 holds the max | ntile; dense rank |
| pegy null when pe ≤ 0 or growth+yield ≤ 0; shareholder_yield buyback = −share_count_change_8q/2 | Mirrors H5; "annualized over 2 years" | Compound annualization |
| rho over D8-sufficient deciles, ≥ 5 required; LOW-to-MID exempt from rho | Spec's monotonic test needs readable deciles; no monotone direction declared for inst_pct | rho over all deciles regardless of D8 |
| Pass on a label at any lag; composite per lag from members passing at any lag | GROWTH-001 any-lag rule | Lag-0 only |
| Composite fallback top-3 labeled UNCONFIRMED | Section 4 text | Skipping the composite |

All in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: S6 in full.
- OPEN: S7 holdout (2020-01 to 2025-06) for single features and the composite, with the reading the spec lists; expected win_50 per 10 picks by regime. decile.py needs a holdout mode (window parameter) the way stats.py got one in S5. Note that no feature can meet the full section 3 PASS on win_50.
- OPEN (carried): rename the environment variable to SHARADAR_API_KEY.
- BACKLOG.md was updated this session: Chunk 4b section added, S6 DONE, S7 TODO.

## Open Questions for Matt

1. Three declared directions are backward with |rho| ≥ 0.83. E6 forbids flipping them in this chunk. If a chunk 4c re-declares them, that is a spec entry; nothing here does it.
2. The composite's decile 10 is 2.4% of rows because a mean of three integer deciles has few distinct values. If the candidate pool must be nearer 10%, the recipe (for example ranking the raw mean with ties broken by a member) is a decisions.md change for S7 or later.
3. Momentum's U-shape on the 12-month label is the largest structural finding of the session; both tails beat the middle. The spec has no hypothesis for the bottom tail, so it is reported and not tested.

## SESSION REVIEW [MANDATORY]

5/5 for execution: every S6 item ran, the identity proof caught a real reproducibility defect in S3 and fixed it without changing any published verdict, labels were hand-checked, and the report reads the tables without flipping a direction. What went wrong: nothing in the deliverable; the spec's assumption that all raw values were in features.parquet cost one extension and its verification.

## MATT-NOTE

(for Matt)
