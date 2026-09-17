# BACKLOG.md — matts-predicts

One task per build session. Spec: specs/GROWTH-001-multibagger-pattern-mining.md.
Status words: TODO, IN PROGRESS, DONE, BLOCKED.

## Section 2 Growth — multibagger pattern-mining study

S1 — Scaffold repo, requirements, Sharadar auth test, verify table
names. Wrap.
Status: DONE (built) 2026-09-17, with one open gate. Scaffold, pinned
requirements, and src/sharadar_check.py are committed. Table names
verified against Sharadar and Nasdaq docs. The live auth test could
NOT run from Claude Code on the web: no NASDAQ_DATA_LINK_API_KEY in the
environment and the egress proxy blocks data.nasdaq.com. See
docs/wrapits/ for the S1 wrap.
Open gate for Matt: run the auth test on a machine with the key and
network access (steps in the S1 wrap) and paste the output into the
next session.

S2 — Ingest (SF1 ARQ, SEP, DAILY, TICKERS, SF2, SF3, SP500),
universe.parquet, labels, base rate. Stop if no delistings in the
price table. Stop if base rate is outside 0.5%–5%. Wrap.
Status: TODO. Blocked on the S1 auth test passing.

S3 — Features (spec section 5) at T-0, T-3, T-6, T-12 and regime
tags (section 6). Write the point-in-time unit test from section 10
before computing any feature. H12 is unavailable (no Sharadar short
interest field) — report it as such. Use SHARADAR/SP500 for H16
constituent history. Wrap.
Status: TODO.

S4 — Build-window statistics (section 7) and
reports/build_window_results.md. No recommendations. Wrap.
Status: TODO.

S5 — Holdout (section 8) and reports/holdout_results.md. Only after
the S4 wrap is committed. Wrap.
Status: TODO.
