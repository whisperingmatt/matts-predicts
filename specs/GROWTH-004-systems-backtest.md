# SPEC GROWTH-004: Chunk 5 — Six Complete Systems, Backtested As Written

Repo: matts-predicts
Path: strategies/02-growth/specs/GROWTH-004-systems-backtest.md
Spec version: 1.0 — 2026-09-17
Status: LOCKED for build. Changes require a decisions.md entry.
Reuses: universe, prices, fundamentals, features, regime from GROWTH-001/002/003. GROWTH-003 S9 (clustering) is deferred; this spec takes priority.

## 0. Purpose (cold-start context)

Nine sessions tested whether individual ratios predict winners. They don't, much. But a trading system is an entry rule + exit rule + sizing rule + regime filter, judged on expectancy per trade and compound return with drawdown. No complete system has been run. This spec runs six published systems exactly as their authors specified, on our data, with costs, and scores them on one board. Then the best one gets autopsied (GROWTH-005, later): its own trades split into winners and losers to find the clues.

Do not improve any system. Run it as written. If a rule cannot be implemented from our data, substitute the closest available proxy, record the substitution in decisions.md, and flag it in the report.

## 1. Engine (shared by all systems)

G1. Event-driven monthly or weekly loop as each system specifies, on the GROWTH-001 universe ($5 / $1M floors, point-in-time). Daily prices from stocks (closeadj, volume). Fundamentals ARQ by filing date.
G2. Costs: 0.10% commission per side plus slippage of 0.10% (marketcap ≥ $2B) or 0.25% (< $2B). Applied to every fill.
G3. Fills at next day's open after a signal on the close (no same-bar fills). Stops fill at the stop price or the next open if gapped through, whichever is worse.
G4. Capital $100,000 nominal, no leverage, no shorting, cash earns 0.
G5. Position sizing per system; default equal-weight across the system's slot count, cash held when no qualifying candidate.
G6. Regime filter per system; default none.
G7. Windows: build 2006-01 to 2019-12, holdout 2020-01 to 2025-06. Systems run continuously across both; results reported per window. No parameter changes between windows.
G8. Metrics per system per window: trades, win rate, avg winner %, avg loser %, expectancy % per trade, profit factor, CAGR, max drawdown, worst 12-month return, Sharpe (rf = 0), turnover, avg holding days, per-year return table, vs SPY buy-and-hold over the same window.
G9. Every closed trade is written to trades_<system>.parquet with entry/exit dates and prices, reason for exit, and the full feature row at entry (for GROWTH-005 autopsy).
G10. Deterministic: single-threaded where sums occur, fixed seeds, sorted outputs.

## 2. The six systems

### S-A. O'Neil CANSLIM (How to Make Money in Stocks)
Universe filter at signal: C quarterly EPS YoY ≥ 25% and higher than prior quarter's YoY; A annual EPS growth ≥ 25% each of last 3 fiscal years (use 12 trailing ARQ quarters summed per year); N price within 5% of 52-week high; S shares outstanding not rising over 8 quarters OR buyback (share count falling); L relative strength percentile ≥ 80 (12m return rank in universe); I institutional % rising QoQ (2013+ only; before 2013 skip the I test and flag); M SPY above its 50-day and 200-day.
Entry: close at a new 52-week high with volume ≥ 1.5× 50-day average volume. Buy next open.
Exit: hard stop 8% below entry. Take profit at +20% unless +20% reached within 3 weeks of entry, in which case hold with a trailing exit on a close below the 50-day SMA. Also exit on close below 50-day SMA at any time after week 8.
Slots: 10, equal weight. Signals evaluated weekly (Friday close).

### S-B. Minervini Trend Template + VCP (Trade Like a Stock Market Wizard)
Trend template (all must hold): price > 150-day SMA and > 200-day SMA; 150 > 200; 200-day SMA rising for ≥ 1 month (22 trading days); 50-day SMA > 150 and > 200; price > 50-day; price ≥ 30% above 52-week low; price within 25% of 52-week high; RS percentile ≥ 70.
Entry: VCP breakout — GROWTH-001 H14 pattern (successive contractions, volume dry-up) completed, then a close above the pivot (highest high of the final contraction) on volume ≥ 1.25× 50-day average. Buy next open.
Exit: initial stop 7% below entry. When gain ≥ 2× initial risk (+14%), sell half and move stop to breakeven on the rest. Trailing exit on remainder: close below 50-day SMA, or close below 20-day SMA on above-average volume. Hard maximum stop 10% at all times.
Slots: 10, equal weight. Weekly evaluation.

