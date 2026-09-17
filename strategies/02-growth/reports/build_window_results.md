# Build-window results — Section 2 Growth, spec section 7

Window 2006-01 to 2019-12 (D4). 393,429 universe stock-months per lag, four lags (T-0, T-3, T-6, T-12).
Every number comes from src/stats.py over data/processed/{features,labels,regime,universe}.parquet.
The holdout was not read.

Definitions. A cell's rows are the universe rows where the flag is non-null. base = launches / rows in
that set; rate = launches / flag-TRUE rows; lift = rate / base. coverage = non-null rows / all rows and
sits beside every lift. CI is the 95% Wilson interval on rate, divided by base. D8: a cell needs at least
100 launch events among flag-TRUE rows (or in the bucket, for base rates); below that it reads
"insufficient". PASS = lift >= 2.0 with lower CI >= 1.5 at any lag. CRASH-ONLY = passes overall but in no
drawdown bucket below 20%. No recommendations are made in this report.

## Reading

This section reads the tables below. It states what held and what did not in the build window, 2006-01 to 2019-12, on the D1 definition (300% forward 24-month return). It makes no recommendation; that is for the chat session after the holdout (spec section 8).

**The base rate is small and the regime moves it more than any signal.** One universe stock-month in 152 launched (2,603 of 393,429, 0.66%). Inside the four SPY drawdown buckets the rate is 0.54%, 0.43%, 0.48%, and 2.98%: entering in a drawdown deeper than 30% multiplied the base by five and a half, and that bucket holds a quarter of all launches on 5.6% of the rows. Months since the trough splits the same way: 0.75% in the first year after a trough, 0.37% to 0.38% after it. By entry year the rate runs from 5 launches in all of 2007 to 2.29% in 2009 and 2.14% in 2019; four years (2006, 2007, 2014, 2015) have too few launches to print a rate under D8. Any signal's lift has to be read against this: a lift of 2.4 in a calm market gives about 1.3%, less than half the no-signal rate in a deep drawdown.

**Three flags pass the section 7 criterion, and they are two ideas.** Relative strength passes at lags 3, 6, and 12 for both horizons. For the 12-month flag the lift is 2.11 at lag 3, 2.36 at lag 6, and 2.46 at lag 12 with lower confidence bounds of 1.92, 2.15, and 2.23; the 6-month flag runs 2.02, 2.26, 2.40. At lag 0 both fall short (1.86 and 1.90): being in the top decile three to twelve months before the decision date is a stronger sign than being there on the day. The flag passes inside the calm bucket (drawdown under 10%) at every lag, so it is not crash-only; in the deep-drawdown bucket only lag 12 has enough events, at 1.95. Coverage is high (80% to 99%) and each cell holds 400 to 480 launches. The two horizons together form the only combination that clears D8 with a lift above the singles: 2.87 [2.54, 3.25] at lag 12 on 247 events, catching 9.5% of all launches.

Institutional sponsorship passes at every lag, 2.15 to 2.39 with lower bounds 1.80 to 2.03, on 118 to 139 events. Three things limit that reading. Coverage is 35% to 43% because holdings begin in mid-2013, so every event is from 2014 to 2019. No drawdown bucket beyond 10% holds a single event, so the flag has never been observed in a stressed market and the crash-only test cannot be applied to it. And the underlying 13F percentages exceed 100% for about a tenth of rows (decisions.md, S3), which cannot set this under-40% flag but says the level is measured loosely. Every combination that includes sponsorship or the insider flag falls under 100 events.

**Two flags come close.** Insider clustering (three or more distinct open-market buyers in 90 days) has lift 1.94 [1.69, 2.23] at lag 0, failing only the 2.0 line, and it decays fast: 1.80 at lag 3, 1.15 at lag 6, insufficient at lag 12. PEG below 0.5 sits at 1.53 to 1.64 across lags with lower bounds up to 1.48, on 43% coverage. Neglect (market cap under $2B) is 1.32 to 1.47 on more than 1,900 events per lag with a lower bound of 1.41 at lag 0: small caps launch more often, but not twice as often, and the flag is true for 55% of rows.

**Four flags are the reverse of their hypothesis, with tight intervals.** Near the 52-week high (close at or above 85% of it) has lift 0.40 [0.37, 0.44] at lag 0 and no better than 0.55 at any lag, on 500 to 650 events: stocks near their highs launched at well under half the base. No dilution (shares up 2% or less over eight quarters) is 0.55 to 0.61, so the launches came disproportionately from companies that had been issuing shares. FCF divergence is 0.51 to 0.61. Dividend yield above 2%, a control expected to do nothing, is 0.34 to 0.47. These are descriptions of which stocks moved 300% in 2006 to 2019, not signals to invert; they say the launch population was far from its highs, diluting, and paying no dividend.

**Six flags show nothing.** Operating leverage 0.99, volatility contraction 1.03, leverage_ok 1.10, price-to-book under 1.5 at 1.19, compressed multiple 1.38 at best, EPS acceleration 1.37 at best with a lower bound of 1.14. The PE-under-15 control reaches 1.55 [1.43, 1.69] at lag 3, more than the spec expected of a control and above two of the hypotheses; it also forms the second D8-clearing combination with PEG under 0.5 (2.13 at lag 3, 249 events).

**One flag cannot be read.** Stage 2 (Weinstein cross) is true for 2.5% of rows and produces 29 to 44 launches per lag; D8 blocks every cell, overall and by regime. H12, H16, H2, H3, H17, and H18 were never computed (unavailable or deferred).

**On launch_200 and launch_500.** At 200% the same ordering holds with lower lifts: the 12-month strength flag runs 1.71 at lag 0 to 2.17 at lag 12; sponsorship 1.64 to 1.88; insiders 1.74 at lag 0 fading to 1.12. At 500% D8 leaves cells in only seven of the nineteen computed flags; where it does, 12-month strength is 2.41 to 2.97 at lags 3 to 12, sponsorship and insiders are insufficient at every lag, and near-high is 0.36 to 0.49.

**Expected launches per ten picks.** With the best combination (both strength flags at lag 12, lift 2.87) the arithmetic 10 x bucket base rate x lift gives 0.16 expected launches per ten picks in the calm bucket, 0.12 to 0.14 in the 10% to 30% buckets, and 0.85 in the deeper-than-30% bucket; the second combination gives 0.12 and 0.64. Under the build-window numbers, ten picks by any combination that clears D8 produce well under one 300% winner unless entered in a deep drawdown, and the deep-drawdown figure rests on 654 launches concentrated in 2008 and 2009 entries. The formula assumes the lift is the same in every regime; the section 7.3 tables show the strength flags passing in the calm bucket and unreadable in most others.

**Sector and entry year.** At the cell level D8 leaves four readable cells out of 154: Consumer Cyclical in 2009 (4.5%) and 2019 (3.6%), Healthcare in 2016 (3.1%) and 2019 (3.9%), Technology in 2019 (3.7%). The sector totals are readable for seven sectors. Healthcare launched at 1.53% (844 of 55,199 rows), a third of all launches on a seventh of the rows; Communication Services 0.88%, Consumer Cyclical 0.85%, Technology 0.78%, Basic Materials 0.72%, Energy 0.48%, Industrials 0.37%. Financial Services had 81 launches on 60,200 rows and Utilities none on 13,387, both insufficient under D8 and both far below the base by count alone. Sector is the tickers table's current value, not the sector at the time.

**What this report does not say.** It does not say which signals to use; that decision waits for the holdout. It does not say the lifts will hold out of sample. It does not correct for the many cells tested. It reads single-signal lifts inside a base rate that regime and year move by an order of magnitude more than any flag.

## 7.1 Base rates by year

