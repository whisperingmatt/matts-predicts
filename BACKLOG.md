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
Status: IN PROGRESS, BLOCKED 2026-09-17 on network policy. Done and
committed: persistence ruling (data/ does not persist between cloud
sessions), src/fetch_bulk.py (bulk Full History setup script, verified
up to the redirect), src/ingest.py (zip to parquet converter, verified
on a 74,195-row tickers fixture), config.BULK_TABLES adds funds. Not
done: the bulk downloads themselves, universe.parquet, labels, base
rates, delisting check, holdings 2013 note. Blocker: api.sharadar.com
redirects years=full to static-sharadar.nyc3.digitaloceanspaces.com
and the web environment's egress proxy refuses that host (403).
Options for Matt, in the S2 wrap: allow that host in the environment's
network policy; or run fetch_bulk.py on his machine; or approve a
paged-API pull (~3,000 requests, 2–3 hours). Next S2 session resumes
at the download step once one is chosen.

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
