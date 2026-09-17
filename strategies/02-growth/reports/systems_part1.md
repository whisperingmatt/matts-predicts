# Systems part 1 — GROWTH-004 S10: S-A CANSLIM, S-B Minervini, S-C Weinstein

STATUS: PROVISIONAL — the section 4 sanity check is half complete: the engine leg is in reports/engine_sanity.md, the TradingView leg is pending Matt's run. Verdicts stand only once the two AAPL trade lists reconcile.

Engine per spec section 1 (src/engine.py): daily event loop on the GROWTH-001 universe, fills at the next
open, stops at the stop or the gapped open, 0.10% commission plus 0.10% / 0.25% slippage per side by market
cap, $100,000, no leverage, equal weight across ten slots, cash when nothing qualifies, continuous 2006-01
to 2025-06 with results per window (build 2006-01 to 2019-12, holdout 2020-01 to 2025-06). Every rule is
run as written or by the proxy listed in the substitution table; nothing was tuned. Every number comes
from src/systems_part1.py; trades with the full feature row at entry are in
data/processed/trades_<system>.parquet (regenerable) and the core trade columns in reports/s10_trades_*.csv.

## Pass criteria (section 3, fixed before results)

PASS: in both windows, expectancy per trade > 0 after costs, CAGR above SPY's, and max drawdown no worse
than 1.5x SPY's. MARGINAL: CAGR above SPY's in both windows but one of the other four checks fails. Expectancy
for the pass test is per dollar deployed (net profit / capital put into trades in the window), because a
half-position sale is its own row and the plain mean of row returns overweights it; both are shown. Rank by
holdout CAGR / holdout max drawdown. The three systems below are ranked; S-D to S-F join the board in S11.

| system | verdict | build CAGR | SPY | build maxDD | build exp. | holdout CAGR | SPY | holdout maxDD | holdout exp. | holdout CAGR/DD | trades |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S-C_weinstein | FAIL | 3.9% | 9.2% | -38.4% | 2.67% | 5.6% | 14.3% | -33.8% | 2.73% | 0.16 | 336 |
| S-B_minervini | FAIL | -0.4% | 9.2% | -34.0% | -0.13% | 1.6% | 14.3% | -35.8% | 0.34% | 0.04 | 1717 |
| S-A_canslim | FAIL | 0.8% | 9.2% | -6.2% | 2.52% | -0.7% | 14.3% | -8.4% | -1.43% | -0.09 | 74 |

## Substitutions (every proxy for an as-written rule; also in decisions.md)

