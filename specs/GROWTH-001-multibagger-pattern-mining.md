# SPEC: Section 2 Growth Strategy — Multibagger Pattern-Mining Study

Repo: matts-predicts
Path: strategies/02-growth/
Spec version: 1.0 — 2026-09-17
Status: LOCKED for build. Changes require a decisions.md entry.

## 0. Read this first (cold-start context)

You have no memory of prior sessions. This is all you need.

Matt is building three stock strategies. This is the middle one: US equities, 12–24 month holds, medium-to-high risk, targeting a 10-stock portfolio where 1–2 positions are expected to return 300%+. Before designing entry/exit rules, we are running a historical study to find which signals actually preceded past 300% two-year moves ("launches") and by how much.

Chat designed the hypotheses. Code runs the data. This spec is the contract between the two.

Do not add hypotheses, change thresholds, or "improve" the method. If something is impossible as written, stop and report exactly what and why. Try once, then stop.

## 1. Repo scaffold (Session 1)

Create at repo root if missing:

* CLAUDE.md — rules for working in this repo
* decisions.md — rulings (seed with section 2 of this spec)
* BACKLOG.md — task list (seed with section 9)
* specs/ — this file goes here
* docs/wrapits/ — session wrap docs, filename WRAPIT_YYYY-MM-DD-HHMM_topic-slug.md

Create under strategies/02-growth/:

* data/raw/ (gitignored), data/processed/ (gitignored)
* src/ingest.py, src/universe.py, src/labels.py, src/features.py, src/regime.py, src/stats.py
* reports/
* README.md — one paragraph, points to this spec

Python 3.11+. Use pandas, numpy, duckdb or parquet for storage, nasdaqdatalink for Sharadar. Pin versions in requirements.txt.

## 2. Locked decisions

D1. Launch = forward 24-month close-to-close return ≥ 300% from a month-end decision date. Also record ≥ 200% and ≥ 500% flags.

D2. All features computed point-in-time using Sharadar filing dates (datekey), never period dates (calendardate). No look-ahead.

D3. Universe floors at decision date: price ≥ $5, trailing 20-day average dollar volume ≥ $1,000,000.

D4. Build window 2006-01 to 2019-12. Holdout 2020-01 to 2026-06. Holdout is not opened until single-signal and combination results on the build window are final and written to reports/.

D5. Every stock-month is tagged with market regime (section 6). All results reported raw and by regime bucket.

D6. Primary data source: Sharadar via Nasdaq Data Link (tables SF1, SEP, DAILY, TICKERS, SF2, SF3). Verify table names against current Sharadar docs before coding; report if they have changed.

D7. H2 (surprise streak) and H3 (estimate revisions) are DEFERRED. No consensus estimate feed in pass one. Do not proxy them.

D8. Minimum 100 launch events per reporting cell. Below that, report "insufficient" — no number.

D9. Combinations capped at three signals.

## 3. Universe rules (Session 2)

Include: US common stocks (Sharadar category "Domestic Common Stock") on NYSE, NASDAQ, NYSEMKT. Exclude: ADRs, SPACs, closed-end funds, REITs, any ticker with fewer than four quarters of reported EPS in the trailing 12 months at decision date. Apply D3 floors monthly. A stock enters and exits the universe month by month; do not filter on whether it survives to the end. Delisted tickers must be present. If the ingested price table contains no delistings, stop — the data is wrong.

Output: data/processed/universe.parquet — one row per (ticker, month_end) that qualifies.

## 4. Launch labeling (Session 2)

For each universe row, compute fwd_24m_return = close(t+24 months) / close(t) − 1, using Sharadar adjusted close (closeadj). If the stock delists before t+24, use the last available adjusted close; treat delist as terminal. Flags: launch_300, launch_200, launch_500. Report base rates: count and percentage of launches per year and overall, build window only.

## 5. Feature definitions (Session 3)

Compute every feature at T-0 and also lagged at T-3, T-6, T-12 months (feature value as it stood that many months earlier). Nulls where data insufficient — never fill.

Fundamentals from SF1, dimension ARQ (as-reported quarterly), joined on datekey ≤ decision date.

### Group A — earnings engine

* H1 eps_accel: EPS growth YoY for last three quarters, q0 > q1 > q2 and q0 ≥ 0.25. Also store raw q0 growth.
* H4 op_leverage: revenue YoY growth rising over last 4 quarters AND operating margin (opinc/revenue) q0 > q4.

### Group B — multiple engine

* H5 peg: pe / (trailing 4-quarter EPS growth × 100). Flags peg < 1.0 and peg < 0.5. Null if EPS ≤ 0 or growth ≤ 0.
* H6 compressed_multiple: pe below own trailing 5-year median AND EPS growth above own 5-year median. Requires 20 quarters of history; else null.
* H7 neglect: marketcap < $2B. Analyst count unavailable in Sharadar — record marketcap only, note the gap.
* H8 fcf_divergence: FCF per share slope over 4 quarters > 0 AND price return over same period between −10% and +10%.