| year | rows | launch_300 | rate_300 | launch_200 | rate_200 | launch_500 | rate_500 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2006 | 30,752 | 86 | insufficient | 198 | 0.64% | 21 | insufficient |
| 2007 | 31,216 | 5 | insufficient | 24 | insufficient | 0 | insufficient |
| 2008 | 27,861 | 164 | 0.59% | 491 | 1.76% | 22 | insufficient |
| 2009 | 24,501 | 561 | 2.29% | 1540 | 6.29% | 113 | 0.46% |
| 2010 | 26,486 | 101 | 0.38% | 362 | 1.37% | 34 | insufficient |
| 2011 | 26,564 | 126 | 0.47% | 439 | 1.65% | 41 | insufficient |
| 2012 | 25,569 | 180 | 0.70% | 604 | 2.36% | 46 | insufficient |
| 2013 | 27,212 | 111 | 0.41% | 389 | 1.43% | 23 | insufficient |
| 2014 | 28,980 | 35 | insufficient | 125 | 0.43% | 3 | insufficient |
| 2015 | 29,363 | 76 | insufficient | 239 | 0.81% | 17 | insufficient |
| 2016 | 28,677 | 274 | 0.96% | 737 | 2.57% | 60 | insufficient |
| 2017 | 29,081 | 107 | 0.37% | 376 | 1.29% | 16 | insufficient |
| 2018 | 29,085 | 176 | 0.61% | 477 | 1.64% | 47 | insufficient |
| 2019 | 28,082 | 601 | 2.14% | 1407 | 5.01% | 186 | 0.66% |
| overall | 393,429 | 2603 | 0.66% | 7408 | 1.88% | 629 | 0.16% |

## Base rate inside each regime bucket (section 6 buckets, decision month)

| bucket type | bucket | rows | launch_300 | rate_300 | launch_200 | rate_200 | launch_500 | rate_500 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| drawdown | 0-10 | 304,121 | 1644 | 0.54% | 4573 | 1.50% | 416 | 0.14% |
| drawdown | 10-20 | 38,904 | 168 | 0.43% | 543 | 1.40% | 54 | insufficient |
| drawdown | 20-30 | 28,427 | 137 | 0.48% | 491 | 1.73% | 36 | insufficient |
| drawdown | >30 | 21,977 | 654 | 2.98% | 1801 | 8.19% | 123 | 0.56% |
| mst | 0-12 | 297,665 | 2240 | 0.75% | 6276 | 2.11% | 515 | 0.17% |
| mst | 13-24 | 33,927 | 125 | 0.37% | 393 | 1.16% | 43 | insufficient |
| mst | >24 | 61,837 | 238 | 0.38% | 739 | 1.20% | 71 | insufficient |

## Launch rate (launch_300) by sector and entry year

Cell = launches / universe rows for that sector and year; D8 applied per cell. The last column and
row are the same cells summed, so a sector or a year can pass D8 where its cells do not.

| sector | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | all years (launches/rows) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Basic Materials | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 0.72% (167/23,178) |
| Communication Services | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 0.88% (151/17,198) |
| Consumer Cyclical | insufficient | insufficient | insufficient | 4.5% | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 3.6% | 0.85% (431/50,732) |
| Consumer Defensive | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient (67/20,552) |
| Energy | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 0.48% (148/31,140) |
| Financial Services | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient (81/60,200) |
| Healthcare | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 3.1% | insufficient | insufficient | 3.9% | 1.53% (844/55,199) |
| Industrials | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 0.37% (214/58,299) |
| Real Estate | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient (21/2,164) |
| Technology | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | 3.7% | 0.78% (479/61,319) |
| Unknown | insufficient | insufficient | insufficient | n/a | insufficient | insufficient | n/a | n/a | insufficient | n/a | insufficient | insufficient | n/a | n/a | insufficient (0/61) |
| Utilities | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient | insufficient (0/13,387) |
| all sectors | insufficient | insufficient | 0.59% | 2.29% | 0.38% | 0.47% | 0.70% | 0.41% | insufficient | insufficient | 0.96% | 0.37% | 0.61% | 2.14% | 0.66% |

## 7.2 Single-signal lift, launch_300, by lag

rows_true = flag-TRUE rows; events = launches among them; rate = events / rows_true.

