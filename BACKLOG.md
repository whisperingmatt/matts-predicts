# BACKLOG.md — matts-predicts

One task per build session. Spec: specs/GROWTH-001-multibagger-pattern-mining.md.
Status words: TODO, IN PROGRESS, DONE, BLOCKED.

## Section 2 Growth — multibagger pattern-mining study

S1 — Scaffold repo, requirements, Sharadar auth test, verify table
names. Wrap.
Status: DONE (verified) 2026-09-17. Scaffold, pinned requirements,
and src/sharadar_check.py are committed. D6 was superseded the same
day: the subscription is on the Sharadar direct API, not Nasdaq Data
Link, so the check was rewritten against api.sharadar.com and run live
from Claude Code on the web with Matt's key: RESULT PASS, all seven
tables (tickers, fundamentals, stocks, daily, insiders, holdings,
sp500) returned rows from 2006–2013 windows with every required column
present. Table and column mapping is in decisions.md. See docs/wrapits/
for the S1 and S1b wraps.

S2 — Ingest (fundamentals ARQ, stocks, daily, tickers, insiders,
holdings, sp500 — direct-API names; NDL names in decisions.md),
universe.parquet, labels, base rate. Stop if no delistings in the
price table. Stop if base rate is outside 0.5%–5%. Wrap.
Status: DONE (verified) 2026-09-17. Bulk host allowed by Matt; all
eight Full History files pulled and converted (manifest in
data/raw/ingest_manifest.json, regenerable). universe.parquet: 588,301
rows, 7,787 tickers, 4,361 delisted; build window 393,429 rows.
labels.parquet: every build-window row labeled. Base rate 0.66%
(launch_300), inside the 0.5%–5% gate. reports/s2_base_rates.md has the
per-year table. holdings starts 2013-06-30, insiders 2008-01-02; both
recorded in decisions.md. See the S2 wraps in docs/wrapits/.
Note for S3: every cloud session starts by running
`python -m src.fetch_bulk` then `python -m src.ingest` (about 8 minutes
for the conversion), then `python -m src.universe` and
`python -m src.labels` (about 15 seconds together).

S3 — Features (spec section 5) at T-0, T-3, T-6, T-12 and regime
tags (section 6). Write the point-in-time unit test from section 10
before computing any feature. H12 is unavailable (no Sharadar short
interest field) — report it as such. Use the sp500 table for H16
constituent history. Wrap.
Status: DONE (verified) 2026-09-17. tests/test_point_in_time.py (4
tests) written first and passing. features.parquet: 2,353,204 rows =
588,301 universe rows x 4 lags; zero rows with fundamentals filed after
their as-of date; lag rows match the lag-0 rows of the earlier month
exactly. regime.parquet: 342 month ends 1998-01..2026-06 with SPY
drawdown, months since trough, VIX. reports/s3_feature_coverage.md has
non-null percent per flag per year. Unavailable: H2, H3, H17, H18
(deferred), H12 (no short interest), H16 (no ETF shares outstanding in
any Sharadar table — funds is OHLCV only). Interpretations in
decisions.md "S3 feature interpretations".
Note for S4: session startup is fetch_bulk, ingest, universe, labels,
regime, features (about eleven minutes). Join features to labels on
(ticker, month_end) and to regime on month_end (or asof_month_end for
the regime at the lagged date; the spec's 7.3 buckets by the decision
month).

S4 — Build-window statistics (section 7) and
reports/build_window_results.md. No recommendations. Wrap.
Status: DONE (verified) 2026-09-17. src/stats.py computes 7.1–7.5 plus
Matt's three additions (sector x entry-year table, base rate per
regime bucket, expected winners per ten picks). Lift among non-null
rows with coverage beside it; Wilson CI; D8 in launch events
everywhere. Verdicts on launch_300: PASS h9_rs6_top_decile (lags 3, 6,
12), h9_rs12_top_decile (3, 6, 12), h10_sponsorship (all lags; data
from 2014 only, no crisis-regime cells). Everything else FAIL or
insufficient (h13_stage2). 69 combinations evaluated, 5 meet D8; best
is rs6 AND rs12 at lag 12, lift 2.87 [2.54, 3.25], 247 events, catches
9.5% of launches. Full tables in reports/build_window_results.md and
reports/s4_*.csv; reading in reports/build_window_reading.md.
Definitions in decisions.md "S4 statistics definitions".
Note for S5: session startup is fetch_bulk, ingest, universe, labels,
regime, features, stats (about twelve minutes). stats.py reads only
build-window rows; S5 needs a holdout mode that reruns 7.1–7.5 on
2020-01 to 2026-06 for the passing signals and the top-20
combinations only, per section 8, and its CONFIRM rule (lift >= 1.5,
lower CI >= 1.0). Labels past 2024-06 are null (24 months not yet
observable), so the holdout effectively ends at 2024-06 decision
dates; record that when S5 opens it.

