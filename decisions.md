# decisions.md — matts-predicts

Rulings that constrain future work. A locked spec changes only with an
entry here. Newest entries at the bottom of each section. Ruled-out
approaches at the end of the file.

## Section 2 Growth — locked decisions (from GROWTH-001 v1.0, 2026-09-17)

D1. Launch = forward 24-month close-to-close return ≥ 300% from a
month-end decision date. Also record ≥ 200% and ≥ 500% flags.

D2. All features computed point-in-time using Sharadar filing dates
(datekey), never period dates (calendardate). No look-ahead.

D3. Universe floors at decision date: price ≥ $5, trailing 20-day
average dollar volume ≥ $1,000,000.

D4. Build window 2006-01 to 2019-12. Holdout 2020-01 to 2026-06.
Holdout is not opened until single-signal and combination results on
the build window are final and written to reports/.

D5. Every stock-month is tagged with market regime (spec section 6).
All results reported raw and by regime bucket.

D6. Primary data source: Sharadar via Nasdaq Data Link (tables SF1,
SEP, DAILY, TICKERS, SF2, SF3). Verify table names against current
Sharadar docs before coding; report if they have changed.
[SUPERSEDED 2026-09-17 — see "D6 SUPERSEDED" under Repo rulings: the
subscription is on the Sharadar direct API; table and column names
mapped there.]

D7. H2 (surprise streak) and H3 (estimate revisions) are DEFERRED. No
consensus estimate feed in pass one. Do not proxy them.

D8. Minimum 100 launch events per reporting cell. Below that, report
"insufficient" — no number.

D9. Combinations capped at three signals.

## Repo rulings

2026-09-17 — Spec lives at specs/GROWTH-001-multibagger-pattern-mining.md.
Reason: spec section 1 says "specs/ — this file goes here"; naming
follows <TRACK>-<NNN>-<slug>.md so it cannot collide with bare SPEC-N
names used in other repos. The placeholder file the repo was created
with ("02-growth/Spec version: 1.0 — 2026-09-17", 1 byte, colon in the
name) was removed because a colon in a filename blocks checkout on
Windows. Alternatives rejected: keeping the file under 02-growth/ (not
where the spec says it goes; empty anyway).

2026-09-17 — Strategy code lives under strategies/02-growth/ as the
spec's section 1 lays out, not under a top-level 02-growth/.

2026-09-17 — Sharadar API key comes only from the environment variable
NASDAQ_DATA_LINK_API_KEY. Reason: spec section 10 and standing secrets
rule. Alternatives rejected: .env committed to repo; key on command line.

2026-09-17 — D6 table-name verification result: SHARADAR/SF1, SEP,
DAILY, TICKERS, SF2, SF3 all still exist under those names on Nasdaq
Data Link (source: Nasdaq help article 533 lists the Core US Equities
Bundle tables SF1, TICKERS, DAILY, SP500, ACTIONS, EVENTS, SF2, SF3,
SF3A, SF3B, SEP, SFP). Names have not changed. The bundle also carries
SHARADAR/SP500 (index additions, removals, and quarterly constituent
snapshots back to 1998), which is the constituent history H16 asks
for; use it rather than the SPDR marketcap proxy when S3 is built.

2026-09-17 — H12 short_fuel marked UNAVAILABLE. Reason: SHARADAR/DAILY
carries only ev, evebit, evebitda, marketcap, pb, pe, ps. No short
interest field exists in any Sharadar table. Spec section 5 says mark
unavailable and move on; do not substitute.

2026-09-17 — Pinned stack: Nasdaq-Data-Link 1.0.4, pandas 3.0.5,
numpy 2.4.6, duckdb 1.5.5, pyarrow 25.0.1, pytest 9.1.1. Reason: latest
versions that install and import cleanly together on Python 3.11 on
2026-09-17. pandas 3 is a major version; if S2 hits a pandas 3
behavior change, pin down to the 2.x line with an entry here rather
than working around it in code.