| flag | lag | coverage | true share | rows_true | events | rate | lift | CI low | CI high | cell |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| h1_eps_accel | 0 | 64.0% | 10.1% | 25,537 | 65 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h1_eps_accel | 3 | 63.4% | 10.3% | 25,664 | 89 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h1_eps_accel | 6 | 62.9% | 10.4% | 25,665 | 118 | 0.46% | 1.32 | 1.10 | 1.58 |  |
| h1_eps_accel | 12 | 61.7% | 10.4% | 25,231 | 116 | 0.46% | 1.37 | 1.14 | 1.64 |  |
| h4_op_leverage | 0 | 92.5% | 6.9% | 25,063 | 115 | 0.46% | 0.80 | 0.67 | 0.96 |  |
| h4_op_leverage | 3 | 91.3% | 6.9% | 24,922 | 132 | 0.53% | 0.95 | 0.80 | 1.12 |  |
| h4_op_leverage | 6 | 90.1% | 7.0% | 24,877 | 135 | 0.54% | 0.99 | 0.84 | 1.17 |  |
| h4_op_leverage | 12 | 87.9% | 7.1% | 24,513 | 114 | 0.47% | 0.87 | 0.73 | 1.05 |  |
| h5_peg_lt_1 | 0 | 43.5% | 62.7% | 107,386 | 382 | 0.36% | 1.24 | 1.12 | 1.37 |  |
| h5_peg_lt_1 | 3 | 43.6% | 62.6% | 107,301 | 440 | 0.41% | 1.33 | 1.21 | 1.46 |  |
| h5_peg_lt_1 | 6 | 43.3% | 62.6% | 106,518 | 431 | 0.40% | 1.27 | 1.16 | 1.40 |  |
| h5_peg_lt_1 | 12 | 42.6% | 62.1% | 104,140 | 383 | 0.37% | 1.18 | 1.07 | 1.30 |  |
| h5_peg_lt_05 | 0 | 43.5% | 42.2% | 72,282 | 317 | 0.44% | 1.53 | 1.37 | 1.70 |  |
| h5_peg_lt_05 | 3 | 43.6% | 42.0% | 71,951 | 365 | 0.51% | 1.64 | 1.48 | 1.82 |  |
| h5_peg_lt_05 | 6 | 43.3% | 41.7% | 71,055 | 348 | 0.49% | 1.54 | 1.39 | 1.71 |  |
| h5_peg_lt_05 | 12 | 42.6% | 41.0% | 68,691 | 293 | 0.43% | 1.37 | 1.22 | 1.53 |  |
| h6_compressed_multiple | 0 | 63.0% | 22.6% | 56,070 | 160 | 0.29% | 1.03 | 0.89 | 1.21 |  |
| h6_compressed_multiple | 3 | 62.5% | 22.8% | 56,038 | 222 | 0.40% | 1.38 | 1.21 | 1.57 |  |
| h6_compressed_multiple | 6 | 61.9% | 22.8% | 55,509 | 209 | 0.38% | 1.30 | 1.13 | 1.49 |  |
| h6_compressed_multiple | 12 | 60.8% | 22.6% | 54,034 | 180 | 0.33% | 1.14 | 0.98 | 1.32 |  |
| h7_neglect | 0 | 99.7% | 54.6% | 213,992 | 2083 | 0.97% | 1.47 | 1.41 | 1.53 |  |
| h7_neglect | 3 | 100.0% | 55.1% | 216,828 | 2043 | 0.94% | 1.43 | 1.37 | 1.49 |  |
| h7_neglect | 6 | 99.9% | 55.6% | 218,696 | 1976 | 0.90% | 1.37 | 1.31 | 1.43 |  |
| h7_neglect | 12 | 99.2% | 56.5% | 220,470 | 1895 | 0.86% | 1.32 | 1.27 | 1.38 |  |
| h8_fcf_divergence | 0 | 97.9% | 11.9% | 45,818 | 149 | 0.33% | 0.51 | 0.43 | 0.60 |  |
| h8_fcf_divergence | 3 | 96.6% | 12.0% | 45,400 | 153 | 0.34% | 0.54 | 0.46 | 0.63 |  |
| h8_fcf_divergence | 6 | 95.3% | 12.0% | 45,018 | 166 | 0.37% | 0.61 | 0.52 | 0.71 |  |
| h8_fcf_divergence | 12 | 92.8% | 11.9% | 43,287 | 143 | 0.33% | 0.57 | 0.49 | 0.67 |  |
| h9_rs6_top_decile | 0 | 99.9% | 10.0% | 39,379 | 482 | 1.22% | 1.86 | 1.70 | 2.03 |  |
| h9_rs6_top_decile | 3 | 92.0% | 9.5% | 34,290 | 428 | 1.25% | 2.02 | 1.84 | 2.22 | PASS |
| h9_rs6_top_decile | 6 | 87.7% | 9.2% | 31,894 | 432 | 1.35% | 2.26 | 2.06 | 2.48 | PASS |
| h9_rs6_top_decile | 12 | 80.6% | 9.0% | 28,710 | 401 | 1.40% | 2.40 | 2.18 | 2.64 | PASS |
| h9_rs12_top_decile | 0 | 99.0% | 10.0% | 39,007 | 478 | 1.23% | 1.90 | 1.73 | 2.07 |  |
| h9_rs12_top_decile | 3 | 91.2% | 9.7% | 34,670 | 439 | 1.27% | 2.11 | 1.92 | 2.31 | PASS |
| h9_rs12_top_decile | 6 | 87.0% | 9.5% | 32,542 | 447 | 1.37% | 2.36 | 2.15 | 2.58 | PASS |
| h9_rs12_top_decile | 12 | 79.9% | 9.4% | 29,466 | 413 | 1.40% | 2.46 | 2.23 | 2.70 | PASS |
| h10_sponsorship | 0 | 43.3% | 4.8% | 8,103 | 122 | 1.51% | 2.17 | 1.82 | 2.59 | PASS |
| h10_sponsorship | 3 | 41.4% | 5.0% | 8,160 | 124 | 1.52% | 2.15 | 1.80 | 2.55 | PASS |
| h10_sponsorship | 6 | 39.3% | 5.2% | 8,018 | 139 | 1.73% | 2.39 | 2.03 | 2.82 | PASS |
| h10_sponsorship | 12 | 35.0% | 5.3% | 7,360 | 120 | 1.63% | 2.22 | 1.86 | 2.65 | PASS |
| h11_insider_cluster | 0 | 82.4% | 4.0% | 13,058 | 196 | 1.50% | 1.94 | 1.69 | 2.23 |  |
| h11_insider_cluster | 3 | 80.5% | 4.0% | 12,826 | 181 | 1.41% | 1.80 | 1.55 | 2.08 |  |
| h11_insider_cluster | 6 | 78.7% | 4.1% | 12,812 | 118 | 0.92% | 1.15 | 0.96 | 1.38 |  |
| h11_insider_cluster | 12 | 75.3% | 4.5% | 13,412 | 98 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h13_stage2 | 0 | 99.9% | 2.5% | 9,730 | 30 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h13_stage2 | 3 | 99.6% | 2.4% | 9,509 | 29 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h13_stage2 | 6 | 98.8% | 2.4% | 9,309 | 29 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h13_stage2 | 12 | 96.5% | 2.5% | 9,471 | 44 | insufficient | insufficient | insufficient | insufficient | insufficient |
| h14_vol_contraction | 0 | 100.0% | 9.8% | 38,409 | 261 | 0.68% | 1.03 | 0.91 | 1.16 |  |
| h14_vol_contraction | 3 | 99.9% | 9.6% | 37,879 | 206 | 0.54% | 0.82 | 0.72 | 0.94 |  |
| h14_vol_contraction | 6 | 99.8% | 9.6% | 37,743 | 209 | 0.55% | 0.84 | 0.74 | 0.96 |  |
| h14_vol_contraction | 12 | 98.3% | 9.4% | 36,220 | 193 | 0.53% | 0.84 | 0.73 | 0.96 |  |
| h15_near_high | 0 | 99.3% | 51.9% | 202,715 | 533 | 0.26% | 0.40 | 0.37 | 0.44 |  |
| h15_near_high | 3 | 98.3% | 51.9% | 200,751 | 524 | 0.26% | 0.41 | 0.38 | 0.45 |  |
| h15_near_high | 6 | 97.2% | 52.3% | 199,763 | 583 | 0.29% | 0.47 | 0.43 | 0.51 |  |
| h15_near_high | 12 | 94.9% | 53.0% | 197,832 | 645 | 0.33% | 0.55 | 0.51 | 0.59 |  |
| h20_leverage_ok | 0 | 99.7% | 61.3% | 240,388 | 1640 | 0.68% | 1.03 | 0.98 | 1.08 |  |
| h20_leverage_ok | 3 | 99.1% | 61.9% | 241,355 | 1690 | 0.70% | 1.06 | 1.01 | 1.11 |  |
| h20_leverage_ok | 6 | 98.5% | 62.5% | 242,213 | 1748 | 0.72% | 1.10 | 1.05 | 1.15 |  |
| h20_leverage_ok | 12 | 96.8% | 63.4% | 241,312 | 1716 | 0.71% | 1.10 | 1.05 | 1.16 |  |
| h21_no_dilution | 0 | 94.4% | 56.3% | 208,987 | 728 | 0.35% | 0.57 | 0.53 | 0.62 |  |
| h21_no_dilution | 3 | 93.1% | 56.0% | 205,182 | 668 | 0.33% | 0.55 | 0.51 | 0.59 |  |
| h21_no_dilution | 6 | 91.9% | 55.7% | 201,372 | 658 | 0.33% | 0.56 | 0.52 | 0.61 |  |
| h21_no_dilution | 12 | 89.6% | 55.2% | 194,431 | 655 | 0.34% | 0.61 | 0.56 | 0.65 |  |
| ctl_pe_lt_15 | 0 | 80.0% | 30.4% | 95,637 | 509 | 0.53% | 1.45 | 1.33 | 1.58 |  |
| ctl_pe_lt_15 | 3 | 80.1% | 30.2% | 95,211 | 567 | 0.60% | 1.55 | 1.43 | 1.69 |  |
| ctl_pe_lt_15 | 6 | 79.9% | 30.0% | 94,243 | 478 | 0.51% | 1.29 | 1.18 | 1.41 |  |
| ctl_pe_lt_15 | 12 | 79.1% | 29.4% | 91,489 | 418 | 0.46% | 1.14 | 1.03 | 1.25 |  |
| ctl_pb_lt_15 | 0 | 96.6% | 24.0% | 91,250 | 682 | 0.75% | 1.19 | 1.10 | 1.28 |  |
| ctl_pb_lt_15 | 3 | 96.9% | 23.8% | 90,873 | 612 | 0.67% | 1.07 | 0.99 | 1.16 |  |
| ctl_pb_lt_15 | 6 | 96.8% | 23.7% | 90,366 | 484 | 0.54% | 0.85 | 0.78 | 0.93 |  |
| ctl_pb_lt_15 | 12 | 95.8% | 23.6% | 88,914 | 353 | 0.40% | 0.65 | 0.59 | 0.72 |  |
| ctl_divyield_gt_2 | 0 | 100.0% | 25.2% | 99,117 | 310 | 0.31% | 0.47 | 0.42 | 0.53 |  |
| ctl_divyield_gt_2 | 3 | 99.9% | 24.9% | 97,970 | 289 | 0.29% | 0.45 | 0.40 | 0.50 |  |
| ctl_divyield_gt_2 | 6 | 99.9% | 24.6% | 96,512 | 246 | 0.25% | 0.39 | 0.34 | 0.44 |  |
| ctl_divyield_gt_2 | 12 | 98.7% | 24.0% | 93,269 | 206 | 0.22% | 0.34 | 0.30 | 0.39 |  |