S5 — Holdout (section 8) and reports/holdout_results.md. Only after
the S4 wrap is committed. Wrap.
Status: DONE (verified) 2026-09-17. Window 2020-01 to 2024-06 (labels
unobservable after 2024-08; decisions.md). src/holdout.py on the
parametrized src/stats.py. Tested per Matt's S5 brief: the three
build PASS flags, the two-horizon pair at every lag, PEG<0.5 AND PE<15
at lag 3, and the four backward signals inverted; launch_200 beside
launch_300 throughout; sector pooled; regime buckets as S4.
CONFIRMS: h9_rs6_top_decile at lags 0 and 3 (2.03 [1.83, 2.25] at
lag 0), h9_rs12_top_decile at lags 0 and 3 (1.63 [1.45, 1.83]), the
pair at lags 0, 3, 6 (2.02 [1.75, 2.34] at lag 0). NOT CONFIRMED:
lags 6 and 12 of the singles (the build window's strongest cells),
h10_sponsorship (1.39 to 1.44, lower bound under 1.5 everywhere),
PEG AND PE (insufficient, 0.96), all four inverted flags (three have
a lift ceiling under 1.5 by construction). Full tables in
reports/holdout_results.md and reports/s5_*.csv; reading in
reports/holdout_reading.md.
This ends chunk four. Chunk five (scoring model, entry, exit) happens
in chat with reports/build_window_results.md and
reports/holdout_results.md as input. No further build session is
scheduled in this repo until chat produces a new spec.

## Chunk 4b — GROWTH-002 decile retest (specs/GROWTH-002-decile-retest.md)

S6 — 12-month labels (E1), two new features (E3), decile ranks within
month and lag (E2), build-window single-feature tables in declared
directions, composite (section 4). reports/decile_build_results.md.
Wrap, PR. Do not open the holdout.
Status: DONE (verified) 2026-09-17. labels12.parquet (win_50 base
11.70% in the build window, inside the 3%-25% gate). Six raw values the
spec expected in features.parquet were appended by extending
features.py; every pre-existing column verified unchanged, and the 13F
share sum made exact so the file is now reproducible run to run (the
S5 holdout report moved by one row in two sponsorship cells as a
result; no verdict changed). deciles.parquet holds ranks for every
month. Build-window result: NO feature passes on win_50 in its
declared direction (best extreme-cell lift 1.48, inst_pct_delta_qoq at
lag 0); three declared directions run backward with near-perfect
monotone curves (pct_from_52w_high, share_count_change_8q,
shareholder_yield); momentum's decile curve is not monotone. Composite
built from the top 3 by extreme-decile lift, UNCONFIRMED, decile 10 =
2.4% of rows, win_50 lift 1.12. Definitions in decisions.md "Chunk
4b". Reading in reports/decile_build_reading.md.

S7 — Holdout single-feature and composite on 2020-01 to 2025-06.
reports/decile_holdout_results.md with a plain-prose reading. Wrap,
PR. Ends chunk 4b.
Status: DONE (verified) 2026-09-17. src/decile_holdout.py on the
parametrized src/decile.py. Holdout 164,889 rows per lag, win_50
16.98%, win_100 5.84%; launch_300 observable through 2024-08 only and
counted on observable rows. No feature passes the full section 3
criterion on win_50, as expected; CONFIRMED on win_100: marketcap
(all lags), peg and pegy (lags 0, 3); on launch_300: marketcap (all
lags). Composite (Matt's S7 recipe: mean of raw percentile ranks;
unconfirmed top-3 membership): holdout decile 10 = 6.1% of rows,
win_50 lift 1.16 [1.11, 1.21], win_100 1.41. Exploratory realized
volatility deciles reported outside the pass criteria with their
correlation to marketcap (-0.47 to -0.51), pct_from_52w_high (+0.48
to +0.54), share_count_change_8q (+0.32 to +0.41). The S6 build
report was regenerated under the S7 composite recipe. Rulings in
decisions.md "S7 holdout rulings".
Chunk 4b ends here. No further build session in this repo until chat
produces a new spec; both decile reports plus the two GROWTH-001
reports are the inputs.

## Chunk 4c — GROWTH-003 winner anatomy (specs/GROWTH-003-winner-anatomy.md)

S8 — Section 2 fields on the existing grid (events table ingested),
8-K coverage per code per year, the four anatomy tables (3.1 to 3.4)
for launch_300 and win_100, build and holdout pooled (F2), plus
Matt's section 3.5 (win_100 against loss_50 by decile).
reports/anatomy_tables.md with a plain-prose reading. Wrap, PR.
Status: DONE (verified) 2026-09-17. src/anatomy.py; events bulk table
added to fetch_bulk/ingest (2,531,005 rows, 1993-11 to 2026-09);
data/processed/anatomy_fields.parquet (2,289,378 rows, regenerable).
launch_300: 4,301 winners in 529,158 rows; win_100: 20,367 in 558,318.
Largest gaps for both labels: drawdown from the three-year high,
realized volatility, price level, market cap, loss-making latest
quarter, years listed, SPY drawdown over 30%; 8-K counts flat before
T-0; during the move, unregistered equity sales and >10% share growth
about twice the population rate. Section 3.5: win_100 and loss_50
rates rise together in every feature, ratio 0.30 to 0.82 in all but
two cells (base 0.48). Rulings in decisions.md "Chunk 4c".

S9 — Clustering into winner types (spec section 4): k-means k 2..6
with silhouette, HDBSCAN check, per-cluster fingerprints, timeline per
cluster, population frequency per cluster. reports/winner_types.md.
Ends chunk 4c. Do not start until Matt's brief.
Startup for a fresh container: fetch_bulk, ingest (now includes
events), universe, labels, regime, features, labels12, decile, anatomy
(~14 min).
