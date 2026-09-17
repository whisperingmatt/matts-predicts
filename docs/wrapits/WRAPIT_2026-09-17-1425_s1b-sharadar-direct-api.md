project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S1b: D6 superseded, Sharadar check rewritten for the direct API, run live, PASS
status: COMPLETE — the S1 auth gate is closed with a live PASS; S2 was not started on Matt's instruction.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1 hour

---

## What Was Built or Changed

Matt ruled that D6 is wrong: the subscription is on the Sharadar direct API (api.sharadar.com), not Nasdaq Data Link. The API docs were read (sharadar.com/docs/getting-started, /auth, and the fundamentals, stocks, daily, tickers, insiders, holdings, sp500 pages) and src/sharadar_check.py was rewritten to call `https://api.sharadar.com/v1.0/data/<table>?api_key=...&format=json` with plain HTTPS via requests. The Nasdaq-Data-Link package was dropped from requirements.txt and requests 2.33.1 pinned in its place. config.py now carries the direct-API base URL, the seven direct-API table names, and the key variable names. The supersession, the SF1/SEP/DAILY/TICKERS/SF2/SF3/SP500 to fundamentals/stocks/daily/tickers/insiders/holdings/sp500 mapping, and the column renames (datekey → fundamentals.date, filingdate → insiders.date, calendardate → holdings.date, investorname → holdings.investorid) are recorded in decisions.md. CLAUDE.md environment facts were corrected. The check was run live in this environment with Matt's key and returned PASS.

Two findings changed the script's design. First, api.sharadar.com serves the trailing year of any ticker to any request, with a bad key or no key at all, so a query for recent AAPL data proves nothing. The check therefore probes MSFT in 2006 to 2013 windows: only rows older than a year prove the key was accepted and the subscription covers the table. Second, the API's from= and to= parameters default to one year ago and yesterday, so any pull that omits them silently returns one year of data. Both facts are in CLAUDE.md and decisions.md.

## Files Touched [MANDATORY]

- strategies/02-growth/src/sharadar_check.py (rewritten)
- strategies/02-growth/src/config.py (API base URL, table names, key variable names)
- strategies/02-growth/requirements.txt (Nasdaq-Data-Link removed, requests added)
- strategies/02-growth/README.md (data route and key variable)
- decisions.md (D6 marked superseded; four new rulings; one ruled-out line)
- CLAUDE.md (environment facts: data route, key variable, name mapping, API quirks, network reach)
- BACKLOG.md (S1 DONE verified; S2 unblocked, not started)
- docs/wrapits/WRAPIT_2026-09-17-1425_s1b-sharadar-direct-api.md (this file)

## Environment Variables [MANDATORY]

SHARADAR_API_KEY — new primary name, read by src/sharadar_check.py. Not set in this environment.
NASDAQ_DATA_LINK_API_KEY — fallback name. Present in this session's environment (it was not present in the S1 session). The script reported it as the key source. Value never printed or written anywhere.

## Services and Integrations Touched [MANDATORY]

Sharadar direct API, api.sharadar.com — seven read-only GET requests of at most 5 rows each with Matt's key, plus about twenty probe requests with the public test key, a deliberately bad key, or no key while establishing the response shape and the unauthenticated tier's behavior. No writes, no subscription changes.
Nasdaq Data Link — no longer used. Not contacted.

## Endpoints Added or Changed [MANDATORY]

None added. The endpoint the check calls changed from data.nasdaq.com/api/v3/datatables/SHARADAR/<TABLE> to api.sharadar.com/v1.0/data/<table>.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. `cd strategies/02-growth && python -m src.sharadar_check` with the key from the environment. Returned `RESULT: PASS — all tables reachable with history, all required columns present`, exit 0. Per table: tickers 3 rows 28 columns; fundamentals 2 rows 112 columns (filing dates 2006-01-01..2006-06-30, ARQ); stocks 5 rows 10 columns (2006-01-03..2006-01-10); daily 5 rows 10 columns (same window); insiders 5 rows 23 columns (2008-07-01..2008-12-31); holdings 5 rows 6 columns (2013-07-01..2013-12-31, SHR); sp500 2 rows 7 columns (2006-01-01..2006-06-30). No MISSING lines.

2. Same command with neither key variable set. Returned `FAIL: neither SHARADAR_API_KEY nor NASDAQ_DATA_LINK_API_KEY is set. Nothing was queried.`, exit 1.

3. Same command with SHARADAR_API_KEY=bad-key-xyz. Returned OK for tickers (no date column, so it cannot prove auth), FAIL with `0 rows in a historical window — key not accepted, or the subscription does not include this table or this history` for the other six, `RESULT: FAIL`, exit 1. A grep of that output for the bad key string found 0 occurrences.

4. `python -m pytest -q` in strategies/02-growth. Returned 1 skipped (placeholder only). Expected.

5. `pip install` of the revised requirements.txt into a fresh .venv on Python 3.11.15. Returned all six packages at the pinned versions.

6. Docs verification for the request format: sharadar.com/docs/getting-started, /auth, and the seven table pages, fetched through Firecrawl because the egress proxy blocks sharadar.com from the shell. Live probes confirmed: JSON body is `{"count": N, "data": [...]}`; unknown table returns HTTP 403 `{"error":"Forbidden","description":"Unknown table."}`; bad key or no key returns HTTP 200 with trailing-year data for AAPL and MSFT; historical windows return `{"count":0,"data":[]}` with a bad key.

State: check BUILT and VERIFIED live. S1 gate CLOSED.

