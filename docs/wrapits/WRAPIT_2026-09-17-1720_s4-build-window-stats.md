project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S4: build-window statistics per section 7, reports/build_window_results.md
status: COMPLETE — all of 7.1 to 7.6 plus Matt's three additions computed, reported, and read in prose. Holdout not opened.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1 hour

---

## What Was Built or Changed

src/stats.py implements spec section 7 on the build window only. It joins features (four lags), labels, regime, and universe, filters to 2006-01 to 2019-12 before anything is computed, and never reads holdout rows. It produces the 7.1 base rates by year; single-signal lift for every available flag at every lag on launch_300, launch_200, and launch_500, with lift computed among non-null rows and coverage beside it, Wilson 95% intervals, and D8 on launch events; the same by SPY drawdown bucket and months-since-trough bucket (7.3); 2- and 3-signal combinations within each lag among flags clearing lift 1.5 and 100 events (7.4), ranked by lift then catch; controls identically (7.5); and the three additions from Matt's brief: launch rate by sector and entry year with D8 per cell and the marginals, the base rate inside each regime bucket, and expected launches per ten picks for the top combinations by regime bucket (10 × bucket base rate × combination lift). Verdicts apply the section 7 pass/fail lines and the crash-only test.

The report reports/build_window_results.md holds every table plus a prose reading. The reading lives in reports/build_window_reading.md and is inserted verbatim when the report is regenerated, so the numbers can be rebuilt without retyping the prose. Full long-form results are in reports/s4_single_signal.csv, s4_combinations.csv, s4_expected_winners.csv, s4_sector_year.csv, s4_base_rates.csv. No recommendations anywhere.

## Files Touched [MANDATORY]

- strategies/02-growth/src/stats.py (rewritten from stub)
- strategies/02-growth/reports/build_window_results.md (new; committed)
- strategies/02-growth/reports/build_window_reading.md (new; committed)
- strategies/02-growth/reports/s4_single_signal.csv, s4_combinations.csv, s4_expected_winners.csv, s4_sector_year.csv, s4_base_rates.csv (new; committed)
- decisions.md (one ruling: S4 statistics definitions)
- BACKLOG.md (S4 DONE verified; S5 startup note and the holdout end-date caveat)
- docs/wrapits/WRAPIT_2026-09-17-1720_s4-build-window-stats.md (this file)

## Environment Variables [MANDATORY]

None used. No network access this session; all inputs were the parquet files built in S2 and S3 in this same container.

## Services and Integrations Touched [MANDATORY]

None.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. Join completeness before computing: 1,573,716 build-window feature rows (393,429 × 4 lags); labels present on 1,573,716; regime buckets on 1,573,716; sector on 1,573,472 (244 rows over 61 universe stock-months have no sector in the tickers table and are reported as Unknown).

2. `python -m src.stats`: `build-window rows: 1,573,716 (393,429 per lag)`; verdict table printed (below); `combinations evaluated: 69, meeting D8: 5`; `RESULT: PASS — report written`, exit 0, about 9 seconds. A first run failed formatting a verdict row where pandas had turned a None into NaN; fixed and rerun. The final run embedded the reading.

3. Verdicts, launch_300: PASS h9_rs6_top_decile (lags 3, 6, 12; best lag 12 lift 2.40, CI low 2.18, 401 events, coverage 80.6%), h9_rs12_top_decile (3, 6, 12; lag 12 lift 2.46, CI low 2.23, 413 events), h10_sponsorship (0, 3, 6, 12; lag 6 lift 2.39, CI low 2.03, 139 events, coverage 39.3%). FAIL: h1 (1.37 best), h4 (0.99), h5_peg_lt_1 (1.33), h5_peg_lt_05 (1.64, CI low 1.48), h6 (1.38), h7 (1.47, CI low 1.41, 2,083 events), h8 (0.61), h11 (1.94, CI low 1.69 at lag 0), h14 (1.03), h15 (0.55 best, 0.40 at lag 0), h20 (1.10), h21 (0.61), ctl_pe_lt_15 (1.55, CI low 1.43), ctl_pb_lt_15 (1.19), ctl_divyield_gt_2 (0.47). Insufficient: h13_stage2 (29 to 44 events per lag). No flag is crash-only: both strength flags pass in the drawdown 0-10 bucket at every lag; h10 has zero events in every drawdown bucket beyond 10%.

4. Base rate by regime bucket: drawdown 0-10 0.54% (1,644 launches on 304,121 rows), 10-20 0.43% (168), 20-30 0.48% (137), >30 2.98% (654 on 21,977); months since trough 0-12 0.75%, 13-24 0.37%, >24 0.38%. launch_500 insufficient in four of the seven buckets.

5. Combinations: 69 evaluated across four lags, 5 meet D8, all 2-signal. Best: rs6 AND rs12 at lag 12, lift 2.87 [2.54, 3.25], 247 events, catch 9.5%, non-null share 79.9%; the same pair at lags 6, 3, 0 (2.85, 2.38, 2.16); h5_peg_lt_05 AND ctl_pe_lt_15 at lag 3, 2.13 [1.89, 2.42], 249 events. Every 3-signal combination and every combination containing h10 or h11 has under 100 events.

6. Expected winners per ten picks (top combination): 0.16 in drawdown 0-10, 0.12 in 10-20, 0.14 in 20-30, 0.85 in >30; 0.22 / 0.11 / 0.11 by months since trough.

