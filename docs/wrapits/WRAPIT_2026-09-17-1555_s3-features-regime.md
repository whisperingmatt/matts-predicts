project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S3: point-in-time test, features at four lags, regime tags, coverage table
status: COMPLETE — features.parquet and regime.parquet built and verified; six hypotheses recorded unavailable or deferred. S4 not started.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1.5 hours

---

## What Was Built or Changed

The section 10 point-in-time test came first. tests/test_point_in_time.py runs the same function the pipeline runs on a two-row grid for AAPL around the 2019-07-31 filing of the quarter ending 2019-06-30: on 2019-07-30 the feature must see the 2019-03-31 quarter, on 2019-07-31 the new one, and no quarter used (q0 through q8) may be filed after the decision date. Four tests, all passing before features.py ran.

src/features.py implements section 5. A base grid holds every (ticker, month_end) for the 7,787 universe tickers from 2003 on, each with the ticker's last trade in the month. Fundamentals come from ARQ rows, one per quarter with the earliest filing kept, with all quarter-sequence math done per filing and then joined to the grid point in time on filing date. Price features come from 27,050,864 daily rows (H14 breakouts, H15 52-week high) and weekly bars derived from them (H13). Valuation is the daily table's marketcap, pe, pb on the decision date. H10 uses 13F holdings treated as public 45 days after quarter end, with shares outstanding rescaled to the reporting basis because Sharadar restates sharesbas for splits and holdings units are as reported. H11 counts distinct insiders filing open-market purchases in the trailing 90 days. The lag-L row of each universe (ticker, month_end) is the base row at month_end minus L months. Unavailable and deferred hypotheses are all-null boolean columns so S4 reports them rather than losing them.

H16 sector_flow is newly marked UNAVAILABLE: the funds table carries OHLCV only, and no Sharadar table has ETF shares outstanding, so the SPDR shares-outstanding leg cannot be computed. The sector-weight leg would be computable but is not built alone (spec section 10: do not substitute).

src/regime.py implements section 6 from SPY month-end closeadj in the funds table and the CBOE VIX daily CSV. Drawdown episodes run from one all-time high to the next; months since trough counts from the current episode's trough, or the last closed one when at a high.

Every interpretation the spec text left open is in decisions.md under "S3 feature interpretations" and "Regime tags".

## Files Touched [MANDATORY]

- strategies/02-growth/tests/test_point_in_time.py (rewritten from the skipped placeholder; 4 tests)
- strategies/02-growth/src/features.py (rewritten from stub)
- strategies/02-growth/src/regime.py (rewritten from stub)
- strategies/02-growth/reports/s3_feature_coverage.md (new; committed)
- decisions.md (two rulings: S3 feature interpretations; regime tags)
- BACKLOG.md (S3 DONE verified; S4 startup note)
- docs/wrapits/WRAPIT_2026-09-17-1555_s3-features-regime.md (this file)
- data/processed/features.parquet, regime.parquet, data/raw/VIX_History.csv (gitignored, regenerable)

## Environment Variables [MANDATORY]

None new. NASDAQ_DATA_LINK_API_KEY was not needed this session (data already on disk from S2 in the same container).

## Services and Integrations Touched [MANDATORY]

cdn.cboe.com — one GET of VIX_History.csv (472,717 bytes), reachable through the proxy. Sharadar not contacted this session.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None. New local parquet files as listed; not committed.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

1. `python -m pytest -q tests/test_point_in_time.py` before any feature run: `4 passed in 5.08s`. Rerun at session end with the full suite: `4 passed`.

2. `python -m src.regime`: `regime.parquet: 342 month ends 1998-01-31..2026-06-30`; drawdown buckets 0-10: 224, 10-20: 53, 20-30: 37, >30: 28; deepest drawdown −50.8% at 2009-02-28; VIX populated 342 of 342, max 59.9 at 2008-10-31; `RESULT: PASS — every month tagged`, exit 0. Spot rows: 2008-10-31 drawdown −36.1% bucket >30, VIX 59.89; 2009-03-31 trough date 2009-02-28, 1 month since trough; 2020-03-31 −19.4% bucket 10-20, VIX 53.54.

