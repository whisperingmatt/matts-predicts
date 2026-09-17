# Engine sanity check — GROWTH-004 section 4 (S-C Weinstein on AAPL, 2010-01 to 2019-12)

Status: ENGINE LEG COMPLETE, TRADINGVIEW LEG PENDING. The TradingView Strategy Tester cannot be run from
Claude Code on the web (it needs Matt's TradingView login in a browser). The engine trade list, the Pine
script, and the exact settings are below; the reconciliation section at the end is to be filled after the
TradingView run. Until it is, every result in reports/systems_part1.md is PROVISIONAL.

## Engine run

Split-adjusted raw prices (Sharadar open, high, low, close, the same basis as TradingView's default,
dividends unadjusted), weekly bars Monday to Friday, one slot, $100,000, 100% of equity per trade, costs
0.10% commission + 0.10% slippage per side (AAPL is above $2B throughout). Entry on the week's close when
the weekly close crosses above the 30-week SMA, the SMA is at or above its value four weeks earlier, the
close is above the highest close of the prior 26 weeks, weekly volume is at least twice the 26-week
average (current week included), the 26-week relative return against SPY is positive and above the prior
week's, and SPY's weekly close is above its own 30-week SMA. Fill at the next Monday open. Exit at the
next open after a weekly close below the 30-week SMA with the SMA at or below its value four weeks
earlier; protective stop 10% below the fill.

Entry signals on AAPL in the window (position or not): 0.

### Crossover weeks and why they did or did not enter

Every week in which AAPL's weekly close crossed above its 30-week SMA, with each entry condition. This is
the table to compare against TradingView bar by bar when the trade lists are empty: the SMA, the prior
26-week high close, the volume multiple of the 26-week average, the 26-week relative return against SPY.

| week end | close | SMA30 | SMA30 4w ago | 26w high close | vol / 26w avg | RS26 | RS26 prev | SPY > 30w | entry |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2010-09-03 | 9.24 | 8.73 | 8.48 | 9.79 | 0.76 | 0.218 | 0.224 | False | False |
| 2011-07-01 | 12.26 | 12.09 | 12.01 | 12.86 | 0.79 | -0.001 | -0.001 | True | False |
| 2011-12-02 | 13.92 | 13.23 | 13.06 | 15.07 | 0.71 | 0.185 | 0.237 | True | False |
| 2013-08-02 | 16.52 | 15.78 | 16.15 | 16.96 | 0.68 | -0.098 | -0.109 | True | False |
| 2014-02-07 | 18.56 | 18.15 | 17.61 | 20.00 | 0.99 | 0.078 | 0.038 | True | False |
| 2014-04-25 | 20.43 | 18.96 | 18.68 | 20.00 | 1.30 | 0.027 | -0.035 | True | False |
| 2015-07-17 | 32.41 | 30.99 | 30.57 | 33.14 | 0.78 | 0.161 | 0.083 | True | False |
| 2016-04-01 | 27.50 | 26.98 | 27.15 | 30.27 | 0.70 | -0.061 | -0.125 | True | False |
| 2016-07-29 | 26.05 | 24.81 | 25.09 | 27.50 | 1.39 | -0.045 | -0.147 | True | False |
| 2018-02-16 | 43.11 | 41.19 | 40.58 | 44.62 | 1.51 | -0.027 | -0.073 | True | False |
| 2018-04-06 | 42.10 | 42.09 | 41.76 | 45.00 | 1.07 | 0.062 | 0.039 | False | False |
| 2018-05-04 | 45.96 | 42.63 | 42.09 | 45.00 | 1.57 | 0.035 | -0.038 | False | False |
| 2019-03-22 | 47.76 | 46.80 | 47.83 | 56.44 | 1.04 | -0.082 | -0.140 | True | False |
| 2019-06-07 | 47.54 | 44.52 | 45.47 | 52.94 | 0.98 | 0.034 | -0.018 | True | False |

### Trade list A — stop evaluated on weekly bars (TradingView weekly-chart convention: the stop fills at the
stop price when the week's low crosses it, or at the week's open when the week opens below it)

| entry | entry px | exit | exit px | reason | return | days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |

### Trade list B — stop evaluated daily (the production engine, G3: the stop fills at the stop price or the
day's open if gapped through)

| entry | entry px | exit | exit px | reason | return | days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |

## Supplementary ticker — ACN (fills get tested where AAPL takes no trade)

Same rules, same window, same settings; in TradingView change the symbol to NYSE:ACN. Not part of
the spec's pass criterion, which names AAPL; reported so a fill, a stop and a Stage 3 exit can be compared.

Trade list A (weekly-bar stop):

| entry | entry px | exit | exit px | reason | return | days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2016-10-03 | 121.71 | 2017-01-23 | 114.67 | stage3_close_below_sma30 | -5.98% | 112 |

Trade list B (daily stop, production engine):

| entry | entry px | exit | exit px | reason | return | days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2016-10-03 | 121.71 | 2017-01-23 | 114.67 | stage3_close_below_sma30 | -5.98% | 112 |

Crossover weeks:

| week end | close | SMA30 | SMA30 4w ago | 26w high close | vol / 26w avg | RS26 | RS26 prev | SPY > 30w | entry |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2010-09-17 | 40.56 | 40.07 | 40.32 | 44.67 | 0.80 | -0.006 | -0.045 | True | False |
| 2011-10-07 | 55.92 | 55.41 | 55.28 | 63.43 | 0.99 | 0.165 | 0.130 | False | False |
| 2011-12-02 | 58.38 | 56.23 | 56.15 | 63.43 | 0.47 | 0.092 | 0.083 | True | False |
| 2012-01-27 | 56.42 | 55.67 | 56.00 | 61.76 | 0.79 | -0.064 | -0.071 | True | False |
| 2012-06-15 | 59.08 | 58.67 | 58.80 | 65.02 | 1.02 | -0.011 | -0.056 | True | False |
| 2012-06-29 | 60.09 | 58.86 | 58.55 | 65.02 | 1.43 | 0.041 | 0.031 | True | False |
| 2012-07-27 | 60.43 | 59.42 | 58.86 | 65.02 | 0.84 | 0.018 | 0.022 | True | False |
| 2013-07-12 | 75.52 | 75.52 | 74.69 | 82.24 | 1.39 | -0.051 | -0.044 | True | False |
| 2013-09-20 | 77.32 | 76.48 | 76.44 | 82.24 | 1.02 | -0.046 | -0.105 | True | False |
| 2013-11-15 | 78.02 | 75.98 | 76.12 | 82.24 | 1.23 | -0.120 | -0.138 | True | False |
| 2013-12-20 | 80.55 | 75.39 | 75.95 | 79.40 | 1.88 | -0.111 | -0.159 | True | False |
| 2014-04-17 | 78.90 | 78.72 | 78.20 | 84.43 | 0.99 | 0.013 | -0.005 | True | False |
| 2014-05-02 | 79.36 | 79.07 | 78.58 | 84.43 | 0.88 | 0.019 | 0.006 | True | False |
| 2014-05-16 | 79.53 | 79.49 | 78.72 | 84.43 | 0.77 | -0.024 | -0.013 | True | False |
| 2014-08-29 | 81.06 | 80.62 | 80.93 | 83.93 | 0.70 | -0.097 | -0.113 | True | False |
| 2014-10-03 | 80.32 | 80.24 | 80.66 | 83.53 | 1.40 | -0.025 | -0.057 | True | False |
| 2014-10-31 | 81.12 | 79.96 | 80.24 | 83.53 | 1.10 | -0.047 | -0.053 | True | False |
| 2015-09-11 | 97.35 | 95.94 | 94.82 | 103.74 | 0.85 | 0.159 | 0.122 | False | False |
| 2016-01-22 | 102.24 | 101.97 | 101.41 | 109.10 | 1.32 | 0.103 | 0.118 | False | False |
| 2016-03-04 | 103.18 | 101.90 | 102.25 | 109.10 | 0.78 | 0.050 | 0.078 | True | False |
| 2016-09-30 | 122.17 | 114.26 | 112.34 | 118.94 | 2.08 | 0.004 | -0.070 | True | True |
| 2017-02-10 | 117.60 | 116.26 | 116.02 | 123.31 | 0.95 | -0.018 | -0.050 | True | False |
| 2017-04-21 | 119.23 | 118.84 | 118.09 | 125.22 | 1.00 | -0.059 | -0.110 | True | False |
| 2018-03-29 | 153.50 | 149.91 | 146.30 | 162.95 | 1.36 | 0.085 | 0.033 | False | False |
| 2018-04-20 | 152.41 | 151.34 | 149.13 | 162.95 | 1.01 | 0.054 | 0.037 | True | False |
| 2018-11-09 | 165.15 | 162.25 | 161.02 | 174.19 | 0.83 | 0.033 | 0.004 | False | False |
| 2018-11-30 | 164.52 | 163.19 | 161.75 | 174.19 | 1.41 | 0.028 | 0.040 | False | False |
| 2019-02-15 | 159.23 | 158.99 | 160.36 | 174.19 | 0.85 | -0.008 | 0.014 | True | False |
| 2019-10-18 | 187.08 | 186.87 | 183.68 | 201.12 | 1.01 | 0.019 | 0.014 | True | False |
| 2019-11-01 | 188.22 | 187.44 | 185.52 | 201.12 | 0.85 | 0.021 | -0.015 | True | False |

## TradingView leg — what Matt runs

Warnings before step 1: leave dividend adjustment OFF on the chart (Sharadar's split-adjusted series is the
TradingView default); do not enable the bar magnifier; the date range is set inside the script. TradingView
has no percent slippage, so the 0.10% slippage is folded into a 0.20% commission.

1. TradingView, chart NASDAQ:AAPL, interval W (weekly).
2. Pine Editor, paste strategies/02-growth/tradingview/weinstein_stage2_aapl.pine, Add to chart.
3. Strategy Tester tab, Properties: initial capital 100000, order size 100% of equity, commission 0.2% (already
   set by the script), slippage 0, verify "Recalculate after order is filled" is off.
4. List of Trades tab: export (the download icon) and paste the entry date, entry price, exit date, exit price
   and exit type for every trade into the reconciliation section below, or into the chat.
5. Also note the Strategy Tester's total trade count and net profit.

## Reconciliation (to fill after the TradingView run)

Pass criterion (section 4): entry dates match trade list A within one bar and the trade counts match. With
zero engine trades on AAPL, the check is that TradingView also takes zero and that its indicator values on
the crossover weeks above agree (in particular the volume multiples of 1.30 and 1.57 on the two weeks that
cleared the 26-week base); the ACN list tests the fills.
Known sources of small differences to check first: TradingView's weekly volume against Sharadar's daily
sum; a week where AAPL's data ends on a Thursday holiday; SPY from AMEX:SPY against Sharadar funds.

| ticker | engine entry | TradingView entry | match | note |
| --- | --- | --- | --- | --- |
| AAPL | (no trades) | | | |
| ACN | 2016-10-03 | | | |