### Group C — recognition and flow

* H9 rel_strength: 6-month and 12-month return skipping most recent month, ranked as percentile within universe that month. Flag top decile.
* H10 sponsorship: from SF3, institutional % of shares outstanding; flag if rising QoQ AND level < 40%.
* H11 insider_cluster: from SF2, count of open-market purchases (transactioncode P) by distinct insiders in trailing 90 days. Flag ≥ 3.
* H12 short_fuel: short interest % of float from DAILY if available, flag > 10%. If field absent, mark H12 unavailable and move on.

### Group D — stage and structure

* H13 stage2: close > 30-week SMA, 30-week SMA rising over 4 weeks, prior 26 weeks range within ±20% (base), volume on crossing week > 1.5× 50-day average. Flag if cross occurred within last 8 weeks.
* H14 vol_contraction: 20-day ATR/price declining over three consecutive 20-day windows AND 20-day average volume declining, followed by a close above the 20-day high. Flag if pattern completed within last 4 weeks.
* H15 near_high: close ≥ 0.85 × 52-week high.

### Group E — AI-era

* H16 sector_flow: sector SPDR (XLK, XLF, XLE, XLV, XLY, XLP, XLI, XLB, XLU, XLRE, XLC) shares outstanding change over 3 months > 0 AND sector weight in S&P 500 below its 10-year mean. Sector weight from GICS sector aggregation of SP500 constituents' marketcap; if constituent history unavailable, use SPDR marketcap ratio as proxy and note it.
* H17 sector_surprise: DEFERRED with H2/H3.
* H18 attention: DEFERRED — no historical source in pass one.

### Group F — filters

* H20 leverage_ok: (debt − cash) / EBITDA < 2, or net cash.
* H21 no_dilution: shares outstanding q0 ≤ q8 × 1.02.

### Control (expected NOT to work — test anyway)

* pe < 15, pb < 1.5, dividend yield > 2%.

Output: data/processed/features.parquet, one row per (ticker, month_end, lag).

## 6. Regime tags (Session 3)

Per month_end: SPX drawdown from prior all-time high (from SEP using SPY closeadj), VIX close (source: CBOE historical CSV, free). Buckets: drawdown 0–10%, 10–20%, 20–30%, >30%; months-since-trough 0–12, 13–24, >24.

## 7. Statistics and reports (Session 4 — build window only)

7.1 Base rate table: launches / universe rows, per year and overall.
7.2 Single-signal lift: for each flag × lag, launch rate when flag true ÷ base rate. Report lift, event count, and 95% CI (Wilson). Apply D8.
7.3 Same, within each regime bucket.
7.4 Combinations: all 2- and 3-signal ANDs among flags with single-signal lift ≥ 1.5 and ≥ 100 events. Rank by lift, then by coverage (what fraction of launches the combo catches).
7.5 Control signals reported identically.
7.6 Write reports/build_window_results.md with tables and a plain-prose reading of what held and what didn't. No recommendations in this session.

Pass/fail criteria, set now, before results:

* Study is VALID if base rate is between 0.5% and 5% overall and delisted tickers appear in the universe. Outside that range, stop and report — something is wrong with universe or labeling.
* A signal PASSES if lift ≥ 2.0 with lower CI ≥ 1.5 at any lag in the build window.
* A signal is CRASH-ONLY if it passes overall but fails in every regime bucket with drawdown < 20%.

## 8. Holdout (Session 5 — only after Session 4 wrap is committed)

Rerun 7.1–7.5 on 2020-01 to 2026-06 for passing signals and top-20 combinations only. A signal CONFIRMS if holdout lift ≥ 1.5 with lower CI ≥ 1.0. Write reports/holdout_results.md. This ends chunk four. Chunk five (scoring model, entry/exit) happens in chat with these two reports as input.

## 9. Sessions (one task each)

S1 Scaffold repo, requirements, Sharadar auth test, verify table names. Wrap.
S2 Ingest, universe, labels, base rate. Wrap.
S3 Features and regime tags. Wrap.
S4 Build-window statistics and report. Wrap.
S5 Holdout report. Wrap.

Each session ends with a WRAPIT in docs/wrapits/ stating what ran, what the numbers were, and what broke. Never report a step as done if it errored.

## 10. Warnings before you start

* Sharadar is paid. Confirm subscription and API key exist before S1; do not attempt workarounds with free data.
* Full SEP history is large. Ingest incrementally and cache to parquet; do not hold raw in memory.
* Point-in-time joins are the most common bug in this kind of study. Write a unit test: for a known ticker and date, assert the feature uses a filing dated on or before that date.
* If any feature's underlying field is missing from Sharadar, mark the hypothesis unavailable in the report. Do not substitute.