## How to Verify This Is Working Right Now

Warning first: put the key in the environment, never on the command line, or it lands in shell history.

1. Terminal: `git clone https://github.com/whisperingmatt/matts-predicts && cd matts-predicts`
2. `git checkout claude/nice-dijkstra-801d68` (or main once merged)
3. `python3.11 -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
4. `pip install -r strategies/02-growth/requirements.txt`
5. `export SHARADAR_API_KEY=<key from Bitwarden>` (Windows PowerShell: `$env:SHARADAR_API_KEY="<key>"`)
6. `cd strategies/02-growth && python -m src.sharadar_check`
7. Expected last line: `RESULT: PASS — all tables reachable with history, all required columns present`.

## What Breaks and How to Fix It

- All six dated tables FAIL with 0 rows while tickers is OK: the key is wrong or expired, or the subscription is a trailing-year tier. Check the key on sharadar.com, signed in, under the Authentication docs page.
- Only insiders and holdings FAIL with 0 rows: the subscription is Fundamentals or Prices only, not the Bundle or Investors product. Stop and report; H8 to H10 and H13 to H15 depend on those tables.
- `HTTP 403 ... Unknown table.`: a table was renamed on Sharadar's side. Check sharadar.com/docs and record the new name in decisions.md.
- A pull in S2 returns exactly one year of data: from= was omitted. The API defaults to one year ago.

## Environment Facts Learned [MANDATORY]

- api.sharadar.com is reachable from Claude Code on the web; sharadar.com (docs) and data.nasdaq.com are not. Recorded in CLAUDE.md. This means S2 ingest can run in this environment, subject to disk for the parquet cache.
- The unauthenticated tier of api.sharadar.com returns the trailing year for any ticker, with any key or none. Auth can only be proven by requesting older rows. Recorded in CLAUDE.md and decisions.md.
- from= and to= default to one year ago and yesterday on every dated table. Recorded in CLAUDE.md and decisions.md.
- format=json returns large integers as strings (for example revenue "109417000000"); format=csv returns plain numbers. S2 ingest should use csv, or the years=full bulk zip. Recorded in CLAUDE.md.
- limit defaults to 10000 rows; skip pages. years=full redirects to a bulk CSV zip; status=True reports its size. Recorded in CLAUDE.md.
- holdings has investorid (six-character code), not investorname. Recorded in decisions.md.
- NASDAQ_DATA_LINK_API_KEY is now set in this environment, unlike the S1 session.

## Ephemeral Outputs Not Yet Saved

None. Full check output is reproduced under Gate Tests.

## Plain English Summary for Matt

You were right about the data route. The check script now talks to sharadar.com's own API, and it passed here with your key: all seven tables answered with data from 2006, 2008, and 2013, and every field the study needs is there under its new name. The Sharadar API has one trap worth knowing: it hands out the last year of data to anyone, key or no key, so a test that only asks for recent Apple prices proves nothing. The check now asks for old Microsoft data instead, which only a paid key can get. Another trap: if a query does not say a start date, the API quietly gives you one year. Both are written into the repo rules so S2 does not fall into them. S2 is unblocked and not started, as you asked.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| D6 superseded: Sharadar direct API, tables fundamentals/stocks/daily/tickers/insiders/holdings/sp500 | Matt's ruling; that is where the subscription is | Nasdaq Data Link (no subscription) |
| Keep direct-API column names in code; spec's datekey = fundamentals.date, filingdate = insiders.date, calendardate = holdings.date, investorname = holdings.investorid | Avoids a rename layer whose only job is matching the spec's wording | Renaming at ingest to NDL names |
| Key variable SHARADAR_API_KEY, fallback NASDAQ_DATA_LINK_API_KEY | Old name is wrong but already set in environments | Hard rename; keep old name only |
| Nasdaq-Data-Link dropped, requests 2.33.1 pinned | Direct API is plain HTTPS | Keep NDL client unused |
| Check probes MSFT in 2006–2013 windows, not AAPL | Unauthenticated tier serves trailing year for any ticker; AAPL is the public sample | Probe recent AAPL (proves nothing) |

All five are in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: Matt runs src/sharadar_check.py with the key and pastes output. Ran here, PASS; output above.
- DONE: If the SF3 required-column check fails, correct the list. The holdings column list was corrected from the docs before running (investorid, date); no failure.
- DONE: Decide whether S2 runs on Matt's machine or in a web session. api.sharadar.com is reachable from the web environment, so either works; disk for the parquet cache is the remaining constraint.
- OPEN: S2 is unblocked. Next build session starts it. Every pull must set from= and to=; full tables should come from years=full bulk zips.
- BACKLOG.md was updated this session: S1 DONE (verified), S2 unblocked and not started.

## Open Questions for Matt

1. The key in this environment is stored under the old name NASDAQ_DATA_LINK_API_KEY. Rename it to SHARADAR_API_KEY in the environment settings when convenient; the fallback keeps working until then.
2. S2 will need roughly 1 to 2 GB of disk for the bulk zips plus parquet. Does the web environment's allowance cover that, or should S2 run on your machine?

## SESSION REVIEW [MANDATORY]

5/5. The task was done exactly as scoped: docs read, script rewritten, decision recorded with the mapping, check run live and passed, S2 not started. What went wrong: nothing in the deliverable. One near miss: the first draft probed AAPL, which would have reported PASS with a bad key. Caught by testing a bad key before trusting the result.

## MATT-NOTE

(for Matt)