| system | rule as written | original term | what runs |
| --- | ---: | ---: | ---: |
| all | Universe membership at signal | GROWTH-001 universe by month end | a stock is eligible on a date when a universe row exists for the latest month end on or before it |
| all | Next-open fill | next day's open | the ticker's next bar after the signal; a ticker with no bar the next day fills at its next bar within five trading days, then the order lapses; a new evaluation replaces unfilled orders |
| all | Slippage tier | marketcap >= $2B | daily.marketcap on the fill day (USD millions); unknown market cap takes the 0.25% tier |
| all | Equal weight | equal weight across slots | each entry sized to equity / slots at the fill, capped by cash; whole shares |
| all | Candidate order | not specified | when candidates exceed free slots, the highest relative-strength rank enters first; ties by ticker |
| all | Delisting while held | not specified | when a held ticker has no further bar in the data it is closed at its last close, small-cap slippage, reason delisted |
| all | Open positions at 2025-06-30 | not specified | closed at the last close, reason end_of_test, kept in the trade stats and flagged |
| all | Expectancy per trade | expectancy % per trade after costs | for the pass test: net profit over capital deployed in the window's closed trade rows; the plain mean of row returns is shown beside it (partial sales are separate rows) |
| all | Trade window | per window | a trade belongs to the window of its exit date; the equity curve is continuous across windows |
| S-A | C quarterly EPS YoY >= 25%, higher than the prior quarter's YoY | quarterly EPS | ARQ eps (basic, split-adjusted to today's basis) by filing date; YoY needs a positive year-ago quarter; prior quarter's YoY on the same basis |
| S-A | A annual EPS growth >= 25% each of the last 3 fiscal years | 3 fiscal years | 12 trailing ARQ quarters summed into three years as the spec directs, which gives two annual growth rates, both >= 25%, with positive bases; quarter spacing checked (q4 at 11-13 months, q8 at 23-25, q11 at 32-34) |
| S-A | N price within 5% of 52-week high | 52-week high | implied by the entry: the close is a new 52-week closing high |
| S-A | S shares not rising over 8 quarters or buyback | shares outstanding | ARQ sharesbas now <= sharesbas eight quarters earlier, no tolerance |
| S-A | L relative strength percentile >= 80 | O'Neil RS rating | percent rank of the 252-trading-day return among universe members on the evaluation day |
| S-A | I institutional % rising QoQ (2013+) | institutional ownership | features.parquet inst_pct > inst_pct_prev at the latest month end on or before the evaluation day (13F, 45-day lag); the test is skipped before 2013-01-01 and both segments are reported |
| S-A | M SPY above 50-day and 200-day | SPY | funds SPY closeadj above both SMAs on the evaluation day |
| S-A | Entry: close at a new 52-week high, volume >= 1.5x 50-day average | new 52-week high | Friday close above the highest close of the prior 252 bars (closing basis), Friday volume >= 1.5x the 50-day average volume |
| S-A | 3 weeks / week 8 | weeks | 15 and 40 trading days from the entry bar |
| S-A | Take profit at +20% | take profit | a limit at 1.20x entry, filled at the limit or the open if gapped above; reaching it inside 15 bars cancels the limit and switches to the 50-day SMA trailing exit |
| S-B | VCP breakout (GROWTH-001 H14) then a close above the pivot on volume >= 1.25x 50-day average | VCP + pivot | an H14 pattern day (close above the prior 20-day high after three successive 20-day contractions in ATR ratio and average volume) inside the evaluation week with that day's volume >= 1.25x the 50-day average; pivot = the prior 20-day high on that day; Friday close still above the pivot; the trend template checked on the Friday |
| S-B | 200-day SMA rising for >= 1 month | rising | SMA200 today above SMA200 22 trading days earlier |
| S-B | RS percentile >= 70 | RS | same 252-day return percent rank as S-A |
| S-B | Trailing exit on the remainder | remainder | the 50-day and 20-day SMA exits apply only after the half sale at +14%; before it the 7% stop (and the 10% hard stop) are the only exits |
| S-B | Close below 20-day SMA on above-average volume | above average | volume above the 50-day average |
| S-C | Weekly bars | weekly | Monday-to-Friday weeks from daily bars; close = last trading day, volume = sum |
| S-C | 30-week SMA flattened or turned up | flattened | SMA30 this week >= SMA30 four weeks earlier |
| S-C | Weekly volume >= 2x 26-week average | 26-week average | 26 weeks including the current one (TradingView ta.sma convention) |
| S-C | RS vs SPY positive and rising | rising | 26-week relative return above zero and above the prior week's value |
| S-C | Stage 3/4 exit | SMA flat or declining | weekly close below SMA30 with SMA30 <= its value four weeks earlier |
| S-C | Regime | SPY below its 30-week SMA | SPY weekly close (closeadj) below its 30-week SMA on the evaluation week: no new entries |

## S-A_canslim

