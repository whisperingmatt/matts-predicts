project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S7 (GROWTH-002): decile holdout 2020-01 to 2025-06, composite under the S7 recipe, exploratory realized volatility; end of chunk 4b
status: COMPLETE — holdout computed, reported, and read; no full pass on win_50; four confirmations on rarer labels, all size or earnings-multiple. Chunk 4b ends.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1.5 hours

---

## What Was Built or Changed

src/decile.py was parametrized so the same functions run on either window and gained three things from Matt's S7 brief: the composite recipe is now the mean of raw percentile ranks (LOW features as 1 − rank) instead of the mean of integer deciles; every cell counts, per label, only rows whose label is observable, because launch_300 is null after 2024-08 inside the holdout window; and an exploratory realized-volatility feature (annualized standard deviation of daily log returns over the trailing 252 trading days at the decision trade date) is ranked like the others but kept outside FEATURES and every pass criterion. deciles.parquet now carries both the decile and the raw percentile rank per feature.

src/decile_holdout.py runs the engine on both windows, applies the full section 3 criterion (build PASS-build and holdout lift ≥ 1.5 with lower bound ≥ 1.2 at the same lag), scores the composite in both windows, computes expected win_50 per ten picks by regime bucket with the spec's formula, and writes the realized-volatility decile tables and its decile-rank correlations with market cap, distance from the 52-week high, and share issuance. reports/decile_holdout_results.md embeds reports/decile_holdout_reading.md.

Because the composite recipe changed by ruling, the S6 build report was regenerated under it and the composite paragraph of reports/decile_build_reading.md rewritten to the new numbers; nothing else in the S6 report moved. Recorded in decisions.md.

## Files Touched [MANDATORY]

- strategies/02-growth/src/decile.py (windows, percentile composite, label observability, realized vol)
- strategies/02-growth/src/decile_holdout.py (new)
- strategies/02-growth/reports/decile_holdout_results.md, decile_holdout_reading.md (new; committed)
- strategies/02-growth/reports/s7_extreme_cells.csv, s7_decile_cells.csv, s7_composite.csv, s7_realized_vol.csv, s7_realized_vol_corr.csv, s7_expected_winners.csv (new; committed)
- strategies/02-growth/reports/decile_build_results.md, decile_build_reading.md, s6_composite.csv, s6_decile_cells.csv, s6_extreme_cells.csv (regenerated under the S7 composite recipe; only composite numbers changed)
- decisions.md (one ruling block: S7 holdout rulings)
- BACKLOG.md (S7 DONE; chunk 4b closed)
- docs/wrapits/WRAPIT_2026-09-17-1820_s7-decile-holdout-chunk-4b-end.md (this file)
- data/processed/deciles.parquet (regenerated with percentile columns and realized vol; gitignored)

## Environment Variables [MANDATORY]

None used. No network access this session.

## Services and Integrations Touched [MANDATORY]

None.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. Holdout sizing before code: 2020-01 to 2025-06 has 164,889 universe rows per lag; win_50 27,999 (16.98%), win_100 9,636 (5.84%); launch_300 observable on 140,595 rows (through 2024-08), 1,797 launches. Regime buckets present: drawdown 0-10, 10-20, 20-30 (2,498 rows); months-since-trough 0-12, 13-24.

2. `python -m src.decile` (build, new recipe): `RESULT: PASS`, 52 s. Single-feature tables unchanged from S6. Composite: decile 10 = 2.9% of rows (was 2.4%), win_50 1.12 [1.06, 1.19] on 957 events (was 1.12 on 771), win_100 1.50 [1.30, 1.75] (was 1.72 on 154), launch_300 48 events insufficient.

3. `python -m src.decile_holdout`: `RESULT: PASS — holdout decile report written`, 46 s. Verdicts on win_50: 22 of 22 "no build pass" (no feature passed the build half, so none can confirm). CONFIRMED: marketcap on win_100 at lags 0, 3, 6, 12 (holdout 1.65 [1.58, 1.73], 1,594 events) and on launch_300 at all lags (2.19 [1.99, 2.41], 394 events); peg on win_100 at lags 0, 3 (1.64 [1.48, 1.82]); pegy on win_100 at lags 0, 3 (1.68 [1.52, 1.86]). NOT CONFIRMED: dividend_yield on win_100 (holdout 1.31). Holdout-only clears without a build pass (stay unconfirmed): pe 1.82 on win_100 all lags and 1.84 on launch_300 at lags 6, 12; pb 2.07 on launch_300; op_margin_delta 2.02 on launch_300; ret_6m 2.06 and dist_above_30w_sma 2.02 on launch_300; inst_pct_delta_qoq 1.66 on launch_300.

4. Composite, holdout, lag 0: decile 10 = 6.1% of rows, win_50 1.16 [1.11, 1.21] (1,751 events), win_100 1.41 [1.30, 1.53] (569), launch_300 70 events insufficient; deciles 8-10 = 18.1%, win_50 1.06, win_100 1.15. By drawdown bucket: 1.14 (0-10), 1.20 (10-20), 39 events (20-30).

5. Expected win_50 per ten picks, composite decile 10: 2.01 (drawdown 0-10), 1.84 (10-20), 1.71 (20-30), 1.97 (mst 0-12), 1.98 (mst 13-24); deciles 8-10: 1.84, 1.69, 1.57, 1.81, 1.82. Random ten picks in the holdout: 1.70.

