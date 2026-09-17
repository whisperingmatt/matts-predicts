project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S1: scaffold repo, pin requirements, Sharadar auth test, verify table names
status: IN PROGRESS — scaffold and table verification are done; the live Sharadar auth test could not run from this environment (no API key present, and the egress proxy blocks data.nasdaq.com).
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1 hour

---

## What Was Built or Changed

Repo went from a single 1-byte placeholder file to the full section 1 scaffold. Governance files (CLAUDE.md, decisions.md, BACKLOG.md) seeded from spec sections 2 and 9. Spec placed at specs/GROWTH-001-multibagger-pattern-mining.md, transcribed from the locked v1.0 text with no changes to wording, thresholds, or rules. strategies/02-growth/ created with src stubs for ingest, universe, labels, features, regime, stats (each raises NotImplementedError naming its session), a config module holding the spec constants, a Sharadar check script, a skipped placeholder for the section 10 point-in-time test, README, and pinned requirements.txt. Root .gitignore excludes .venv, data/raw, data/processed, and .env.

The placeholder file the repo was created with ("02-growth/Spec version: 1.0 — 2026-09-17") was removed. It was empty and its name contained a colon, which blocks checkout on Windows.

## Files Touched [MANDATORY]

- .gitignore (new)
- CLAUDE.md (new)
- decisions.md (new)
- BACKLOG.md (new)
- specs/GROWTH-001-multibagger-pattern-mining.md (new)
- docs/wrapits/WRAPIT_2026-09-17-1134_s1-scaffold-sharadar-verify.md (this file)
- strategies/02-growth/README.md (new)
- strategies/02-growth/requirements.txt (new)
- strategies/02-growth/src/__init__.py, config.py, sharadar_check.py (new)
- strategies/02-growth/src/ingest.py, universe.py, labels.py, features.py, regime.py, stats.py (new stubs)
- strategies/02-growth/tests/__init__.py, test_point_in_time.py (new, skipped placeholder)
- strategies/02-growth/data/raw/.gitkeep, data/processed/.gitkeep, reports/.gitkeep (new)
- 02-growth/Spec version: 1.0 — 2026-09-17 (deleted)

## Environment Variables [MANDATORY]

NASDAQ_DATA_LINK_API_KEY — read by src/sharadar_check.py and every later ingest step. Not present in this session's environment. Never committed.

## Services and Integrations Touched [MANDATORY]

Nasdaq Data Link (Sharadar) — attempted, blocked at the network layer (see Gate Tests). No account, subscription, or key was touched or confirmed.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. Table-name verification (D6). Ran web lookups against Nasdaq help article 533 ("column definitions for the Sharadar data feeds") and sharadar.com/docs pages for fundamentals, stocks, daily, insiders, holdings, tickers, sp500. Returned: SHARADAR/SF1, SEP, DAILY, TICKERS, SF2, SF3 all exist under those names. Bundle also lists SP500, ACTIONS, EVENTS, SF3A, SF3B, SFP. No table has been renamed. Every SF1 field the section 5 features use (revenue, opinc, eps, fcf, fcfps, sharesbas, debt, cashneq, ebitda, pe, pb, divyield, marketcap, price) is present. SEP has closeadj. SF2 has transactioncode. DAILY has ev, evebit, evebitda, marketcap, pb, pe, ps and nothing else — no short-interest field.

2. `pip install nasdaq-data-link pandas numpy duckdb pyarrow pytest` into .venv on Python 3.11.15. Returned: all installed and imported cleanly. Versions pinned in requirements.txt.

3. `python -m src.sharadar_check` with no key. Returned: `FAIL: environment variable NASDAQ_DATA_LINK_API_KEY is not set. Nothing was queried.` exit 1. Expected.

4. `NASDAQ_DATA_LINK_API_KEY=dummy python -m src.sharadar_check`. Returned, for all seven tables: `ProxyError ... Tunnel connection failed: 403 Forbidden` against data.nasdaq.com. exit 1. The request URLs printed in the errors show the filters translate correctly (for example `filingdate.gte=2019-01-01&filingdate.lte=2019-12-31` on SF2). The failure is the environment's egress policy, not the script and not authentication. Direct `curl` to data.nasdaq.com from the shell fails the same way, and the proxy status endpoint logs the host as `connect_rejected`.

5. `python -m pytest -q` in strategies/02-growth. Returned: 1 skipped. Expected (placeholder only).

State: scaffold BUILT and verified by inspection. Sharadar auth NOT verified live. Table names VERIFIED against docs.

## How to Verify This Is Working Right Now