### Verdicts (launch_300, section 7 pass/fail criteria)

| flag | status | verdict | passing lags | best lag | lift | CI low | events | coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| h1_eps_accel | available | FAIL | - | 12 | 1.37 | 1.14 | 116 | 61.7% |
| h4_op_leverage | available | FAIL | - | 6 | 0.99 | 0.84 | 135 | 90.1% |
| h5_peg_lt_1 | available | FAIL | - | 3 | 1.33 | 1.21 | 440 | 43.6% |
| h5_peg_lt_05 | available | FAIL | - | 3 | 1.64 | 1.48 | 365 | 43.6% |
| h6_compressed_multiple | available | FAIL | - | 3 | 1.38 | 1.21 | 222 | 62.5% |
| h7_neglect | available | FAIL | - | 0 | 1.47 | 1.41 | 2083 | 99.7% |
| h8_fcf_divergence | available | FAIL | - | 6 | 0.61 | 0.52 | 166 | 95.3% |
| h9_rs6_top_decile | available | PASS | 6,12,3 | 12 | 2.40 | 2.18 | 401 | 80.6% |
| h9_rs12_top_decile | available | PASS | 6,3,12 | 12 | 2.46 | 2.23 | 413 | 79.9% |
| h10_sponsorship | available | PASS | 6,12,3,0 | 6 | 2.39 | 2.03 | 139 | 39.3% |
| h11_insider_cluster | available | FAIL | - | 0 | 1.94 | 1.69 | 196 | 82.4% |
| h13_stage2 | available | insufficient | - | - | - | - | - | - |
| h14_vol_contraction | available | FAIL | - | 0 | 1.03 | 0.91 | 261 | 100.0% |
| h15_near_high | available | FAIL | - | 12 | 0.55 | 0.51 | 645 | 94.9% |
| h20_leverage_ok | available | FAIL | - | 12 | 1.10 | 1.05 | 1716 | 96.8% |
| h21_no_dilution | available | FAIL | - | 12 | 0.61 | 0.56 | 655 | 89.6% |
| ctl_pe_lt_15 | available | FAIL | - | 3 | 1.55 | 1.43 | 567 | 80.1% |
| ctl_pb_lt_15 | available | FAIL | - | 0 | 1.19 | 1.10 | 682 | 96.6% |
| ctl_divyield_gt_2 | available | FAIL | - | 0 | 0.47 | 0.42 | 310 | 100.0% |

Unavailable or deferred, no lift computed: h12_short_fuel (UNAVAILABLE — no short-interest field in Sharadar), h16_sector_flow (UNAVAILABLE — no ETF shares-outstanding field in Sharadar (funds is OHLCV only)), h2_surprise_streak (DEFERRED (D7)), h3_estimate_revisions (DEFERRED (D7)), h17_sector_surprise (DEFERRED), h18_attention (DEFERRED)

## 7.3 Single-signal lift within each SPY drawdown bucket, launch_300

Cell = lift (events) or insufficient. Lift is against the base rate of the same bucket among non-null rows.

