project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S10 (GROWTH-004): shared backtest engine, section 4 sanity check (engine leg), systems S-A CANSLIM, S-B Minervini, S-C Weinstein
status: IN PROGRESS — engine built and verified on fills; three systems run and reported PROVISIONAL; the TradingView leg of the sanity check is Matt's and no verdict stands until it reconciles.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~3 hours

---

## What Was Built or Changed

specs/GROWTH-004-systems-backtest.md placed. src/engine.py is new: data prep to bars.parquet (22M daily rows for every ticker ever in the universe from 2003, adjusted and split-only OHLC, SMAs, 52-week extremes, ATR, the H14 pattern day, daily market cap, point-in-time universe membership), weekly and weekly_raw parquet (30-week SMA, prior 26-week high close, 26-week average volume, 26-week relative return against SPY), SPY daily and weekly; an event-driven daily simulator with next-open fills, intraday stops and limits with the gap rule, the G2 cost model, equal-weight sizing over slots, delisting handling, continuous windows; window metrics per G8; trades with the features.parquet lag-0 row at entry per G9. src/systems_part1.py is new: signal tables in duckdb (relative-strength percent ranks on every week end, CANSLIM fundamentals by filing date, S-B trend template plus H14 breakout, S-C weekly Stage 2 conditions), the three system classes, the section 4 sanity run on AAPL with a supplementary ticker, the Pine script, and both reports.

Three fills were checked by hand against the bars and match to the cent. Two consecutive runs give identical checksums for all sixteen outputs.

## Files Touched [MANDATORY]

