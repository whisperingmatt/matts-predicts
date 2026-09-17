project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S2 part 2: bulk ingest to parquet, universe, launch labels, base rates
status: COMPLETE — S2 delivered and verified; base rate 0.66% inside the gate; delisted tickers present. S3 not started.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1.5 hours across both S2 parts

---

## What Was Built or Changed

Matt allowed the bulk host in the environment's network policy, and the download that failed in S2 part 1 went through. src/fetch_bulk.py pulled all eight Full History zips (3.4 GB) and src/ingest.py converted them to parquet in eight minutes. The tickers bulk file turned out to carry legacy table codes (SEP, SF1, SF2, SF3B, SFP) in its table column where the paged API says stocks, fundamentals, and so on; universe.py accepts both.

src/universe.py implements spec section 3. Membership comes from the tickers table: price-table rows with category Domestic Common Stock or its Primary Class variant, exchange NYSE, NASDAQ, or NYSEMKT, industry not Shell Companies (SPACs) and not starting REIT. Secondary share classes are excluded so one issuer is one launch. Each ticker's last trade on or before each month end is the decision row; D3 floors use closeunadj for the $5 price and the 20-day mean of close times volume for dollar volume. The EPS filter counts distinct fiscal quarters with non-null ARQ eps filed on or before the decision date with quarter ends in the trailing 16 months, requiring four. The script stops if the price table has no delistings.

src/labels.py implements section 4. For each universe row the t+24m price is the last trade on or before the month end 24 calendar months later, via an ASOF join; no trade in that month means delist is terminal and the last closeadj stands in. Flags launch_200, launch_300, launch_500. It writes labels.parquet and reports/s2_base_rates.md for the build window only and enforces the section 7 validity gate.

Holdings history begins 2013-06-30 and insiders 2008-01-02; both limits and their effect on H10 and H11 are recorded in decisions.md.

## Files Touched [MANDATORY]