2026-09-17 — D6 SUPERSEDED: the subscription is on the Sharadar direct
API (api.sharadar.com), not Nasdaq Data Link. Matt's ruling, this
session. Request format, from sharadar.com/docs/getting-started:
https://api.sharadar.com/v1.0/data/<table>?api_key=<key>&<filters>
with format=json returning {"count": N, "data": [ {column: value} ]}.
Table name mapping (NDL name → direct-API name, verified against each
table's docs page and a live PASS on 2026-09-17):
SF1 → fundamentals; SEP → stocks; DAILY → daily; TICKERS → tickers;
SF2 → insiders; SF3 → holdings; SP500 → sp500.
Column name mapping for names the spec or S1 used:
SF1 datekey → fundamentals.date (filing date; D2 point-in-time key);
SF2 filingdate → insiders.date; SF3 calendardate → holdings.date
(quarter end); SF3 investorname → holdings.investorid (six-character
code; no name column). All other required columns keep their names.
Rule for S2 ingest: keep direct-API column names as delivered. Where
the spec says datekey, code reads fundamentals.date. Do not rename.
Alternatives rejected: renaming at ingest to the NDL names (adds a
translation layer whose only purpose is matching the spec's wording);
staying on Nasdaq Data Link (no subscription there).

2026-09-17 — API key environment variable is SHARADAR_API_KEY, with
NASDAQ_DATA_LINK_API_KEY read as a fallback. Reason: the old name is
wrong for a sharadar.com key, but it is already set in the Claude Code
web environment and possibly on Matt's machine; the fallback avoids a
silent break. The check script prints which name it used, never the
value. Alternatives rejected: hard rename (breaks existing
environments); keeping only the old name (misleading).

2026-09-17 — Pinned stack change: Nasdaq-Data-Link 1.0.4 removed,
requests 2.33.1 added. Reason: the direct API is plain HTTPS; the NDL
client cannot call it. Other pins unchanged.

2026-09-17 — Sharadar auth gate: the check probes MSFT, not AAPL, in
2006–2013 windows. Reason: verified live that api.sharadar.com serves
the trailing year for any ticker with a bad key or no key at all, and
AAPL is the public sample. Only rows older than one year prove the key
and the subscription. Any future data pull that omits from= gets one
year of data silently; S2 ingest must always set from= and to=.

2026-09-17 — data/ does NOT persist between Claude Code cloud sessions.
Evidence: each session runs in a fresh, ephemeral container (the platform
documents this); the .venv built in the S1 session was absent when the
S1b session started and had to be rebuilt; no persistent volume is
mounted under the repo. Within one session the container survives across
turns (the S1b .venv was still present when S2 began in the same session).
Rule: every cloud session that needs data runs src/fetch_bulk.py first,
then src/ingest.py. Nothing under data/ is treated as durable; anything
worth keeping is committed (reports, manifests of row counts) or
regenerated. Alternatives rejected: committing parquet (multi-GB, and
Sharadar terms); a cloud volume (none is offered by the environment).

2026-09-17 — Sharadar bulk downloads are BLOCKED from Claude Code on the
web. api.sharadar.com answers years=full with a 302 to
static-sharadar.nyc3.digitaloceanspaces.com and the egress proxy rejects
the CONNECT to that host with 403 (policy denial, logged by the proxy as
connect_rejected). Verified 2026-09-17 with tickers.csv.zip; the
download=1 flag redirects to the same host. The paged API on
api.sharadar.com is allowed, capped at 100,000 rows per request (HTTP 400
"limit too large" above that), about 3 seconds per 100,000-row page.
S2 ingest via bulk files therefore needs either (a) the environment's
network policy to allow static-sharadar.nyc3.digitaloceanspaces.com, or
(b) running src/fetch_bulk.py on Matt's machine, or (c) a paged-API
pull of roughly 3,000 requests over 2–3 hours. Matt decides; recorded as
an open question in the S2 wrap. Not ruled out: any of the three.

## Ruled out (do not re-suggest without a specific new reason)

- Free data substitutes for Sharadar (spec section 10).
- Proxies for H2, H3, H17, H18 (D7, spec section 5).
- Filling nulls in features (spec section 5).
- Any short-interest proxy for H12 (spec section 5; no Sharadar field).
- Nasdaq Data Link as the data route (no subscription there; D6 superseded).
