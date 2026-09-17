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

2026-09-17 — Bulk downloads UNBLOCKED: Matt allowed
static-sharadar.nyc3.digitaloceanspaces.com in the matts-predicts
environment's network policy. src/fetch_bulk.py pulled all eight Full
History files from Claude Code on the web the same day. The earlier
entry's options (a) is the one taken.

2026-09-17 — Universe rules mapping (spec section 3 onto Sharadar's
current field values; implemented in src/universe.py):
Category: the spec says "Domestic Common Stock". Sharadar now splits
that into Domestic Common Stock, ... Primary Class, ... Secondary Class.
Included: the plain value and Primary Class. Excluded: Secondary Class,
so one issuer contributes one launch. ADRs, Canadian filers, preferred,
CEF, ETF, ETN, ETD, UNIT are other category values and drop out.
Exchange: NYSE, NASDAQ, NYSEMKT, as the spec lists.
SPACs: Sharadar industry = "Shell Companies" (1,666 domestic common
tickers). REITs: industry starting "REIT" (about 480 tickers). Both are
excluded by industry. Real estate operating companies are not REITs and
stay in.
Limitation: category, exchange, and industry are the current values in
the tickers table; Sharadar keeps no history for them, so a ticker that
changed exchange or business is classified by its last state.
Price floor: closeunadj (the price that traded that day), not the
split-adjusted close. Dollar volume: mean of close*volume over the 20
trading days ending on the decision date's trade (split adjustments
cancel in the product). Fewer than 20 prior trading days disqualifies
the month.
EPS history: at least four distinct fiscal quarters (calendardate) with
non-null eps in fundamentals ARQ, filed on or before the decision date
(fundamentals.date, the spec's datekey), with quarter ends inside the
trailing 16 months. Reason: "four quarters in the trailing 12 months"
cannot be met literally at most month ends because the latest quarter
is not yet filed; 16 months is 12 months of quarter ends plus one
quarter of filing lag (10-K up to 90 days). Alternatives rejected:
literal 12-month window (empties the universe); dimension ART (not what
the spec names; not guaranteed present).
Table codes: the bulk tickers.csv.zip carries legacy codes in its
"table" column (SEP, SF1, SF2, SF3B, SFP) while the paged API returns
modern names (stocks, fundamentals, ...). Code accepts both.

2026-09-17 — Label mechanics (spec section 4; src/labels.py): t is the
universe row's trade date; t+24m is the last trade on or before the
month end 24 calendar months later, found with an ASOF join on the
price table. No trade in that target month means the last available
closeadj is used and delisted_before_t24 is set (delist is terminal).
A target month end after the last price date gives a null return, so
holdout rows near the data edge stay unlabeled rather than guessed.
Base rates are reported for the build window only; holdout rows are
labeled in labels.parquet but nothing about them is printed.

2026-09-17 — History-start limitations from the ingested Full History
files (data/raw/ingest_manifest.json): holdings (SF3) begins
2013-06-30, insiders (SF2) begins 2008-01-02, while the
build window begins 2006-01-31. H10 sponsorship is therefore null for
every decision date before 2013-09 (the first quarter end plus filing
lag) and H11 insider_cluster is null before 2008-04 (90-day trailing
window). Spec section 5 says never fill; S4 reports these features on
the months where they exist and marks the earlier cells "insufficient"
if they fall under D8. stocks, daily, fundamentals, sp500, and funds all
reach back before 2006. Alternatives rejected: shifting the build window
(D4 is locked); proxying either feature (ruled out).

2026-09-17 — S2 result numbers, build window 2006-01 to 2019-12
(reports/s2_base_rates.md): 393,429 universe rows, 6,168 tickers,
2,603 launch_300 rows (0.66%), 7,408 launch_200 (1.88%), 629
launch_500 (0.16%). Validity gate passed (0.5% to 5%). 4,361 of the
7,787 universe tickers are delisted today. Three rows were recomputed
independently with pandas from the price table and matched to 1e-9.

2026-09-17 — S3 feature interpretations (spec section 5 onto Sharadar
fields; implemented in src/features.py). Each item is where the spec
text left a choice; none changes a threshold.
Quarter sequence: ARQ rows per (ticker, calendardate), earliest filing
kept when a quarter is re-filed (10-K repeating a 10-Q, amendments carry
identical figures). Lags are prior quarters in calendardate order and
each use checks the month distance (q4 = 12 months back, q8 = 24), so a
missing quarter yields null rather than a wrong pair.
Point in time: the grid joins the latest quarter with filing date <=
decision date (ASOF); tests/test_point_in_time.py holds AAPL 2019-07-30
versus 2019-07-31 around the 2019-07-31 filing.
Lags T-3/T-6/T-12: the base feature row at last_day(month_end - L
months) for the same ticker; null when the ticker had no trade that
month.
H1: YoY EPS growth null when the base quarter's EPS <= 0.
H4: revenue YoY growth over q0..q3 strictly rising; operating margin
opinc/revenue q0 > q4; null if any revenue used is not positive.
H5: pe is the daily table's pe on the decision date (Damodaran, TTM);
trailing 4-quarter EPS growth = sum(eps q0..q3)/sum(eps q4..q7) - 1;
null if either sum <= 0 or pe <= 0.
H6: daily pe on the decision date below the median of the ticker's own
SF1 quarterly pe (positive values) over q0..q19, AND YoY EPS growth q0
above the median of its own q0..q19 growths; null unless 20 quarters
exist. Both SF1 pe and daily pe are marketcap over TTM earnings.
H7: daily marketcap (USD millions) < 2000 on the decision date.
H8: FCF-per-share slope over q3..q0 by least squares (sign of
3*q0 + q1 - q2 - 3*q3); price return = closeadj at q0's quarter end over
closeadj at q4's quarter end - 1, i.e. the four quarters the slope
spans; flag when slope > 0 and return within [-10%, +10%].
H9: 6-month return = closeadj(m-1)/closeadj(m-7) - 1, 12-month =
closeadj(m-1)/closeadj(m-13) - 1 (skipping the latest month);
percent_rank within the universe rows of that month; top decile =
percentile >= 0.9; two flags (rs6, rs12). Null when the row was not in
the universe that month.
H10: 13F holdings for quarter end Q are treated as public 45 days after
Q (the SEC deadline; Sharadar holdings has no filing date column).
Institutional shares = sum(units)*1000 over securitytype SHR. Sharadar
sharesbas is restated to today's split basis while holdings units are
as reported, so shares outstanding at Q = sharesbas(ARQ, calendardate
Q, filed <= decision date) * close/closeunadj at Q. Verified on AAPL
2019-12-31: 60.9% institutional after rescaling, 15% without. Flag =
level < 40% and level > prior quarter's level.
H11: distinct ownername with transactioncode P and securityadcode NA
(non-derivative acquisition) whose filing date falls in the trailing 90
days; flag >= 3; null before 2008-04-01 (data starts 2008-01-02).
H13: weekly bars from daily rows (week = Monday-start calendar week,
close = last trade, volume = sum). Cross = weekly close above the
30-week SMA after the prior week closed at or below it; SMA rising =
SMA30 > SMA30 four weeks earlier; base = over the 26 weeks before the
cross week, (max - min)/midpoint of weekly closes <= 0.4 (i.e. within
+/-20%); volume = the cross week's average daily volume > 1.5x the
average daily volume of the prior 10 trading weeks (about 50 days).
Flag if such a cross week ended within 56 days before the decision
trade date; null with fewer than 34 weeks of history.
H14: per trading day, ATR20/close and 20-day average volume; a
completed pattern is a close above the prior 20-day high on a day where
both ratios were lower at day -1 than at day -21, and lower at -21 than
at -41. Flag if a completion falls within 28 days before the decision
trade date; null with fewer than 62 trading days of history.
H15: close on the decision trade date >= 0.85 x the highest daily high
over the trailing 252 trading days; null with fewer than 252.
H16: UNAVAILABLE. The funds table (SFP) carries OHLCV only; no Sharadar
table has ETF shares outstanding, so the "shares outstanding change"
leg cannot be computed. The S&P 500 sector-weight leg would be
computable from sp500 constituents, daily marketcap, and tickers.sector
but is not built alone (spec section 10: do not substitute).
H20: EBITDA is the trailing four ARQ quarters; net cash (debt - cash <=
0) is TRUE outright; positive net debt with EBITDA <= 0 is FALSE.
H21: sharesbas q0 <= sharesbas q8 x 1.02; Sharadar sharesbas is split
adjusted (AAPL 2013 shows 25.0bn, today's basis) so no adjustment.
Control: daily pe < 15 and pb < 1.5 with non-positive values null; SF1
divyield (a fraction, 0.023 = 2.3%) > 0.02.
Unavailable and deferred hypotheses (H2, H3, H12, H16, H17, H18) are
all-null boolean columns in features.parquet so S4 reports them as
unavailable rather than silently omitting them.

2026-09-17 — Regime tags (spec section 6; src/regime.py): SPY month-end
closeadj from the funds table; all-time high over month-end closes; a
drawdown episode runs from one all-time high to the next and its trough
is the lowest month-end close inside it; months_since_trough counts
from the current episode's trough while in drawdown, else from the
trough of the episode just closed. Consequence: the 2011 dip sits
inside the 2007-2013 episode (SPY's total-return series did not regain
its 2007 high until 2012), so months-since-trough there is 31, not the
2011 low. VIX close from the CBOE daily CSV, last close on or before
the month end, fetched to data/raw/VIX_History.csv. Buckets as the spec
lists; no VIX bucket is specified, so the raw close is stored.

2026-09-17 — S4 statistics definitions (spec section 7 plus Matt's S4
brief; implemented in src/stats.py):
Lift among non-null rows: for a flag at a lag, the cell's rows are the
build-window universe rows where the flag is non-null; base = launches
over those rows; rate = launches over flag-TRUE rows; lift = rate/base.
Coverage (non-null rows over all rows) is reported beside every lift.
Reason: a null is "data insufficient", not "signal absent"; comparing
against a base that includes nulls would mix the two.
Confidence interval: 95% Wilson on rate with n = flag-TRUE rows,
divided by base, which is treated as fixed because it rests on the
whole non-null set. Alternatives rejected: a ratio CI (adds width the
base's sample size does not justify); a normal approximation (poor at
the low rates here).
D8 "events" = launch events: launches among flag-TRUE rows for a lift
cell, launches inside the bucket for a base-rate cell. Both counts are
printed so the reader can see how far a cell falls short.
PASS/CRASH-ONLY as section 7 states, on launch_300. CRASH-ONLY is
judged across all lags: passes overall at some lag, but no (lag,
drawdown bucket 0-10 or 10-20) cell passes.
Combinations (7.4): formed within one lag from the flags that clear
lift >= 1.5 and >= 100 events at that lag, so every flag in a
combination is as of the same decision date. Controls are eligible on
the same terms. Coverage of a combination ("catch") = launches caught
over all launches at that lag; the non-null share is shown beside it.
launch_200 and launch_500 rates are shown for the same combinations.
Expected winners (Matt's addition): for the top ten D8-passing
combinations, per regime bucket, 10 x bucket base rate x the
combination's overall lift. The bucket base rate needs >= 100 launches
(D8). This assumes lift does not vary by regime; the 7.3 tables are the
check on that assumption.
Sector x entry-year table (Matt's addition): launch_300 rate per
(sector, year) cell with D8 per cell, plus the row and column sums of
the same cells so the reader sees where D8 is met at the margin. Rows
with no sector in the tickers table are "Unknown" (61 universe rows).
Regime bucket of a row is the decision month's bucket (month_end), at
every lag; the lagged feature value is combined with the regime the
decision is made in.
The report's plain-prose reading lives in reports/build_window_reading.md
and is inserted verbatim when the report is regenerated, so numbers can
be regenerated without retyping the prose. It contains no
recommendations (7.6).

2026-09-17 — S5 holdout rulings (Matt's S5 brief, superseding section
8's wording where they differ; implemented in src/holdout.py):
Window: 2020-01 to 2024-06, not D4's 2026-06. A 24-month return is not
observable after 2024-08 decision dates with prices to 2026-09-16, so
2024-06 is the last month end whose full cohort is labeled; D4's end
date stands for the universe and features, and the holdout statistics
stop where the labels do.
Tested: the three build-window PASS flags (h9_rs6_top_decile,
h9_rs12_top_decile, h10_sponsorship carried with its calm-only caveat),
the two-horizon strength combination at every lag, the fifth
D8-clearing build combination (h5_peg_lt_05 AND ctl_pe_lt_15 at lag 3;
section 8's "top-20 combinations" reduces to these five), and the four
backward build-window signals as inverted flags: NOT h15_near_high,
NOT h21_no_dilution, NOT h8_fcf_divergence, NOT ctl_divyield_gt_2
(null stays null). Inverting a backward signal is a test of whether
the reverse description survives, not a new hypothesis; the spec's
hypotheses stay as written and the inverted flags are labeled as
inverted everywhere.
launch_200 reported beside launch_300 in every table. Sector table
pooled across years. Regime buckets as S4. CONFIRM = holdout lift
>= 1.5 with lower CI >= 1.0 on a D8-sufficient cell (section 8).
Build-window numbers for the tested flags are recomputed in holdout.py
with the same code for the comparison columns; the S4 report is not
regenerated and its numbers are unchanged.
This session ends chunk four. Chunk five (scoring model, entry, exit)
happens in chat with reports/build_window_results.md and
reports/holdout_results.md as input.

## Ruled out (do not re-suggest without a specific new reason)

- Free data substitutes for Sharadar (spec section 10).
- Proxies for H2, H3, H17, H18 (D7, spec section 5).
- Filling nulls in features (spec section 5).
- Any short-interest proxy for H12 (spec section 5; no Sharadar field).
- Nasdaq Data Link as the data route (no subscription there; D6 superseded).