Warnings first: the key must be in the environment, not on the command line, or it lands in shell history. Do this on a machine that can reach data.nasdaq.com (Matt's own machine, not Claude Code on the web).

1. Terminal: `git clone https://github.com/whisperingmatt/matts-predicts && cd matts-predicts`
2. `git checkout claude/inspiring-lovelace-z043ut` (or main once merged)
3. `python3.11 -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
4. `pip install -r strategies/02-growth/requirements.txt`
5. `export NASDAQ_DATA_LINK_API_KEY=<key from Bitwarden>` (Windows PowerShell: `$env:NASDAQ_DATA_LINK_API_KEY="<key>"`)
6. `cd strategies/02-growth && python -m src.sharadar_check`
7. Expected last line: `RESULT: PASS — all tables reachable, all required columns present`. Paste the full output into the S2 session.

## What Breaks and How to Fix It

- Any `FAIL SHARADAR/<table>: ... 403` or `NotFoundError` from the check script on Matt's machine means the subscription does not cover that table (SF2 and SF3 are the Investors product; SF1/SEP/DAILY/TICKERS/SP500 are Core US Equities). Stop and report which tables failed; do not proceed to S2.
- `MISSING required columns` on SF3: the SF3 column list in the script (investorname, securitytype, calendardate, value, units) was not confirmed from the Nasdaq page, which was truncated. If only SF3 columns are flagged, print the columns line and adjust REQUIRED_COLUMNS in src/sharadar_check.py with a decisions.md note.
- `ProxyError ... 403` on Matt's machine would mean a corporate proxy; not expected at home.

## Environment Facts Learned [MANDATORY]

- Claude Code on the web cannot reach data.nasdaq.com or sharadar.com; the egress proxy rejects CONNECT with 403. Recorded in CLAUDE.md. All live Sharadar pulls for S2 onward must run elsewhere, or the environment's network policy must allow those two hosts.
- Nasdaq Data Link column names differ from Sharadar's newer direct API (api.sharadar.com): NDL uses datekey (SF1) and filingdate (SF2); the direct API calls both `date`. The spec and this repo use the NDL names. Recorded in CLAUDE.md.
- SHARADAR/DAILY has no short-interest field. H12 short_fuel is unavailable. Recorded in CLAUDE.md and decisions.md.
- SHARADAR/SP500 exists with additions, removals, and quarterly constituent snapshots back to 1998. H16 can use real constituent history rather than the SPDR proxy. Recorded in decisions.md.
- Nasdaq-Data-Link 1.0.4 installs alongside pandas 3.0.5 and imports cleanly; it has not yet been exercised against real data because of the network block.

## Ephemeral Outputs Not Yet Saved

None. All outputs are in the commit.

## Plain English Summary for Matt

The repo now has its rules, its backlog, the locked spec in the right place, and the code skeleton for the study. The six Sharadar tables the spec names still exist under those names, and every data field the features need is there, with one exception: Sharadar has no short-interest data, so the H12 signal is out, as the spec allows. One thing did not happen: the live login test against Sharadar. This environment cannot reach Nasdaq's servers at all, and no API key was available to it. The test script is written and behaves correctly up to the network. You need to run it once on your own machine with your key (steps above) and paste the result into the next session. S2 does not start until that passes.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| Spec at specs/GROWTH-001-multibagger-pattern-mining.md; colon-named placeholder deleted | Spec section 1 says specs/; colon breaks Windows checkout; naming avoids bare SPEC-N collisions | Keep 02-growth/ file (empty, wrong place) |
| Code under strategies/02-growth/, not top-level 02-growth/ | Spec section 1 layout | Top-level 02-growth/ |
| API key only via NASDAQ_DATA_LINK_API_KEY | Spec section 10, secrets rule | .env in repo; key on command line |
| H12 short_fuel UNAVAILABLE | DAILY has no short-interest field; spec says mark and move on | Any proxy |
| Use SHARADAR/SP500 for H16 constituent history in S3 | Table exists with history to 1998; spec prefers real constituents over the SPDR proxy | SPDR marketcap proxy (fallback only) |
| Pin latest versions (pandas 3.0.5 etc.) | Install and import cleanly on 2026-09-17 | Pin pandas 2.x preemptively (revisit only if S2 hits a pandas 3 change) |

All six are in decisions.md.

## Open Items for Next Session [MANDATORY]

- OPEN: Matt runs src/sharadar_check.py on his machine with the key; pastes output. S2 is blocked until PASS.
- OPEN: If the SF3 required-column check fails, correct the list from the printed columns and note it in decisions.md.
- OPEN: Decide whether S2 runs on Matt's machine or in a Claude Code environment whose network policy allows data.nasdaq.com. Ingesting full SEP through the web environment also needs enough disk for the parquet cache.
- BACKLOG.md was updated this session: S1 marked DONE (built) with the open gate; S2 marked blocked on it.

## Open Questions for Matt

1. Does the Sharadar subscription include the Investors product (SF2 insiders, SF3 institutions), or only Core US Equities? The check script will answer this, but if you already know, say so before running it.
2. Where should S2 run: your machine, or a web session with the network policy widened for data.nasdaq.com?

## SESSION REVIEW [MANDATORY]

4/5. Scaffold, spec placement, and table verification are complete and evidenced. What went wrong: the auth test, which section 9 names as an S1 deliverable, could not run here. Two blockers stacked: no key in the environment and a hard network block on the data host. Neither was discoverable before the session started. The script was still written and exercised to the point the environment allows, and the exact failure text is recorded above.

## MATT-NOTE

(for Matt)