| metric | build 2006-01 to 2019-12 | holdout 2020-01 to 2025-06 |
| --- | ---: | ---: |
| trades | 46 | 28 |
| win rate | 50.0% | 35.7% |
| avg winner | 12.1% | 9.3% |
| avg loser | -6.9% | -7.3% |
| expectancy per trade row (mean return) | 2.57% | -1.36% |
| expectancy per dollar (net profit / capital deployed, the pass test) | 2.52% | -1.43% |
| profit factor | 1.72 | 0.69 |
| CAGR | 0.8% | -0.7% |
| total return | 12.0% | -4.0% |
| max drawdown | -6.2% | -8.4% |
| worst 12-month | -4.6% | -4.9% |
| Sharpe (rf 0) | 0.38 | -0.24 |
| turnover (annual) | 0.34 | 0.45 |
| avg holding days | 44.54 | 37.93 |
| SPY CAGR | 9.2% | 14.3% |
| SPY max drawdown | -55.2% | -33.7% |
| equity start / end | 100,000 / 112,015 | 112,015 / 107,567 |

Per-year return against SPY (calendar years; a year's return is equity at its last close over the prior
year's last close):

| year | system | SPY |
| --- | ---: | ---: |
| 2006 | 3.4% | 15.8% |
| 2007 | -2.9% | 5.1% |
| 2008 | -2.4% | -36.8% |
| 2009 | -0.6% | 26.4% |
| 2010 | 5.9% | 15.1% |
| 2011 | -1.8% | 1.9% |
| 2012 | 1.4% | 16.0% |
| 2013 | 0.0% | 32.3% |
| 2014 | 3.3% | 13.5% |
| 2015 | 0.6% | 1.3% |
| 2016 | -1.7% | 12.0% |
| 2017 | 4.2% | 21.7% |
| 2018 | 2.7% | -4.6% |
| 2019 | -0.4% | 31.2% |
| 2020 | -0.8% | 18.4% |
| 2021 | -4.1% | 28.7% |
| 2022 | -1.7% | -18.2% |
| 2023 | 4.7% | 26.2% |
| 2024 | -1.2% | 24.9% |
| 2025 | -0.8% | 6.1% |

Exit reasons (all closed trades, both windows):

| reason | trades | share | mean return |
| --- | ---: | ---: | ---: |
| close_below_sma50 | 25 | 33.8% | 1.32% |
| end_of_test | 1 | 1.4% | 1.28% |
| stop_8pct | 32 | 43.2% | -8.46% |
| take_profit_20pct | 16 | 21.6% | 19.79% |

S-A segments (spec section 6): the I test is skipped before 2013 and applied from 2013; the run is
continuous and the segments are cut from it:

| metric | 2006-01 to 2012-12 (no I test) | 2013-01 to 2019-12 (with I test) |
| --- | ---: | ---: |
| trades | 32 | 14 |
| win rate | 43.8% | 64.3% |
| avg winner | 11.0% | 13.8% |
| avg loser | -6.7% | -7.6% |
| expectancy per trade row (mean return) | 1.01% | 6.15% |
| expectancy per dollar (net profit / capital deployed, the pass test) | 0.88% | 6.07% |
| profit factor | 1.23 | 3.21 |
| CAGR | 0.4% | 1.2% |
| total return | 2.8% | 8.9% |
| max drawdown | -6.2% | -2.1% |
| worst 12-month | -4.6% | -2.0% |
| Sharpe (rf 0) | 0.17 | 0.68 |
| turnover (annual) | 0.46 | 0.22 |
| avg holding days | 44.16 | 45.43 |
| SPY CAGR | 4.1% | 14.6% |
| SPY max drawdown | -55.2% | -19.3% |
| equity start / end | 100,000 / 102,836 | 102,836 / 112,015 |

## S-B_minervini

| metric | build 2006-01 to 2019-12 | holdout 2020-01 to 2025-06 |
| --- | ---: | ---: |
| trades | 1100 | 617 |
| win rate | 48.5% | 47.8% |
| avg winner | 14.8% | 15.6% |
| avg loser | -7.0% | -6.6% |
| expectancy per trade row (mean return) | 3.56% | 4.02% |
| expectancy per dollar (net profit / capital deployed, the pass test) | -0.13% | 0.34% |
| profit factor | 0.97 | 1.07 |
| CAGR | -0.4% | 1.6% |
| total return | -5.6% | 8.9% |
| max drawdown | -34.0% | -35.8% |
| worst 12-month | -24.6% | -26.7% |
| Sharpe (rf 0) | 0.03 | 0.18 |
| turnover (annual) | 5.88 | 7.37 |
| avg holding days | 42.81 | 30.90 |
| SPY CAGR | 9.2% | 14.3% |
| SPY max drawdown | -55.2% | -33.7% |
| equity start / end | 100,000 / 94,360 | 94,360 / 102,741 |

Per-year return against SPY (calendar years; a year's return is equity at its last close over the prior
year's last close):

| year | system | SPY |
| --- | ---: | ---: |
| 2006 | -0.7% | 15.8% |
| 2007 | 5.2% | 5.1% |
| 2008 | -10.8% | -36.8% |
| 2009 | 5.0% | 26.4% |
| 2010 | 6.4% | 15.1% |
| 2011 | -7.7% | 1.9% |
| 2012 | -5.4% | 16.0% |
| 2013 | 33.0% | 32.3% |
| 2014 | -10.3% | 13.5% |
| 2015 | -4.3% | 1.3% |
| 2016 | -7.2% | 12.0% |
| 2017 | 4.4% | 21.7% |
| 2018 | -12.4% | -4.6% |
| 2019 | 7.0% | 31.2% |
| 2020 | -3.8% | 18.4% |
| 2021 | -2.8% | 28.7% |
| 2022 | -17.1% | -18.2% |
| 2023 | 7.7% | 26.2% |
| 2024 | 20.0% | 24.9% |
| 2025 | 8.7% | 6.1% |

Exit reasons (all closed trades, both windows):

| reason | trades | share | mean return |
| --- | ---: | ---: | ---: |
| breakeven_stop | 68 | 4.0% | -1.24% |
| close_below_sma20_volume | 325 | 18.9% | 17.10% |
| close_below_sma50 | 33 | 1.9% | 12.19% |
| delisted | 59 | 3.4% | 4.70% |
| end_of_test | 10 | 0.6% | 13.02% |
| half_at_2R | 434 | 25.3% | 14.06% |
| stop_7pct | 788 | 45.9% | -7.59% |

## S-C_weinstein

| metric | build 2006-01 to 2019-12 | holdout 2020-01 to 2025-06 |
| --- | ---: | ---: |
| trades | 203 | 133 |
| win rate | 40.9% | 27.1% |
| avg winner | 23.2% | 40.5% |
| avg loser | -10.1% | -10.6% |
| expectancy per trade row (mean return) | 3.51% | 3.21% |
| expectancy per dollar (net profit / capital deployed, the pass test) | 2.67% | 2.73% |
| profit factor | 1.43 | 1.35 |
| CAGR | 3.9% | 5.6% |
| total return | 70.9% | 34.7% |
| max drawdown | -38.4% | -33.8% |
| worst 12-month | -36.6% | -25.7% |
| Sharpe (rf 0) | 0.34 | 0.35 |
| turnover (annual) | 1.30 | 1.88 |
| avg holding days | 157.14 | 100.95 |
| SPY CAGR | 9.2% | 14.3% |
| SPY max drawdown | -55.2% | -33.7% |
| equity start / end | 100,000 / 170,921 | 170,921 / 230,225 |

Per-year return against SPY (calendar years; a year's return is equity at its last close over the prior
year's last close):

| year | system | SPY |
| --- | ---: | ---: |
| 2006 | -9.9% | 15.8% |
| 2007 | 11.1% | 5.1% |
| 2008 | -6.9% | -36.8% |
| 2009 | 2.4% | 26.4% |
| 2010 | -6.3% | 15.1% |
| 2011 | -5.9% | 1.9% |
| 2012 | 22.1% | 16.0% |
| 2013 | 32.0% | 32.3% |
| 2014 | 7.7% | 13.5% |
| 2015 | 11.5% | 1.3% |
| 2016 | 1.2% | 12.0% |
| 2017 | 15.4% | 21.7% |
| 2018 | -6.0% | -4.6% |
| 2019 | -4.3% | 31.2% |
| 2020 | 32.9% | 18.4% |
| 2021 | -2.2% | 28.7% |
| 2022 | -11.9% | -18.2% |
| 2023 | 21.6% | 26.2% |
| 2024 | 5.9% | 24.9% |
| 2025 | -8.6% | 6.1% |

Exit reasons (all closed trades, both windows):

| reason | trades | share | mean return |
| --- | ---: | ---: | ---: |
| delisted | 77 | 22.9% | 10.40% |
| end_of_test | 8 | 2.4% | 31.33% |
| stage3_close_below_sma30 | 61 | 18.2% | 37.28% |
| stop_10pct | 190 | 56.5% | -11.50% |


## Reading

Status first: every number here is provisional until the section 4 sanity check is reconciled against TradingView, which is Matt's step (reports/engine_sanity.md has the script, the settings and the table to fill). Three engine fills were checked by hand against the bars and agree to the cent: an S-B stop that gapped through and filled at the open, an S-A take-profit limit filled at the open above the limit, and an S-C Monday-open entry with the small-cap slippage tier.

None of the three systems passes section 3, in either window, and the failures are of different kinds.

S-C Weinstein is the best of the three and still fails on return. It compounds at 3.9% a year in the build window and 5.6% in the holdout against 9.2% and 14.3% for SPY, with drawdowns of 38% and 34% that sit inside 1.5 times SPY's, and a positive expectancy per dollar in both windows (2.7%). Its trades are the shape the book describes: 190 of 336 rows end at the 10% stop for a mean −11.5%, 61 end at the Stage 3 exit for a mean +37% after 408 days on average, and 77 end because the ticker left the data, mostly acquisitions, for a mean +10%. Win rate is 41% in the build window and 27% in the holdout. The system holds about six of its ten slots on average, fewer in 2008, 2009 and 2022 when the SPY regime filter shuts new entries. It beat SPY in six of twenty calendar years.

S-B Minervini trades the most and earns nothing net. 1,717 trade rows in twenty years, 46% of them stopped out at 7% for a mean −7.6%, 25% half-sales at +14%, and the remainder trailing exits with a mean of +12% to +17%. The mean row return is +3.6%, which looks healthy, but the half-sales count as rows, and per dollar deployed the expectancy is −0.1% in the build window and +0.3% in the holdout; the profit factor is 0.97 and 1.07. CAGR is −0.4% and +1.6% against SPY's 9.2% and 14.3%, with drawdowns of 34% and 36%. It fails on return in both windows and on expectancy in the build window. Turnover is six to seven times equity a year, so the 0.2% to 0.35% round-trip cost bill is about 1.5% of equity a year, which is most of the gap between a mean row return above zero and a flat equity curve.

S-A CANSLIM barely trades. The seven conditions together with a new 52-week closing high on 1.5 times average volume and a rising market produce 95 signals in twenty years and 74 trades, and the system holds 0.4 positions on average, so 96% of the capital sits in cash. Its trades are fine on their own terms (expectancy per dollar +2.5% in the build window, 16 take-profits at +20%, 32 stops at −8.5%) but the equity curve moves 12% in fourteen years and −4% in the holdout. The I test cuts the signal count further from 2013 (14 trades in seven years against 32 in the seven before) and the trades that remain are better (expectancy 6.1% against 1.0%, win rate 64% against 44%), on a sample too small to weigh. It fails on return in both windows and on expectancy in the holdout.

What the three have in common is that the entry rules as written are rarely satisfied on a universe of 2,500 to 3,500 stocks a week, that the stops are hit more often than the books imply, and that the winners, where they come, do not pay for the stops after costs. None of this says anything yet about S-D to S-F, which are ranking systems without stops and are S11's work.
