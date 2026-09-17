project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S2 part 1: persistence ruling, bulk setup script, parquet converter; ingest blocked by egress policy
status: BLOCKED — bulk downloads cannot leave this environment; universe, labels, and base rates not started. Matt chooses one of three unblock routes.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1 hour

---

## What Was Built or Changed

The session began with the persistence question. Answer: data/ does not persist between Claude Code cloud sessions. Each session is a fresh container; the .venv built in the S1 session was gone when the S1b session started, and no persistent volume is mounted. Within a session the container survives across turns. Recorded in decisions.md and CLAUDE.md.

Because data does not persist, src/fetch_bulk.py was written as the setup script. It asks api.sharadar.com for each table's bulk file status, downloads years=full only when the local zip is missing or the wrong size, writes to a .part file, and never prints the key. src/ingest.py was rewritten from its stub into a zip-to-parquet converter using duckdb, streaming the CSV with whole-file type sniffing, deleting the CSV afterward, and writing data/raw/ingest_manifest.json with rows, columns, and date range per table. config.py gained BULK_TABLES, which adds funds to the seven check tables.

Then the ingest hit a wall. api.sharadar.com answers years=full with a 302 to static-sharadar.nyc3.digitaloceanspaces.com, and this environment's egress proxy refuses the CONNECT to that host with 403. The proxy logs it as a policy denial and its README says to report such hosts, not route around them. The download=1 flag redirects to the same host. So no bulk file could be pulled, and nothing that depends on the data was built: no universe.parquet, no labels, no base rates, no delisting check. The holdings 2013 start limitation was already recorded in decisions.md on 2026-09-17 (holdings history begins June 2013) and stays there; it was not re-verified against data this session.

The paged API on api.sharadar.com is allowed. Measured: 100,000 rows is the hard cap per request (HTTP 400 above it), and one 100,000-row page returns in about 3 seconds. A full paged pull of all eight tables is roughly 3,000 requests over two to three hours. That is a method change from Matt's instruction to use bulk downloads, so it was not attempted.

Matt sent the bulk URL format mid-session. It is the format the script already uses; the block is downstream of it. The link he pasted contained the real key, not a redacted one. Nothing from it was written to the repo or any file.

## Files Touched [MANDATORY]

- strategies/02-growth/src/fetch_bulk.py (new)
- strategies/02-growth/src/ingest.py (rewritten from stub)
- strategies/02-growth/src/config.py (BULK_TABLES)
- decisions.md (two rulings: persistence; bulk egress block and options)
- CLAUDE.md (environment facts: blocked host, paged cap, persistence)
- BACKLOG.md (S2 IN PROGRESS, BLOCKED, with what is done and the options)
- docs/wrapits/WRAPIT_2026-09-17-1435_s2-ingest-blocked-bulk-egress.md (this file)

## Environment Variables [MANDATORY]

NASDAQ_DATA_LINK_API_KEY — present in this environment; used by fetch_bulk.py via the fallback name. Value never printed.
SHARADAR_API_KEY — not present in this environment yet, despite Matt's note that the key is there; the container's variables are fixed at start. Read first when present.

## Services and Integrations Touched [MANDATORY]

api.sharadar.com — read-only: eight status=True calls, two years=full calls (redirected, then refused by the proxy), three paged CSV calls (stocks one month, tickers twice) to measure the cap and speed. No writes.
static-sharadar.nyc3.digitaloceanspaces.com — CONNECT attempted three times, refused by the egress proxy each time.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None. No parquet exists under data/ in the repo tree; the converter test used the scratchpad.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. `python -m src.fetch_bulk sp500 tickers`. Returned, for both tables, `FAIL <table>: ProxyError: HTTPSConnectionPool(host='static-sharadar.nyc3.digitaloceanspaces.com', port=443) ... Tunnel connection failed: 403 Forbidden`, `RESULT: FAIL — 0 MB present`, exit 1. The key did not appear in the output. The proxy status endpoint listed the host under recentRelayFailures as connect_rejected.

2. `curl -L` of the tickers years=full URL directly. Returned `CONNECT tunnel failed, response 403`, 0 bytes. Same with download=1 (302 to the same host).

3. `python -m src.ingest --raw-dir <scratchpad> tickers` on a zip built from a paged-API tickers CSV (74,195 rows). Returned `OK tickers: 74,195 rows, 28 columns, lastpricedate 1996-09-05..2026-09-16, parquet 3 MB`, `RESULT: PASS`, exit 0. The CSV was deleted after conversion; the manifest was written. Follow-up query on the parquet: date columns typed DATE; stocks-table rows split isdelisted Y 14,642 / N 6,331.

4. Paged-API cap: tickers with limit=200000 returned HTTP 400 `{"error":"limit too large","description":"limit cannot exceed 100,000 rows ...}`. stocks from=2010-01-01 to=2010-01-31 limit=100000 format=csv returned exactly 100,000 rows in 3 seconds (the month has more; the cap truncated it).

5. Bulk status for all eight tables: fundamentals 629.9 MB, stocks 945.1 MB, daily 729.4 MB, tickers 4.71 MB, insiders 235.3 MB, holdings 583.4 MB, sp500 278.7 KB, funds 290.7 MB, all available=True, modified 2026-09-16/17.

