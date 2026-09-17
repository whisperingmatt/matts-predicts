matts-predicts — Standing Rules
Project
Three US stock strategies under research by Matt (solo operator, Sydney).
This repo is the canonical source of truth. Chat designs hypotheses,
Claude Code runs the data. The spec is the contract between the two.
Do not add hypotheses, change thresholds, or "improve" the method. If
something is impossible as written, stop and report exactly what and why.
Structure (monorepo)
specs/             — locked specs, <TRACK>-<NNN>-<slug>.md
decisions.md       — rulings; changes to a locked spec need an entry here
BACKLOG.md         — next tasks, one task per build session
docs/wrapits/      — session wrap docs
strategies/02-growth/ — Section 2 Growth: multibagger pattern-mining study
    src/       ingest, universe, labels, features, regime, stats
    data/raw/  data/processed/  (gitignored, regenerable from Sharadar)
    reports/   build_window_results.md, holdout_results.md
    tests/     point-in-time unit tests
Locked (see specs/GROWTH-001-multibagger-pattern-mining.md section 2)
Launch definition, point-in-time joins on datekey, universe floors,
build window 2006-01 to 2019-12, holdout 2020-01 to 2026-06, regime
tagging, Sharadar as the only data source, deferred hypotheses, minimum
100 events per cell, combinations capped at three signals.
Holdout is not opened until build-window results are final and committed
to reports/.
Session rules
One task per build session, from BACKLOG.md, spec'd in specs/.
Read decisions.md and the latest docs/wrapits/ file before any work.
Discussion and build never mix.
No session ends until BACKLOG.md reflects this session's completed work.
Operator rules (how to work with Matt)
Actions first, numbered, imperative, exact app/tab/button/file/line.
Warnings and conditions BEFORE step 1, never after.
Complete step lists upfront, not drip-fed.
When uncertain, give options with honest odds before attempting.
Never pretend something worked when it didn't. Try once, then stop
and report exactly what went wrong.
Track what Matt has ruled out (bottom of decisions.md). Never
re-suggest a rejected approach without a specific new reason.
Verification (non-negotiable)
Pass/fail criteria exist in the spec BEFORE building starts.
Evidence, not assertions: actual commands run, actual output.
Nothing is reported COMPLETE without a gate-test line in the wrap
stating what was run and what it returned. "Built" and "verified"
are different states — say which one is true.
Environment facts (permanent — do not rediscover)
Python 3.11. Virtualenv at .venv/ (gitignored). Pinned versions in
strategies/02-growth/requirements.txt.
Sharadar is reached via the Sharadar direct API, base URL
https://api.sharadar.com/v1.0/data/<table>, using the requests package.
The subscription is on sharadar.com, not Nasdaq Data Link. The API key
is read from the environment variable SHARADAR_API_KEY (fallback name
NASDAQ_DATA_LINK_API_KEY, kept because existing environments set it).
Never commit it. Never pass it on a command line that gets logged.
Direct-API table names: fundamentals (SF1), stocks (SEP), daily,
tickers, insiders (SF2), holdings (SF3), sp500. Column names differ
from the Nasdaq Data Link feed: fundamentals.date is the filing date
the spec calls datekey; insiders.date is the filing date NDL called
filingdate; holdings.date is the quarter end NDL called calendardate
and holdings has investorid, not investorname. This repo uses the
direct-API names in code; the spec's NDL names map as above.
Direct-API quirks (verified 2026-09-17): from= and to= default to one
year ago and yesterday, so every historical pull must set them; the
unauthenticated tier returns the trailing year for any ticker and any
key, so only rows older than one year prove authentication; limit
defaults to 10000 with skip for paging; years=full gives a bulk CSV
zip; format=json returns large integers as strings, format=csv does
not.
Claude Code on the web (this environment) can reach api.sharadar.com
but cannot reach sharadar.com (docs) or data.nasdaq.com — the egress
proxy returns 403 on CONNECT for those two. Verified 2026-09-17.
The daily table has no short-interest field (ev, evebit, evebitda,
marketcap, pb, pe, ps only). H12 short_fuel is unavailable from
Sharadar. Verified 2026-09-17 against sharadar.com/docs/daily and a
live query.
No colon in any committed filename — invalid on Windows paths, blocks
every checkout on Matt's machine.
Commits and wraps
Commit after each completed task; message = two-line mini-wrap.
Session end: WRAPIT_YYYY-MM-DD-HHMM_topic-slug.md (no colon) to
docs/wrapits/, Sydney time (AEST/AEDT), synthesized from the commit log.
Fill every MANDATORY section of the template below — write "None"
explicitly if nothing applies.
Secrets
Never in this repo. Environment variables at runtime. Variable NAMES
only in code.
Style
Internal docs: American spelling, prose, no filler, no hype.
Reports: every number traceable to a query in src/. No fabricated
statistics. Cells below the D8 minimum say "insufficient", never a number.
WRAPIT template
    project: matts-predicts
    session-type: [build / work / experiment / dump]
    session: YYYY-MM-DD AEST — [one-line description]
    status: [COMPLETE / IN PROGRESS / BLOCKED — one sentence]
    claude-interface: [Chat-Work / Chat-Home / Cowork / Code]
    source: [interface + date]
    session-duration: [approximate hours]

    ---

    ## What Was Built or Changed
    ## Files Touched [MANDATORY]
    ## Environment Variables [MANDATORY]
    ## Services and Integrations Touched [MANDATORY]
    ## Endpoints Added or Changed [MANDATORY]
    ## Database Changes [MANDATORY]
    ## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]
    ## How to Verify This Is Working Right Now
    ## What Breaks and How to Fix It
    ## Environment Facts Learned [MANDATORY — constraints/quirks found,
       or "None"; anything permanent also goes to CLAUDE.md]
    ## Ephemeral Outputs Not Yet Saved
    ## Plain English Summary for Matt [MANDATORY]
    ## Decisions Made [MANDATORY — Decision | Reason | Alternatives
       rejected, or "None"; survivors must also land in decisions.md]
    ## Open Items for Next Session [MANDATORY — DONE: <item> closes
       existing items; confirm BACKLOG.md was updated this session]
    ## Open Questions for Matt
    ## SESSION REVIEW [MANDATORY — 1-5 rating + what went wrong]
    ## MATT-NOTE [Optional session rating]
