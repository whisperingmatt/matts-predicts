project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S5: holdout per section 8 on 2020-01 to 2024-06, reports/holdout_results.md; end of chunk four
status: COMPLETE — holdout computed, reported, and read; relative strength confirms at short lags, nothing else does. Chunk four ends.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1 hour

---

## What Was Built or Changed

src/stats.py was parametrized so the same functions run on either window: load() takes start and end dates and adds the four inverted flags (NOT of the build window's backward signals, null preserved), single_signal() takes a flag list, and the combination evaluator was split out as evaluate_combos() so a fixed list of combinations can be scored. Its output order was also made deterministic; duckdb's GROUP BY order is not stable, which had let the committed S4 CSVs come out in a different row order on every run. The build-window report regenerates identically except that the passing-lag lists are now sorted ascending.

src/holdout.py implements section 8 under Matt's S5 brief. It loads the build window and the holdout with the same code, scores the tested flags and combinations in both, writes reports/holdout_results.md with build cells beside holdout cells, embeds reports/holdout_reading.md, and writes reports/s5_single_signal.csv, s5_combinations.csv, s5_base_rates.csv, s5_sector.csv. Tested: h9_rs6_top_decile, h9_rs12_top_decile, h10_sponsorship (carried with its calm-only caveat), the two-horizon pair at every lag, PEG < 0.5 AND PE < 15 at lag 3 (the fifth build combination that met D8, section 8's top-20 reduced to what existed), and inv_h15_near_high, inv_h21_no_dilution, inv_h8_fcf_divergence, inv_ctl_divyield_gt_2. launch_200 beside launch_300 in every table; sector pooled across years; regime buckets as S4; CONFIRM = lift ≥ 1.5 with lower CI ≥ 1.0 on a D8 cell.

The window ends 2024-06 rather than D4's 2026-06 because 24-month returns are not observable after 2024-08 decision dates with prices to 2026-09-16. Recorded in decisions.md with the rest of the S5 rulings.

## Files Touched [MANDATORY]

- strategies/02-growth/src/stats.py (parametrized; deterministic ordering; evaluate_combos split out)
- strategies/02-growth/src/holdout.py (new)
- strategies/02-growth/reports/holdout_results.md, holdout_reading.md (new; committed)
- strategies/02-growth/reports/s5_single_signal.csv, s5_combinations.csv, s5_base_rates.csv, s5_sector.csv (new; committed)
- strategies/02-growth/reports/build_window_results.md, s4_single_signal.csv, s4_combinations.csv, s4_expected_winners.csv (regenerated: same numbers, stable row order, combination CSV gains launch_200 lift columns)
- decisions.md (one ruling: S5 holdout rulings)
- BACKLOG.md (S5 DONE; chunk four ends)
- docs/wrapits/WRAPIT_2026-09-17-1740_s5-holdout-chunk-four-end.md (this file)

## Environment Variables [MANDATORY]

None used. No network access this session.

## Services and Integrations Touched [MANDATORY]

None.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. Holdout sizing before code: last month_end with an observable 24-month return 2024-08-31; 2020-01 to 2024-06 has 135,729 universe rows per lag, 1,698 launch_300, 3,757 launch_200; buckets present drawdown 0-10 / 10-20 / 20-30 and months-since-trough 0-12 / 13-24, absent >30 and >24.

2. Regression on the refactor: `python -m src.stats` regenerated the build report; s4_single_signal.csv is identical to the committed file after sorting both (`cmp` on sorted copies: identical); build_window_results.md differs only in the order of the passing-lag lists (6,12,3 became 3,6,12). Run twice after the ordering fix: identical output both times.

3. `python -m src.holdout`: `rows 2020-01-31..2024-06-30: 542,916 (135,729 per lag)`; `RESULT: PASS — holdout report written`, exit 0, 4 seconds. Run twice: s5_single_signal.csv md5 identical (f537…4b14) both times.

4. Verdicts, launch_300: h9_rs6_top_decile CONFIRMS at lags 0 (2.03 [1.83, 2.25], 343 events) and 3 (1.78 [1.57, 2.01]); lags 6 and 12 not confirmed (1.49, 1.16). h9_rs12_top_decile CONFIRMS at lags 0 (1.63 [1.45, 1.83]) and 3 (1.55 [1.36, 1.77]); lags 6 and 12 not (1.29, 1.24). h10_sponsorship NOT CONFIRMED at every lag (1.39 to 1.44, lower bounds 1.18 to 1.22, 110 to 135 events). inv_h15_near_high 1.23 to 1.29, inv_h21_no_dilution 1.40 to 1.44, inv_h8_fcf_divergence 1.03 to 1.05, inv_ctl_divyield_gt_2 1.14 to 1.15: none confirmed. launch_200: rs6 confirms at 0, 3, 6; rs12 at 0, 3; nothing else.

5. Combinations: rs6 AND rs12 CONFIRMS at lags 0 (2.02 [1.75, 2.34], 177 events, catch 10.4%), 3 (1.88 [1.59, 2.21]), 6 (1.57 [1.30, 1.89]); lag 12 insufficient (81 events, 1.27); the same three lags confirm at 200%. PEG < 0.5 AND PE < 15 at lag 3: 79 events, insufficient, 0.96; 1.07 at 200%.