| flag | lag | 0-10 | 10-20 | 20-30 | >30 |
| --- | --- | ---: | ---: | ---: | ---: |
| h1_eps_accel | 0 | insufficient (20) | insufficient (3) | insufficient (10) | insufficient (32) |
| h1_eps_accel | 3 | insufficient (42) | insufficient (9) | insufficient (2) | insufficient (36) |
| h1_eps_accel | 6 | insufficient (55) | insufficient (11) | insufficient (1) | insufficient (51) |
| h1_eps_accel | 12 | insufficient (47) | insufficient (2) | insufficient (1) | insufficient (66) |
| h4_op_leverage | 0 | insufficient (73) | insufficient (3) | insufficient (15) | insufficient (24) |
| h4_op_leverage | 3 | insufficient (77) | insufficient (6) | insufficient (14) | insufficient (35) |
| h4_op_leverage | 6 | insufficient (73) | insufficient (15) | insufficient (9) | insufficient (38) |
| h4_op_leverage | 12 | insufficient (70) | insufficient (18) | insufficient (9) | insufficient (17) |
| h5_peg_lt_1 | 0 | 1.17 [1.01, 1.36] (171) | insufficient (24) | insufficient (12) | 1.17 [1.01, 1.36] (175) |
| h5_peg_lt_1 | 3 | 1.30 [1.13, 1.50] (188) | insufficient (20) | insufficient (7) | 1.27 [1.12, 1.44] (225) |
| h5_peg_lt_1 | 6 | 1.28 [1.11, 1.47] (190) | insufficient (19) | insufficient (8) | 1.20 [1.05, 1.37] (214) |
| h5_peg_lt_1 | 12 | 1.22 [1.06, 1.41] (185) | insufficient (6) | insufficient (16) | 1.13 [0.98, 1.31] (176) |
| h5_peg_lt_05 | 0 | 1.44 [1.22, 1.70] (141) | insufficient (20) | insufficient (10) | 1.42 [1.21, 1.66] (146) |
| h5_peg_lt_05 | 3 | 1.66 [1.42, 1.94] (160) | insufficient (20) | insufficient (6) | 1.48 [1.29, 1.71] (179) |
| h5_peg_lt_05 | 6 | 1.69 [1.45, 1.96] (167) | insufficient (18) | insufficient (8) | 1.30 [1.12, 1.52] (155) |
| h5_peg_lt_05 | 12 | 1.60 [1.37, 1.86] (159) | insufficient (4) | insufficient (12) | 1.24 [1.04, 1.49] (118) |
| h6_compressed_multiple | 0 | insufficient (75) | insufficient (11) | insufficient (7) | insufficient (67) |
| h6_compressed_multiple | 3 | insufficient (97) | insufficient (14) | insufficient (3) | 1.27 [1.05, 1.53] (108) |
| h6_compressed_multiple | 6 | 1.51 [1.25, 1.82] (111) | insufficient (12) | insufficient (3) | insufficient (83) |
| h6_compressed_multiple | 12 | 1.45 [1.20, 1.75] (108) | insufficient (7) | insufficient (7) | insufficient (58) |
| h7_neglect | 0 | 1.46 [1.38, 1.54] (1259) | 1.37 [1.16, 1.62] (136) | 1.55 [1.30, 1.83] (130) | 1.29 [1.19, 1.40] (558) |
| h7_neglect | 3 | 1.44 [1.37, 1.53] (1260) | 1.33 [1.12, 1.57] (132) | 1.50 [1.26, 1.79] (127) | 1.24 [1.14, 1.34] (524) |
| h7_neglect | 6 | 1.42 [1.35, 1.50] (1254) | 1.36 [1.15, 1.61] (134) | 1.47 [1.24, 1.75] (128) | 1.13 [1.03, 1.23] (460) |
| h7_neglect | 12 | 1.39 [1.31, 1.47] (1212) | 1.42 [1.20, 1.67] (139) | 1.47 [1.24, 1.74] (133) | 1.12 [1.02, 1.24] (411) |
| h8_fcf_divergence | 0 | 0.59 [0.49, 0.71] (111) | insufficient (9) | insufficient (11) | insufficient (18) |
| h8_fcf_divergence | 3 | insufficient (85) | insufficient (16) | insufficient (7) | insufficient (45) |
| h8_fcf_divergence | 6 | insufficient (89) | insufficient (15) | insufficient (8) | insufficient (54) |
| h8_fcf_divergence | 12 | insufficient (63) | insufficient (9) | insufficient (3) | insufficient (68) |
| h9_rs6_top_decile | 0 | 2.11 [1.90, 2.34] (345) PASS | insufficient (40) | insufficient (41) | insufficient (56) |
| h9_rs6_top_decile | 3 | 2.38 [2.13, 2.65] (315) PASS | insufficient (48) | insufficient (30) | insufficient (35) |
| h9_rs6_top_decile | 6 | 2.46 [2.19, 2.76] (285) PASS | insufficient (45) | insufficient (31) | insufficient (71) |
| h9_rs6_top_decile | 12 | 2.66 [2.36, 3.00] (260) PASS | insufficient (25) | insufficient (13) | 1.95 [1.61, 2.35] (103) |
| h9_rs12_top_decile | 0 | 2.14 [1.93, 2.38] (337) PASS | insufficient (57) | insufficient (41) | insufficient (43) |
| h9_rs12_top_decile | 3 | 2.46 [2.21, 2.75] (318) PASS | insufficient (45) | insufficient (29) | insufficient (47) |
| h9_rs12_top_decile | 6 | 2.61 [2.33, 2.92] (298) PASS | insufficient (39) | insufficient (19) | insufficient (91) |
| h9_rs12_top_decile | 12 | 2.63 [2.33, 2.97] (259) PASS | insufficient (34) | insufficient (16) | 1.92 [1.59, 2.31] (104) |
| h10_sponsorship | 0 | 2.17 [1.82, 2.60] (118) PASS | insufficient (4) | insufficient (0) | insufficient (0) |
| h10_sponsorship | 3 | 2.17 [1.82, 2.59] (121) PASS | insufficient (3) | insufficient (0) | insufficient (0) |
| h10_sponsorship | 6 | 2.37 [2.00, 2.80] (133) PASS | insufficient (6) | insufficient (0) | insufficient (0) |
| h10_sponsorship | 12 | 2.25 [1.88, 2.69] (117) PASS | insufficient (3) | insufficient (0) | insufficient (0) |
| h11_insider_cluster | 0 | insufficient (87) | insufficient (21) | insufficient (6) | insufficient (82) |
| h11_insider_cluster | 3 | insufficient (79) | insufficient (10) | insufficient (4) | insufficient (88) |
| h11_insider_cluster | 6 | insufficient (68) | insufficient (3) | insufficient (3) | insufficient (44) |
| h11_insider_cluster | 12 | insufficient (69) | insufficient (8) | insufficient (8) | insufficient (13) |
| h13_stage2 | 0 | insufficient (23) | insufficient (5) | insufficient (2) | insufficient (0) |
| h13_stage2 | 3 | insufficient (23) | insufficient (3) | insufficient (1) | insufficient (2) |
| h13_stage2 | 6 | insufficient (21) | insufficient (0) | insufficient (3) | insufficient (5) |
| h13_stage2 | 12 | insufficient (31) | insufficient (4) | insufficient (1) | insufficient (8) |
| h14_vol_contraction | 0 | 1.10 [0.95, 1.29] (164) | insufficient (10) | insufficient (17) | insufficient (70) |
| h14_vol_contraction | 3 | 0.92 [0.77, 1.08] (135) | insufficient (14) | insufficient (12) | insufficient (45) |
| h14_vol_contraction | 6 | 0.92 [0.78, 1.08] (142) | insufficient (16) | insufficient (13) | insufficient (38) |
| h14_vol_contraction | 12 | 0.93 [0.78, 1.10] (127) | insufficient (10) | insufficient (21) | insufficient (35) |
| h15_near_high | 0 | 0.47 [0.43, 0.52] (428) | insufficient (33) | insufficient (33) | insufficient (39) |
| h15_near_high | 3 | 0.47 [0.43, 0.52] (408) | insufficient (46) | insufficient (44) | insufficient (26) |
| h15_near_high | 6 | 0.48 [0.43, 0.53] (397) | insufficient (65) | insufficient (47) | insufficient (74) |
| h15_near_high | 12 | 0.56 [0.51, 0.61] (437) | insufficient (42) | insufficient (21) | 0.78 [0.66, 0.92] (145) |
| h20_leverage_ok | 0 | 1.07 [1.01, 1.13] (1050) | 1.01 [0.84, 1.21] (112) | insufficient (84) | 0.96 [0.87, 1.06] (394) |
| h20_leverage_ok | 3 | 1.08 [1.02, 1.15] (1072) | 0.99 [0.82, 1.19] (109) | insufficient (82) | 1.02 [0.93, 1.12] (427) |
| h20_leverage_ok | 6 | 1.11 [1.05, 1.18] (1106) | 0.99 [0.82, 1.20] (108) | insufficient (87) | 1.06 [0.96, 1.16] (447) |
| h20_leverage_ok | 12 | 1.12 [1.06, 1.19] (1086) | 1.08 [0.90, 1.30] (111) | insufficient (91) | 1.00 [0.92, 1.10] (428) |
| h21_no_dilution | 0 | 0.49 [0.45, 0.54] (385) | insufficient (25) | insufficient (31) | 0.80 [0.71, 0.89] (287) |
| h21_no_dilution | 3 | 0.47 [0.42, 0.52] (350) | insufficient (20) | insufficient (28) | 0.78 [0.70, 0.88] (270) |
| h21_no_dilution | 6 | 0.48 [0.43, 0.53] (347) | insufficient (19) | insufficient (28) | 0.81 [0.72, 0.91] (264) |
| h21_no_dilution | 12 | 0.56 [0.50, 0.61] (368) | insufficient (23) | insufficient (28) | 0.81 [0.72, 0.92] (236) |
| ctl_pe_lt_15 | 0 | 1.12 [0.97, 1.30] (179) | insufficient (15) | insufficient (14) | 1.15 [1.03, 1.28] (301) |
| ctl_pe_lt_15 | 3 | 1.21 [1.06, 1.39] (198) | insufficient (14) | insufficient (13) | 1.22 [1.10, 1.35] (342) |
| ctl_pe_lt_15 | 6 | 1.14 [0.99, 1.32] (189) | insufficient (11) | insufficient (18) | 0.96 [0.85, 1.08] (260) |
| ctl_pe_lt_15 | 12 | 1.27 [1.11, 1.46] (202) | insufficient (6) | insufficient (23) | 0.92 [0.80, 1.06] (187) |
| ctl_pb_lt_15 | 0 | 0.90 [0.80, 1.01] (281) | insufficient (21) | insufficient (27) | 1.28 [1.16, 1.42] (353) |
| ctl_pb_lt_15 | 3 | 0.81 [0.71, 0.91] (254) | insufficient (19) | insufficient (24) | 1.20 [1.08, 1.34] (315) |
| ctl_pb_lt_15 | 6 | 0.76 [0.67, 0.86] (243) | insufficient (17) | insufficient (27) | 0.84 [0.73, 0.97] (197) |
| ctl_pb_lt_15 | 12 | 0.65 [0.56, 0.74] (198) | insufficient (13) | insufficient (30) | 0.81 [0.68, 0.98] (112) |
| ctl_divyield_gt_2 | 0 | insufficient (97) | insufficient (3) | insufficient (7) | 0.94 [0.82, 1.07] (203) |
| ctl_divyield_gt_2 | 3 | insufficient (95) | insufficient (2) | insufficient (9) | 0.88 [0.77, 1.02] (183) |
| ctl_divyield_gt_2 | 6 | insufficient (92) | insufficient (3) | insufficient (9) | 0.76 [0.65, 0.90] (142) |
| ctl_divyield_gt_2 | 12 | insufficient (90) | insufficient (5) | insufficient (10) | 0.68 [0.56, 0.83] (101) |

## 7.3 Single-signal lift within each months-since-trough bucket, launch_300

Cell = lift (events) or insufficient. Lift is against the base rate of the same bucket among non-null rows.