State: fetch_bulk.py BUILT, verified to the redirect and blocked there. ingest.py BUILT and VERIFIED on a fixture. Ingest, universe, labels, base rates NOT STARTED.

## How to Verify This Is Working Right Now

Warning first: the key goes in the environment, never on the command line. On a machine that can reach static-sharadar.nyc3.digitaloceanspaces.com (your own):

1. `git clone https://github.com/whisperingmatt/matts-predicts && cd matts-predicts && git checkout claude/nice-dijkstra-801d68`
2. `python3.11 -m venv .venv && source .venv/bin/activate && pip install -r strategies/02-growth/requirements.txt`
3. `export SHARADAR_API_KEY=<key>`
4. `cd strategies/02-growth && python -m src.fetch_bulk` — expect eight OK lines and `RESULT: PASS — 3419 MB present`. About 3.4 GB of zips.
5. `python -m src.ingest` — expect eight OK lines with row counts and date ranges, `RESULT: PASS`. Needs roughly 6 GB free for the largest CSV during conversion.

## What Breaks and How to Fix It

- `ProxyError ... digitaloceanspaces.com ... 403` from fetch_bulk.py: the network policy blocks the bulk host. Allow it in the environment settings or run on another machine.
- `FAIL <table>: downloaded N bytes, status said M`: the transfer was cut. Re-run; the .part file is discarded and the download restarts.
- ingest.py `expected one CSV member`: Sharadar changed the zip layout. Inspect with `unzip -l` and adjust extract_csv.
- ingest.py out of memory on stocks: preserve_insertion_order is already off; if it still fails, raise the machine's memory or convert with `SET threads=2`.

## Environment Facts Learned [MANDATORY]

- data/ does not persist between cloud sessions; the container is ephemeral. CLAUDE.md and decisions.md.
- static-sharadar.nyc3.digitaloceanspaces.com is blocked by the egress policy; api.sharadar.com is not. CLAUDE.md and decisions.md.
- Paged API cap is 100,000 rows per request; about 3 seconds per full page. CLAUDE.md and decisions.md.
- Bulk Full History zips total about 3.4 GB; the environment reports 30 GB writable, so disk is not the constraint. This wrap only.
- Tickers table has 74,195 rows across tables stocks, fundamentals, holdings_investor, insiders, funds; 14,642 of 20,973 stocks-table tickers are delisted, so delistings are present at the metadata level. This wrap only; the price-table delisting check in spec section 3 is still to be run on stocks data.

## Ephemeral Outputs Not Yet Saved

The scratchpad fixture (tickers.csv.zip, tickers.parquet, ingest_manifest.json) is disposable. Nothing else.

## Plain English Summary for Matt

Two facts first. Data does not survive between cloud sessions, so I wrote the setup script you asked for, and it works right up to the point where Sharadar hands the download off to its file host. That host is on the block list of this environment's network policy, which you chose when you created the environment, so no bulk file could come in and none of the data work happened. The converter that turns the zips into parquet is written and tested on a real 74,000-row file, so once the zips arrive the rest is ready to run. You need to pick one of three routes below. The one I recommend is adding the file host to the environment's allowed domains, because it fixes every future session too.

Also: the link you pasted mid-session contained your actual API key, not a redacted one. It went nowhere from here, but if that chat is shared anywhere, rotate the key on sharadar.com.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| data/ is not durable; every cloud session runs fetch_bulk.py then ingest.py | Ephemeral container, verified | Committing parquet; a cloud volume (none offered) |
| Bulk download block recorded with three unblock routes, none chosen | Policy denial is Matt's to lift or route around; paged pull is a method change | Silently switching to the paged API |
| funds added to BULK_TABLES, not to the S1 check TABLES | S3 needs SPY and SPDRs; the check script's queries are keyed per table | Adding funds to the check |

All three are in decisions.md.

## Open Items for Next Session [MANDATORY]

- OPEN: Matt picks the unblock route (question 1 below). S2 resumes at `python -m src.fetch_bulk`.
- OPEN: once data is in, build universe.py and labels.py per sections 3 and 4, run the delisting check on stocks, report base rates by year, confirm the holdings 2013 start against the manifest.
- OPEN: rename the environment variable to SHARADAR_API_KEY in the environment settings (carried from S1b; still under the old name here).
- BACKLOG.md was updated this session: S2 IN PROGRESS, BLOCKED, with what is done and the options.

## Open Questions for Matt

1. Which route: (a) add static-sharadar.nyc3.digitaloceanspaces.com to this environment's allowed domains, then re-run S2 in a new cloud session — cleanest, and my recommendation; (b) run `python -m src.fetch_bulk` on your machine, then either run ingest and the rest there or accept that cloud sessions still cannot pull; (c) approve a paged-API pull here, about 3,000 requests over 2–3 hours, identical data, unknown rate-limit behavior on your account.
2. If (a): the docs host sharadar.com could be allowed at the same time so future sessions can read the docs directly instead of through a third-party fetcher.

## SESSION REVIEW [MANDATORY]

3/5. The persistence question was answered with evidence, and the setup script and converter are real and tested. The main deliverable, ingest through base rates, did not happen because of a network policy that could not be discovered before the first download attempt. What went wrong beyond that: nothing; the block was found on the smallest file, reported once, and not worked around.

## MATT-NOTE

(for Matt)