- specs/GROWTH-004-systems-backtest.md (new, from Matt's upload)
- strategies/02-growth/src/engine.py, src/systems_part1.py (new)
- strategies/02-growth/tradingview/weinstein_stage2_aapl.pine (new)
- strategies/02-growth/reports/engine_sanity.md, systems_part1.md, systems_part1_reading.md (new)
- strategies/02-growth/reports/s10_metrics.csv, s10_per_year.csv, s10_substitutions.csv, s10_trades_S-A_canslim.csv, s10_trades_S-B_minervini.csv, s10_trades_S-C_weinstein.csv, s10_equity_*.csv, s10_sanity_aapl_weekly_stop.csv, s10_sanity_aapl_daily_stop.csv, s10_sanity_aapl_crossovers.csv, s10_sanity_ACN_weekly_stop.csv (new)
- decisions.md ("Chunk 5" section), BACKLOG.md (Chunk 5: S10, S11), CLAUDE.md (price adjustment facts, TradingView, data prep)
- docs/wrapits/WRAPIT_2026-09-17-2349_s10-engine-systems-part1.md (this file)
- data/processed/bars.parquet, weekly.parquet, weekly_raw.parquet, spy.parquet, spy_weekly.parquet, trades_S-A_canslim.parquet, trades_S-B_minervini.parquet, trades_S-C_weinstein.parquet (gitignored, regenerable)

## Environment Variables [MANDATORY]

None used (no data was fetched; the S2 raw parquet files were still on disk in this container).

## Services and Integrations Touched [MANDATORY]

GitHub for the PR. No Sharadar calls. TradingView not reachable from here.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

- `python -c "from src.engine import build_data; ..."` → bars 22M rows, weekly, weekly_raw, spy_daily 7,221, spy_weekly 1,499 rows; build_data done in 263s.
- `python -m src.systems_part1 --no-build` → signals rs 2,529,579 / sig_a 95 / sig_b 5,958 / sig_c 743 / sig_c_raw 760; sanity AAPL signals 0, trades 0 / 0, ACN trades 1 / 1; S-A 74 trades, build CAGR 0.8% maxDD −6.2%, holdout −0.7% / −8.4%, FAIL; S-B 1,717 trades, −0.4% / −34.0%, 1.6% / −35.8%, FAIL; S-C 336 trades, 3.9% / −38.4%, 5.6% / −33.8%, FAIL; RESULT: PASS (provisional); 34 s.
- Hand check of three fills against bars.parquet: ARW (S-B) entry 2006-02-27 at open 35.49 x 1.001 = 35.5255, stop 33.04 gapped on 2006-03-13 (open 32.89) filled 32.857; DECK (S-A) entry 9.7598, limit 11.7117 reached 2010-11-24 with open 11.75 above it, filled 11.738 on bar 17; MZTI (S-C) Monday open 24.686 x 1.0025 = 24.748, Stage 3 exit at the next open 25.253 x 0.9975. All match the trade rows.
- Cash never negative in any run (min cash 0 for S-B and S-C when fully invested, 40,418 for S-A).
- Reproducibility: md5 of ten s10 CSVs, both reports and the Pine script identical across two consecutive runs (16 of 16).
- `python -m pytest -q tests` → 4 passed.
- Section 4 TradingView leg: NOT RUN (needs Matt).

## How to Verify This Is Working Right Now

1. In the container: `cd strategies/02-growth && python -m src.systems_part1 --no-build` (34 s when bars.parquet exists; without it, drop the flag and allow 5 minutes).
2. Confirm the scoreboard in reports/systems_part1.md reads S-C 3.9% / 5.6%, S-B −0.4% / 1.6%, S-A 0.8% / −0.7%.
3. Matt: run the Pine script per reports/engine_sanity.md on NASDAQ:AAPL weekly (expect zero trades and the crossover-week values), then NYSE:ACN (expect one trade, entry 2016-10-03, exit 2017-01-23), and fill the reconciliation table.

## What Breaks and How to Fix It

If TradingView shows trades on AAPL, compare its volume multiple on 2014-04-25 and 2018-05-04 (engine 1.30x and 1.57x) and its SMA values in the crossover table; a data difference there is the first suspect, a rule difference the second. If the ACN entry date differs by one bar, check whether TradingView's weekly bar ended on a holiday-shortened week. If bars.parquet is missing, run without --no-build. If memory fails on the bars load (about 1.5 GB), raise LOAD_START in systems_part1.py; indicators are computed in SQL over full history so the loop needs only the trading window plus a year.

## Environment Facts Learned [MANDATORY — constraints/quirks found, or "None"; anything permanent also goes to CLAUDE.md]

- Sharadar open/high/low/close are split-adjusted, closeadj adds dividends, closeunadj is raw; TradingView's default matches close. Added to CLAUDE.md.
- TradingView cannot be run from this environment. Added to CLAUDE.md.
- duckdb fetchnumpy returns masked arrays for nullable columns; np.ma.filled is needed before arithmetic. Handled in src/engine.py.
- build_data takes about 4.5 minutes single-threaded and writes 2.7 GB. Added to CLAUDE.md.

## Ephemeral Outputs Not Yet Saved

None. The trades parquet files carry the feature rows and are regenerable in 40 seconds.

## Plain English Summary for Matt [MANDATORY]

The engine works and I checked three of its fills by hand against the price bars; they match to the cent, including a stop that gapped and filled at the open. The one thing I cannot do from here is the TradingView half of the sanity check, so everything below is provisional until you run the Pine script (five numbered steps in reports/engine_sanity.md). AAPL turns out to take no Weinstein trade at all in 2010 to 2019 under the rules as written, because no crossover week ever reaches twice the 26-week volume, so on AAPL the check is that TradingView also shows zero and that its indicator values on the fourteen crossover weeks agree with the table; I added ACN, which takes one trade, so a fill and an exit get compared too. On the three systems: all fail. Weinstein is the best and compounds at 4% to 6% a year against SPY's 9% to 14% with drawdowns near 35%. Minervini trades 1,700 times, gets stopped out 46% of the time, and ends flat after costs. CANSLIM finds 95 signals in twenty years and sits in cash. One engine bug was caught before any number was read: tickers that got delisted while held were never closed and slowly jammed every slot; the fix closes them at their last price.

## Decisions Made [MANDATORY — Decision | Reason | Alternatives rejected, or "None"; survivors must also land in decisions.md]

- Run S-A, S-B, S-C and report PROVISIONAL rather than stop at the sanity check | the TradingView leg needs Matt; the engine leg is done and fills were hand-checked | stopping with the engine only.
- Sanity check on split-adjusted raw prices, dividends off | TradingView's default series | closeadj (would not match).
- Supplementary sanity ticker ACN | AAPL takes zero trades as written | none (zero-trade check only).
- Expectancy for the pass test per dollar deployed | partial sales are separate rows and inflate the mean row return | mean of row returns (shown beside it).
- Delisted-while-held positions closed at the last close | otherwise dead tickers jam slots | leaving them (the bug).
- Entries carried up to five trading days when the next bar is missing | halts and ticker gaps | dropping them.
- Every proxy in the substitution table (26 rows) | spec section 6 | none.
All in decisions.md "Chunk 5".

## Open Items for Next Session [MANDATORY — DONE: <item> closes existing items; confirm BACKLOG.md was updated this session]

- DONE: engine (section 1), engine leg of section 4, S-A, S-B, S-C, both reports.
- OPEN: TradingView leg of section 4 (Matt), then the reconciliation table in reports/engine_sanity.md; if it fails, the engine is corrected before S11.
- S11 (S-D, S-E, S-F, scoreboard) waits for Matt's brief and the reconciliation.
- Carried: rename the environment variable to SHARADAR_API_KEY.
- BACKLOG.md updated this session (Chunk 5 added).

## Open Questions for Matt

- Do you accept per-dollar expectancy as the pass-test definition, or should the plain mean of row returns decide (S-B would then pass the expectancy test in both windows while its equity curve is flat)?
- If the AAPL zero-trade result reconciles but you want a fill-level check inside the spec's own terms, which second ticker should be named in a decisions.md entry?

## SESSION REVIEW [MANDATORY — 1-5 rating + what went wrong]

3. The delisting bug produced a first set of results that were wrong (two systems flat in the holdout); it was caught from the trade counts against the signal counts before anything was written, but a first-pass engine should have handled it. The reserved word "pivot" cost one run, an indentation slip another. The TradingView leg could not be done here, so the session ends IN PROGRESS by design of the spec.

## MATT-NOTE [Optional session rating]