| flag | lag | 0-12 | 13-24 | >24 |
| --- | --- | ---: | ---: | ---: |
| h1_eps_accel | 0 | insufficient (54) | insufficient (2) | insufficient (9) |
| h1_eps_accel | 3 | insufficient (72) | insufficient (1) | insufficient (16) |
| h1_eps_accel | 6 | 1.38 [1.14, 1.67] (106) | insufficient (1) | insufficient (11) |
| h1_eps_accel | 12 | 1.46 [1.21, 1.75] (113) | insufficient (0) | insufficient (3) |
| h4_op_leverage | 0 | 1.01 [0.83, 1.22] (103) | insufficient (8) | insufficient (4) |
| h4_op_leverage | 3 | 1.22 [1.02, 1.46] (120) | insufficient (9) | insufficient (3) |
| h4_op_leverage | 6 | 1.24 [1.04, 1.48] (120) | insufficient (9) | insufficient (6) |
| h4_op_leverage | 12 | insufficient (87) | insufficient (13) | insufficient (14) |
| h5_peg_lt_1 | 0 | 1.25 [1.13, 1.39] (334) | insufficient (4) | insufficient (44) |
| h5_peg_lt_1 | 3 | 1.35 [1.22, 1.49] (398) | insufficient (2) | insufficient (40) |
| h5_peg_lt_1 | 6 | 1.32 [1.19, 1.45] (396) | insufficient (1) | insufficient (34) |
| h5_peg_lt_1 | 12 | 1.21 [1.09, 1.34] (357) | insufficient (7) | insufficient (19) |
| h5_peg_lt_05 | 0 | 1.55 [1.37, 1.74] (275) | insufficient (2) | insufficient (40) |
| h5_peg_lt_05 | 3 | 1.66 [1.49, 1.85] (327) | insufficient (1) | insufficient (37) |
| h5_peg_lt_05 | 6 | 1.57 [1.41, 1.75] (314) | insufficient (1) | insufficient (33) |
| h5_peg_lt_05 | 12 | 1.39 [1.24, 1.57] (271) | insufficient (7) | insufficient (15) |
| h6_compressed_multiple | 0 | 1.09 [0.93, 1.29] (142) | insufficient (1) | insufficient (17) |
| h6_compressed_multiple | 3 | 1.43 [1.24, 1.64] (194) | insufficient (2) | insufficient (26) |
| h6_compressed_multiple | 6 | 1.26 [1.09, 1.46] (175) | insufficient (4) | insufficient (30) |
| h6_compressed_multiple | 12 | 1.07 [0.92, 1.26] (152) | insufficient (2) | insufficient (26) |
| h7_neglect | 0 | 1.49 [1.42, 1.56] (1777) | 1.55 [1.28, 1.86] (109) | 1.38 [1.20, 1.59] (197) |
| h7_neglect | 3 | 1.45 [1.38, 1.52] (1736) | 1.53 [1.27, 1.84] (111) | 1.38 [1.20, 1.58] (196) |
| h7_neglect | 6 | 1.38 [1.32, 1.45] (1668) | 1.53 [1.28, 1.84] (114) | 1.36 [1.18, 1.56] (194) |
| h7_neglect | 12 | 1.33 [1.27, 1.40] (1582) | 1.54 [1.29, 1.84] (120) | 1.37 [1.19, 1.57] (193) |
| h8_fcf_divergence | 0 | 0.48 [0.40, 0.57] (124) | insufficient (3) | insufficient (22) |
| h8_fcf_divergence | 3 | 0.53 [0.45, 0.63] (133) | insufficient (3) | insufficient (17) |
| h8_fcf_divergence | 6 | 0.60 [0.51, 0.70] (146) | insufficient (7) | insufficient (13) |
| h8_fcf_divergence | 12 | 0.58 [0.49, 0.68] (129) | insufficient (10) | insufficient (4) |
| h9_rs6_top_decile | 0 | 1.79 [1.62, 1.97] (399) | insufficient (37) | insufficient (46) |
| h9_rs6_top_decile | 3 | 1.98 [1.79, 2.19] (363) | insufficient (33) | insufficient (32) |
| h9_rs6_top_decile | 6 | 2.18 [1.97, 2.41] (370) PASS | insufficient (32) | insufficient (30) |
| h9_rs6_top_decile | 12 | 2.42 [2.19, 2.68] (364) PASS | insufficient (15) | insufficient (22) |
| h9_rs12_top_decile | 0 | 1.82 [1.65, 2.01] (396) | insufficient (47) | insufficient (35) |
| h9_rs12_top_decile | 3 | 2.07 [1.87, 2.28] (374) PASS | insufficient (37) | insufficient (28) |
| h9_rs12_top_decile | 6 | 2.34 [2.12, 2.58] (393) PASS | insufficient (27) | insufficient (27) |
| h9_rs12_top_decile | 12 | 2.43 [2.20, 2.69] (369) PASS | insufficient (12) | insufficient (32) |
| h10_sponsorship | 0 | 2.17 [1.82, 2.60] (119) PASS | insufficient (3) | insufficient (0) |
| h10_sponsorship | 3 | 2.16 [1.81, 2.58] (122) PASS | insufficient (2) | insufficient (0) |
| h10_sponsorship | 6 | 2.38 [2.01, 2.81] (134) PASS | insufficient (5) | insufficient (0) |
| h10_sponsorship | 12 | 2.16 [1.80, 2.59] (114) PASS | insufficient (6) | insufficient (0) |
| h11_insider_cluster | 0 | 1.84 [1.58, 2.14] (167) | insufficient (6) | insufficient (23) |
| h11_insider_cluster | 3 | 1.79 [1.54, 2.09] (162) | insufficient (1) | insufficient (18) |
| h11_insider_cluster | 6 | 1.15 [0.96, 1.39] (108) | insufficient (2) | insufficient (8) |
| h11_insider_cluster | 12 | insufficient (80) | insufficient (9) | insufficient (9) |
| h13_stage2 | 0 | insufficient (17) | insufficient (4) | insufficient (9) |
| h13_stage2 | 3 | insufficient (20) | insufficient (4) | insufficient (5) |
| h13_stage2 | 6 | insufficient (18) | insufficient (3) | insufficient (8) |
| h13_stage2 | 12 | insufficient (40) | insufficient (1) | insufficient (3) |
| h14_vol_contraction | 0 | 1.11 [0.97, 1.26] (224) | insufficient (12) | insufficient (25) |
| h14_vol_contraction | 3 | 0.90 [0.77, 1.03] (181) | insufficient (8) | insufficient (17) |
| h14_vol_contraction | 6 | 0.84 [0.72, 0.97] (174) | insufficient (14) | insufficient (21) |
| h14_vol_contraction | 12 | 0.83 [0.71, 0.98] (150) | insufficient (15) | insufficient (28) |
| h15_near_high | 0 | 0.39 [0.35, 0.43] (427) | insufficient (37) | insufficient (69) |
| h15_near_high | 3 | 0.39 [0.35, 0.43] (417) | insufficient (48) | insufficient (59) |
| h15_near_high | 6 | 0.45 [0.41, 0.49] (468) | insufficient (43) | insufficient (72) |
| h15_near_high | 12 | 0.54 [0.50, 0.59] (547) | insufficient (25) | insufficient (73) |
| h20_leverage_ok | 0 | 1.05 [0.99, 1.10] (1385) | insufficient (95) | 0.98 [0.84, 1.14] (160) |
| h20_leverage_ok | 3 | 1.08 [1.03, 1.14] (1444) | insufficient (91) | 0.97 [0.83, 1.14] (155) |
| h20_leverage_ok | 6 | 1.11 [1.06, 1.17] (1502) | insufficient (94) | 1.00 [0.85, 1.17] (152) |
| h20_leverage_ok | 12 | 1.10 [1.05, 1.16] (1470) | 1.36 [1.12, 1.65] (100) | 1.02 [0.87, 1.20] (146) |
| h21_no_dilution | 0 | 0.58 [0.53, 0.62] (652) | insufficient (16) | insufficient (60) |
| h21_no_dilution | 3 | 0.56 [0.51, 0.60] (605) | insufficient (15) | insufficient (48) |
| h21_no_dilution | 6 | 0.57 [0.53, 0.62] (598) | insufficient (16) | insufficient (44) |
| h21_no_dilution | 12 | 0.62 [0.58, 0.68] (592) | insufficient (17) | insufficient (46) |
| ctl_pe_lt_15 | 0 | 1.52 [1.38, 1.66] (469) | insufficient (5) | insufficient (35) |
| ctl_pe_lt_15 | 3 | 1.62 [1.49, 1.77] (520) | insufficient (8) | insufficient (39) |
| ctl_pe_lt_15 | 6 | 1.29 [1.18, 1.42] (428) | insufficient (12) | insufficient (38) |
| ctl_pe_lt_15 | 12 | 1.15 [1.04, 1.27] (375) | insufficient (12) | insufficient (31) |
| ctl_pb_lt_15 | 0 | 1.25 [1.15, 1.35] (628) | insufficient (15) | insufficient (39) |
| ctl_pb_lt_15 | 3 | 1.14 [1.05, 1.24] (565) | insufficient (16) | insufficient (31) |
| ctl_pb_lt_15 | 6 | 0.87 [0.79, 0.96] (429) | insufficient (19) | insufficient (36) |
| ctl_pb_lt_15 | 12 | 0.67 [0.60, 0.75] (304) | insufficient (17) | insufficient (32) |
| ctl_divyield_gt_2 | 0 | 0.50 [0.44, 0.56] (295) | insufficient (1) | insufficient (14) |
| ctl_divyield_gt_2 | 3 | 0.47 [0.42, 0.53] (278) | insufficient (0) | insufficient (11) |
| ctl_divyield_gt_2 | 6 | 0.41 [0.36, 0.47] (236) | insufficient (1) | insufficient (9) |
| ctl_divyield_gt_2 | 12 | 0.36 [0.32, 0.42] (192) | insufficient (6) | insufficient (8) |

