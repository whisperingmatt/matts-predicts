project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S8 (GROWTH-003): winner anatomy tables, build and holdout pooled; events (8-K) table ingested; Matt's section 3.5 loss_50 addition
status: COMPLETE — spec placed, events table ingested, every section-2 field computed, 8-K coverage per code per year, tables 3.1 to 3.5 written and read; no recommendations made; Session 9 not started.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~2.5 hours

---

## What Was Built or Changed

specs/GROWTH-003-winner-anatomy.md placed from Matt's upload. The Sharadar events table (8-K item codes) was added to config.BULK_TABLES and ingest.DATE_COLUMN, fetched (11.5 MB zip) and ingested (2,531,005 rows, 1993-11 to 2026-09). The code mapping was read from Sharadar's descriptions table: item X.0Y is stored as the two-digit code "XY", pipe-joined per filing date; the modern numbering starts 2004-08-23.

src/anatomy.py is new. It builds every section-2 field on a dense monthly grid (7,787 tickers by 294 months, 2,289,378 rows, written to data/processed/anatomy_fields.parquet): tickers age and categories; three-year drawdown and months since the three-year low; realized volatility; 20-day dollar volume; price bucket; market cap; ARQ profitability, revenue growth, margins, cash and net debt to market cap, capex and R&D to revenue, share count change 4q and 8q, revenue-growth streak and quarters since last loss; the ten 8-K codes in the trailing 12 months and in the 12 months after (forward-looking, suffix _f12) with the CEO-change, financing and deal proxies; insider net buys and officer buys trailing 12 months; 13F level and 4-quarter delta; regime. It then builds the two populations (launch_300 to 2024-06, win_100 to 2025-06, pooled per F2), Matt's 3.5 table (win_100 rate, loss_50 rate, ratio, median 12-month return per decile of the 22 GROWTH-002 features plus realized volatility), the 3.1 profile (numeric medians at T-0, T-6, T-12 with coverage, count-field means, decile medians and means, categorical share ratios), the 3.2 timeline (T-24 to T+24 in 3-month steps, population overlay aligned on calendar month), the 3.3 during-move table, and the 3.4 sector by drawdown bucket table. reports/anatomy_tables.md embeds reports/anatomy_reading.md; nine s8_*.csv files carry every table unrounded.

Determinism: the first run with four duckdb threads moved the new mean columns by floating-point noise between runs (the report text was unchanged). The module now runs single-threaded; two consecutive runs produced identical checksums for all ten outputs. Runtime 3.5 minutes.

## Files Touched [MANDATORY]

