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
Status: TODO.

S4 — Build-window statistics (section 7) and
reports/build_window_results.md. No recommendations. Wrap.
Status: TODO.

S5 — Holdout (section 8) and reports/holdout_results.md. Only after
the S4 wrap is committed. Wrap.
Status: TODO.