## 7.4 Combinations (2- and 3-signal ANDs), launch_300

Candidates per lag: flags with lift >= 1.5 and >= 100 events at that lag.
catch = launches the combination catches / all launches at that lag. non-null share = rows where every
flag in the combination is non-null / all rows. Ranked by lift, then catch. Top 20 shown; all in
reports/s4_combinations.csv.

- lag 0: h5_peg_lt_05, h9_rs6_top_decile, h9_rs12_top_decile, h10_sponsorship, h11_insider_cluster
- lag 3: h5_peg_lt_05, h9_rs6_top_decile, h9_rs12_top_decile, h10_sponsorship, h11_insider_cluster, ctl_pe_lt_15
- lag 6: h5_peg_lt_05, h9_rs6_top_decile, h9_rs12_top_decile, h10_sponsorship
- lag 12: h9_rs6_top_decile, h9_rs12_top_decile, h10_sponsorship

| combination | lag | rows_true | events | rate_300 | lift | CI low | CI high | catch | non-null share | rate_200 | rate_500 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| h9_rs6_top_decile AND h9_rs12_top_decile | 12 | 15,073 | 247 | 1.64% | 2.87 | 2.54 | 3.25 | 9.5% | 79.9% | 4.46% | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile | 6 | 16,785 | 279 | 1.66% | 2.85 | 2.54 | 3.20 | 10.7% | 87.0% | 3.98% | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile | 3 | 18,067 | 259 | 1.43% | 2.38 | 2.11 | 2.69 | 10.0% | 91.2% | 3.71% | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile | 0 | 20,657 | 289 | 1.40% | 2.16 | 1.93 | 2.43 | 11.1% | 99.0% | 3.36% | insufficient |
| h5_peg_lt_05 AND ctl_pe_lt_15 | 3 | 37,788 | 249 | 0.66% | 2.13 | 1.89 | 2.42 | 9.6% | 43.6% | 2.01% | insufficient |
| h5_peg_lt_05 AND h10_sponsorship AND h11_insider_cluster | 0 | 61 | 1 | insufficient | insufficient | insufficient | insufficient | 0.0% | 18.3% | insufficient | insufficient |
| h5_peg_lt_05 AND h10_sponsorship AND h11_insider_cluster | 3 | 58 | 1 | insufficient | insufficient | insufficient | insufficient | 0.0% | 17.6% | insufficient | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile AND h10_sponsorship | 12 | 508 | 21 | insufficient | insufficient | insufficient | insufficient | 0.8% | 31.9% | insufficient | insufficient |
| h5_peg_lt_05 AND h9_rs6_top_decile AND h10_sponsorship | 6 | 136 | 2 | insufficient | insufficient | insufficient | insufficient | 0.1% | 16.3% | insufficient | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile AND h10_sponsorship | 6 | 622 | 21 | insufficient | insufficient | insufficient | insufficient | 0.8% | 36.3% | insufficient | insufficient |
| h5_peg_lt_05 AND h9_rs6_top_decile AND h10_sponsorship | 3 | 167 | 2 | insufficient | insufficient | insufficient | insufficient | 0.1% | 17.2% | insufficient | insufficient |
| h9_rs6_top_decile AND h10_sponsorship | 12 | 820 | 27 | insufficient | insufficient | insufficient | insufficient | 1.0% | 32.2% | insufficient | insufficient |
| h5_peg_lt_05 AND h11_insider_cluster AND ctl_pe_lt_15 | 3 | 1,325 | 25 | insufficient | insufficient | insufficient | insufficient | 1.0% | 33.9% | insufficient | insufficient |
| h9_rs12_top_decile AND h10_sponsorship | 12 | 853 | 26 | insufficient | insufficient | insufficient | insufficient | 1.0% | 31.9% | insufficient | insufficient |
| h5_peg_lt_05 AND h9_rs12_top_decile AND h10_sponsorship | 6 | 182 | 2 | insufficient | insufficient | insufficient | insufficient | 0.1% | 16.3% | insufficient | insufficient |
| h9_rs12_top_decile AND h10_sponsorship | 6 | 1,040 | 30 | insufficient | insufficient | insufficient | insufficient | 1.2% | 36.3% | insufficient | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile AND h10_sponsorship | 3 | 770 | 22 | insufficient | insufficient | insufficient | insufficient | 0.8% | 38.9% | insufficient | insufficient |
| h5_peg_lt_05 AND h9_rs6_top_decile AND h10_sponsorship | 0 | 206 | 2 | insufficient | insufficient | insufficient | insufficient | 0.1% | 18.3% | insufficient | insufficient |
| h9_rs6_top_decile AND h10_sponsorship | 3 | 1,195 | 34 | insufficient | insufficient | insufficient | insufficient | 1.3% | 39.3% | insufficient | insufficient |
| h9_rs6_top_decile AND h9_rs12_top_decile AND h10_sponsorship | 0 | 1,019 | 29 | insufficient | insufficient | insufficient | insufficient | 1.1% | 42.8% | insufficient | insufficient |

69 combinations evaluated, 5 with >= 100 events.

## Expected launches per ten picks, top ten combinations, by regime bucket