### S-C. Weinstein Stage 2 (Secrets for Profiting in Bull and Bear Markets)
Weekly bars. 30-week SMA of weekly close.
Entry: weekly close crosses above the 30-week SMA, the SMA has flattened or turned up (30-week SMA now ≥ 4 weeks ago), price breaks above the highest weekly close of the prior 26 weeks (base resistance), weekly volume ≥ 2× 26-week average, and RS vs SPY (26-week relative return) is positive and rising. Buy next Monday open.
Exit: weekly close below the 30-week SMA when the SMA is flat or declining (Stage 3/4 entry). Initial protective stop 10% below entry.
Slots: 10, equal weight. Regime: no new entries when SPY is below its own 30-week SMA.

### S-D. Clenow Stocks on the Move
Ranking: annualized exponential regression slope of ln(close) over the last 90 trading days, multiplied by the regression R². Rank universe descending.
Eligibility: price above 100-day SMA; no single-day move > 15% in the last 90 days; in the top 20% of the ranking.
Regime: new positions only when SPY is above its 200-day SMA. Existing positions are not force-sold on regime change.
Sizing: risk parity — position size such that ATR(20) × shares = 0.1% of portfolio value (target daily risk). Cap any position at 10% of portfolio.
Rebalance: weekly (Wednesday). Sell if the stock leaves the top 20%, closes below its 100-day SMA, or has a > 15% gap. Fill freed cash with the next highest-ranked eligible names. Resize positions every other week.
Clenow's universe is the S&P 500; run it TWICE — once on S&P 500 constituents (sp500 table, point-in-time) as written, once on our full universe as an adaptation, clearly labelled.

### S-E. Gray & Vogel Quantitative Momentum
Universe: largest 40% of our universe by market cap each rebalance (their "investable" cut).
Screen 1: 12-month return skipping the most recent month ("12-2"), top decile.
Screen 2 (frog-in-the-pan): within that decile, rank by the fraction of positive daily returns over the 12-2 window minus fraction of negative days (higher = smoother); keep the top half.
Hold: equal weight. Rebalance quarterly (they use overlapping tranches; run the simple quarterly version and flag it).
Run TWICE: 50 positions as written; 10 positions as a concentration test, clearly labelled.
No stop-loss (as written).

### S-F. Greenblatt Magic Formula (control)
Earnings yield = EBIT / enterprise value; return on capital = EBIT / (net working capital + net fixed assets). Rank each, sum ranks, take the top 30 with marketcap > $50M (raise to our $1M-dollar-volume floor), excluding financials and utilities as he does.
Hold equal weight for 12 months, rebalance annually (stagger: enter one-twelfth of positions each month in the first year, then roll).
No stop-loss (as written).

## 3. Pass criteria (set now, before results)

A system PASSES if, in BOTH build and holdout windows: expectancy per trade > 0 after costs, CAGR > SPY CAGR over the same window, and max drawdown ≤ 1.5 × SPY max drawdown over the same window.
A system is MARGINAL if it passes CAGR in both windows but fails one of the other two.
Report all six regardless. Rank by holdout CAGR / holdout max drawdown.

## 4. Engine sanity check (required before any system result is reported)

Reproduce S-C (Weinstein) on one ticker, AAPL 2010–2019, in the engine, and separately with TradingView's Strategy Tester using the same rules and a matching cost model. Record both trade lists in reports/engine_sanity.md. Entry dates must match within one bar and trade count must match; explain any difference. If it cannot be reconciled, stop and report before running the six.

## 5. Sessions (one task each)

S10: engine (section 1), sanity check (section 4), systems S-A, S-B, S-C. Write reports/systems_part1.md. Wrap, PR.
S11: systems S-D (both universes), S-E (both sizes), S-F. Write reports/systems_scoreboard.md with the full board, per-year tables, and a plain-prose reading of which systems passed, which failed, and on what. Wrap, PR. Chunk 5 ends here; GROWTH-005 (autopsy of the best system's trades) follows.

## 6. Warnings before starting

- Every "as written" rule that needs a proxy from our data is recorded in decisions.md with the original and the substitute. The report lists all substitutions in one table.
- Fundamentals for S-A and S-F use filing dates. A quarter is not visible until filed.
- SPY series: use the funds table (SPY closeadj). SP500 constituents from the sp500 table, point-in-time, for S-D's first run.
- No parameter tuning. If a system takes zero trades in a window, that is the result; report it.
- Run S-A without the I test for 2006–2012 and with it for 2013+; report both segments.
