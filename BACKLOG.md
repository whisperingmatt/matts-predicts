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
Status: TODO.