6. Regime: rs6 confirms inside the calm bucket at lags 0, 3, 6 (2.19, 2.02, 1.77) and rs12 at the same lags; the 10-20 bucket holds 28 to 81 events for the strength flags and 32 to 37 for sponsorship, unreadable. inv_h21 reaches 1.60 to 1.64 CONFIRM cells in the 13-24 months-since-trough bucket.

7. Base rates: overall 1.25%; by year 2020 1.74%, 2021 insufficient (93), 2022 0.99%, 2023 1.56%, 2024 H1 2.40%; drawdown 0-10 1.21%, 10-20 1.35%, 20-30 insufficient (34); mst 0-12 1.14%, 13-24 2.16%. Sector pooled: Energy 2.77%, Industrials 1.71%, Basic Materials 1.63%, Technology 1.61%, Healthcare 1.32%, Consumer Cyclical 0.93%; Financial Services, Communication Services, Consumer Defensive, Utilities, Real Estate insufficient.

State: S5 BUILT and VERIFIED (stable across reruns; build column reconciles with S4 to the last digit).

## How to Verify This Is Working Right Now

Warning first: a fresh cloud session has no data; steps 2 to 3 take about eleven minutes and the key must be in the environment.

1. New session, branch claude/nice-dijkstra-801d68 (or main once merged): `cd strategies/02-growth`
2. `python -m src.fetch_bulk && python -m src.ingest`
3. `python -m src.universe && python -m src.labels && python -m src.regime && python -m src.features`
4. `python -m src.stats && python -m src.holdout` — expect `RESULT: PASS` from both and `confirming (300): ['h9_rs12_top_decile', 'h9_rs6_top_decile']`.
5. `git diff --stat reports/` — no change unless Sharadar restated history after 2026-09-17.

## What Breaks and How to Fix It

- The holdout window must move: H_START and H_END are constants at the top of holdout.py; the last observable month is printed by the sizing query in this wrap's gate test 1 and should be rechecked against the new price data end.
- A tested flag disappears: TESTED in holdout.py names columns of features.parquet plus the INVERTED map in stats.py; a rename in features.py must be carried to both.
- Row order changes in a CSV after a duckdb upgrade: the sort in single_signal() is on FLAGS order; if a new flag is added outside FLAGS or INVERTED it sorts to the end with a NaN key.

## Environment Facts Learned [MANDATORY]

- duckdb's GROUP BY output order is not stable between runs; anything written to a committed file must be sorted explicitly. Worth a line in CLAUDE.md if another script writes committed tables.
- An inverted majority flag has a lift ceiling of one over its true share (61% true caps at 1.64), so three of the four inverted signals could not reach 1.5 by construction. This wrap and the reading.

## Ephemeral Outputs Not Yet Saved

None.

## Plain English Summary for Matt

The holdout is a different market from the build years: launches were twice as common, the deep-drawdown regime never occurred, and the sector leaders changed, with Energy first where it had been near last. Against that, one thing held. Stocks in the top tenth of six- and twelve-month performance on the decision date launched at 1.6 to 2 times the base, and the two together at 2 times, catching a tenth of all launches. What did not hold is the build window's strongest form of the same idea: strength a year before entry, which was the best cell in 2006 to 2019, did nothing in 2020 to 2024. Sponsorship fell to about 1.4 and is not confirmed. The cheap-PEG-and-PE combination vanished. Turning the four backward signals around confirmed none; three of them could not have cleared the bar mathematically, and the diluter flag came closest at 1.4. Chunk four is finished. What to build from this is the chat conversation the spec reserves for chunk five, with both reports as its inputs.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| Holdout window 2020-01 to 2024-06 | Labels unobservable after 2024-08 | D4's 2026-06 with null labels |
| Test list per Matt's brief; PEG AND PE kept as section 8's top-20 | Operator ruling plus the spec's letter | Testing all 69 build combinations |
| Inverted flags labeled inverted, null preserved | Test of the reverse description, not a new hypothesis | Adding them to FEATURE_STATUS |
| Build cells recomputed in holdout.py with the same code | Like-for-like comparison | Reading S4's CSV |
| Deterministic CSV ordering in FLAGS order | Committed tables must be reproducible | Alphabetical (changes combination names) |

All in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: S5 holdout and report. DONE: chunk four.
- OPEN: none in this repo until chat produces a chunk-five spec. If a chunk-five spec arrives, it starts as a new spec file under specs/ with its own decisions and backlog entries.
- OPEN (carried, non-blocking): rename the environment variable to SHARADAR_API_KEY.
- BACKLOG.md was updated this session: S5 DONE, chunk four closed.

## Open Questions for Matt

1. The strength signal's confirmation is at lags 0 and 3 only; its build-window strength was at lag 12. Chunk five should decide which form, if any, it builds on. Both are in the reports.
2. D4 names the holdout end as 2026-06. When prices reach 2028-06 the last two years of decision dates become observable; the holdout can then be rerun on the full window by changing two constants.

## SESSION REVIEW [MANDATORY]

5/5. The holdout ran under the exact brief, every cell is D8-checked, results are stable across reruns, and the refactor left the S4 numbers untouched. What went wrong: the regression check caught unstable row order in the S4 CSVs that had been committed unnoticed in S4; fixed here, numbers unchanged.

## MATT-NOTE

(for Matt)