- strategies/02-growth/src/universe.py (rewritten from stub)
- strategies/02-growth/src/labels.py (rewritten from stub)
- strategies/02-growth/reports/s2_base_rates.md (new; committed)
- decisions.md (rulings: bulk unblocked; universe rules mapping; label mechanics; history-start limits; S2 numbers)
- BACKLOG.md (S2 DONE verified; S3 note on session startup)
- docs/wrapits/WRAPIT_2026-09-17-1510_s2-ingest-universe-labels-base-rates.md (this file)
- data/raw/*.csv.zip, data/raw/*.parquet, data/raw/ingest_manifest.json, data/processed/universe.parquet, data/processed/labels.parquet (gitignored; regenerable; gone when this container is reclaimed)

## Environment Variables [MANDATORY]

NASDAQ_DATA_LINK_API_KEY — present; used by fetch_bulk.py via the fallback name. Never printed.
SHARADAR_API_KEY — still not present in this container (variables are fixed at session start).

## Services and Integrations Touched [MANDATORY]

api.sharadar.com — eight status calls and eight years=full downloads (read-only).
static-sharadar.nyc3.digitaloceanspaces.com — eight bulk file downloads, 3.4 GB total, now allowed by policy.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None in any database. New local parquet files under data/ as listed above; not committed.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. `python -m src.fetch_bulk`: eight OK lines, `RESULT: PASS`, exit 0. Sizes: fundamentals 629.9 MB, stocks 945.1 MB, daily 729.4 MB, tickers 4.71 MB, insiders 235.3 MB, holdings 583.4 MB, sp500 278.7 KB, funds 290.7 MB.

2. `python -m src.ingest` (all eight): `RESULT: PASS`, exit 0, 8m09s for the six large tables. Rows and date ranges: fundamentals 3,216,835 (filing dates 1990-06-06..2026-09-16); stocks 45,342,215 (1997-12-31..2026-09-16); daily 39,807,689 (1998-12-01..); insiders 11,552,908 (2008-01-02..); holdings 81,196,386 (2013-06-30..2026-06-30); funds 15,627,051 (1997-12-31..); tickers 74,195; sp500 59,674 (actions from 1957, quarterly snapshots from 1998-03-31).

3. `python -m src.universe`: `price table: 20,973 tickers, 14,642 delisted`; ticker funnel priced 20,973 → domestic common 15,715 → on exchanges 15,701 → SPACs removed 894, REITs removed 475 → eligible 14,332 (10,482 delisted); month-end funnel candidate rows 1,090,156 → with 20-day history 1,086,076 → pass price 801,819 → pass both floors 619,316 → after EPS filter 588,301 rows, 7,787 tickers, 4,361 delisted. Build-window rows per year 24,501 (2009) to 31,216 (2007). `RESULT: PASS — universe written; delisted tickers present`, exit 0, 8 seconds.

4. `python -m src.labels`: 588,301 rows, 534,024 with a return, 54,277 not yet observable (holdout tail), 0 build-window rows without a return. Build window overall: 393,429 rows, 2,603 launch_300 (0.66%), 7,408 launch_200 (1.88%), 629 launch_500 (0.16%), 37,460 rows delisted before t+24. Per-year rate_300 from 0.02% (2007) to 2.29% (2009); full table in reports/s2_base_rates.md. `RESULT: PASS — base rate inside [0.5%, 5%], every build-window row labeled`, exit 0.

5. Independent spot check with pandas straight from stocks.parquet, three rows: AAPL 2006-01-31 (survivor) manual 0.7927 vs labels 0.7927369, match; ABI1 2008-06-30 (delisted, last trade 2008-11-21) manual −0.1684 delisted True vs labels −0.1683861 True, match; ANVGQ 2009-03-31 (launch_500) manual 5.0650 vs labels 5.0649573, launch_300 True, match. All three matched to 1e-9.

6. ARQ EPS coverage: non-null eps on 96–98% of ARQ rows per filing year 2003–2019; filing lag median 41 days, p90 78, p99 154 days. Supports the 16-month window.

7. `pytest -q`: 1 skipped (S3 placeholder). Expected.

State: S2 BUILT and VERIFIED.

## How to Verify This Is Working Right Now

Warning first: a fresh cloud session has no data; steps 2 and 3 take about ten minutes and 8 GB of disk. The key must be in the environment.

1. New session on this repo, branch claude/nice-dijkstra-801d68 (or main once merged): `cd strategies/02-growth`
2. `python -m src.fetch_bulk` — expect eight OK lines, `RESULT: PASS — 3419 MB present`.
3. `python -m src.ingest` — expect eight OK lines with the row counts in gate test 2, `RESULT: PASS`.
4. `python -m src.universe` — expect `universe: 588,301 rows, 7,787 tickers, 4,361 of them delisted` and `RESULT: PASS`.
5. `python -m src.labels` — expect the table in reports/s2_base_rates.md reproduced on screen, overall 0.66%, `RESULT: PASS`.
Counts will drift slightly as Sharadar restates history; the gate outcomes should not.

## What Breaks and How to Fix It

- `STOP: the price table contains no delisted tickers`: the stocks parquet is wrong or truncated. Re-run fetch_bulk and ingest for stocks.
- `RESULT: FAIL` from labels with a base rate outside the gate: do not tune anything. Report the number and stop; the universe or labeling is wrong per spec section 7.
- duckdb out-of-memory on universe: memory_limit is 10 GB with a temp directory under data/processed; on a smaller machine lower the limit, duckdb spills to disk.
- Ticker funnel drops to zero at domestic_common: the tickers table column changed name or values again; inspect `SELECT "table", category, count(*)` and update the constants at the top of universe.py with a decisions.md entry.

## Environment Facts Learned [MANDATORY]

- The bulk tickers file's table column uses legacy codes (SEP, SF1, SF2, SF3B, SFP); the paged API returns modern names. Recorded in decisions.md; code accepts both. Add to CLAUDE.md if it bites again.
- Conversion of the six large tables takes about 8 minutes and needs about 8 GB free during the largest CSV extraction (stocks CSV about 4.5 GB). This wrap and BACKLOG.
- holdings begins 2013-06-30, insiders 2008-01-02. decisions.md.
- fundamentals filing dates start 1990-06-06 for a handful of rows although Sharadar documents history from 1998. Harmless; noted here only.
- duckdb ASOF JOIN and QUALIFY work as used on duckdb 1.5.5.

## Ephemeral Outputs Not Yet Saved

All parquet under data/ is ephemeral by the persistence ruling; everything needed to regenerate it is committed, and every reported number is in this wrap, decisions.md, or reports/s2_base_rates.md.

## Plain English Summary for Matt

Your network change worked. All eight Sharadar tables came down and were converted in about ten minutes. The monthly universe has about 30,000 stock-months a year in the build window, roughly 2,500 to 3,200 stocks each year, and more than half of the stocks that ever qualified are delisted today, so survivorship bias is not the problem here. A 300 percent two-year move happened in 0.66 percent of stock-months, which sits inside the sanity range the spec set before we looked. The rate swings hard with the starting year: buying at the March 2009 bottom gave 2.3 percent, buying in 2007 gave almost nothing. That is the regime effect S3 will tag. Two things were interpretations, not spec text, and are written down: what counts as a SPAC or REIT in Sharadar's fields, and the 16-month window for the four-quarters-of-EPS rule, because the literal 12 months is impossible to meet before the latest quarter is filed.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| Category: plain and Primary Class included, Secondary Class excluded | One issuer, one launch | Including secondary classes |
| SPAC = industry Shell Companies; REIT = industry starting REIT | Only fields Sharadar offers | Name matching |
| Price floor on closeunadj; dollar volume on close × volume | Actual traded price; product is adjustment-invariant | Split-adjusted close for the floor |
| EPS filter: 4 distinct quarters within trailing 16 months, filed by decision date | Literal 12 months is unmeetable given filing lag | Literal 12 months; dimension ART |
| t+24m by ASOF join; no trade in target month = terminal | Section 4 wording | Forward-fill or drop |
| Null return when t+24m is past the data edge | Not observable | Partial-period return |
| Holdings and insiders start limits recorded; H10 null before 2013-09, H11 before 2008-04 | Spec: never fill | Shifting D4; proxies |

All in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: Matt picks the unblock route. Route (a) taken; bulk pulled in-cloud.
- DONE: build universe.py and labels.py, delisting check, base rates by year, holdings 2013 start confirmed against the manifest.
- OPEN: S3 features and regime tags (BACKLOG). Write the section 10 point-in-time test first. Session startup is fetch_bulk, ingest, universe, labels (about ten minutes).
- OPEN: rename the environment variable to SHARADAR_API_KEY in the environment settings.
- BACKLOG.md was updated this session: S2 DONE (verified), S3 startup note added.

## Open Questions for Matt

1. The 16-month EPS window is my reading of "four quarters of reported EPS in the trailing 12 months". If you meant something stricter, say so and universe.py changes one constant.
2. 2007 decision dates produced 5 launches in 31,216 rows because t+24 lands in the 2009 trough. That is real, not a bug. Worth knowing before S4 reads per-year lifts.

## SESSION REVIEW [MANDATORY]

5/5 for part 2. Everything in the S2 task ran, every number is traceable to a script, three labels were reproduced independently, and the gate passed without tuning. What went wrong: the tickers bulk file's legacy table codes cost one wasted query before I looked at the distinct values. Across both parts of S2, the network block cost a session boundary and a decision from Matt; that was unavoidable.

## MATT-NOTE

(for Matt)