Cell = 10 x (bucket base rate for launch_300) x (combination's overall lift). This assumes the
combination's lift is the same in every regime; section 7.3 shows where single signals are not.
Buckets with fewer than 100 launches read insufficient.

| combination | lag | lift | drawdown 0-10 | drawdown 10-20 | drawdown 20-30 | drawdown >30 | mst 0-12 | mst 13-24 | mst >24 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| h9_rs6_top_decile AND h9_rs12_top_decile | 12 | 2.87 | 0.16 | 0.12 | 0.14 | 0.85 | 0.22 | 0.11 | 0.11 |
| h9_rs6_top_decile AND h9_rs12_top_decile | 6 | 2.85 | 0.15 | 0.12 | 0.14 | 0.85 | 0.21 | 0.11 | 0.11 |
| h9_rs6_top_decile AND h9_rs12_top_decile | 3 | 2.38 | 0.13 | 0.10 | 0.11 | 0.71 | 0.18 | 0.09 | 0.09 |
| h9_rs6_top_decile AND h9_rs12_top_decile | 0 | 2.16 | 0.12 | 0.09 | 0.10 | 0.64 | 0.16 | 0.08 | 0.08 |
| h5_peg_lt_05 AND ctl_pe_lt_15 | 3 | 2.13 | 0.12 | 0.09 | 0.10 | 0.64 | 0.16 | 0.08 | 0.08 |

## 7.5 Control signals

The three controls (pe < 15, pb < 1.5, dividend yield > 2%) are in every table above under ctl_*,
computed identically. Their verdict rows are in the verdict table.

## Single-signal lift, launch_200, by lag

| flag | lag 0 | lag 3 | lag 6 | lag 12 |
| --- | ---: | ---: | ---: | ---: |
| h1_eps_accel | 0.86 [0.76, 0.97] (269) | 1.03 [0.92, 1.14] (315) | 1.10 [0.99, 1.22] (331) | 1.35 [1.22, 1.49] (385) |
| h4_op_leverage | 0.87 [0.78, 0.96] (374) | 0.88 [0.80, 0.98] (372) | 0.91 [0.83, 1.01] (377) | 1.12 [1.03, 1.23] (446) |
| h5_peg_lt_1 | 1.18 [1.12, 1.24] (1336) | 1.21 [1.15, 1.27] (1468) | 1.20 [1.14, 1.26] (1474) | 1.16 [1.10, 1.22] (1366) |
| h5_peg_lt_05 | 1.39 [1.31, 1.48] (1061) | 1.42 [1.34, 1.50] (1152) | 1.39 [1.31, 1.47] (1139) | 1.31 [1.24, 1.40] (1023) |
| h6_compressed_multiple | 1.05 [0.97, 1.14] (612) | 1.15 [1.06, 1.23] (683) | 1.22 [1.13, 1.31] (716) | 1.13 [1.05, 1.22] (641) |
| h7_neglect | 1.39 [1.36, 1.43] (5624) | 1.36 [1.33, 1.40] (5558) | 1.31 [1.28, 1.35] (5405) | 1.28 [1.24, 1.31] (5237) |
| h8_fcf_divergence | 0.51 [0.47, 0.56] (431) | 0.60 [0.55, 0.65] (489) | 0.64 [0.58, 0.69] (506) | 0.68 [0.63, 0.75] (505) |
| h9_rs6_top_decile | 1.65 [1.56, 1.74] (1219) | 1.82 [1.71, 1.92] (1125) | 1.90 [1.80, 2.02] (1090) | 2.13 [2.01, 2.26] (1092) |
| h9_rs12_top_decile | 1.71 [1.62, 1.81] (1237) | 1.88 [1.77, 1.99] (1156) | 2.03 [1.92, 2.15] (1161) | 2.17 [2.04, 2.29] (1116) |
| h10_sponsorship | 1.64 [1.45, 1.85] (249) | 1.73 [1.54, 1.95] (271) | 1.88 [1.68, 2.11] (294) | 1.83 [1.63, 2.06] (269) |
| h11_insider_cluster | 1.74 [1.60, 1.90] (503) | 1.71 [1.56, 1.86] (493) | 1.30 [1.18, 1.43] (381) | 1.12 [1.00, 1.26] (295) |
| h13_stage2 | insufficient (84) | insufficient (98) | 0.76 [0.64, 0.90] (130) | 0.80 [0.68, 0.94] (135) |
| h14_vol_contraction | 1.07 [1.00, 1.15] (774) | 0.92 [0.85, 0.99] (653) | 0.91 [0.84, 0.98] (645) | 0.85 [0.78, 0.92] (562) |
| h15_near_high | 0.51 [0.48, 0.53] (1911) | 0.51 [0.49, 0.53] (1880) | 0.54 [0.52, 0.57] (1961) | 0.60 [0.58, 0.63] (2074) |
| h20_leverage_ok | 1.04 [1.01, 1.07] (4703) | 1.07 [1.04, 1.10] (4856) | 1.10 [1.07, 1.13] (4988) | 1.11 [1.08, 1.14] (4943) |
| h21_no_dilution | 0.72 [0.69, 0.74] (2634) | 0.70 [0.67, 0.72] (2466) | 0.69 [0.66, 0.72] (2355) | 0.70 [0.67, 0.73] (2233) |
| ctl_pe_lt_15 | 1.43 [1.36, 1.49] (1752) | 1.45 [1.39, 1.52] (1826) | 1.30 [1.24, 1.36] (1642) | 1.13 [1.07, 1.19] (1397) |
| ctl_pb_lt_15 | 1.21 [1.16, 1.27] (2005) | 1.11 [1.06, 1.16] (1833) | 0.93 [0.89, 0.98] (1530) | 0.76 [0.72, 0.81] (1203) |
| ctl_divyield_gt_2 | 0.54 [0.51, 0.57] (1004) | 0.50 [0.47, 0.54] (931) | 0.44 [0.41, 0.47] (800) | 0.38 [0.35, 0.41] (652) |

## Single-signal lift, launch_500, by lag

| flag | lag 0 | lag 3 | lag 6 | lag 12 |
| --- | ---: | ---: | ---: | ---: |
| h1_eps_accel | insufficient (9) | insufficient (14) | insufficient (24) | insufficient (31) |
| h4_op_leverage | insufficient (26) | insufficient (24) | insufficient (20) | insufficient (30) |
| h5_peg_lt_1 | insufficient (76) | insufficient (95) | insufficient (84) | insufficient (56) |
| h5_peg_lt_05 | insufficient (68) | insufficient (83) | insufficient (69) | insufficient (39) |
| h6_compressed_multiple | insufficient (29) | insufficient (45) | insufficient (41) | insufficient (24) |
| h7_neglect | 1.51 [1.38, 1.64] (518) | 1.46 [1.33, 1.59] (505) | 1.40 [1.28, 1.53] (491) | 1.38 [1.26, 1.51] (471) |
| h8_fcf_divergence | insufficient (28) | insufficient (32) | insufficient (38) | insufficient (28) |
| h9_rs6_top_decile | 1.99 [1.67, 2.37] (125) | insufficient (98) | 2.31 [1.90, 2.80] (102) | insufficient (94) |
| h9_rs12_top_decile | 1.76 [1.45, 2.13] (105) | 2.41 [2.01, 2.88] (116) | 2.66 [2.21, 3.19] (115) | 2.97 [2.46, 3.59] (108) |
| h10_sponsorship | insufficient (51) | insufficient (42) | insufficient (46) | insufficient (42) |
| h11_insider_cluster | insufficient (56) | insufficient (38) | insufficient (19) | insufficient (28) |
| h13_stage2 | insufficient (10) | insufficient (9) | insufficient (8) | insufficient (10) |
| h14_vol_contraction | insufficient (63) | insufficient (46) | insufficient (50) | insufficient (46) |
| h15_near_high | insufficient (93) | 0.36 [0.30, 0.44] (110) | 0.46 [0.39, 0.54] (135) | 0.49 [0.42, 0.58] (134) |
| h20_leverage_ok | 1.03 [0.93, 1.14] (397) | 1.05 [0.96, 1.16] (406) | 1.10 [1.00, 1.21] (422) | 1.09 [0.99, 1.20] (396) |
| h21_no_dilution | 0.38 [0.31, 0.45] (113) | 0.39 [0.32, 0.47] (111) | 0.42 [0.35, 0.51] (114) | 0.51 [0.43, 0.61] (125) |
| ctl_pe_lt_15 | insufficient (97) | insufficient (93) | insufficient (69) | insufficient (64) |
| ctl_pb_lt_15 | 0.94 [0.79, 1.12] (129) | 0.82 [0.68, 0.99] (112) | 0.74 [0.61, 0.90] (101) | insufficient (80) |
| ctl_divyield_gt_2 | insufficient (41) | insufficient (37) | insufficient (35) | insufficient (30) |