- specs/GROWTH-003-winner-anatomy.md (new, from Matt's upload)
- strategies/02-growth/src/anatomy.py (new)
- strategies/02-growth/src/config.py (events added to BULK_TABLES)
- strategies/02-growth/src/ingest.py (events added to DATE_COLUMN)
- strategies/02-growth/reports/anatomy_tables.md (new)
- strategies/02-growth/reports/anatomy_reading.md (new)
- strategies/02-growth/reports/s8_events_coverage.csv, s8_loss50_base.csv, s8_loss50_deciles.csv, s8_profile_numeric.csv, s8_profile_deciles.csv, s8_profile_categorical.csv, s8_timeline.csv, s8_during_move.csv, s8_sector_regime.csv (new)
- decisions.md (new section "Chunk 4c")
- BACKLOG.md (Chunk 4c: S8 DONE, S9 pending)
- docs/wrapits/WRAPIT_2026-09-17-2010_s8-winner-anatomy.md (this file)
- data/raw/events.csv.zip, events.parquet, ingest_manifest.json; data/processed/anatomy_fields.parquet (gitignored, regenerable)

## Environment Variables [MANDATORY]

NASDAQ_DATA_LINK_API_KEY (fallback name) read by fetch_bulk for the events download. SHARADAR_API_KEY is still not set in the environment. Nothing added or changed.

## Services and Integrations Touched [MANDATORY]

api.sharadar.com: one status call and one bulk download (events, redirect to the DigitalOcean host), one descriptions query (table = eventcodes, 37 rows). sharadar.com/docs/events read through Firecrawl. GitHub for the PR.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None (parquet files only; data/ is gitignored).

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

- `python -m src.fetch_bulk events` → OK events: downloaded 11513210 bytes; RESULT: PASS.
- `python -m src.ingest events` → 2,531,005 rows, 3 columns, date 1993-11-08..2026-09-16; RESULT: PASS.
- `python -m src.anatomy` → launch_300: 4,301 winners in 529,158 rows; win_100: 20,367 winners in 558,318 rows; RESULT: PASS. Runtime 3m31s single-threaded.
- Label self-check from the timeline table: win_100 winners' median price return at T+12 is +136.4% (must be at least +100%); launch_300 winners' at T+24 is +399.2% (must be at least +300%). Both hold.
- Reproducibility: md5 of all nine s8_*.csv files and anatomy_tables.md identical across two consecutive runs (10 of 10 OK) after the switch to one thread; with four threads two CSVs differed by floating-point noise.
- `python -m pytest -q tests` → 4 passed.
- 3.5 cell count: 222 decile cells at lag 0, 221 sufficient (realized_vol_12m decile 1 has 94 wins).

## How to Verify This Is Working Right Now

1. In a fresh container: `python -m src.fetch_bulk && python -m src.ingest && python -m src.universe && python -m src.labels && python -m src.regime && python -m src.features && python -m src.labels12 && python -m src.decile && python -m src.anatomy` (about 14 minutes).
2. Confirm the last line reads RESULT: PASS and reports/anatomy_tables.md line count is 1195.
3. Confirm the 3.2 table shows +136.4% at k=+12 for win_100 and +399.2% at k=+24 for launch_300.

## What Breaks and How to Fix It

If fetch_bulk fails on events with a 403 on CONNECT, the DigitalOcean redirect host has been removed from the environment's network policy; re-allow static-sharadar.nyc3.digitaloceanspaces.com. If anatomy.py raises on a missing column in features.parquet, S6's feature extension has not been run (deciles.parquet must exist too). If checksums differ between runs, someone raised the thread count; the module sets threads = 1 for that reason.

## Environment Facts Learned [MANDATORY — constraints/quirks found, or "None"; anything permanent also goes to CLAUDE.md]

- Sharadar events table: columns ticker, date (8-K filing date), eventcodes (pipe-joined two-digit codes; item X.0Y = "XY"; codes 34 = 13G, 35 = 13D, 91 = exhibits also present). The code list is the descriptions table with table = eventcodes (the descriptions endpoint rejects limit= and needs format=csv; the full CSV does not parse as a single table, so filter with table=eventcodes). Modern item numbering starts 2004-08-23. Added to CLAUDE.md.
- duckdb avg() over doubles is order-dependent under multiple threads; single-thread execution makes it reproducible. Same class as the S6 13F sum fix.

## Ephemeral Outputs Not Yet Saved

None. Every table is in reports/; data/ is regenerable.

## Plain English Summary for Matt [MANDATORY]

The winners look the same from every angle the spec asked for. Before the move they are smaller, younger, more volatile, further below their three-year high, more often loss-making, and more often trading under $10 than the population at the same month; they hold more cash and less debt and have issued more stock. The 8-K record before the move is flat: winners and population file the same items at the same rate, and the 5.02 "CEO change" proxy fires for over 80% of all companies a year, so it says nothing. During the move about a quarter of winners raise equity (unregistered sales at twice the population rate, share count growth over 10% at two and a half times); acquisitions and leadership changes run at the population rate. Both winner groups fell into T-0 while the population rose, and their revenue growth bottoms at T-0 and then triples over the following two years. The sector picture depends on the market: Healthcare leads in calm markets, Consumer Cyclical, Energy and Basic Materials lead after a 30% SPY drawdown, where win rates are three times the calm rate. Your loss_50 addition gives the sharpest single finding of the session: across all 23 features, the deciles that win most are the deciles that lose most, and the win-to-loss ratio stays between 0.30 and 0.82 almost everywhere (base 0.48). The one cell above 1.0 is an artifact of 15 crisis months. No recommendations are made; that is Session 9's clustering and then chat.

## Decisions Made [MANDATORY — Decision | Reason | Alternatives rejected, or "None"; survivors must also land in decisions.md]

- Spec at root specs/ | CLAUDE.md structure | the spec header's strategies/02-growth/specs/.
- F2 pooling recorded; launch_300 window ends 2024-06 as the spec says | descriptive, holdout gate does not apply | ending at 2024-08 (last observable month).
- loss_50 = fwd_12m_return <= -0.50; ratio insufficient when either count is under 100; report shows lag 0, CSV all lags | Matt's brief plus F4 | showing all four lags in the report (four times the length).
- Event code mapping and windows (trailing m-11..m, forward m+1..m+12, null before 2005-08 and after 2025-08) | data start of the modern numbering | counting the pre-2004 legacy codes.
- Insider counts are Form 4 rows, not distinct owners | spec says count buys minus count sells | H11's distinct-owner rule.
- 13F level reused from features.parquet, delta by self join at month minus 12 | no recomputation of validated logic | recomputing the 45-day-lag rule.
- ARQ staleness 16 months | the universe's own EPS window | no staleness rule (features.py) or 12 months.
- Streaks capped at 12 and stopped by history start | simple, documented | null when history is short.
- Timeline population overlay = median over winners of the population median at each winner's month + k | F3 alignment on calendar month | pooled population median (weights months by population size).
- scalemarketcap, drawdown bucket and months-since-trough bucket added to the categorical table with the not-point-in-time caveat on scalemarketcap | section-2 categoricals | omitting them.
- Count fields reported as means beside medians | medians of small counts tie | medians only.
- Single-threaded duckdb in anatomy.py | reproducible means | exact-decimal casts on every averaged column.
All recorded in decisions.md "Chunk 4c".

## Open Items for Next Session [MANDATORY — DONE: <item> closes existing items; confirm BACKLOG.md was updated this session]

- DONE: S8 per GROWTH-003 sections 2, 3 and 3.5.
- S9 clustering (spec section 4) waits for Matt's brief. Not started.
- Carried: rename the environment variable to SHARADAR_API_KEY (non-blocking).
- BACKLOG.md updated this session (Chunk 4c added: S8 DONE, S9 pending; startup sequence now includes anatomy).

## Open Questions for Matt

- Does Session 9 cluster on the numeric section-2 fields as computed here (37 numeric fields plus 23 percentile ranks), and should the T-6 and T-12 values enter as separate features or only T-0?
- The 5.02 proxy is uninformative as built; the events table has no finer CEO-change code. Keep it in the S9 feature set or drop it before standardizing?
- scalemarketcap is not point in time. Exclude it from S9 (the marketcap decile covers size at T-0)?

## SESSION REVIEW [MANDATORY — 1-5 rating + what went wrong]

4. The spec was missing from the repo at the start and had to be requested; the descriptions endpoint needed two attempts to find the eventcodes filter, and one error message printed the API key to the tool log (not to the repo; later calls redact it). The first anatomy run used four threads and was not reproducible; caught by the checksum test before commit. The reading's first draft overstated the sufficient cell count (229 versus 221); caught by recount.

## MATT-NOTE [Optional session rating]