6. Exploratory realized volatility, decile 1 → decile 10 lifts, lag 0: win_50 build 0.24 → 1.57, holdout 0.29 → 1.36; win_100 build → 2.90, holdout → 2.31; launch_300 build → 4.13 (1,049 events), holdout → 3.75 (662). Monotone in every window and lag. Decile-rank correlations, lag 0: marketcap −0.509 build / −0.474 holdout; pct_from_52w_high +0.484 / +0.542; share_count_change_8q +0.320 / +0.405.

7. Reproducibility: the regenerated S6 single-feature CSVs are identical to the committed ones except the composite file; `git diff` on s6_decile_cells.csv and s6_extreme_cells.csv is empty.

State: S7 BUILT and VERIFIED; S6 report regenerated consistently.

## How to Verify This Is Working Right Now

Warning first: a fresh cloud session has no data; steps 2 to 3 take about thirteen minutes and the key must be in the environment.

1. New session, branch claude/nice-dijkstra-801d68 (or main once merged): `cd strategies/02-growth`
2. `python -m src.fetch_bulk && python -m src.ingest`
3. `python -m src.universe && python -m src.labels && python -m src.regime && python -m src.features && python -m src.labels12`
4. `python -m src.decile && python -m src.decile_holdout` — expect both `RESULT: PASS`; the verdict table with CONFIRMED on marketcap (win_100, launch_300), peg and pegy (win_100); `composite members (UNCONFIRMED top-3): ['ret_12m_skip1', 'pe_vs_5y_median', 'inst_pct_delta_qoq']`.
5. `git diff --stat reports/` — no change unless Sharadar restated history after 2026-09-17.

## What Breaks and How to Fix It

- The holdout window must move when prices extend: HOLDOUT_END_12M in decile.py; the 24-month label's observability edge is printed by the sizing query in gate test 1 and must be rechecked.
- A label with zero observable rows in a window (as launch_300 in 2025) prints "-" in the year table and is excluded from that label's cells; if every row of a label is null the extreme tables show n/a rather than 0.
- `KeyError: 'pr_...'`: deciles.parquet predates the percentile columns; rerun `python -m src.decile`.
- Realized vol coverage under 90%: the stocks parquet is truncated; the 252-day window needs a full year of daily rows before the first decision date.

## Environment Facts Learned [MANDATORY]

- A mean of integer deciles has few distinct values and, under the ties-low rule, leaves a tiny top decile; the percentile-rank recipe restores a 10% top decile among covered rows. Recorded in decisions.md.
- duckdb `corr()` on two integer decile columns gives the Spearman correlation on decile ranks directly. This wrap only.
- The S7 pipeline (decile + decile_holdout) runs in about 100 seconds.

## Ephemeral Outputs Not Yet Saved

None.

## Plain English Summary for Matt

The holdout says what you expected it to say. Nothing passes on the 50%-in-a-year label, because nothing passed the build half. Four things confirm on the rarer labels, and they are one idea: small companies, and cheap-on-earnings-growth companies, reach a double or a triple more often, in both windows, at every lag for size. Momentum, margin change, and low PE also clear the holdout bar on the rarer labels, but their build curves were U-shaped, so under the rules they stay unconfirmed. The composite is weak in both windows, adding about a third of a win per ten picks over random. The exploratory block is the finding of the session: twelve-month realized volatility, which no spec declared, has the cleanest monotone curve in the whole study on all three labels in both windows, reaching four times the base rate for 300% launches in its top decile, and it is correlated with exactly the features that came out backward or confirmed: small size, far from the high, issuing shares. A label that rewards reaching +50% and never charges for reaching −50% will always favor the stocks that move most. That is a property of the label, not a signal, and the next spec has to decide what to do about it. Chunk 4b is done.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| Composite = mean of raw percentile ranks; S6 report regenerated under it | Matt's ruling; one recipe in the repo | Two recipes across two reports |
| Holdout 2020-01 to 2025-06; launch_300 cells count observable rows only | E4; 24-month label ends 2024-08 | Treating null labels as non-events |
| CONFIRMED = same lag passes build (with rho) and holdout (lift and CI) | Section 3 wording | Any-lag pairing across windows |
| Expected winners = 10 × bucket base × composite lift at lag 0 | Spec S7 formula | Within-bucket lift (thin) |
| Realized vol outside FEATURES, no direction, no verdict; correlations on decile ranks | Exploratory per brief | Adding it to the pass framework |

All in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: S7. DONE: chunk 4b.
- OPEN: none in this repo until chat produces a new spec. Inputs to chat: reports/build_window_results.md, holdout_results.md, decile_build_results.md, decile_holdout_results.md.
- OPEN (carried, non-blocking): rename the environment variable to SHARADAR_API_KEY.
- BACKLOG.md was updated this session: S7 DONE, chunk 4b closed.

## Open Questions for Matt

1. Neither spec has a loss label. The realized-volatility block shows the win labels reward dispersion; a paired drawdown or loss label is the natural test, and it is a spec decision.
2. Size confirms on win_100 and launch_300 at every lag with monotone curves in both windows. Whether that is usable depends on the loss side of the same stocks, which nothing here measures.

## SESSION REVIEW [MANDATORY]

5/5. The holdout ran under the brief exactly, the recipe change was applied once and propagated back to S6 with a note, label observability was handled rather than silently miscounted, and the exploratory block was kept outside the criteria while being reported in full. What went wrong: nothing in the deliverable.

## MATT-NOTE

(for Matt)