7. Sector × entry year: 4 of 154 cells readable under D8; sector totals readable for 7 of 12 rows; Healthcare 1.53% (844 launches), Financial Services 81 launches on 60,200 rows and Utilities 0 on 13,387 (both insufficient).

8. Hand check of one lift cell from the CSV against a direct query: not run separately; the CSV cells are the script's own aggregates, and the base rate overall (2,603 / 393,429 = 0.66%) matches the S2 report exactly, as does every yearly count.

State: S4 BUILT and VERIFIED against the S2 base rates; lift cells are single-sourced from stats.py.

## How to Verify This Is Working Right Now

Warning first: a fresh cloud session has no data; steps 2 to 4 take about eleven minutes and the key must be in the environment.

1. New session, branch claude/nice-dijkstra-801d68 (or main once merged): `cd strategies/02-growth`
2. `python -m src.fetch_bulk && python -m src.ingest`
3. `python -m src.universe && python -m src.labels && python -m src.regime && python -m src.features`
4. `python -m src.stats` — expect the verdict table with three PASS rows (h9_rs6_top_decile, h9_rs12_top_decile, h10_sponsorship), `combinations evaluated: 69, meeting D8: 5`, `RESULT: PASS — report written`.
5. `git diff --stat reports/` — the regenerated tables should match the committed ones to the last digit unless Sharadar restated history since 2026-09-17.

## What Breaks and How to Fix It

- Verdicts change after a data refresh: expected in the last digit; a flag flipping PASS to FAIL means a restated history, not a bug. Record the new numbers in a decisions.md entry before trusting either.
- `KeyError` on a flag name: FEATURE_STATUS in features.py changed; stats.py takes its flag list from there, so a renamed flag must be renamed in both.
- The reading section is missing from the report: reports/build_window_reading.md was not found; the script inserts it only when present.
- Expected-winners table empty: no combination met D8; the CSV still lists every combination with its event count.

## Environment Facts Learned [MANDATORY]

- The whole section 7 computation runs in about nine seconds in duckdb on this machine; the report writer is the slow part at a few seconds. This wrap only.
- Nothing permanent. No new constraints on the environment.

## Ephemeral Outputs Not Yet Saved

None. Every table is committed under reports/.

## Plain English Summary for Matt

The study's answer for 2006 to 2019 is narrow. Of nineteen signals we could compute, one idea passed cleanly: stocks that were already in the top tenth of six- and twelve-month performers three to twelve months before the entry date launched at about two and a half times the base rate, and the two horizons together reach 2.9 times on 247 launches. Institutional sponsorship also passed, but on data that only starts in 2014 and has never seen a bear market, so treat it as unconfirmed. Insider buying just missed. Four signals point the wrong way with narrow error bars: stocks near their 52-week high, stocks that were not diluting, positive free-cash-flow trends, and dividend payers all launched at half the base rate or less. The rest did nothing, and the Weinstein stage-2 signal fires too rarely to be judged. The biggest number in the report is not a signal at all: entering after a 30% market drawdown multiplied the base rate by five and a half, more than any signal does. Ten picks by the best combination, in a normal market, would be expected to contain about a sixth of one 300% winner. The holdout is the next session and stays closed until this wrap is merged.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| Lift among non-null rows; coverage beside every lift | Matt's brief; null is insufficient data, not signal absence | Base including nulls |
| Wilson on rate with base fixed | Base rests on far more rows | Ratio CI; normal approximation |
| D8 events = launch events | D8 text | Row counts |
| Combinations within one lag; controls eligible | Same decision date for every flag | Cross-lag combinations |
| Expected winners = 10 × bucket base × overall lift | Matt's formula | Within-bucket lift (mostly insufficient) |
| Sector × year with D8 per cell plus marginals | Matt's table, D8 everywhere | Row-count threshold |
| Reading kept in a separate committed file and embedded | Regenerable numbers, stable prose | Prose inside the script |

All in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: S4 statistics and report.
- OPEN: S5 holdout per section 8, only after this wrap is merged: 7.1 to 7.5 on 2020-01 to 2026-06 for the three passing signals and the top-20 combinations (only five meet D8 in the build window; the CSV lists all 69). CONFIRM rule: lift ≥ 1.5 with lower CI ≥ 1.0. Labels are null after 2024-06 decision dates, so the holdout's observable span is 2020-01 to 2024-06; record that when opening it.
- OPEN: S5 must add a holdout mode to stats.py; today it hard-filters to the build window.
- OPEN: rename the environment variable to SHARADAR_API_KEY (carried).
- BACKLOG.md was updated this session: S4 DONE (verified), S5 notes.

## Open Questions for Matt

1. D8 at 100 launch events makes the sector × year table almost entirely "insufficient" (4 readable cells of 154). The marginals are readable. If you want the cells, D8 would need a row-count reading for descriptive tables, which is a spec change for decisions.md.
2. h10 sponsorship passes only on 2014 to 2019 data with no bear-market cells. Section 7's crash-only test cannot be applied to it. Whether it counts as "passing" for the holdout list is your call; it is on the list as the criterion is written.
3. The two strength horizons pass separately and as a pair. For the holdout, section 8 says "passing signals and top-20 combinations"; both readings are included as written.

## SESSION REVIEW [MANDATORY]

5/5. Every part of section 7 and all three additions were computed from one script, every cell is D8-checked, the report reads the tables without recommending, and the base rates reconcile exactly with S2. What went wrong: one formatting crash on the first run, fixed in one line.

## MATT-NOTE

(for Matt)
