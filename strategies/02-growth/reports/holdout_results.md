# Holdout results — Section 2 Growth, spec section 8

Window 2020-01 to 2024-06. 135,729 universe stock-months per lag, four lags. 1,698 launch_300
(1.25%) and 3,757 launch_200 (2.77%). Every number comes from src/holdout.py
over the same parquet files as S4. D4 names 2026-06 as the holdout end; 24-month returns are not
observable after 2024-08 decision dates with prices to 2026-09-16, so the window ends 2024-06.

Tested (Matt's S5 brief and section 8): the three build-window PASS flags, the two-horizon strength
combination at every lag, the fifth D8-clearing build combination, and the four backward build
signals inverted. Definitions as in S4: lift among non-null rows, coverage beside it, Wilson CI on
the flagged rate over a fixed base, D8 at 100 launch events. CONFIRM = lift >= 1.5 with
lower CI >= 1.0 on a D8-sufficient cell. Build-window columns are recomputed here with the same
code. No recommendations.

## Reading

This section reads the holdout tables below, 2020-01 to 2024-06, against the build window. It states what confirmed and what did not under the section 8 rule (lift at least 1.5 with a lower bound at least 1.0, on a cell with at least 100 launches). It makes no recommendation; chunk five takes both reports into chat.

**The holdout is a different market.** One stock-month in 80 launched (1,698 of 135,729, 1.25%), nearly twice the build window's 0.66%. Entries in 2020 launched at 1.74%, 2023 at 1.56%, and the first half of 2024 at 2.40%; 2021 entries produced 93 launches on 32,823 rows and cannot be printed. The regime buckets that drove the build window are absent: no month sat deeper than 30% below SPY's high, and the two drawdowns the holdout contains (March 2020, most of 2022) left 34 launches in the 20-30 bucket, too few to read. The 10-20 bucket launched at 1.35% against 1.21% in calm months, and the year after a trough at 2.16% against 1.14%, the same direction as the build window at a smaller distance. Sector rates reordered: Energy led at 2.77% where it had been 0.48%, Healthcare fell from first to 1.32%, and Industrials, Basic Materials, and Technology sat at 1.6% to 1.7%. Financial Services stayed at the bottom by count (89 launches on 22,109 rows).

**Relative strength confirms, at short lags, and the lag pattern reverses.** The 6-month top-decile flag confirms at lag 0 (2.03 [1.83, 2.25], 343 launches) and lag 3 (1.78 [1.57, 2.01]); the 12-month flag confirms at lag 0 (1.63 [1.45, 1.83]) and lag 3 (1.55 [1.36, 1.77]). At lags 6 and 12 neither confirms: 1.49 and 1.16 for the 6-month flag, 1.29 and 1.24 for the 12-month. In the build window the lift rose with lag, from below 2 at lag 0 to 2.4 at lag 12; in the holdout it falls with lag. Strength on the decision date is what carried over; strength a year earlier did not. Inside the calm bucket the 6-month flag confirms at lags 0, 3, and 6 (2.19, 2.02, 1.77) and the 12-month flag at the same three lags; the 10-20 drawdown bucket holds 49 to 81 launches per cell for these flags and cannot be read, so how strength behaved through the 2020 and 2022 drawdowns is not established at D8. At 200% the 6-month flag confirms at lags 0, 3, and 6 and the 12-month at 0 and 3.

**The two-horizon combination confirms at lags 0, 3, and 6.** Both flags together give 2.02 [1.75, 2.34] at lag 0 on 177 launches, catching 10.4% of all holdout launches; 1.88 [1.59, 2.21] at lag 3; 1.57 [1.30, 1.89] at lag 6. Lag 12 has 81 launches and reads insufficient at 1.27. The build window's best cell, 2.87 at lag 12, is the one the holdout cannot confirm. At 200% the pair confirms at the same three lags (1.75, 1.79, 1.64). The pair does not beat the 6-month flag alone at lag 0 (2.02 against 2.03); its lift in the build window came from the lag-12 cells that did not survive.

**Sponsorship does not confirm.** With holdings now covering 95% of rows, the flag runs 1.39 to 1.44 at lags 0 to 6 with lower bounds 1.18 to 1.22, under the 1.5 line at every lag, and at 200% it is 1.08 to 1.12, indistinguishable from nothing. Its build-window pass (2.15 to 2.39) rested on 2014 to 2019 calm-market cells; the holdout's stressed buckets hold 32 to 37 launches for it and stay unreadable, so the calm-only caveat is neither resolved nor lifted. The build window's other D8 combination, PEG under 0.5 with PE under 15, has 79 launches in the holdout at 0.96 and is insufficient; at 200% it is 1.07. Nothing of its build lift of 2.13 carried over.

**None of the inverted signals confirms, and three of the four could not have.** An inverted flag that is true for most rows has a ceiling on its lift of one over its true share: not-near-high is true for 61% of rows (ceiling 1.64), not-fcf-divergence for 90% (1.11), no-or-low-dividend for 74% (1.34). Their holdout lifts are 1.23 to 1.29, 1.03 to 1.05, and 1.14 to 1.15, all with lower bounds above 1.0 and all below 1.5; the build-window recomputation gives 1.51 to 1.64, 1.05 to 1.07, and 1.18 to 1.21. The diluter flag (shares up more than 2% over eight quarters) is true for 41% of rows, ceiling 2.4, and runs 1.40 to 1.44 with lower bounds 1.31 to 1.35: the launch population remained tilted toward companies issuing shares, in the holdout as in the build window, at a lift under the confirmation line overall and above it (1.60 to 1.64) in the year after a trough. These are descriptions of the launch population that held direction out of sample; inverting a backward signal did not produce a confirmed forward one.

**What this report does not say.** It does not rank signals for use. Its confirmations rest on four and a half years that contain one crash, one bear market, and no drawdown beyond 30%. It does not correct for the number of cells tested across both windows. The strength result is the one finding that appears in both windows at the confirmation line; its strongest build-window form, a year of lag, is the form that failed.

## 7.1 Base rates by year (holdout)

| year | rows | launch_300 | rate_300 | launch_200 | rate_200 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2020 | 28,682 | 498 | 1.74% | 1234 | 4.30% |
| 2021 | 32,823 | 93 | insufficient | 235 | 0.72% |
| 2022 | 30,420 | 301 | 0.99% | 723 | 2.38% |
| 2023 | 29,277 | 458 | 1.56% | 938 | 3.20% |
| 2024 | 14,527 | 348 | 2.40% | 627 | 4.32% |
| overall | 135,729 | 1698 | 1.25% | 3757 | 2.77% |

## Base rate inside each regime bucket (holdout)

| bucket type | bucket | rows | launch_300 | rate_300 | launch_200 | rate_200 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| drawdown | 0-10 | 98,461 | 1196 | 1.21% | 2545 | 2.58% |
| drawdown | 10-20 | 34,770 | 468 | 1.35% | 1115 | 3.21% |
| drawdown | 20-30 | 2,498 | 34 | insufficient | 97 | insufficient |
| mst | 0-12 | 121,373 | 1388 | 1.14% | 3187 | 2.63% |
| mst | 13-24 | 14,356 | 310 | 2.16% | 570 | 3.97% |

Buckets absent from the holdout: drawdown >30, months-since-trough >24.

## Launch rate by sector, pooled across the holdout

| sector | rows | launch_300 | rate_300 | launch_200 | rate_200 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Basic Materials | 7,444 | 121 | 1.63% | 270 | 3.63% |
| Communication Services | 5,042 | 29 | insufficient | 106 | 2.10% |
| Consumer Cyclical | 17,141 | 159 | 0.93% | 400 | 2.33% |
| Consumer Defensive | 6,518 | 62 | insufficient | 139 | 2.13% |
| Energy | 6,964 | 193 | 2.77% | 461 | 6.62% |
| Financial Services | 22,109 | 89 | insufficient | 246 | 1.11% |
| Healthcare | 25,674 | 338 | 1.32% | 701 | 2.73% |
| Industrials | 19,046 | 326 | 1.71% | 717 | 3.76% |
| Real Estate | 979 | 3 | insufficient | 5 | insufficient |
| Technology | 21,063 | 340 | 1.61% | 645 | 3.06% |
| Unknown | 1 | 0 | insufficient | 0 | insufficient |
| Utilities | 3,748 | 38 | insufficient | 67 | insufficient |

## 7.2 Single-signal lift, launch_300: build window beside holdout

Build cell = lift [CI] (events) recomputed on 2006-01 to 2019-12. Holdout columns follow.

| flag | lag | build | coverage | true share | rows_true | events | rate | lift | CI low | CI high | holdout |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| h9_rs6_top_decile | 0 | 1.86 [1.70, 2.03] (482) | 99.9% | 10.0% | 13,573 | 343 | 2.53% | 2.03 | 1.83 | 2.25 | CONFIRM |
| h9_rs6_top_decile | 3 | 2.02 [1.84, 2.22] (428) | 93.5% | 9.5% | 12,083 | 250 | 2.07% | 1.78 | 1.57 | 2.01 | CONFIRM |
| h9_rs6_top_decile | 6 | 2.26 [2.06, 2.48] (432) | 90.7% | 9.3% | 11,478 | 199 | 1.73% | 1.49 | 1.30 | 1.71 | not confirmed |
| h9_rs6_top_decile | 12 | 2.40 [2.18, 2.64] (401) | 86.6% | 9.1% | 10,653 | 143 | 1.34% | 1.16 | 0.99 | 1.36 | not confirmed |
| h9_rs12_top_decile | 0 | 1.90 [1.73, 2.07] (478) | 98.4% | 10.0% | 13,385 | 271 | 2.02% | 1.63 | 1.45 | 1.83 | CONFIRM |
| h9_rs12_top_decile | 3 | 2.11 [1.92, 2.31] (439) | 92.3% | 9.7% | 12,171 | 220 | 1.81% | 1.55 | 1.36 | 1.77 | CONFIRM |
| h9_rs12_top_decile | 6 | 2.36 [2.15, 2.58] (447) | 89.6% | 9.6% | 11,649 | 174 | 1.49% | 1.29 | 1.11 | 1.49 | not confirmed |
| h9_rs12_top_decile | 12 | 2.46 [2.23, 2.70] (413) | 85.6% | 9.4% | 10,863 | 154 | 1.42% | 1.24 | 1.06 | 1.45 | not confirmed |
| h10_sponsorship | 0 | 2.17 [1.82, 2.59] (122) | 95.5% | 5.9% | 7,599 | 131 | 1.72% | 1.39 | 1.18 | 1.65 | not confirmed |
| h10_sponsorship | 3 | 2.15 [1.80, 2.55] (124) | 95.0% | 6.0% | 7,693 | 135 | 1.75% | 1.43 | 1.21 | 1.69 | not confirmed |
| h10_sponsorship | 6 | 2.39 [2.03, 2.82] (139) | 94.5% | 5.9% | 7,618 | 135 | 1.77% | 1.44 | 1.22 | 1.70 | not confirmed |
| h10_sponsorship | 12 | 2.22 [1.86, 2.65] (120) | 91.5% | 5.8% | 7,240 | 110 | 1.52% | 1.24 | 1.03 | 1.49 | not confirmed |
| inv_h15_near_high | 0 | 1.64 [1.57, 1.72] (2003) | 98.9% | 60.9% | 81,715 | 1291 | 1.58% | 1.27 | 1.21 | 1.34 | not confirmed |
| inv_h15_near_high | 3 | 1.64 [1.57, 1.71] (1940) | 97.6% | 60.5% | 80,162 | 1226 | 1.53% | 1.23 | 1.17 | 1.30 | not confirmed |
| inv_h15_near_high | 6 | 1.58 [1.51, 1.66] (1803) | 96.3% | 61.3% | 80,058 | 1275 | 1.59% | 1.28 | 1.21 | 1.35 | not confirmed |
| inv_h15_near_high | 12 | 1.51 [1.44, 1.59] (1575) | 93.5% | 61.5% | 78,034 | 1232 | 1.58% | 1.29 | 1.22 | 1.36 | not confirmed |
| inv_h21_no_dilution | 0 | 1.55 [1.47, 1.63] (1522) | 94.0% | 40.8% | 52,071 | 901 | 1.73% | 1.40 | 1.31 | 1.49 | not confirmed |
| inv_h21_no_dilution | 3 | 1.57 [1.50, 1.66] (1504) | 92.6% | 40.7% | 51,134 | 895 | 1.75% | 1.42 | 1.33 | 1.52 | not confirmed |
| inv_h21_no_dilution | 6 | 1.55 [1.47, 1.63] (1444) | 91.2% | 40.6% | 50,236 | 886 | 1.76% | 1.44 | 1.35 | 1.54 | not confirmed |
| inv_h21_no_dilution | 12 | 1.48 [1.41, 1.57] (1303) | 88.5% | 40.6% | 48,773 | 816 | 1.67% | 1.41 | 1.31 | 1.50 | not confirmed |
| inv_h8_fcf_divergence | 0 | 1.07 [1.02, 1.11] (2305) | 97.2% | 90.0% | 118,747 | 1526 | 1.29% | 1.04 | 0.99 | 1.09 | not confirmed |
| inv_h8_fcf_divergence | 3 | 1.06 [1.02, 1.11] (2213) | 95.8% | 89.7% | 116,600 | 1485 | 1.27% | 1.03 | 0.98 | 1.09 | not confirmed |
| inv_h8_fcf_divergence | 6 | 1.05 [1.01, 1.10] (2097) | 94.4% | 89.8% | 115,098 | 1455 | 1.26% | 1.03 | 0.98 | 1.08 | not confirmed |
| inv_h8_fcf_divergence | 12 | 1.06 [1.01, 1.11] (1966) | 91.5% | 89.5% | 111,190 | 1417 | 1.27% | 1.05 | 0.99 | 1.10 | not confirmed |
| inv_ctl_divyield_gt_2 | 0 | 1.18 [1.13, 1.23] (2291) | 100.0% | 74.4% | 100,956 | 1444 | 1.43% | 1.14 | 1.09 | 1.20 | not confirmed |
| inv_ctl_divyield_gt_2 | 3 | 1.18 [1.14, 1.23] (2306) | 99.9% | 74.5% | 101,019 | 1443 | 1.43% | 1.14 | 1.09 | 1.20 | not confirmed |
| inv_ctl_divyield_gt_2 | 6 | 1.20 [1.15, 1.25] (2341) | 99.8% | 74.6% | 101,089 | 1441 | 1.43% | 1.15 | 1.09 | 1.21 | not confirmed |
| inv_ctl_divyield_gt_2 | 12 | 1.21 [1.16, 1.26] (2290) | 98.1% | 74.7% | 99,362 | 1422 | 1.43% | 1.15 | 1.10 | 1.21 | not confirmed |

## 7.2 Single-signal lift, launch_200: build window beside holdout

Build cell = lift [CI] (events) recomputed on 2006-01 to 2019-12. Holdout columns follow.

| flag | lag | build | coverage | true share | rows_true | events | rate | lift | CI low | CI high | holdout |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| h9_rs6_top_decile | 0 | 1.65 [1.56, 1.74] (1219) | 99.9% | 10.0% | 13,573 | 649 | 4.78% | 1.73 | 1.61 | 1.87 | CONFIRM |
| h9_rs6_top_decile | 3 | 1.82 [1.71, 1.92] (1125) | 93.5% | 9.5% | 12,083 | 532 | 4.40% | 1.65 | 1.52 | 1.79 | CONFIRM |
| h9_rs6_top_decile | 6 | 1.90 [1.80, 2.02] (1090) | 90.7% | 9.3% | 11,478 | 463 | 4.03% | 1.52 | 1.39 | 1.66 | CONFIRM |
| h9_rs6_top_decile | 12 | 2.13 [2.01, 2.26] (1092) | 86.6% | 9.1% | 10,653 | 313 | 2.94% | 1.11 | 0.99 | 1.24 | not confirmed |
| h9_rs12_top_decile | 0 | 1.71 [1.62, 1.81] (1237) | 98.4% | 10.0% | 13,385 | 558 | 4.17% | 1.50 | 1.39 | 1.63 | CONFIRM |
| h9_rs12_top_decile | 3 | 1.88 [1.77, 1.99] (1156) | 92.3% | 9.7% | 12,171 | 491 | 4.03% | 1.51 | 1.39 | 1.65 | CONFIRM |
| h9_rs12_top_decile | 6 | 2.03 [1.92, 2.15] (1161) | 89.6% | 9.6% | 11,649 | 414 | 3.55% | 1.34 | 1.22 | 1.47 | not confirmed |
| h9_rs12_top_decile | 12 | 2.17 [2.04, 2.29] (1116) | 85.6% | 9.4% | 10,863 | 303 | 2.79% | 1.06 | 0.95 | 1.18 | not confirmed |
| h10_sponsorship | 0 | 1.64 [1.45, 1.85] (249) | 95.5% | 5.9% | 7,599 | 225 | 2.96% | 1.08 | 0.95 | 1.23 | not confirmed |
| h10_sponsorship | 3 | 1.73 [1.54, 1.95] (271) | 95.0% | 6.0% | 7,693 | 230 | 2.99% | 1.09 | 0.96 | 1.23 | not confirmed |
| h10_sponsorship | 6 | 1.88 [1.68, 2.11] (294) | 94.5% | 5.9% | 7,618 | 235 | 3.08% | 1.12 | 0.98 | 1.27 | not confirmed |
| h10_sponsorship | 12 | 1.83 [1.63, 2.06] (269) | 91.5% | 5.8% | 7,240 | 222 | 3.07% | 1.12 | 0.98 | 1.27 | not confirmed |
| inv_h15_near_high | 0 | 1.53 [1.49, 1.57] (5365) | 98.9% | 60.9% | 81,715 | 2862 | 3.50% | 1.27 | 1.22 | 1.31 | not confirmed |
| inv_h15_near_high | 3 | 1.53 [1.49, 1.57] (5205) | 97.6% | 60.5% | 80,162 | 2676 | 3.34% | 1.20 | 1.16 | 1.25 | not confirmed |
| inv_h15_near_high | 6 | 1.50 [1.46, 1.54] (4934) | 96.3% | 61.3% | 80,058 | 2745 | 3.43% | 1.23 | 1.19 | 1.28 | not confirmed |
| inv_h15_near_high | 12 | 1.45 [1.41, 1.49] (4418) | 93.5% | 61.5% | 78,034 | 2690 | 3.45% | 1.25 | 1.20 | 1.30 | not confirmed |
| inv_h21_no_dilution | 0 | 1.37 [1.33, 1.41] (3908) | 94.0% | 40.8% | 52,071 | 1848 | 3.55% | 1.28 | 1.23 | 1.34 | not confirmed |
| inv_h21_no_dilution | 3 | 1.39 [1.35, 1.43] (3864) | 92.6% | 40.7% | 51,134 | 1827 | 3.57% | 1.30 | 1.24 | 1.36 | not confirmed |
| inv_h21_no_dilution | 6 | 1.39 [1.35, 1.44] (3782) | 91.2% | 40.6% | 50,236 | 1819 | 3.62% | 1.32 | 1.26 | 1.38 | not confirmed |
| inv_h21_no_dilution | 12 | 1.37 [1.33, 1.41] (3547) | 88.5% | 40.6% | 48,773 | 1759 | 3.61% | 1.33 | 1.27 | 1.39 | not confirmed |
| inv_h8_fcf_divergence | 0 | 1.07 [1.04, 1.09] (6627) | 97.2% | 90.0% | 118,747 | 3395 | 2.86% | 1.03 | 1.00 | 1.06 | not confirmed |
| inv_h8_fcf_divergence | 3 | 1.05 [1.03, 1.08] (6366) | 95.8% | 89.7% | 116,600 | 3311 | 2.84% | 1.02 | 0.99 | 1.06 | not confirmed |
| inv_h8_fcf_divergence | 6 | 1.05 [1.02, 1.08] (6125) | 94.4% | 89.8% | 115,098 | 3245 | 2.82% | 1.02 | 0.99 | 1.06 | not confirmed |
| inv_h8_fcf_divergence | 12 | 1.04 [1.02, 1.07] (5716) | 91.5% | 89.5% | 111,190 | 3152 | 2.83% | 1.03 | 1.00 | 1.07 | not confirmed |
| inv_ctl_divyield_gt_2 | 0 | 1.16 [1.13, 1.18] (6402) | 100.0% | 74.4% | 100,956 | 3085 | 3.06% | 1.10 | 1.07 | 1.14 | not confirmed |
| inv_ctl_divyield_gt_2 | 3 | 1.16 [1.14, 1.19] (6469) | 99.9% | 74.5% | 101,019 | 3087 | 3.06% | 1.10 | 1.07 | 1.14 | not confirmed |
| inv_ctl_divyield_gt_2 | 6 | 1.18 [1.15, 1.21] (6590) | 99.8% | 74.6% | 101,089 | 3088 | 3.05% | 1.11 | 1.07 | 1.14 | not confirmed |
| inv_ctl_divyield_gt_2 | 12 | 1.20 [1.17, 1.23] (6512) | 98.1% | 74.7% | 99,362 | 3099 | 3.12% | 1.12 | 1.09 | 1.16 | not confirmed |

### Verdicts (section 8 CONFIRM rule)

| flag | why tested | launch_300 | confirming lags 300 | confirming lags 200 | best holdout cell (300) |
| --- | --- | --- | ---: | ---: | ---: |
| h9_rs6_top_decile | PASS in build (lags 3, 6, 12) | CONFIRMS | 0,3 | 0,3,6 | 2.03 [1.83, 2.25] at lag 0 |
| h9_rs12_top_decile | PASS in build (lags 3, 6, 12) | CONFIRMS | 0,3 | 0,3 | 1.63 [1.45, 1.83] at lag 0 |
| h10_sponsorship | PASS in build, calm-only: 2014-2019 data, no bear-market cell | NOT CONFIRMED | - | - | 1.44 [1.22, 1.70] at lag 6 |
| inv_h15_near_high | inverted: NOT near 52-week high (build lift 0.40-0.55) | NOT CONFIRMED | - | - | 1.29 [1.22, 1.36] at lag 12 |
| inv_h21_no_dilution | inverted: shares up more than 2% over 8 quarters (build lift 0.55-0.61) | NOT CONFIRMED | - | - | 1.44 [1.35, 1.54] at lag 6 |
| inv_h8_fcf_divergence | inverted: NOT fcf_divergence (build lift 0.51-0.61) | NOT CONFIRMED | - | - | 1.05 [0.99, 1.10] at lag 12 |
| inv_ctl_divyield_gt_2 | inverted: dividend yield <= 2% or none (build lift 0.34-0.47) | NOT CONFIRMED | - | - | 1.15 [1.10, 1.21] at lag 12 |

## 7.3 Holdout lift within each SPY drawdown bucket, launch_300

| flag | lag | 0-10 | 10-20 | 20-30 |
| --- | --- | ---: | ---: | ---: |
| h9_rs6_top_decile | 0 | 2.19 [1.94, 2.47] (260) CONFIRM | insufficient (81) | insufficient (2) |
| h9_rs6_top_decile | 3 | 2.02 [1.76, 2.31] (199) CONFIRM | insufficient (49) | insufficient (2) |
| h9_rs6_top_decile | 6 | 1.77 [1.52, 2.06] (164) CONFIRM | insufficient (33) | insufficient (2) |
| h9_rs6_top_decile | 12 | insufficient (98) | insufficient (41) | insufficient (4) |
| h9_rs12_top_decile | 0 | 1.86 [1.63, 2.12] (218) CONFIRM | insufficient (51) | insufficient (2) |
| h9_rs12_top_decile | 3 | 1.81 [1.57, 2.09] (180) CONFIRM | insufficient (38) | insufficient (2) |
| h9_rs12_top_decile | 6 | 1.51 [1.29, 1.78] (143) CONFIRM | insufficient (28) | insufficient (3) |
| h9_rs12_top_decile | 12 | 1.25 [1.04, 1.50] (111) | insufficient (40) | insufficient (3) |
| h10_sponsorship | 0 | insufficient (92) | insufficient (34) | insufficient (5) |
| h10_sponsorship | 3 | insufficient (94) | insufficient (37) | insufficient (4) |
| h10_sponsorship | 6 | insufficient (94) | insufficient (36) | insufficient (5) |
| h10_sponsorship | 12 | insufficient (75) | insufficient (32) | insufficient (3) |
| inv_h15_near_high | 0 | 1.32 [1.24, 1.41] (871) | 1.18 [1.07, 1.30] (387) | insufficient (33) |
| inv_h15_near_high | 3 | 1.27 [1.19, 1.36] (847) | 1.15 [1.03, 1.27] (347) | insufficient (32) |
| inv_h15_near_high | 6 | 1.32 [1.24, 1.41] (894) | 1.19 [1.07, 1.32] (357) | insufficient (24) |
| inv_h15_near_high | 12 | 1.27 [1.20, 1.36] (925) | 1.33 [1.18, 1.49] (286) | insufficient (21) |
| inv_h21_no_dilution | 0 | 1.40 [1.29, 1.51] (650) | 1.42 [1.25, 1.61] (236) | insufficient (15) |
| inv_h21_no_dilution | 3 | 1.42 [1.32, 1.54] (650) | 1.43 [1.26, 1.63] (230) | insufficient (15) |
| inv_h21_no_dilution | 6 | 1.46 [1.35, 1.57] (648) | 1.40 [1.23, 1.60] (221) | insufficient (17) |
| inv_h21_no_dilution | 12 | 1.45 [1.34, 1.56] (604) | 1.31 [1.14, 1.50] (198) | insufficient (14) |
| inv_h8_fcf_divergence | 0 | 1.03 [0.97, 1.09] (1087) | 1.06 [0.96, 1.16] (410) | insufficient (29) |
| inv_h8_fcf_divergence | 3 | 1.02 [0.96, 1.08] (1052) | 1.07 [0.97, 1.17] (405) | insufficient (28) |
| inv_h8_fcf_divergence | 6 | 1.03 [0.97, 1.09] (1038) | 1.04 [0.95, 1.15] (391) | insufficient (26) |
| inv_h8_fcf_divergence | 12 | 1.06 [1.00, 1.13] (1030) | 1.01 [0.91, 1.12] (360) | insufficient (27) |
| inv_ctl_divyield_gt_2 | 0 | 1.14 [1.07, 1.21] (1016) | 1.15 [1.04, 1.27] (398) | insufficient (30) |
| inv_ctl_divyield_gt_2 | 3 | 1.15 [1.08, 1.22] (1014) | 1.13 [1.02, 1.24] (398) | insufficient (31) |
| inv_ctl_divyield_gt_2 | 6 | 1.16 [1.09, 1.23] (1015) | 1.11 [1.01, 1.23] (396) | insufficient (30) |
| inv_ctl_divyield_gt_2 | 12 | 1.18 [1.11, 1.25] (1010) | 1.09 [0.98, 1.20] (382) | insufficient (30) |

## 7.3 Holdout lift within each SPY drawdown bucket, launch_200

| flag | lag | 0-10 | 10-20 | 20-30 |
| --- | --- | ---: | ---: | ---: |
| h9_rs6_top_decile | 0 | 1.85 [1.69, 2.02] (469) CONFIRM | 1.54 [1.33, 1.78] (172) CONFIRM | insufficient (8) |
| h9_rs6_top_decile | 3 | 1.87 [1.70, 2.06] (405) CONFIRM | 1.24 [1.04, 1.48] (120) | insufficient (7) |
| h9_rs6_top_decile | 6 | 1.73 [1.56, 1.92] (353) CONFIRM | 1.12 [0.93, 1.35] (103) | insufficient (7) |
| h9_rs6_top_decile | 12 | 1.17 [1.03, 1.33] (221) | insufficient (83) | insufficient (9) |
| h9_rs12_top_decile | 0 | 1.67 [1.52, 1.84] (421) CONFIRM | 1.19 [1.01, 1.41] (131) | insufficient (6) |
| h9_rs12_top_decile | 3 | 1.75 [1.58, 1.93] (382) CONFIRM | 1.04 [0.86, 1.26] (102) | insufficient (7) |
| h9_rs12_top_decile | 6 | 1.53 [1.38, 1.71] (318) CONFIRM | insufficient (87) | insufficient (9) |
| h9_rs12_top_decile | 12 | 1.10 [0.96, 1.25] (214) | insufficient (83) | insufficient (6) |
| h10_sponsorship | 0 | 1.04 [0.89, 1.22] (152) | insufficient (64) | insufficient (9) |
| h10_sponsorship | 3 | 1.00 [0.85, 1.17] (150) | insufficient (71) | insufficient (9) |
| h10_sponsorship | 6 | 1.09 [0.93, 1.27] (158) | insufficient (69) | insufficient (8) |
| h10_sponsorship | 12 | 1.09 [0.93, 1.27] (149) | insufficient (64) | insufficient (9) |
| inv_h15_near_high | 0 | 1.31 [1.25, 1.37] (1852) | 1.16 [1.09, 1.24] (918) | insufficient (92) |
| inv_h15_near_high | 3 | 1.25 [1.20, 1.31] (1793) | 1.08 [1.01, 1.15] (792) | insufficient (91) |
| inv_h15_near_high | 6 | 1.27 [1.21, 1.32] (1836) | 1.14 [1.07, 1.22] (834) | insufficient (75) |
| inv_h15_near_high | 12 | 1.24 [1.19, 1.29] (1928) | 1.30 [1.21, 1.40] (699) | insufficient (63) |
| inv_h21_no_dilution | 0 | 1.30 [1.23, 1.37] (1294) | 1.26 [1.16, 1.37] (517) | insufficient (37) |
| inv_h21_no_dilution | 3 | 1.33 [1.26, 1.40] (1292) | 1.25 [1.15, 1.37] (499) | insufficient (36) |
| inv_h21_no_dilution | 6 | 1.35 [1.28, 1.43] (1293) | 1.24 [1.14, 1.35] (487) | insufficient (39) |
| inv_h21_no_dilution | 12 | 1.37 [1.30, 1.45] (1250) | 1.23 [1.12, 1.34] (469) | insufficient (40) |
| inv_h8_fcf_divergence | 0 | 1.03 [0.98, 1.07] (2323) | 1.04 [0.98, 1.11] (982) | insufficient (90) |
| inv_h8_fcf_divergence | 3 | 1.02 [0.98, 1.06] (2259) | 1.04 [0.98, 1.11] (965) | insufficient (87) |
| inv_h8_fcf_divergence | 6 | 1.02 [0.98, 1.06] (2211) | 1.03 [0.96, 1.09] (949) | insufficient (85) |
| inv_h8_fcf_divergence | 12 | 1.04 [1.00, 1.09] (2182) | 1.00 [0.94, 1.07] (886) | insufficient (84) |
| inv_ctl_divyield_gt_2 | 0 | 1.10 [1.05, 1.14] (2080) | 1.12 [1.05, 1.19] (923) | insufficient (82) |
| inv_ctl_divyield_gt_2 | 3 | 1.10 [1.05, 1.15] (2073) | 1.11 [1.04, 1.18] (931) | insufficient (83) |
| inv_ctl_divyield_gt_2 | 6 | 1.11 [1.06, 1.16] (2077) | 1.09 [1.02, 1.16] (926) | insufficient (85) |
| inv_ctl_divyield_gt_2 | 12 | 1.13 [1.09, 1.18] (2083) | 1.09 [1.02, 1.16] (927) | insufficient (89) |

## 7.3 Holdout lift within each months-since-trough bucket, launch_300

| flag | lag | 0-12 | 13-24 |
| --- | --- | ---: | ---: |
| h9_rs6_top_decile | 0 | 1.95 [1.73, 2.19] (270) CONFIRM | insufficient (73) |
| h9_rs6_top_decile | 3 | 1.51 [1.31, 1.75] (174) CONFIRM | insufficient (76) |
| h9_rs6_top_decile | 6 | 1.33 [1.13, 1.56] (143) | insufficient (56) |
| h9_rs6_top_decile | 12 | 1.09 [0.91, 1.32] (110) | insufficient (33) |
| h9_rs12_top_decile | 0 | 1.47 [1.28, 1.69] (200) | insufficient (71) |
| h9_rs12_top_decile | 3 | 1.26 [1.07, 1.48] (145) | insufficient (75) |
| h9_rs12_top_decile | 6 | 1.03 [0.86, 1.24] (112) | insufficient (62) |
| h9_rs12_top_decile | 12 | 1.23 [1.03, 1.46] (124) | insufficient (30) |
| h10_sponsorship | 0 | 1.32 [1.08, 1.59] (102) | insufficient (29) |
| h10_sponsorship | 3 | 1.35 [1.11, 1.63] (104) | insufficient (31) |
| h10_sponsorship | 6 | 1.37 [1.13, 1.65] (106) | insufficient (29) |
| h10_sponsorship | 12 | insufficient (88) | insufficient (22) |
| inv_h15_near_high | 0 | 1.30 [1.23, 1.38] (1101) | 1.20 [1.04, 1.38] (190) |
| inv_h15_near_high | 3 | 1.27 [1.19, 1.35] (1034) | 1.09 [0.94, 1.25] (192) |
| inv_h15_near_high | 6 | 1.32 [1.24, 1.40] (1070) | 1.13 [0.98, 1.29] (205) |
| inv_h15_near_high | 12 | 1.29 [1.22, 1.38] (993) | 1.22 [1.08, 1.39] (239) |
| inv_h21_no_dilution | 0 | 1.37 [1.27, 1.47] (724) | 1.64 [1.42, 1.90] (177) CONFIRM |
| inv_h21_no_dilution | 3 | 1.40 [1.30, 1.50] (720) | 1.61 [1.40, 1.87] (175) CONFIRM |
| inv_h21_no_dilution | 6 | 1.42 [1.32, 1.53] (713) | 1.60 [1.38, 1.86] (173) CONFIRM |
| inv_h21_no_dilution | 12 | 1.36 [1.26, 1.47] (642) | 1.64 [1.42, 1.90] (174) CONFIRM |
| inv_h8_fcf_divergence | 0 | 1.03 [0.98, 1.09] (1247) | 1.06 [0.95, 1.19] (279) |
| inv_h8_fcf_divergence | 3 | 1.04 [0.98, 1.10] (1217) | 1.01 [0.89, 1.13] (268) |
| inv_h8_fcf_divergence | 6 | 1.04 [0.99, 1.10] (1197) | 0.98 [0.87, 1.11] (258) |
| inv_h8_fcf_divergence | 12 | 1.04 [0.98, 1.10] (1142) | 1.09 [0.97, 1.23] (275) |
| inv_ctl_divyield_gt_2 | 0 | 1.13 [1.07, 1.19] (1171) | 1.25 [1.11, 1.41] (273) |
| inv_ctl_divyield_gt_2 | 3 | 1.13 [1.07, 1.20] (1174) | 1.24 [1.10, 1.40] (269) |
| inv_ctl_divyield_gt_2 | 6 | 1.13 [1.07, 1.20] (1173) | 1.24 [1.10, 1.40] (268) |
| inv_ctl_divyield_gt_2 | 12 | 1.15 [1.09, 1.22] (1163) | 1.18 [1.05, 1.33] (259) |

## 7.3 Holdout lift within each months-since-trough bucket, launch_200

| flag | lag | 0-12 | 13-24 |
| --- | --- | ---: | ---: |
| h9_rs6_top_decile | 0 | 1.66 [1.53, 1.80] (529) CONFIRM | 2.13 [1.79, 2.52] (120) CONFIRM |
| h9_rs6_top_decile | 3 | 1.46 [1.33, 1.61] (400) | 2.72 [2.31, 3.20] (132) CONFIRM |
| h9_rs6_top_decile | 6 | 1.38 [1.24, 1.53] (353) | 2.27 [1.89, 2.71] (110) CONFIRM |
| h9_rs6_top_decile | 12 | 1.00 [0.89, 1.14] (241) | insufficient (72) |
| h9_rs12_top_decile | 0 | 1.35 [1.23, 1.48] (425) | 2.37 [2.01, 2.78] (133) CONFIRM |
| h9_rs12_top_decile | 3 | 1.27 [1.14, 1.41] (349) | 2.84 [2.43, 3.31] (142) CONFIRM |
| h9_rs12_top_decile | 6 | 1.14 [1.02, 1.27] (295) | 2.38 [2.00, 2.82] (119) CONFIRM |
| h9_rs12_top_decile | 12 | 1.04 [0.92, 1.17] (250) | insufficient (53) |
| h10_sponsorship | 0 | 1.04 [0.91, 1.20] (186) | insufficient (39) |
| h10_sponsorship | 3 | 1.05 [0.91, 1.21] (189) | insufficient (41) |
| h10_sponsorship | 6 | 1.07 [0.93, 1.23] (192) | insufficient (43) |
| h10_sponsorship | 12 | 1.12 [0.98, 1.29] (193) | insufficient (29) |
| inv_h15_near_high | 0 | 1.30 [1.25, 1.35] (2534) | 1.11 [1.00, 1.24] (328) |
| inv_h15_near_high | 3 | 1.23 [1.18, 1.28] (2332) | 1.04 [0.94, 1.16] (344) |
| inv_h15_near_high | 6 | 1.27 [1.22, 1.32] (2392) | 1.04 [0.94, 1.15] (353) |
| inv_h15_near_high | 12 | 1.26 [1.21, 1.31] (2268) | 1.16 [1.06, 1.28] (422) |
| inv_h21_no_dilution | 0 | 1.25 [1.19, 1.31] (1534) | 1.58 [1.42, 1.75] (314) CONFIRM |
| inv_h21_no_dilution | 3 | 1.26 [1.20, 1.33] (1515) | 1.56 [1.40, 1.73] (312) CONFIRM |
| inv_h21_no_dilution | 6 | 1.29 [1.22, 1.35] (1510) | 1.54 [1.39, 1.72] (309) CONFIRM |
| inv_h21_no_dilution | 12 | 1.28 [1.21, 1.34] (1436) | 1.63 [1.46, 1.81] (323) CONFIRM |
| inv_h8_fcf_divergence | 0 | 1.03 [0.99, 1.06] (2877) | 1.06 [0.97, 1.15] (518) |
| inv_h8_fcf_divergence | 3 | 1.03 [0.99, 1.06] (2807) | 1.02 [0.93, 1.11] (504) |
| inv_h8_fcf_divergence | 6 | 1.03 [0.99, 1.07] (2763) | 0.99 [0.90, 1.08] (482) |
| inv_h8_fcf_divergence | 12 | 1.03 [0.99, 1.06] (2641) | 1.08 [0.99, 1.18] (511) |
| inv_ctl_divyield_gt_2 | 0 | 1.08 [1.04, 1.12] (2576) | 1.27 [1.17, 1.38] (509) |
| inv_ctl_divyield_gt_2 | 3 | 1.08 [1.04, 1.12] (2585) | 1.25 [1.15, 1.36] (502) |
| inv_ctl_divyield_gt_2 | 6 | 1.09 [1.05, 1.13] (2590) | 1.24 [1.14, 1.35] (498) |
| inv_ctl_divyield_gt_2 | 12 | 1.12 [1.07, 1.16] (2614) | 1.19 [1.09, 1.29] (485) |

## 7.4 Combinations: build window beside holdout

The two-horizon strength pair at every lag, and PEG < 0.5 AND PE < 15 at lag 3 (the fifth build
combination that met D8). catch = launches caught / all holdout launches at that lag.

| combination | lag | build (300) | rows_true | events_300 | rate_300 | lift_300 | CI low | CI high | catch_300 | holdout 300 | events_200 | lift_200 | CI low 200 | holdout 200 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| h9_rs6_top_decile AND h9_rs12_top_decile | 0 | 2.16 [1.93, 2.43] (289) | 7,057 | 177 | 2.51% | 2.02 | 1.75 | 2.34 | 10.4% | CONFIRM | 343 | 1.75 | 1.58 | CONFIRM |
| h9_rs6_top_decile AND h9_rs12_top_decile | 3 | 2.38 [2.11, 2.69] (259) | 6,276 | 137 | 2.18% | 1.88 | 1.59 | 2.21 | 8.1% | CONFIRM | 300 | 1.79 | 1.60 | CONFIRM |
| h9_rs6_top_decile AND h9_rs12_top_decile | 6 | 2.85 [2.54, 3.20] (279) | 5,981 | 109 | 1.82% | 1.57 | 1.30 | 1.89 | 6.4% | CONFIRM | 261 | 1.64 | 1.46 | CONFIRM |
| h9_rs6_top_decile AND h9_rs12_top_decile | 12 | 2.87 [2.54, 3.25] (247) | 5,571 | 81 | insufficient | insufficient | insufficient | insufficient | 4.8% | insufficient | 167 | 1.14 | 0.98 | not confirmed |
| h5_peg_lt_05 AND ctl_pe_lt_15 | 3 | 2.13 [1.89, 2.42] (249) | 14,924 | 79 | insufficient | insufficient | insufficient | insufficient | 4.7% | insufficient | 277 | 1.07 | 0.95 | not confirmed |