3. `python -m src.features` (final run, grid from 2003): daily_px 27,050,864 rows; h14_days 180,939 completed breakouts; h13_weeks 15,420 qualifying crosses; `features.parquet: 2,353,204 rows (7,787 tickers x 246 month ends x 4 lags)`; `rows whose fundamentals were filed after their as-of date: 0`; `RESULT: PASS — features written, point-in-time clean`, exit 0, 37 seconds. An earlier run failed at the coverage report because the two H5 flag columns were missing from the assembly; fixed and rerun. A second rerun moved the grid start from 2005 to 2003 because 2006 rows at lag 12 lacked the 13-month lookback for H8 and H9; 2006 H8 coverage went from 64.5% to 97.4% and 12-month RS from 90.7% to 98.8%.

4. Lag consistency over the whole table: for L in 3, 6, 12, every lag-L row was compared with the lag-0 row of the same ticker at month_end − L on six columns (h1, rs6_pct, h13, pe, h10, fund_filed). Comparable rows 545,191 / 523,015 / 487,394; mismatches 0 / 0 / 0.

5. Hand recomputation with pandas from the raw parquet, AAPL 2019-12-31 at lag 0: H9 rs6 0.5369 and rs12 0.5191 matched to 1e-9 (percentiles 0.934 and 0.888); H15 ratio 0.9989, flag True, matched; H1 latest quarter 2019-09-30 filed 2019-10-31, g0 0.0411, g1 −0.0678, g2 −0.1014, flag False, all components matched (the script's own boolean printed False only because it compared a pandas timestamp with a date). H10 AAPL 2020-03-31: 60.9% institutional, prior quarter 60.4%, flag False (level above 40%); without the split-basis rescale the figure is 15%, which is wrong.

6. Coverage (reports/s3_feature_coverage.md), lag 0, build window, non-null percent: h1 64.0, h4 92.5, h5 43.5, h6 63.0, h7 99.7, h8 97.9, h9 rs6 99.9 and rs12 99.0, h10 43.3 (95–96 from 2014), h11 82.4 (100 from 2009), h13 99.9, h14 100.0, h15 99.3, h20 99.7, h21 94.4, controls 80.0 / 96.6 / 100.0. At lag 12 the price-history features fall to 80–95 because tickers that had no trade a year earlier get nulls. Unavailable columns are 0.0 in every cell.

State: S3 BUILT and VERIFIED.

## How to Verify This Is Working Right Now

Warning first: a fresh cloud session has no data; steps 2 to 5 take about ten minutes. The key must be in the environment.

1. New session, branch claude/nice-dijkstra-801d68 (or main once merged): `cd strategies/02-growth`
2. `python -m src.fetch_bulk && python -m src.ingest`
3. `python -m src.universe && python -m src.labels`
4. `python -m pytest -q` — expect `4 passed`.
5. `python -m src.regime` — expect `RESULT: PASS — every month tagged`.
6. `python -m src.features` — expect `2,353,204 rows`, `filed after their as-of date: 0`, `RESULT: PASS`.

## What Breaks and How to Fix It

- `RESULT: FAIL — look-ahead rows present`: the ASOF join or the arq dedupe changed. Do not proceed to S4; the point-in-time test should also fail; fix the join.
- cdn.cboe.com unreachable: regime.py stops at the VIX fetch. Copy VIX_History.csv into data/raw/ by hand; the script uses it when present.
- Out of memory in build_price_features: 27 million daily rows with window functions; memory_limit is 10 GB with a temp directory under data/processed. Lower the limit rather than shrinking the windows.
- Coverage collapses for a fundamentals flag: check that fundamentals.parquet has dimension ARQ and that arq dedupe still finds calendardate.

## Environment Facts Learned [MANDATORY]

- funds (SFP) is OHLCV only; no Sharadar table carries ETF shares outstanding. H16 is unavailable. decisions.md.
- Sharadar sharesbas is restated to today's split basis; holdings units and SF1 prices are handled differently (holdings as reported). Any ratio of the two needs the close/closeunadj rescale. decisions.md.
- ARQ has 23,665 (ticker, calendardate) pairs with more than one row: re-filings on later dates with identical figures. decisions.md.
- SF1 pe is negative when TTM earnings are negative; daily pe likewise (34.7% of 2015 rows). Treated as null for the pe-based flags. decisions.md.
- 13F-derived institutional percent exceeds 100 for about a tenth of universe rows after 2015 (p90 1.005, p99 1.16, 162 rows above 1.5): duplicate reporting by affiliated filers and lent shares. It cannot set the H10 flag, which needs under 40%. This wrap; S4 should note it beside H10.
- cdn.cboe.com is allowed by the egress policy. This wrap.
- The whole feature build runs in 37 seconds on this machine; the daily-row windows dominate.

## Ephemeral Outputs Not Yet Saved

None. Every number here is in this wrap, decisions.md, or reports/s3_feature_coverage.md; parquet is regenerable.

## Plain English Summary for Matt

All nineteen computable signals now exist for every stock-month in the universe, each also as it looked three, six, and twelve months earlier. The point-in-time guard you asked for in the spec was written first and passes: no feature anywhere uses a filing that was not yet public. I checked the lagged copies against the originals across the whole table and recomputed four signals by hand for Apple; everything matched. Two signals cannot be built from Sharadar and are recorded as unavailable rather than faked: short interest (known since S1) and the sector-fund money-flow signal, because Sharadar has no fund shares-outstanding data. Coverage is high for price-based signals and lower for the earnings-growth ones, which need positive earnings a year earlier to define growth; that is the data, not a bug. The regime tags are done too: the 2009 bottom, the 2020 crash, and the 2022 bear all land where they should.

## Decisions Made [MANDATORY]

| Decision | Reason | Alternatives rejected |
| --- | --- | --- |
| ARQ quarter sequence keeps the earliest filing per quarter | Re-filings repeat figures; earliest is when public | Latest filing (leaks amended figures backward) |
| Lags check month distance (q4 = 12 months back) | A missing quarter must give null, not a wrong pair | Positional lags only |
| H5, H6, control use daily pe/pb on the decision date; H6 median uses SF1 quarterly pe | Point-in-time price; both are TTM definitions | SF1 pe for the current value |
| H8 return over the four quarters the slope spans | "Same period" | Trailing 12 months to decision date |
| H9 two flags, percentile within the month's universe rows | Spec names both horizons | One combined flag |
| H10 13F public 45 days after quarter end; shares rescaled to reporting basis | No filing date in holdings; sharesbas is split-restated | Using holdings.date as public date; unscaled shares (gives 15% for AAPL) |
| H11 codes P and NA; null before 2008-04 | Open-market common purchases; 90-day window needs data | Including derivative acquisitions |
| H13 weekly bars Monday-start; 50-day volume as prior 10 weeks; base ±20% as range/midpoint ≤ 0.4 | Spec is weekly; approximations stated | Daily-based stage-2 |
| H14 windows at days −1/−21/−41; completion within 28 days | Three consecutive 20-day windows | Rolling minima |
| H16 UNAVAILABLE | No ETF shares outstanding in Sharadar | Sector-weight leg alone; external ETF data |
| H20 EBITDA = trailing four ARQ quarters | ARQ is the mandated dimension | Quarterly EBITDA (wrong scale) |
| Regime episodes from ATH to ATH; trough = lowest close inside | Deterministic, matches the buckets | Local-minimum detection |
| Unavailable hypotheses as all-null columns | S4 reports them as unavailable | Omitting them |

All in decisions.md.

## Open Items for Next Session [MANDATORY]

- DONE: S3 features and regime tags; point-in-time test written first.
- OPEN: S4 build-window statistics per section 7 (BACKLOG). Base rate table, single-signal lift with Wilson CI and D8, by regime, combinations, controls, reports/build_window_results.md. No recommendations.
- OPEN: S4 should state beside H10 that institutional percent exceeds 100 for about a tenth of rows.
- OPEN: rename the environment variable to SHARADAR_API_KEY (carried).
- BACKLOG.md was updated this session: S3 DONE (verified), S4 startup and join notes.

## Open Questions for Matt

1. H16 is unavailable from Sharadar. The spec allows a free external source for VIX only. If you want H16, it needs a ruling on an ETF shares-outstanding source; otherwise it stays unavailable through S5.
2. H9 produces two flags (6- and 12-month). If you meant a single flag, say which horizon, or whether both must be top decile.
3. The H13 base condition reads "prior 26 weeks range within ±20%"; I implemented range over midpoint ≤ 40%. If you meant something else (for example every weekly close within ±20% of the cross price), it is one expression.

## SESSION REVIEW [MANDATORY]

4/5. Everything in scope ran and was verified three ways, and the test came first as the spec demands. What went wrong: two reruns were needed, one for the missing H5 flag columns (caught by the coverage report), one for the grid start date (caught by reading the 2006 coverage row). Both were found by checks, not by luck, and each rerun cost under a minute.

## MATT-NOTE

(for Matt)
