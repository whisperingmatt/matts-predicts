# Decile retest — holdout results (GROWTH-002, S7). End of chunk 4b.

Holdout 2020-01 to 2025-06 (E4). 164,889 universe stock-months per lag, four lags. win_50 27,999
(16.98%), win_100 9,636 (5.84%). launch_300 is observable only through 2024-08
decision dates: 140,595 rows carry it in the holdout, 1,797 launches. Every number comes from
src/decile_holdout.py over the same parquet files as S6; the build window is recomputed with the same code.

Definitions as in reports/decile_build_results.md. Composite recipe (S7): mean of raw percentile ranks,
LOW features as 1 - rank, over rows where every member is non-null, then deciles per (month_end, lag). Full
section 3 pass = build PASS-build and holdout lift >= 1.5 with lower bound >= 1.2 at the same lag.
The realized-volatility block is exploratory and outside the pass criteria. No recommendations.

## Reading

This section reads the holdout tables below (2020-01 to 2025-06) against the build window under GROWTH-002 section 3. A feature is CONFIRMED on a label only where its declared extreme decile passed the build half and also clears lift 1.5 with a lower bound of 1.2 in the holdout, at the same lag. The composite uses the S7 recipe (mean of raw percentile ranks). The realized-volatility block at the end is exploratory, outside every pass criterion, and carries no verdict. No recommendation is made; chunk 4b ends with this report.

**No feature passes the full criterion on win_50.** None passed the build half, so none can be confirmed, and the holdout does not change that: the best declared cell on win_50 is price-to-earnings' cheapest decile at 1.40 [1.35, 1.45], then price-to-book at 1.32, then the momentum flags at 1.21 to 1.23. The holdout base is high, one stock-month in six (16.98%), driven by 2020 entries at 40.81% and 2025 entries at 21.26%; 2021 entries won at 5.80%. As in the build window, the year of entry moves the base more than any feature does.

**Four confirmations, all on the rarer labels, all on price.** Market cap, declared LOW-better, is CONFIRMED on win_100 at every lag (holdout smallest decile 1.65 [1.58, 1.73] on 1,594 events against 2.03 in the build) and on launch_300 at every lag (2.19 [1.99, 2.41] on 394 events against 2.32). PEG and PEGY are CONFIRMED on win_100 at lags 0 and 3 (1.64 [1.48, 1.82] and 1.68 [1.52, 1.86]) and fall short at lags 6 and 12. The zero-dividend decile, PASS-build on win_100 at lags 6 and 12, is NOT CONFIRMED (1.31 in the holdout). Small, cheap on earnings growth, and the doubling label: that is the whole confirmed set, and it is the same population the build window pointed at.

**Several features clear the holdout bar without a build pass.** Price-to-earnings' cheapest decile reaches 1.82 [1.71, 1.94] on win_100 at every lag and 1.84 on launch_300 at lags 6 and 12; price-to-book 2.07 on launch_300; operating-margin change 2.02 on launch_300 at every lag; both momentum flags and distance above the 30-week average 1.57 to 2.06 on win_100 and launch_300 at lags 0 to 6; ownership change 1.66 on launch_300 at lags 3 to 12. None of these passed the build half, in most cases because their build curves were U-shaped rather than because the extreme cell was weak. Under E6 they stay unconfirmed. The U-shape persists in the holdout: 12-month strength runs 1.45 in decile 1, 0.79 in decile 7, 1.23 in decile 10.

**The three backward features stay backward.** Distance from the 52-week high rises from 0.68 in decile 1 to 1.42 in decile 10 on win_50 in the holdout, as it did in the build window. Share issuance and negative shareholder yield lean the same way at smaller amplitude (1.09 to 1.14 in the issuing deciles against 0.86 to 0.95 in the buyback deciles). They were declared the other way and fail; they are not re-declared.

**The composite is a weak object in both windows.** Its members are the unconfirmed top three from the build window (12-month strength, PE versus own 5-year median, ownership change). With the S7 recipe, composite decile 10 holds 2.9% of build rows and 6.1% of holdout rows (the ownership term limits coverage to 29% and 61%), and deciles 8 to 10 hold 8.8% and 18.1%. On win_50 the holdout top decile lifts 1.16 [1.11, 1.21] on 1,751 events, against 1.12 in the build; on win_100 1.41 [1.30, 1.53] against 1.50; on launch_300 70 events, unreadable. It clears neither the 1.5 line nor its own best member. By regime, the top decile is 1.14 in calm months and 1.20 in the 10% to 20% drawdown bucket; the 20% to 30% bucket has 39 events.

**Expected wins per ten picks.** Ten holdout picks from composite decile 10 carry an expected 2.0 win_50 outcomes in the calm bucket, 1.8 in the 10-20 bucket, 1.7 in the 20-30 bucket, and 2.0 in either months-since-trough bucket; from deciles 8 to 10, 1.6 to 1.8. Ten random universe picks carry 1.7 in the holdout overall. The composite adds roughly a third of a win per ten picks, and the arithmetic assumes its lift holds across regimes, which the bucket table shows only for the two buckets with enough events.

**Exploratory: realized volatility is the largest monotone structure in the study, and it is not a declared feature.** Twelve-month realized volatility, ranked like the others, gives a decile curve that rises without a break in both windows: on win_50 from 0.24 (decile 1) to 1.57 (decile 10) in the build and 0.29 to 1.36 in the holdout; on win_100 from an unreadable decile 1 to 2.90 and 2.31; on launch_300 to 4.13 and 3.75 at the top decile on 1,049 and 662 events. Its decile correlates with market cap at −0.51 (build) and −0.47 (holdout), with distance from the 52-week high at +0.48 and +0.54, and with share issuance at +0.32 and +0.41. The confirmed size result, the backward high-distance and issuance results, and the U-shaped momentum tail all sit inside the population this one number describes: high-volatility stocks reach any fixed gain threshold more often because their outcomes are wider in both directions. This block declared no direction and passes nothing. The base-rate difference between buying a stock that can move 50% in a year and one that cannot is not a signal about which will.

**What this report does not say.** It does not rank features for use. It does not say what the twelve-month drawdown of the high-volatility deciles looks like, because no loss label was specified in either spec; a label that pays for reaching +50% and does not charge for reaching −50% rewards dispersion, and that is what these tables measure. It does not correct for the number of cells. It does not re-declare anything. Chunk 4b is complete; both GROWTH-001 reports and both GROWTH-002 reports go to chat as the inputs to whatever comes next.

## Base rates by year (holdout)

| year | rows | win_50 | rate_50 | win_100 | rate_100 | rows with launch_300 | launch_300 | rate_300 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2020 | 28,682 | 11706 | 40.81% | 4730 | 16.49% | 28,682 | 498 | 1.74% |
| 2021 | 32,823 | 1905 | 5.80% | 453 | 1.38% | 32,823 | 93 | insufficient |
| 2022 | 30,420 | 2845 | 9.35% | 717 | 2.36% | 30,420 | 301 | 0.99% |
| 2023 | 29,277 | 5093 | 17.40% | 1317 | 4.50% | 29,277 | 458 | 1.56% |
| 2024 | 29,221 | 3375 | 11.55% | 1060 | 3.63% | 19,393 | 447 | 2.30% |
| 2025 | 14,466 | 3075 | 21.26% | 1359 | 9.39% | 0 | - | - |

## Base rate inside each regime bucket (holdout)

| bucket type | bucket | rows | win_50 | rate_50 | win_100 | rate_100 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| drawdown | 0-10 | 127,621 | 22102 | 17.32% | 7685 | 6.02% |
| drawdown | 10-20 | 34,770 | 5529 | 15.90% | 1869 | 5.38% |
| drawdown | 20-30 | 2,498 | 368 | 14.73% | 82 | insufficient |
| mst | 0-12 | 150,533 | 25542 | 16.97% | 8954 | 5.95% |
| mst | 13-24 | 14,356 | 2457 | 17.11% | 682 | 4.75% |

Buckets absent from the holdout: drawdown >30, months-since-trough >24.

## Extreme-decile cells, win_50: build beside holdout

Build and holdout cells = lift [CI] (events). rho = Spearman over D8 deciles in that window.

| feature | dir | lag | build | rho | build verdict | hold. coverage | hold. cell share | holdout | rho | holdout |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 0 | 1.29 [1.26, 1.32] (5927) | -0.20 |  | 99.9% | 10.0% | 1.19 [1.16, 1.23] (3339) | -0.37 |  |
| ret_6m_skip1 | HIGH | 3 | 1.33 [1.30, 1.37] (6136) | -0.12 |  | 99.5% | 10.0% | 1.21 [1.17, 1.25] (3378) | -0.31 |  |
| ret_6m_skip1 | HIGH | 6 | 1.33 [1.30, 1.36] (6069) | 0.08 |  | 98.6% | 10.0% | 1.21 [1.17, 1.24] (3344) | -0.22 |  |
| ret_6m_skip1 | HIGH | 12 | 1.33 [1.29, 1.36] (5852) | -0.18 |  | 96.2% | 10.0% | 1.17 [1.13, 1.21] (3171) | -0.39 |  |
| ret_12m_skip1 | HIGH | 0 | 1.30 [1.27, 1.33] (5915) | -0.18 |  | 98.6% | 10.0% | 1.23 [1.19, 1.26] (3394) | -0.37 |  |
| ret_12m_skip1 | HIGH | 3 | 1.36 [1.33, 1.39] (6105) | -0.15 |  | 97.4% | 10.0% | 1.23 [1.19, 1.26] (3360) | -0.38 |  |
| ret_12m_skip1 | HIGH | 6 | 1.38 [1.35, 1.42] (6114) | -0.04 |  | 96.2% | 10.0% | 1.19 [1.16, 1.23] (3238) | -0.43 |  |
| ret_12m_skip1 | HIGH | 12 | 1.35 [1.32, 1.38] (5754) | -0.07 |  | 93.8% | 10.0% | 1.13 [1.10, 1.17] (2987) | -0.53 |  |
| eps_growth_q0 | HIGH | 0 | 1.09 [1.06, 1.13] (3570) | -0.25 |  | 67.3% | 10.0% | 1.17 [1.12, 1.21] (2101) | -0.19 |  |
| eps_growth_q0 | HIGH | 3 | 1.12 [1.09, 1.15] (3606) | -0.25 |  | 66.9% | 10.0% | 1.14 [1.10, 1.19] (2058) | -0.13 |  |
| eps_growth_q0 | HIGH | 6 | 1.17 [1.13, 1.20] (3721) | -0.09 |  | 66.4% | 10.0% | 1.13 [1.09, 1.17] (2025) | -0.14 |  |
| eps_growth_q0 | HIGH | 12 | 1.24 [1.20, 1.27] (3834) | 0.15 |  | 65.0% | 10.0% | 1.10 [1.06, 1.15] (1918) | -0.24 |  |
| rev_growth_accel | HIGH | 0 | 1.13 [1.10, 1.16] (4722) | -0.39 |  | 89.9% | 10.0% | 1.15 [1.12, 1.19] (2924) | -0.12 |  |
| rev_growth_accel | HIGH | 3 | 1.10 [1.08, 1.14] (4527) | -0.36 |  | 88.9% | 10.0% | 1.16 [1.12, 1.19] (2888) | 0.08 |  |
| rev_growth_accel | HIGH | 6 | 1.09 [1.06, 1.12] (4369) | -0.54 |  | 87.8% | 10.0% | 1.13 [1.09, 1.17] (2776) | 0.14 |  |
| rev_growth_accel | HIGH | 12 | 1.16 [1.13, 1.19] (4498) | -0.09 |  | 85.7% | 10.0% | 1.07 [1.03, 1.10] (2546) | -0.48 |  |
| op_margin_delta | HIGH | 0 | 1.16 [1.13, 1.19] (5155) | -0.14 |  | 93.2% | 10.0% | 1.20 [1.16, 1.24] (3157) | 0.30 |  |
| op_margin_delta | HIGH | 3 | 1.18 [1.15, 1.21] (5132) | -0.20 |  | 92.3% | 10.0% | 1.21 [1.17, 1.25] (3142) | 0.26 |  |
| op_margin_delta | HIGH | 6 | 1.19 [1.16, 1.22] (5091) | -0.09 |  | 91.3% | 10.0% | 1.20 [1.16, 1.24] (3086) | 0.35 |  |
| op_margin_delta | HIGH | 12 | 1.25 [1.22, 1.28] (5172) | 0.18 |  | 89.3% | 10.0% | 1.10 [1.07, 1.14] (2771) | -0.04 |  |
| peg | LOW | 0 | 1.29 [1.24, 1.34] (2072) | -0.99 |  | 34.4% | 10.0% | 1.18 [1.11, 1.24] (959) | -0.94 |  |
| peg | LOW | 3 | 1.29 [1.24, 1.34] (2134) | -0.93 |  | 34.1% | 10.0% | 1.16 [1.10, 1.23] (989) | -0.95 |  |
| peg | LOW | 6 | 1.27 [1.22, 1.32] (2142) | -0.92 |  | 34.0% | 10.0% | 1.06 [1.00, 1.12] (937) | -0.87 |  |
| peg | LOW | 12 | 1.23 [1.18, 1.28] (2114) | -0.95 |  | 34.2% | 10.0% | 1.10 [1.04, 1.16] (1044) | -0.89 |  |
| pe | LOW | 0 | 1.23 [1.19, 1.26] (4059) | 0.14 |  | 68.7% | 10.2% | 1.40 [1.35, 1.45] (2471) | -0.44 |  |
| pe | LOW | 3 | 1.19 [1.16, 1.22] (3969) | 0.26 |  | 68.6% | 10.2% | 1.37 [1.32, 1.42] (2463) | -0.50 |  |
| pe | LOW | 6 | 1.18 [1.15, 1.22] (3973) | 0.30 |  | 68.4% | 10.2% | 1.31 [1.27, 1.36] (2407) | -0.64 |  |
| pe | LOW | 12 | 1.17 [1.13, 1.20] (3931) | 0.30 |  | 67.9% | 10.2% | 1.30 [1.25, 1.34] (2429) | -0.64 |  |
| pe_vs_5y_median | LOW | 0 | 1.35 [1.31, 1.39] (3659) | -0.39 |  | 62.5% | 10.0% | 1.28 [1.23, 1.33] (2003) | -0.39 |  |
| pe_vs_5y_median | LOW | 3 | 1.33 [1.29, 1.37] (3620) | -0.41 |  | 62.1% | 10.0% | 1.28 [1.23, 1.33] (2018) | -0.48 |  |
| pe_vs_5y_median | LOW | 6 | 1.32 [1.28, 1.36] (3567) | -0.39 |  | 61.6% | 10.0% | 1.23 [1.18, 1.28] (1959) | -0.48 |  |
| pe_vs_5y_median | LOW | 12 | 1.35 [1.31, 1.39] (3624) | -0.41 |  | 60.7% | 10.0% | 1.21 [1.16, 1.25] (1941) | -0.47 |  |
| fcf_ps_slope | HIGH | 0 | 0.91 [0.88, 0.93] (4156) | 0.18 |  | 99.5% | 10.0% | 1.03 [0.99, 1.06] (2867) | 0.50 |  |
| fcf_ps_slope | HIGH | 3 | 0.86 [0.84, 0.89] (3892) | -0.04 |  | 98.2% | 10.0% | 1.02 [0.98, 1.05] (2813) | 0.43 |  |
| fcf_ps_slope | HIGH | 6 | 0.86 [0.84, 0.89] (3839) | -0.18 |  | 97.0% | 10.0% | 1.00 [0.97, 1.04] (2737) | 0.30 |  |
| fcf_ps_slope | HIGH | 12 | 0.87 [0.84, 0.90] (3726) | 0.04 |  | 94.5% | 10.0% | 1.00 [0.96, 1.03] (2653) | -0.22 |  |
| pegy | LOW | 0 | 1.30 [1.25, 1.35] (2147) | -0.98 |  | 35.8% | 10.0% | 1.19 [1.12, 1.26] (1011) | -0.98 |  |
| pegy | LOW | 3 | 1.31 [1.26, 1.36] (2213) | -0.89 |  | 35.5% | 10.0% | 1.17 [1.10, 1.23] (1035) | -0.96 |  |
| pegy | LOW | 6 | 1.29 [1.24, 1.34] (2219) | -0.90 |  | 35.3% | 10.0% | 1.06 [1.00, 1.12] (970) | -0.87 |  |
| pegy | LOW | 12 | 1.25 [1.21, 1.30] (2203) | -0.92 |  | 35.5% | 10.0% | 1.12 [1.06, 1.18] (1086) | -0.95 |  |
| pct_from_52w_high | LOW | 0 | 0.59 [0.57, 0.61] (2686) | 1.00 |  | 98.9% | 10.0% | 0.68 [0.65, 0.71] (1885) | 1.00 |  |
| pct_from_52w_high | LOW | 3 | 0.68 [0.66, 0.70] (3058) | 0.99 |  | 97.8% | 10.0% | 0.70 [0.67, 0.73] (1915) | 1.00 |  |
| pct_from_52w_high | LOW | 6 | 0.75 [0.73, 0.78] (3349) | 1.00 |  | 96.7% | 10.0% | 0.72 [0.69, 0.75] (1957) | 0.99 |  |
| pct_from_52w_high | LOW | 12 | 0.79 [0.76, 0.81] (3378) | 1.00 |  | 94.2% | 10.0% | 0.75 [0.72, 0.78] (1977) | 1.00 |  |
| dist_above_30w_sma | HIGH | 0 | 1.25 [1.23, 1.28] (5784) | -0.22 |  | 99.9% | 10.0% | 1.15 [1.12, 1.19] (3223) | -0.30 |  |
| dist_above_30w_sma | HIGH | 3 | 1.31 [1.28, 1.34] (6039) | -0.15 |  | 99.6% | 10.0% | 1.18 [1.14, 1.21] (3289) | -0.33 |  |
| dist_above_30w_sma | HIGH | 6 | 1.34 [1.31, 1.37] (6091) | 0.15 |  | 98.7% | 10.0% | 1.22 [1.18, 1.26] (3383) | -0.30 |  |
| dist_above_30w_sma | HIGH | 12 | 1.33 [1.30, 1.36] (5884) | 0.03 |  | 96.4% | 10.0% | 1.20 [1.17, 1.24] (3268) | -0.33 |  |
| atr_contraction | HIGH | 0 | 0.99 [0.96, 1.01] (4555) | -0.14 |  | 100.0% | 10.0% | 0.94 [0.91, 0.97] (2636) | -0.30 |  |
| atr_contraction | HIGH | 3 | 1.03 [1.00, 1.06] (4743) | -0.28 |  | 99.9% | 10.0% | 0.96 [0.93, 1.00] (2696) | -0.89 |  |
| atr_contraction | HIGH | 6 | 1.07 [1.04, 1.09] (4910) | -0.03 |  | 99.7% | 10.0% | 1.02 [0.99, 1.05] (2853) | -0.25 |  |
| atr_contraction | HIGH | 12 | 1.09 [1.06, 1.12] (4909) | -0.13 |  | 97.8% | 10.0% | 0.98 [0.95, 1.02] (2705) | -0.77 |  |
| inst_pct | LOWMID | 0 | 0.95 [0.93, 0.97] (6523) | 0.32 |  | 95.8% | 40.0% | 0.96 [0.94, 0.97] (10267) | 0.52 |  |
| inst_pct | LOWMID | 3 | 0.96 [0.93, 0.98] (6306) | 0.27 |  | 95.5% | 40.0% | 0.95 [0.94, 0.97] (10148) | 0.52 |  |
| inst_pct | LOWMID | 6 | 0.96 [0.94, 0.98] (6103) | 0.18 |  | 95.5% | 40.0% | 0.95 [0.93, 0.97] (10174) | 0.42 |  |
| inst_pct | LOWMID | 12 | 0.94 [0.92, 0.97] (5397) | -0.01 |  | 93.2% | 40.0% | 0.95 [0.93, 0.97] (9970) | 0.52 |  |
| inst_pct_delta_qoq | HIGH | 0 | 1.48 [1.42, 1.53] (2448) | 0.22 |  | 95.7% | 10.0% | 1.08 [1.04, 1.12] (2899) | 0.07 |  |
| inst_pct_delta_qoq | HIGH | 3 | 1.43 [1.38, 1.48] (2292) | 0.28 |  | 95.2% | 10.0% | 1.15 [1.12, 1.19] (3071) | 0.08 |  |
| inst_pct_delta_qoq | HIGH | 6 | 1.38 [1.33, 1.44] (2106) | 0.37 |  | 94.8% | 10.0% | 1.13 [1.10, 1.17] (3009) | 0.04 |  |
| inst_pct_delta_qoq | HIGH | 12 | 1.42 [1.36, 1.48] (1934) | 0.20 |  | 92.1% | 10.0% | 1.16 [1.12, 1.20] (3009) | -0.04 |  |
| insider_buy_count_90d | HIGH | 0 | 1.12 [1.08, 1.16] (3153) | 0.10 |  | 100.0% | 6.5% | 1.19 [1.14, 1.23] (2160) | 0.10 |  |
| insider_buy_count_90d | HIGH | 3 | 1.05 [1.02, 1.09] (2923) | 0.10 |  | 100.0% | 6.5% | 1.21 [1.17, 1.26] (2215) | 0.10 |  |
| insider_buy_count_90d | HIGH | 6 | 1.02 [0.99, 1.06] (2896) | -0.20 |  | 99.9% | 6.7% | 1.12 [1.08, 1.17] (2096) | 0.10 |  |
| insider_buy_count_90d | HIGH | 12 | 1.06 [1.02, 1.10] (2761) | 0.00 |  | 98.9% | 7.1% | 0.99 [0.95, 1.03] (1955) | n/a |  |
| net_debt_to_ebitda | LOW | 0 | 1.29 [1.25, 1.32] (4847) | -0.56 |  | 78.6% | 10.0% | 1.03 [0.99, 1.07] (2158) | 0.32 |  |
| net_debt_to_ebitda | LOW | 3 | 1.28 [1.24, 1.31] (4771) | -0.61 |  | 77.9% | 10.0% | 1.01 [0.97, 1.05] (2123) | 0.47 |  |
| net_debt_to_ebitda | LOW | 6 | 1.27 [1.24, 1.31] (4702) | -0.75 |  | 77.2% | 10.0% | 0.97 [0.93, 1.01] (2021) | 0.71 |  |
| net_debt_to_ebitda | LOW | 12 | 1.29 [1.25, 1.32] (4637) | -0.85 |  | 75.8% | 10.0% | 0.97 [0.93, 1.01] (2010) | 0.38 |  |
| share_count_change_8q | LOW | 0 | 0.91 [0.89, 0.94] (3898) | 0.77 |  | 94.7% | 10.0% | 1.14 [1.10, 1.18] (3040) | 0.36 |  |
| share_count_change_8q | LOW | 3 | 0.91 [0.89, 0.94] (3822) | 0.77 |  | 93.5% | 10.0% | 1.13 [1.09, 1.17] (2977) | 0.36 |  |
| share_count_change_8q | LOW | 6 | 0.92 [0.89, 0.94] (3747) | 0.76 |  | 92.2% | 10.0% | 1.13 [1.09, 1.16] (2927) | 0.33 |  |
| share_count_change_8q | LOW | 12 | 0.93 [0.91, 0.96] (3683) | 0.83 |  | 89.8% | 10.0% | 1.10 [1.07, 1.14] (2787) | 0.53 |  |
| shareholder_yield | HIGH | 0 | 0.91 [0.88, 0.93] (3866) | -0.83 |  | 94.7% | 10.0% | 1.11 [1.08, 1.15] (2969) | -0.56 |  |
| shareholder_yield | HIGH | 3 | 0.88 [0.85, 0.91] (3681) | -0.83 |  | 93.5% | 10.0% | 1.11 [1.07, 1.15] (2922) | -0.56 |  |
| shareholder_yield | HIGH | 6 | 0.85 [0.83, 0.88] (3501) | -0.83 |  | 92.2% | 10.0% | 1.09 [1.05, 1.12] (2828) | -0.72 |  |
| shareholder_yield | HIGH | 12 | 0.85 [0.82, 0.88] (3350) | -0.84 |  | 89.8% | 10.0% | 1.06 [1.02, 1.09] (2670) | -0.73 |  |
| marketcap | LOW | 0 | 1.31 [1.28, 1.34] (6033) | -1.00 |  | 99.8% | 10.0% | 1.12 [1.08, 1.15] (3133) | -0.90 |  |
| marketcap | LOW | 3 | 1.28 [1.25, 1.31] (5888) | -0.99 |  | 100.0% | 10.0% | 1.07 [1.04, 1.11] (3011) | -0.85 |  |
| marketcap | LOW | 6 | 1.27 [1.24, 1.30] (5866) | -1.00 |  | 99.9% | 10.0% | 1.05 [1.01, 1.08] (2933) | -0.87 |  |
| marketcap | LOW | 12 | 1.27 [1.24, 1.30] (5802) | -1.00 |  | 98.9% | 10.0% | 1.02 [0.99, 1.06] (2837) | -0.87 |  |
| pb | LOW | 0 | 1.05 [1.02, 1.08] (5430) | 0.65 |  | 94.1% | 11.7% | 1.32 [1.29, 1.36] (4096) | -0.55 |  |
| pb | LOW | 3 | 0.98 [0.95, 1.00] (5095) | 0.79 |  | 94.3% | 11.7% | 1.30 [1.26, 1.33] (4022) | -0.68 |  |
| pb | LOW | 6 | 0.94 [0.92, 0.97] (4862) | 0.87 |  | 94.2% | 11.6% | 1.28 [1.24, 1.31] (3910) | -0.62 |  |
| pb | LOW | 12 | 0.95 [0.92, 0.97] (4823) | 0.88 |  | 93.1% | 11.5% | 1.21 [1.18, 1.25] (3629) | -0.79 |  |
| dividend_yield | LOW | 0 | 1.30 [1.28, 1.31] (29113) | -0.79 |  | 100.0% | 50.9% | 1.09 [1.08, 1.11] (15577) | -0.71 |  |
| dividend_yield | LOW | 3 | 1.29 [1.28, 1.31] (29263) | -0.79 |  | 99.9% | 51.0% | 1.09 [1.08, 1.11] (15607) | -0.71 |  |
| dividend_yield | LOW | 6 | 1.29 [1.28, 1.31] (29381) | -0.89 |  | 99.8% | 51.1% | 1.10 [1.08, 1.11] (15653) | -0.71 |  |
| dividend_yield | LOW | 12 | 1.29 [1.28, 1.30] (29068) | -0.93 |  | 98.2% | 50.8% | 1.10 [1.09, 1.12] (15464) | -0.75 |  |

## Extreme-decile cells, win_100: build beside holdout

Build and holdout cells = lift [CI] (events). rho = Spearman over D8 deciles in that window.

| feature | dir | lag | build | rho | build verdict | hold. coverage | hold. cell share | holdout | rho | holdout |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 0 | 1.75 [1.67, 1.83] (1875) | -0.22 |  | 99.9% | 10.0% | 1.60 [1.53, 1.68] (1542) | -0.26 | pass |
| ret_6m_skip1 | HIGH | 3 | 1.74 [1.67, 1.82] (1861) | -0.15 |  | 99.5% | 10.0% | 1.56 [1.49, 1.64] (1501) | -0.24 | pass |
| ret_6m_skip1 | HIGH | 6 | 1.78 [1.70, 1.86] (1871) | -0.15 |  | 98.6% | 10.0% | 1.57 [1.50, 1.65] (1490) | -0.30 | pass |
| ret_6m_skip1 | HIGH | 12 | 1.71 [1.63, 1.79] (1723) | -0.22 |  | 96.2% | 10.0% | 1.31 [1.24, 1.38] (1211) | -0.47 |  |
| ret_12m_skip1 | HIGH | 0 | 1.73 [1.66, 1.81] (1824) | -0.18 |  | 98.6% | 10.0% | 1.57 [1.50, 1.65] (1493) | -0.36 | pass |
| ret_12m_skip1 | HIGH | 3 | 1.74 [1.66, 1.82] (1792) | -0.22 |  | 97.4% | 10.0% | 1.52 [1.45, 1.60] (1425) | -0.35 | pass |
| ret_12m_skip1 | HIGH | 6 | 1.78 [1.70, 1.86] (1798) | -0.20 |  | 96.2% | 10.0% | 1.42 [1.35, 1.49] (1312) | -0.43 |  |
| ret_12m_skip1 | HIGH | 12 | 1.72 [1.64, 1.80] (1649) | -0.18 |  | 93.8% | 10.0% | 1.24 [1.17, 1.31] (1104) | -0.53 |  |
| eps_growth_q0 | HIGH | 0 | 1.24 [1.16, 1.33] (775) | -0.25 |  | 67.3% | 10.0% | 1.47 [1.37, 1.57] (767) | -0.24 |  |
| eps_growth_q0 | HIGH | 3 | 1.36 [1.27, 1.45] (838) | -0.27 |  | 66.9% | 10.0% | 1.35 [1.26, 1.45] (713) | -0.30 |  |
| eps_growth_q0 | HIGH | 6 | 1.29 [1.21, 1.38] (796) | -0.27 |  | 66.4% | 10.0% | 1.30 [1.21, 1.40] (689) | -0.33 |  |
| eps_growth_q0 | HIGH | 12 | 1.42 [1.32, 1.52] (815) | -0.05 |  | 65.0% | 10.0% | 1.19 [1.10, 1.28] (607) | -0.32 |  |
| rev_growth_accel | HIGH | 0 | 1.36 [1.29, 1.44] (1256) | -0.27 |  | 89.9% | 10.0% | 1.43 [1.36, 1.51] (1206) | -0.10 |  |
| rev_growth_accel | HIGH | 3 | 1.36 [1.29, 1.44] (1219) | -0.26 |  | 88.9% | 10.0% | 1.38 [1.31, 1.46] (1140) | 0.09 |  |
| rev_growth_accel | HIGH | 6 | 1.38 [1.30, 1.46] (1203) | -0.22 |  | 87.8% | 10.0% | 1.41 [1.33, 1.49] (1141) | 0.04 |  |
| rev_growth_accel | HIGH | 12 | 1.46 [1.39, 1.55] (1220) | -0.19 |  | 85.7% | 10.0% | 1.31 [1.23, 1.39] (1021) | -0.30 |  |
| op_margin_delta | HIGH | 0 | 1.59 [1.52, 1.67] (1585) | -0.15 |  | 93.2% | 10.0% | 1.53 [1.46, 1.61] (1348) | 0.20 | pass |
| op_margin_delta | HIGH | 3 | 1.57 [1.49, 1.65] (1531) | -0.07 |  | 92.3% | 10.0% | 1.54 [1.46, 1.62] (1333) | 0.19 | pass |
| op_margin_delta | HIGH | 6 | 1.53 [1.46, 1.61] (1462) | -0.07 |  | 91.3% | 10.0% | 1.52 [1.44, 1.60] (1299) | 0.12 | pass |
| op_margin_delta | HIGH | 12 | 1.63 [1.55, 1.71] (1472) | 0.15 |  | 89.3% | 10.0% | 1.38 [1.30, 1.45] (1140) | -0.25 |  |
| peg | LOW | 0 | 1.71 [1.56, 1.87] (452) | -0.77 | PASS-build | 34.4% | 10.0% | 1.64 [1.48, 1.82] (344) | -0.98 | pass |
| peg | LOW | 3 | 1.71 [1.57, 1.87] (479) | -0.96 | PASS-build | 34.1% | 10.0% | 1.55 [1.39, 1.71] (338) | -0.99 | pass |
| peg | LOW | 6 | 1.63 [1.49, 1.79] (460) | -0.87 | PASS-build | 34.0% | 10.0% | 1.43 [1.29, 1.59] (326) | -0.95 |  |
| peg | LOW | 12 | 1.78 [1.63, 1.94] (503) | -0.81 | PASS-build | 34.2% | 10.0% | 1.46 [1.32, 1.61] (364) | -0.94 |  |
| pe | LOW | 0 | 1.66 [1.56, 1.76] (994) | 0.27 |  | 68.7% | 10.2% | 1.76 [1.65, 1.88] (870) | -0.27 | pass |
| pe | LOW | 3 | 1.60 [1.51, 1.71] (990) | 0.19 |  | 68.6% | 10.2% | 1.82 [1.71, 1.94] (924) | -0.36 | pass |
| pe | LOW | 6 | 1.49 [1.40, 1.59] (929) | 0.20 |  | 68.4% | 10.2% | 1.77 [1.67, 1.88] (930) | -0.38 | pass |
| pe | LOW | 12 | 1.43 [1.34, 1.53] (911) | 0.20 |  | 67.9% | 10.2% | 1.70 [1.60, 1.81] (926) | -0.41 | pass |
| pe_vs_5y_median | LOW | 0 | 1.82 [1.70, 1.95] (838) | -0.27 |  | 62.5% | 10.0% | 1.75 [1.63, 1.87] (737) | -0.31 | pass |
| pe_vs_5y_median | LOW | 3 | 1.76 [1.64, 1.88] (823) | -0.27 |  | 62.1% | 10.0% | 1.67 [1.56, 1.79] (716) | -0.41 | pass |
| pe_vs_5y_median | LOW | 6 | 1.73 [1.61, 1.85] (809) | -0.26 |  | 61.6% | 10.0% | 1.63 [1.52, 1.75] (721) | -0.44 | pass |
| pe_vs_5y_median | LOW | 12 | 1.68 [1.57, 1.80] (791) | -0.22 |  | 60.7% | 10.0% | 1.61 [1.50, 1.73] (727) | -0.42 | pass |
| fcf_ps_slope | HIGH | 0 | 0.87 [0.81, 0.93] (929) | -0.02 |  | 99.5% | 10.0% | 1.04 [0.98, 1.11] (1004) | 0.37 |  |
| fcf_ps_slope | HIGH | 3 | 0.86 [0.80, 0.92] (897) | -0.04 |  | 98.2% | 10.0% | 1.04 [0.98, 1.11] (985) | 0.55 |  |
| fcf_ps_slope | HIGH | 6 | 0.86 [0.80, 0.92] (877) | -0.26 |  | 97.0% | 10.0% | 0.98 [0.92, 1.05] (914) | 0.12 |  |
| fcf_ps_slope | HIGH | 12 | 0.86 [0.80, 0.92] (829) | -0.16 |  | 94.5% | 10.0% | 0.98 [0.92, 1.05] (886) | 0.03 |  |
| pegy | LOW | 0 | 1.73 [1.58, 1.89] (467) | -0.77 | PASS-build | 35.8% | 10.0% | 1.68 [1.52, 1.86] (364) | -0.95 | pass |
| pegy | LOW | 3 | 1.73 [1.59, 1.89] (495) | -0.95 | PASS-build | 35.5% | 10.0% | 1.58 [1.43, 1.74] (356) | -0.98 | pass |
| pegy | LOW | 6 | 1.64 [1.50, 1.80] (472) | -0.79 | PASS-build | 35.3% | 10.0% | 1.43 [1.29, 1.59] (337) | -0.93 |  |
| pegy | LOW | 12 | 1.83 [1.68, 1.99] (526) | -0.75 | PASS-build | 35.5% | 10.0% | 1.48 [1.35, 1.64] (378) | -0.95 |  |
| pct_from_52w_high | LOW | 0 | 0.46 [0.42, 0.50] (488) | 1.00 |  | 98.9% | 10.0% | 0.51 [0.47, 0.56] (485) | 0.99 |  |
| pct_from_52w_high | LOW | 3 | 0.49 [0.45, 0.54] (514) | 1.00 |  | 97.8% | 10.0% | 0.49 [0.45, 0.54] (462) | 0.99 |  |
| pct_from_52w_high | LOW | 6 | 0.56 [0.51, 0.60] (565) | 1.00 |  | 96.7% | 10.0% | 0.51 [0.46, 0.55] (470) | 1.00 |  |
| pct_from_52w_high | LOW | 12 | 0.65 [0.60, 0.70] (626) | 0.96 |  | 94.2% | 10.0% | 0.52 [0.47, 0.57] (464) | 1.00 |  |
| dist_above_30w_sma | HIGH | 0 | 1.73 [1.66, 1.81] (1861) | -0.22 |  | 99.9% | 10.0% | 1.57 [1.50, 1.65] (1512) | -0.22 | pass |
| dist_above_30w_sma | HIGH | 3 | 1.70 [1.62, 1.78] (1816) | -0.25 |  | 99.6% | 10.0% | 1.53 [1.46, 1.61] (1474) | -0.27 | pass |
| dist_above_30w_sma | HIGH | 6 | 1.70 [1.63, 1.78] (1793) | -0.15 |  | 98.7% | 10.0% | 1.59 [1.51, 1.66] (1508) | -0.25 | pass |
| dist_above_30w_sma | HIGH | 12 | 1.70 [1.62, 1.78] (1718) | -0.18 |  | 96.4% | 10.0% | 1.43 [1.36, 1.51] (1326) | -0.27 |  |
| atr_contraction | HIGH | 0 | 1.08 [1.02, 1.14] (1157) | -0.15 |  | 100.0% | 10.0% | 1.07 [1.01, 1.13] (1029) | -0.22 |  |
| atr_contraction | HIGH | 3 | 1.13 [1.07, 1.19] (1211) | -0.16 |  | 99.9% | 10.0% | 1.05 [0.99, 1.11] (1010) | -0.48 |  |
| atr_contraction | HIGH | 6 | 1.18 [1.12, 1.25] (1267) | -0.15 |  | 99.7% | 10.0% | 1.11 [1.05, 1.18] (1069) | -0.19 |  |
| atr_contraction | HIGH | 12 | 1.19 [1.13, 1.26] (1237) | -0.32 |  | 97.8% | 10.0% | 1.08 [1.02, 1.14] (1014) | -0.44 |  |
| inst_pct | LOWMID | 0 | 0.93 [0.89, 0.98] (1474) | -0.71 |  | 95.8% | 40.0% | 0.92 [0.89, 0.95] (3370) | -0.27 |  |
| inst_pct | LOWMID | 3 | 0.95 [0.90, 1.00] (1429) | -0.68 |  | 95.5% | 40.0% | 0.92 [0.89, 0.95] (3311) | -0.22 |  |
| inst_pct | LOWMID | 6 | 0.91 [0.87, 0.96] (1336) | -0.66 |  | 95.5% | 40.0% | 0.91 [0.88, 0.94] (3317) | -0.16 |  |
| inst_pct | LOWMID | 12 | 0.91 [0.86, 0.96] (1181) | -0.58 |  | 93.2% | 40.0% | 0.90 [0.87, 0.93] (3185) | -0.15 |  |
| inst_pct_delta_qoq | HIGH | 0 | 2.06 [1.92, 2.20] (785) | 0.20 |  | 95.7% | 10.0% | 1.36 [1.29, 1.43] (1241) | -0.02 |  |
| inst_pct_delta_qoq | HIGH | 3 | 1.95 [1.82, 2.10] (719) | 0.31 |  | 95.2% | 10.0% | 1.44 [1.37, 1.52] (1306) | 0.07 |  |
| inst_pct_delta_qoq | HIGH | 6 | 1.90 [1.77, 2.05] (664) | 0.25 |  | 94.8% | 10.0% | 1.46 [1.38, 1.54] (1321) | 0.19 |  |
| inst_pct_delta_qoq | HIGH | 12 | 1.95 [1.81, 2.11] (598) | 0.32 |  | 92.1% | 10.0% | 1.47 [1.39, 1.55] (1289) | 0.08 |  |
| insider_buy_count_90d | HIGH | 0 | 1.35 [1.27, 1.44] (893) | 0.30 |  | 100.0% | 6.5% | 1.34 [1.25, 1.43] (840) | 0.10 |  |
| insider_buy_count_90d | HIGH | 3 | 1.37 [1.28, 1.46] (892) | 0.30 |  | 100.0% | 6.5% | 1.30 [1.22, 1.39] (819) | 0.10 |  |
| insider_buy_count_90d | HIGH | 6 | 1.23 [1.15, 1.31] (813) | 0.10 |  | 99.9% | 6.7% | 1.30 [1.22, 1.39] (835) | 0.10 |  |
| insider_buy_count_90d | HIGH | 12 | 1.30 [1.21, 1.40] (732) | 0.40 |  | 98.9% | 7.1% | 1.20 [1.12, 1.28] (813) | n/a |  |
| net_debt_to_ebitda | LOW | 0 | 1.57 [1.48, 1.66] (1173) | -0.12 |  | 78.6% | 10.0% | 1.14 [1.06, 1.23] (723) | 0.55 |  |
| net_debt_to_ebitda | LOW | 3 | 1.53 [1.44, 1.61] (1133) | -0.19 |  | 77.9% | 10.0% | 1.09 [1.02, 1.17] (695) | 0.59 |  |
| net_debt_to_ebitda | LOW | 6 | 1.54 [1.45, 1.63] (1129) | -0.21 |  | 77.2% | 10.0% | 1.07 [0.99, 1.15] (679) | 0.71 |  |
| net_debt_to_ebitda | LOW | 12 | 1.55 [1.46, 1.64] (1105) | -0.22 |  | 75.8% | 10.0% | 1.05 [0.97, 1.13] (659) | 0.70 |  |
| share_count_change_8q | LOW | 0 | 0.64 [0.59, 0.69] (616) | 0.95 |  | 94.7% | 10.0% | 1.08 [1.01, 1.15] (977) | 0.67 |  |
| share_count_change_8q | LOW | 3 | 0.65 [0.60, 0.70] (606) | 0.95 |  | 93.5% | 10.0% | 1.08 [1.02, 1.15] (964) | 0.64 |  |
| share_count_change_8q | LOW | 6 | 0.67 [0.62, 0.72] (609) | 0.95 |  | 92.2% | 10.0% | 1.07 [1.01, 1.14] (939) | 0.66 |  |
| share_count_change_8q | LOW | 12 | 0.69 [0.64, 0.75] (600) | 0.95 |  | 89.8% | 10.0% | 1.04 [0.97, 1.10] (877) | 0.71 |  |
| shareholder_yield | HIGH | 0 | 0.75 [0.70, 0.81] (721) | -0.88 |  | 94.7% | 10.0% | 1.02 [0.96, 1.09] (925) | -0.73 |  |
| shareholder_yield | HIGH | 3 | 0.72 [0.66, 0.77] (670) | -0.93 |  | 93.5% | 10.0% | 1.02 [0.95, 1.08] (904) | -0.72 |  |
| shareholder_yield | HIGH | 6 | 0.69 [0.64, 0.75] (631) | -0.93 |  | 92.2% | 10.0% | 1.03 [0.96, 1.09] (896) | -0.72 |  |
| shareholder_yield | HIGH | 12 | 0.67 [0.62, 0.72] (577) | -0.93 |  | 89.8% | 10.0% | 0.99 [0.93, 1.06] (837) | -0.76 |  |
| marketcap | LOW | 0 | 2.03 [1.95, 2.11] (2178) | -1.00 | PASS-build | 99.8% | 10.0% | 1.65 [1.58, 1.73] (1594) | -1.00 | pass |
| marketcap | LOW | 3 | 1.96 [1.88, 2.04] (2108) | -1.00 | PASS-build | 100.0% | 10.0% | 1.58 [1.50, 1.65] (1521) | -1.00 | pass |
| marketcap | LOW | 6 | 1.90 [1.83, 1.99] (2044) | -1.00 | PASS-build | 99.9% | 10.0% | 1.52 [1.45, 1.60] (1466) | -0.99 | pass |
| marketcap | LOW | 12 | 1.87 [1.79, 1.95] (1975) | -1.00 | PASS-build | 98.9% | 10.0% | 1.53 [1.45, 1.60] (1456) | -0.99 | pass |
| pb | LOW | 0 | 1.33 [1.26, 1.39] (1571) | 0.48 |  | 94.1% | 11.7% | 1.50 [1.43, 1.57] (1591) | -0.22 |  |
| pb | LOW | 3 | 1.23 [1.17, 1.29] (1465) | 0.59 |  | 94.3% | 11.7% | 1.52 [1.45, 1.59] (1615) | -0.16 | pass |
| pb | LOW | 6 | 1.10 [1.05, 1.16] (1302) | 0.58 |  | 94.2% | 11.6% | 1.57 [1.50, 1.64] (1644) | -0.16 | pass |
| pb | LOW | 12 | 1.06 [1.01, 1.12] (1225) | 0.61 |  | 93.1% | 11.5% | 1.48 [1.41, 1.55] (1505) | -0.45 |  |
| dividend_yield | LOW | 0 | 1.56 [1.53, 1.59] (8165) | -0.32 |  | 100.0% | 50.9% | 1.31 [1.28, 1.34] (6443) | -0.46 |  |
| dividend_yield | LOW | 3 | 1.55 [1.52, 1.58] (8167) | -0.43 |  | 99.9% | 51.0% | 1.31 [1.28, 1.34] (6428) | -0.57 |  |
| dividend_yield | LOW | 6 | 1.55 [1.51, 1.58] (8183) | -0.64 | PASS-build | 99.8% | 51.1% | 1.31 [1.28, 1.34] (6427) | -0.61 |  |
| dividend_yield | LOW | 12 | 1.53 [1.50, 1.56] (7973) | -0.79 | PASS-build | 98.2% | 50.8% | 1.31 [1.28, 1.34] (6301) | -0.71 |  |

## Extreme-decile cells, launch_300: build beside holdout

Build and holdout cells = lift [CI] (events). rho = Spearman over D8 deciles in that window.

| feature | dir | lag | build | rho | build verdict | hold. coverage | hold. cell share | holdout | rho | holdout |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 0 | 1.86 [1.70, 2.03] (482) | -0.30 |  | 99.9% | 10.0% | 2.06 [1.87, 2.28] (369) | -0.14 | pass |
| ret_6m_skip1 | HIGH | 3 | 1.93 [1.76, 2.10] (496) | -0.22 |  | 99.5% | 10.0% | 1.78 [1.60, 1.99] (316) | -0.26 | pass |
| ret_6m_skip1 | HIGH | 6 | 2.09 [1.92, 2.28] (528) | -0.12 |  | 98.5% | 10.0% | 1.49 [1.32, 1.68] (262) | -0.33 |  |
| ret_6m_skip1 | HIGH | 12 | 2.13 [1.96, 2.33] (503) | -0.18 |  | 95.9% | 10.0% | 1.15 [1.00, 1.32] (197) | -0.50 |  |
| ret_12m_skip1 | HIGH | 0 | 1.90 [1.73, 2.07] (478) | -0.35 |  | 98.5% | 10.0% | 1.67 [1.49, 1.87] (294) | -0.21 | pass |
| ret_12m_skip1 | HIGH | 3 | 2.01 [1.84, 2.20] (491) | -0.28 |  | 97.2% | 10.0% | 1.53 [1.36, 1.72] (265) | -0.52 | pass |
| ret_12m_skip1 | HIGH | 6 | 2.17 [1.99, 2.36] (511) | -0.15 |  | 95.9% | 10.0% | 1.23 [1.07, 1.40] (210) | -0.61 |  |
| ret_12m_skip1 | HIGH | 12 | 2.30 [2.10, 2.50] (505) | -0.02 |  | 93.2% | 10.0% | 1.14 [0.98, 1.31] (187) | -0.54 |  |
| eps_growth_q0 | HIGH | 0 | 1.23 [1.05, 1.44] (154) | -0.60 |  | 66.7% | 10.0% | 1.79 [1.52, 2.11] (139) | n/a | pass |
| eps_growth_q0 | HIGH | 3 | 1.58 [1.37, 1.82] (192) | -0.30 |  | 66.3% | 10.0% | 1.53 [1.28, 1.82] (124) | n/a | pass |
| eps_growth_q0 | HIGH | 6 | 1.51 [1.31, 1.75] (178) | -0.10 |  | 65.9% | 10.0% | 1.34 [1.12, 1.62] (112) | n/a |  |
| eps_growth_q0 | HIGH | 12 | 1.36 [1.16, 1.59] (154) | -0.30 |  | 64.4% | 10.0% | insufficient (80) | n/a |  |
| rev_growth_accel | HIGH | 0 | 1.67 [1.50, 1.85] (352) | -0.37 |  | 89.3% | 10.0% | 1.74 [1.54, 1.96] (264) | 0.05 | pass |
| rev_growth_accel | HIGH | 3 | 1.72 [1.55, 1.91] (349) | -0.21 |  | 88.2% | 10.0% | 1.61 [1.42, 1.83] (238) | 0.12 | pass |
| rev_growth_accel | HIGH | 6 | 1.76 [1.59, 1.96] (346) | -0.04 |  | 87.0% | 10.0% | 1.51 [1.33, 1.73] (217) | -0.17 | pass |
| rev_growth_accel | HIGH | 12 | 1.54 [1.37, 1.73] (287) | -0.03 |  | 84.7% | 10.0% | 1.18 [1.01, 1.38] (160) | -0.29 |  |
| op_margin_delta | HIGH | 0 | 2.11 [1.93, 2.30] (502) | -0.10 |  | 93.0% | 10.0% | 2.02 [1.81, 2.25] (324) | 0.04 | pass |
| op_margin_delta | HIGH | 3 | 2.01 [1.84, 2.20] (462) | 0.00 |  | 91.9% | 10.0% | 1.77 [1.58, 1.99] (280) | -0.05 | pass |
| op_margin_delta | HIGH | 6 | 1.96 [1.79, 2.15] (435) | 0.08 |  | 90.8% | 10.0% | 1.67 [1.48, 1.88] (259) | -0.11 | pass |
| op_margin_delta | HIGH | 12 | 1.99 [1.80, 2.19] (409) | 0.08 |  | 88.6% | 10.0% | 1.57 [1.38, 1.78] (233) | -0.25 | pass |
| peg | LOW | 0 | 2.19 [1.81, 2.64] (108) | n/a |  | 34.1% | 10.1% | insufficient (21) | n/a |  |
| peg | LOW | 3 | 2.35 [1.98, 2.80] (125) | n/a |  | 34.0% | 10.0% | insufficient (30) | n/a |  |
| peg | LOW | 6 | 2.08 [1.73, 2.50] (113) | n/a |  | 34.0% | 10.0% | insufficient (43) | n/a |  |
| peg | LOW | 12 | 2.06 [1.71, 2.48] (108) | n/a |  | 34.5% | 10.0% | insufficient (56) | n/a |  |
| pe | LOW | 0 | 2.07 [1.82, 2.34] (243) | 0.00 |  | 68.2% | 10.2% | insufficient (93) | n/a |  |
| pe | LOW | 3 | 2.02 [1.79, 2.29] (248) | -0.10 |  | 68.1% | 10.2% | insufficient (99) | n/a |  |
| pe | LOW | 6 | 1.63 [1.43, 1.87] (206) | 0.30 |  | 67.9% | 10.2% | 1.67 [1.41, 1.98] (130) | n/a | pass |
| pe | LOW | 12 | 1.52 [1.32, 1.75] (193) | 0.37 |  | 67.3% | 10.2% | 1.84 [1.57, 2.16] (152) | n/a | pass |
| pe_vs_5y_median | LOW | 0 | 2.36 [2.06, 2.72] (195) | n/a |  | 62.0% | 10.0% | insufficient (68) | n/a |  |
| pe_vs_5y_median | LOW | 3 | 2.18 [1.89, 2.51] (186) | n/a |  | 61.5% | 10.0% | insufficient (73) | n/a |  |
| pe_vs_5y_median | LOW | 6 | 1.80 [1.54, 2.11] (156) | n/a |  | 61.0% | 10.0% | insufficient (94) | n/a |  |
| pe_vs_5y_median | LOW | 12 | 1.75 [1.49, 2.05] (148) | n/a |  | 60.0% | 10.0% | 1.70 [1.42, 2.04] (113) | n/a | pass |
| fcf_ps_slope | HIGH | 0 | 0.87 [0.77, 0.99] (226) | 0.33 |  | 99.4% | 10.0% | 1.02 [0.88, 1.18] (182) | 0.39 |  |
| fcf_ps_slope | HIGH | 3 | 0.83 [0.73, 0.95] (209) | -0.01 |  | 98.0% | 10.0% | 1.03 [0.89, 1.19] (181) | 0.39 |  |
| fcf_ps_slope | HIGH | 6 | 0.76 [0.66, 0.87] (184) | -0.27 |  | 96.6% | 10.0% | 0.95 [0.82, 1.11] (164) | 0.36 |  |
| fcf_ps_slope | HIGH | 12 | 0.80 [0.69, 0.93] (180) | 0.08 |  | 93.9% | 10.0% | 1.04 [0.90, 1.21] (173) | -0.13 |  |
| pegy | LOW | 0 | 2.19 [1.82, 2.64] (110) | n/a |  | 35.5% | 10.0% | insufficient (23) | n/a |  |
| pegy | LOW | 3 | 2.43 [2.05, 2.88] (131) | n/a |  | 35.4% | 10.0% | insufficient (32) | n/a |  |
| pegy | LOW | 6 | 2.09 [1.74, 2.51] (114) | n/a |  | 35.4% | 10.0% | insufficient (44) | n/a |  |
| pegy | LOW | 12 | 2.08 [1.73, 2.50] (112) | n/a |  | 35.8% | 10.0% | insufficient (60) | n/a |  |
| pct_from_52w_high | LOW | 0 | 0.40 [0.33, 0.48] (101) | 1.00 |  | 98.9% | 10.0% | insufficient (86) | 0.93 |  |
| pct_from_52w_high | LOW | 3 | 0.41 [0.33, 0.49] (100) | 1.00 |  | 97.6% | 10.0% | insufficient (92) | 0.98 |  |
| pct_from_52w_high | LOW | 6 | 0.48 [0.40, 0.57] (114) | 0.99 |  | 96.4% | 10.0% | insufficient (95) | 0.94 |  |
| pct_from_52w_high | LOW | 12 | 0.63 [0.54, 0.75] (141) | 0.92 |  | 93.6% | 10.0% | insufficient (89) | 1.00 |  |
| dist_above_30w_sma | HIGH | 0 | 1.87 [1.71, 2.04] (485) | -0.27 |  | 99.9% | 10.0% | 2.02 [1.82, 2.23] (361) | -0.25 | pass |
| dist_above_30w_sma | HIGH | 3 | 1.87 [1.71, 2.04] (482) | -0.32 |  | 99.6% | 10.0% | 1.87 [1.69, 2.08] (333) | -0.21 | pass |
| dist_above_30w_sma | HIGH | 6 | 1.92 [1.76, 2.10] (485) | -0.22 |  | 98.6% | 10.0% | 1.53 [1.36, 1.72] (269) | -0.23 | pass |
| dist_above_30w_sma | HIGH | 12 | 2.00 [1.83, 2.19] (472) | -0.10 |  | 96.0% | 10.0% | 1.28 [1.12, 1.46] (219) | -0.48 |  |
| atr_contraction | HIGH | 0 | 1.15 [1.02, 1.28] (298) | -0.03 |  | 100.0% | 10.0% | 1.19 [1.04, 1.36] (214) | -0.41 |  |
| atr_contraction | HIGH | 3 | 1.32 [1.19, 1.47] (343) | 0.07 |  | 99.9% | 10.0% | 1.20 [1.05, 1.37] (215) | -0.24 |  |
| atr_contraction | HIGH | 6 | 1.30 [1.16, 1.44] (335) | -0.45 |  | 99.7% | 10.0% | 1.20 [1.05, 1.37] (214) | -0.42 |  |
| atr_contraction | HIGH | 12 | 1.31 [1.18, 1.46] (324) | -0.07 |  | 97.7% | 10.0% | 1.09 [0.94, 1.25] (189) | -0.60 |  |
| inst_pct | LOWMID | 0 | 0.88 [0.80, 0.97] (423) | -1.00 |  | 95.7% | 40.0% | 0.93 [0.86, 1.00] (632) | -0.71 |  |
| inst_pct | LOWMID | 3 | 0.87 [0.79, 0.96] (408) | -1.00 |  | 95.3% | 40.0% | 0.88 [0.82, 0.96] (594) | -0.50 |  |
| inst_pct | LOWMID | 6 | 0.87 [0.79, 0.96] (400) | n/a |  | 95.1% | 40.0% | 0.86 [0.80, 0.94] (581) | -0.50 |  |
| inst_pct | LOWMID | 12 | 0.85 [0.76, 0.94] (358) | n/a |  | 92.9% | 40.0% | 0.86 [0.79, 0.93] (560) | -0.50 |  |
| inst_pct_delta_qoq | HIGH | 0 | 2.45 [2.19, 2.75] (290) | n/a |  | 95.6% | 10.0% | 1.49 [1.32, 1.69] (254) | -0.15 |  |
| inst_pct_delta_qoq | HIGH | 3 | 2.33 [2.07, 2.62] (269) | 0.30 |  | 95.1% | 10.0% | 1.59 [1.41, 1.79] (266) | -0.22 | pass |
| inst_pct_delta_qoq | HIGH | 6 | 2.18 [1.92, 2.47] (245) | n/a |  | 94.4% | 10.0% | 1.58 [1.40, 1.78] (263) | -0.07 | pass |
| inst_pct_delta_qoq | HIGH | 12 | 2.11 [1.85, 2.41] (214) | n/a |  | 91.7% | 10.0% | 1.66 [1.48, 1.87] (268) | 0.08 | pass |
| insider_buy_count_90d | HIGH | 0 | 1.80 [1.61, 2.01] (309) | n/a |  | 100.0% | 6.6% | 1.27 [1.09, 1.49] (150) | n/a |  |
| insider_buy_count_90d | HIGH | 3 | 1.52 [1.34, 1.71] (256) | n/a |  | 99.9% | 6.7% | 1.32 [1.13, 1.54] (158) | n/a |  |
| insider_buy_count_90d | HIGH | 6 | 1.17 [1.02, 1.34] (201) | n/a |  | 99.9% | 6.8% | 1.46 [1.26, 1.68] (178) | n/a |  |
| insider_buy_count_90d | HIGH | 12 | 1.08 [0.92, 1.26] (153) | n/a |  | 98.9% | 7.2% | 1.32 [1.14, 1.54] (168) | n/a |  |
| net_debt_to_ebitda | LOW | 0 | 1.76 [1.56, 1.99] (264) | -0.14 |  | 78.1% | 10.0% | insufficient (98) | n/a |  |
| net_debt_to_ebitda | LOW | 3 | 1.73 [1.53, 1.95] (258) | -0.16 |  | 77.4% | 10.0% | 0.98 [0.81, 1.19] (100) | 1.00 |  |
| net_debt_to_ebitda | LOW | 6 | 1.72 [1.52, 1.94] (253) | -0.19 |  | 76.6% | 10.0% | insufficient (97) | n/a |  |
| net_debt_to_ebitda | LOW | 12 | 1.47 [1.28, 1.68] (208) | -0.30 |  | 75.2% | 10.0% | insufficient (84) | -0.10 |  |
| share_count_change_8q | LOW | 0 | 0.55 [0.46, 0.66] (124) | 0.98 |  | 94.2% | 10.0% | 0.94 [0.80, 1.09] (157) | 0.86 |  |
| share_count_change_8q | LOW | 3 | 0.57 [0.47, 0.67] (123) | 0.98 |  | 92.8% | 10.0% | 0.90 [0.77, 1.06] (149) | 0.81 |  |
| share_count_change_8q | LOW | 6 | 0.62 [0.52, 0.73] (130) | 1.00 |  | 91.4% | 10.0% | 0.89 [0.75, 1.04] (143) | 0.83 |  |
| share_count_change_8q | LOW | 12 | 0.75 [0.64, 0.88] (147) | 0.93 |  | 88.7% | 10.0% | 0.88 [0.74, 1.04] (134) | 0.86 |  |
| shareholder_yield | HIGH | 0 | 0.66 [0.56, 0.77] (148) | -0.86 |  | 94.1% | 10.0% | 0.89 [0.76, 1.04] (149) | -1.00 |  |
| shareholder_yield | HIGH | 3 | 0.68 [0.58, 0.79] (147) | -0.89 |  | 92.8% | 10.0% | 0.88 [0.75, 1.04] (145) | -0.93 |  |
| shareholder_yield | HIGH | 6 | 0.67 [0.57, 0.79] (141) | -1.00 |  | 91.4% | 10.0% | 0.79 [0.67, 0.94] (128) | -0.89 |  |
| shareholder_yield | HIGH | 12 | 0.73 [0.62, 0.86] (143) | -0.96 |  | 88.7% | 10.0% | 0.79 [0.66, 0.94] (120) | -0.96 |  |
| marketcap | LOW | 0 | 2.32 [2.14, 2.51] (605) | -0.98 | PASS-build | 99.8% | 10.0% | 2.19 [1.99, 2.41] (394) | -1.00 | pass |
| marketcap | LOW | 3 | 2.21 [2.04, 2.40] (575) | -1.00 | PASS-build | 99.9% | 10.0% | 2.17 [1.97, 2.39] (390) | -0.93 | pass |
| marketcap | LOW | 6 | 2.13 [1.96, 2.31] (553) | -1.00 | PASS-build | 99.9% | 10.0% | 2.11 [1.91, 2.33] (377) | -0.96 | pass |
| marketcap | LOW | 12 | 2.08 [1.92, 2.27] (529) | -0.97 | PASS-build | 98.9% | 10.0% | 1.82 [1.63, 2.03] (321) | -0.98 | pass |
| pb | LOW | 0 | 1.42 [1.29, 1.57] (399) | 0.48 |  | 94.1% | 11.7% | 1.85 [1.67, 2.05] (358) | -0.08 | pass |
| pb | LOW | 3 | 1.24 [1.12, 1.38] (350) | 0.58 |  | 94.3% | 11.7% | 1.91 [1.73, 2.11] (371) | -0.12 | pass |
| pb | LOW | 6 | 0.91 [0.80, 1.03] (254) | 0.66 |  | 94.2% | 11.6% | 2.07 [1.88, 2.28] (397) | -0.21 | pass |
| pb | LOW | 12 | 0.78 [0.68, 0.89] (209) | 0.88 |  | 93.0% | 11.5% | 1.86 [1.68, 2.06] (349) | -0.36 | pass |
| dividend_yield | LOW | 0 | 1.67 [1.60, 1.75] (2126) | n/a |  | 100.0% | 51.4% | 1.46 [1.38, 1.54] (1344) | n/a |  |
| dividend_yield | LOW | 3 | 1.66 [1.59, 1.73] (2119) | n/a |  | 99.9% | 51.5% | 1.45 [1.38, 1.53] (1339) | n/a |  |
| dividend_yield | LOW | 6 | 1.65 [1.58, 1.72] (2113) | n/a |  | 99.8% | 51.6% | 1.44 [1.37, 1.52] (1330) | n/a |  |
| dividend_yield | LOW | 12 | 1.63 [1.56, 1.70] (2026) | n/a |  | 98.1% | 51.2% | 1.46 [1.38, 1.54] (1304) | n/a |  |

## Verdicts (full section 3 criterion, build AND holdout)

| feature | dir | label | verdict | build pass lags | holdout pass lags | confirmed lags | holdout best cell | min holdout lift, calm buckets |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | win_50 | no build pass | - | - | - | 1.21 [1.17, 1.25] lag 3 (3378) | 1.00 |
| ret_6m_skip1 | HIGH | win_100 | no build pass | - | 0,3,6 | - | 1.60 [1.53, 1.68] lag 0 (1542) | 1.14 |
| ret_6m_skip1 | HIGH | launch_300 | no build pass | - | 0,3 | - | 2.06 [1.87, 2.28] lag 0 (369) | 1.15 |
| ret_12m_skip1 | HIGH | win_50 | no build pass | - | - | - | 1.23 [1.19, 1.26] lag 3 (3360) | 1.03 |
| ret_12m_skip1 | HIGH | win_100 | no build pass | - | 0,3 | - | 1.57 [1.50, 1.65] lag 0 (1493) | 1.06 |
| ret_12m_skip1 | HIGH | launch_300 | no build pass | - | 0,3 | - | 1.67 [1.49, 1.87] lag 0 (294) | 1.14 |
| eps_growth_q0 | HIGH | win_50 | no build pass | - | - | - | 1.17 [1.12, 1.21] lag 0 (2101) | 1.02 |
| eps_growth_q0 | HIGH | win_100 | no build pass | - | - | - | 1.47 [1.37, 1.57] lag 0 (767) | 1.09 |
| eps_growth_q0 | HIGH | launch_300 | no build pass | - | 0,3 | - | 1.79 [1.52, 2.11] lag 0 (139) | 1.87 |
| rev_growth_accel | HIGH | win_50 | no build pass | - | - | - | 1.16 [1.12, 1.19] lag 3 (2888) | 0.98 |
| rev_growth_accel | HIGH | win_100 | no build pass | - | - | - | 1.43 [1.36, 1.51] lag 0 (1206) | 1.22 |
| rev_growth_accel | HIGH | launch_300 | no build pass | - | 0,3,6 | - | 1.74 [1.54, 1.96] lag 0 (264) | 1.15 |
| op_margin_delta | HIGH | win_50 | no build pass | - | - | - | 1.21 [1.17, 1.25] lag 3 (3142) | 0.98 |
| op_margin_delta | HIGH | win_100 | no build pass | - | 0,3,6 | - | 1.54 [1.46, 1.62] lag 3 (1333) | 1.26 |
| op_margin_delta | HIGH | launch_300 | no build pass | - | 0,3,6,12 | - | 2.02 [1.81, 2.25] lag 0 (324) | 1.64 |
| peg | LOW | win_50 | no build pass | - | - | - | 1.18 [1.11, 1.24] lag 0 (959) | 0.99 |
| peg | LOW | win_100 | CONFIRMED | 0,3,6,12 | 0,3 | 0,3 | 1.64 [1.48, 1.82] lag 0 (344) | 1.47 |
| peg | LOW | launch_300 | no build pass | - | - | - | - | n/a |
| pe | LOW | win_50 | no build pass | - | - | - | 1.40 [1.35, 1.45] lag 0 (2471) | 1.27 |
| pe | LOW | win_100 | no build pass | - | 0,3,6,12 | - | 1.82 [1.71, 1.94] lag 3 (924) | 1.59 |
| pe | LOW | launch_300 | no build pass | - | 6,12 | - | 1.84 [1.57, 2.16] lag 12 (152) | 2.07 |
| pe_vs_5y_median | LOW | win_50 | no build pass | - | - | - | 1.28 [1.23, 1.33] lag 0 (2003) | 1.20 |
| pe_vs_5y_median | LOW | win_100 | no build pass | - | 0,3,6,12 | - | 1.75 [1.63, 1.87] lag 0 (737) | 1.53 |
| pe_vs_5y_median | LOW | launch_300 | no build pass | - | 12 | - | 1.70 [1.42, 2.04] lag 12 (113) | n/a |
| fcf_ps_slope | HIGH | win_50 | no build pass | - | - | - | 1.03 [0.99, 1.06] lag 0 (2867) | 0.97 |
| fcf_ps_slope | HIGH | win_100 | no build pass | - | - | - | 1.04 [0.98, 1.11] lag 0 (1004) | 0.96 |
| fcf_ps_slope | HIGH | launch_300 | no build pass | - | - | - | 1.04 [0.90, 1.21] lag 12 (173) | 1.04 |
| pegy | LOW | win_50 | no build pass | - | - | - | 1.19 [1.12, 1.26] lag 0 (1011) | 0.99 |
| pegy | LOW | win_100 | CONFIRMED | 0,3,6,12 | 0,3 | 0,3 | 1.68 [1.52, 1.86] lag 0 (364) | 1.47 |
| pegy | LOW | launch_300 | no build pass | - | - | - | - | n/a |
| pct_from_52w_high | LOW | win_50 | no build pass | - | - | - | 0.75 [0.72, 0.78] lag 12 (1977) | 0.61 |
| pct_from_52w_high | LOW | win_100 | no build pass | - | - | - | 0.52 [0.47, 0.57] lag 12 (464) | 0.48 |
| pct_from_52w_high | LOW | launch_300 | no build pass | - | - | - | - | n/a |
| dist_above_30w_sma | HIGH | win_50 | no build pass | - | - | - | 1.22 [1.18, 1.26] lag 6 (3383) | 0.97 |
| dist_above_30w_sma | HIGH | win_100 | no build pass | - | 0,3,6 | - | 1.59 [1.51, 1.66] lag 6 (1508) | 1.10 |
| dist_above_30w_sma | HIGH | launch_300 | no build pass | - | 0,3,6 | - | 2.02 [1.82, 2.23] lag 0 (361) | 1.34 |
| atr_contraction | HIGH | win_50 | no build pass | - | - | - | 1.02 [0.99, 1.05] lag 6 (2853) | 0.84 |
| atr_contraction | HIGH | win_100 | no build pass | - | - | - | 1.11 [1.05, 1.18] lag 6 (1069) | 0.93 |
| atr_contraction | HIGH | launch_300 | no build pass | - | - | - | 1.20 [1.05, 1.37] lag 6 (214) | 1.09 |
| inst_pct | LOWMID | win_50 | no build pass | - | - | - | 0.96 [0.94, 0.97] lag 0 (10267) | 0.94 |
| inst_pct | LOWMID | win_100 | no build pass | - | - | - | 0.92 [0.89, 0.95] lag 0 (3370) | 0.88 |
| inst_pct | LOWMID | launch_300 | no build pass | - | - | - | 0.93 [0.86, 1.00] lag 0 (632) | 0.81 |
| inst_pct_delta_qoq | HIGH | win_50 | no build pass | - | - | - | 1.16 [1.12, 1.20] lag 12 (3009) | 1.08 |
| inst_pct_delta_qoq | HIGH | win_100 | no build pass | - | - | - | 1.47 [1.39, 1.55] lag 12 (1289) | 1.36 |
| inst_pct_delta_qoq | HIGH | launch_300 | no build pass | - | 3,6,12 | - | 1.66 [1.48, 1.87] lag 12 (268) | 1.55 |
| insider_buy_count_90d | HIGH | win_50 | no build pass | - | - | - | 1.21 [1.17, 1.26] lag 3 (2215) | 0.91 |
| insider_buy_count_90d | HIGH | win_100 | no build pass | - | - | - | 1.34 [1.25, 1.43] lag 0 (840) | 0.96 |
| insider_buy_count_90d | HIGH | launch_300 | no build pass | - | - | - | 1.46 [1.26, 1.68] lag 6 (178) | 1.32 |
| net_debt_to_ebitda | LOW | win_50 | no build pass | - | - | - | 1.03 [0.99, 1.07] lag 0 (2158) | 0.79 |
| net_debt_to_ebitda | LOW | win_100 | no build pass | - | - | - | 1.14 [1.06, 1.23] lag 0 (723) | 0.87 |
| net_debt_to_ebitda | LOW | launch_300 | no build pass | - | - | - | 0.98 [0.81, 1.19] lag 3 (100) | n/a |
| share_count_change_8q | LOW | win_50 | no build pass | - | - | - | 1.14 [1.10, 1.18] lag 0 (3040) | 0.98 |
| share_count_change_8q | LOW | win_100 | no build pass | - | - | - | 1.08 [1.02, 1.15] lag 3 (964) | 0.94 |
| share_count_change_8q | LOW | launch_300 | no build pass | - | - | - | 0.94 [0.80, 1.09] lag 0 (157) | 0.85 |
| shareholder_yield | HIGH | win_50 | no build pass | - | - | - | 1.11 [1.08, 1.15] lag 0 (2969) | 0.83 |
| shareholder_yield | HIGH | win_100 | no build pass | - | - | - | 1.03 [0.96, 1.09] lag 6 (896) | 0.78 |
| shareholder_yield | HIGH | launch_300 | no build pass | - | - | - | 0.89 [0.76, 1.04] lag 0 (149) | 0.92 |
| marketcap | LOW | win_50 | no build pass | - | - | - | 1.12 [1.08, 1.15] lag 0 (3133) | 0.98 |
| marketcap | LOW | win_100 | CONFIRMED | 0,3,6,12 | 0,3,6,12 | 0,3,6,12 | 1.65 [1.58, 1.73] lag 0 (1594) | 1.38 |
| marketcap | LOW | launch_300 | CONFIRMED | 0,3,6,12 | 0,3,6,12 | 0,3,6,12 | 2.19 [1.99, 2.41] lag 0 (394) | 2.03 |
| pb | LOW | win_50 | no build pass | - | - | - | 1.32 [1.29, 1.36] lag 0 (4096) | 1.01 |
| pb | LOW | win_100 | no build pass | - | 3,6 | - | 1.57 [1.50, 1.64] lag 6 (1644) | 1.27 |
| pb | LOW | launch_300 | no build pass | - | 0,3,6,12 | - | 2.07 [1.88, 2.28] lag 6 (397) | 2.02 |
| dividend_yield | LOW | win_50 | no build pass | - | - | - | 1.10 [1.09, 1.12] lag 12 (15464) | 1.08 |
| dividend_yield | LOW | win_100 | NOT CONFIRMED | 6,12 | - | - | 1.31 [1.28, 1.34] lag 0 (6443) | 1.31 |
| dividend_yield | LOW | launch_300 | no build pass | - | - | - | 1.46 [1.38, 1.54] lag 12 (1304) | 1.43 |

## Holdout decile lift curves, win_50, lag 0

| feature | dir | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 1.38 (3854) | 1.14 (3196) | 1.01 (2813) | 0.93 (2598) | 0.88 (2456) | 0.83 (2325) | 0.82 (2305) | 0.83 (2310) | 0.99 (2766) | 1.19 (3339) |
| ret_12m_skip1 | HIGH | 1.45 (4001) | 1.14 (3155) | 1.03 (2849) | 0.94 (2587) | 0.84 (2313) | 0.83 (2297) | 0.79 (2190) | 0.82 (2269) | 0.94 (2593) | 1.23 (3394) |
| eps_growth_q0 | HIGH | 1.27 (2293) | 1.10 (1976) | 0.96 (1732) | 0.95 (1703) | 0.88 (1607) | 0.85 (1512) | 0.84 (1522) | 0.96 (1722) | 1.02 (1835) | 1.17 (2101) |
| rev_growth_accel | HIGH | 1.15 (2906) | 1.06 (2680) | 1.01 (2547) | 0.97 (2464) | 0.91 (2291) | 0.85 (2148) | 0.88 (2237) | 0.96 (2427) | 1.06 (2679) | 1.15 (2924) |
| op_margin_delta | HIGH | 1.17 (3090) | 1.02 (2674) | 0.93 (2447) | 0.89 (2342) | 0.86 (2265) | 0.90 (2358) | 0.95 (2487) | 1.02 (2682) | 1.05 (2770) | 1.20 (3157) |
| peg | LOW | 1.18 (959) | 1.22 (987) | 1.19 (962) | 1.12 (904) | 1.06 (857) | 0.90 (733) | 0.97 (789) | 0.87 (703) | 0.75 (608) | 0.76 (618) |
| pe | LOW | 1.40 (2471) | 1.13 (1963) | 0.98 (1704) | 0.93 (1610) | 0.91 (1582) | 0.87 (1512) | 0.86 (1493) | 0.88 (1523) | 0.96 (1661) | 1.05 (1831) |
| pe_vs_5y_median | LOW | 1.28 (2003) | 1.26 (1956) | 1.04 (1629) | 0.93 (1441) | 0.85 (1318) | 0.87 (1361) | 0.80 (1245) | 0.89 (1379) | 1.00 (1560) | 1.09 (1702) |
| fcf_ps_slope | HIGH | 0.98 (2733) | 0.96 (2691) | 0.96 (2687) | 1.03 (2864) | 1.01 (2804) | 1.02 (2859) | 1.02 (2855) | 0.99 (2749) | 1.00 (2799) | 1.03 (2867) |
| pegy | LOW | 1.19 (1011) | 1.23 (1043) | 1.17 (992) | 1.13 (952) | 1.05 (883) | 0.92 (777) | 0.94 (796) | 0.84 (709) | 0.79 (665) | 0.75 (641) |
| pct_from_52w_high | LOW | 0.68 (1885) | 0.75 (2090) | 0.81 (2244) | 0.85 (2360) | 0.91 (2511) | 1.00 (2776) | 1.10 (3052) | 1.20 (3319) | 1.28 (3556) | 1.42 (3946) |
| dist_above_30w_sma | HIGH | 1.33 (3715) | 1.15 (3210) | 1.01 (2814) | 0.93 (2593) | 0.86 (2392) | 0.86 (2396) | 0.86 (2391) | 0.89 (2475) | 0.99 (2756) | 1.15 (3223) |
| atr_contraction | HIGH | 0.99 (2779) | 1.02 (2848) | 1.00 (2811) | 1.01 (2830) | 1.03 (2867) | 1.00 (2802) | 0.99 (2776) | 1.00 (2809) | 1.01 (2829) | 0.94 (2636) |
| inst_pct | LOWMID | 0.97 (2597) | 1.04 (2786) | 0.96 (2561) | 0.95 (2558) | 0.94 (2516) | 0.98 (2632) | 1.05 (2820) | 1.03 (2769) | 0.99 (2667) | 1.08 (2915) |
| inst_pct_delta_qoq | HIGH | 1.14 (3072) | 1.06 (2846) | 1.00 (2670) | 0.91 (2435) | 0.88 (2355) | 0.92 (2469) | 0.93 (2502) | 1.01 (2695) | 1.07 (2860) | 1.08 (2899) |
| insider_buy_count_90d | HIGH | 0.94 (21473) | - | - | - | - | - | 3.50 (701) | 1.46 (1201) | 1.02 (2464) | 1.19 (2160) |
| net_debt_to_ebitda | LOW | 1.03 (2158) | 0.95 (1985) | 0.90 (1875) | 1.05 (2197) | 0.98 (2055) | 1.03 (2149) | 0.96 (1998) | 0.92 (1921) | 1.04 (2175) | 1.14 (2377) |
| share_count_change_8q | LOW | 1.14 (3040) | 0.95 (2538) | 0.86 (2303) | 0.90 (2401) | 0.89 (2371) | 0.97 (2578) | 1.02 (2721) | 1.06 (2831) | 1.11 (2965) | 1.09 (2911) |
| shareholder_yield | HIGH | 1.12 (2980) | 1.16 (3086) | 1.10 (2926) | 1.05 (2806) | 1.03 (2752) | 0.88 (2336) | 0.77 (2049) | 0.86 (2278) | 0.93 (2474) | 1.11 (2969) |
| marketcap | LOW | 1.12 (3133) | 1.16 (3251) | 1.16 (3259) | 1.12 (3137) | 1.10 (3082) | 0.97 (2713) | 0.89 (2501) | 0.92 (2579) | 0.83 (2324) | 0.72 (2020) |
| pb | LOW | 1.32 (4096) | 0.99 (2535) | 1.00 (2629) | 0.95 (2414) | 0.93 (2372) | 0.96 (2502) | 0.93 (2411) | 0.96 (2476) | 0.94 (2475) | 0.96 (2528) |
| dividend_yield | LOW | 1.09 (15577) | - | - | - | 1.63 (444) | 1.03 (2530) | 0.82 (2278) | 0.80 (2178) | 0.82 (2244) | 1.00 (2743) |

## Holdout extreme-cell lift by SPY drawdown bucket, win_50

| feature | lag | 0-10 | 10-20 | 20-30 |
| --- | --- | ---: | ---: | ---: |
| ret_6m_skip1 | 0 | 1.23 [1.19, 1.27] (2722) | 1.04 [0.97, 1.12] (577) | insufficient (40) |
| ret_6m_skip1 | 3 | 1.23 [1.19, 1.27] (2715) | 1.13 [1.05, 1.21] (623) | insufficient (40) |
| ret_6m_skip1 | 6 | 1.26 [1.22, 1.30] (2755) | 1.00 [0.93, 1.08] (547) | insufficient (42) |
| ret_6m_skip1 | 12 | 1.18 [1.14, 1.22] (2543) | 1.13 [1.05, 1.21] (591) | insufficient (37) |
| ret_12m_skip1 | 0 | 1.27 [1.23, 1.32] (2789) | 1.04 [0.96, 1.12] (565) | insufficient (40) |
| ret_12m_skip1 | 3 | 1.27 [1.23, 1.32] (2766) | 1.03 [0.95, 1.11] (551) | insufficient (43) |
| ret_12m_skip1 | 6 | 1.24 [1.20, 1.28] (2662) | 1.03 [0.95, 1.11] (538) | insufficient (38) |
| ret_12m_skip1 | 12 | 1.15 [1.11, 1.19] (2419) | 1.07 [0.99, 1.16] (535) | insufficient (33) |
| eps_growth_q0 | 0 | 1.18 [1.13, 1.23] (1676) | 1.11 [1.02, 1.22] (394) | insufficient (31) |
| eps_growth_q0 | 3 | 1.14 [1.09, 1.19] (1614) | 1.15 [1.06, 1.26] (412) | insufficient (32) |
| eps_growth_q0 | 6 | 1.13 [1.08, 1.18] (1600) | 1.14 [1.04, 1.24] (400) | insufficient (25) |
| eps_growth_q0 | 12 | 1.12 [1.07, 1.17] (1579) | 1.02 [0.92, 1.12] (313) | insufficient (26) |
| rev_growth_accel | 0 | 1.15 [1.11, 1.19] (2327) | 1.15 [1.07, 1.24] (556) | insufficient (41) |
| rev_growth_accel | 3 | 1.15 [1.11, 1.19] (2295) | 1.17 [1.09, 1.26] (547) | insufficient (46) |
| rev_growth_accel | 6 | 1.11 [1.07, 1.15] (2186) | 1.20 [1.11, 1.30] (550) | insufficient (40) |
| rev_growth_accel | 12 | 1.09 [1.05, 1.13] (2084) | 0.98 [0.90, 1.07] (435) | insufficient (27) |
| op_margin_delta | 0 | 1.21 [1.17, 1.26] (2527) | 1.14 [1.06, 1.22] (585) | insufficient (45) |
| op_margin_delta | 3 | 1.22 [1.18, 1.26] (2517) | 1.16 [1.08, 1.25] (584) | insufficient (41) |
| op_margin_delta | 6 | 1.22 [1.18, 1.26] (2496) | 1.13 [1.05, 1.22] (559) | insufficient (31) |
| op_margin_delta | 12 | 1.14 [1.10, 1.18] (2291) | 0.98 [0.90, 1.06] (459) | insufficient (21) |
| peg | 0 | 1.18 [1.10, 1.26] (704) | 1.14 [1.01, 1.28] (230) | insufficient (25) |
| peg | 3 | 1.16 [1.09, 1.24] (742) | 1.12 [0.99, 1.26] (223) | insufficient (24) |
| peg | 6 | 1.08 [1.01, 1.15] (713) | 0.99 [0.87, 1.12] (204) | insufficient (20) |
| peg | 12 | 1.11 [1.04, 1.18] (798) | 1.09 [0.97, 1.22] (230) | insufficient (16) |
| pe | 0 | 1.32 [1.27, 1.38] (1821) | 1.66 [1.54, 1.77] (603) | insufficient (47) |
| pe | 3 | 1.31 [1.26, 1.37] (1851) | 1.58 [1.47, 1.69] (574) | insufficient (38) |
| pe | 6 | 1.27 [1.22, 1.32] (1827) | 1.48 [1.37, 1.59] (545) | insufficient (35) |
| pe | 12 | 1.30 [1.25, 1.35] (1927) | 1.30 [1.20, 1.41] (474) | insufficient (28) |
| pe_vs_5y_median | 0 | 1.23 [1.18, 1.29] (1501) | 1.42 [1.31, 1.54] (458) | insufficient (44) |
| pe_vs_5y_median | 3 | 1.25 [1.19, 1.31] (1541) | 1.35 [1.24, 1.47] (435) | insufficient (42) |
| pe_vs_5y_median | 6 | 1.20 [1.14, 1.25] (1497) | 1.31 [1.20, 1.42] (422) | insufficient (40) |
| pe_vs_5y_median | 12 | 1.21 [1.15, 1.26] (1533) | 1.20 [1.09, 1.31] (380) | insufficient (28) |
| fcf_ps_slope | 0 | 1.01 [0.97, 1.05] (2227) | 1.09 [1.01, 1.17] (602) | insufficient (38) |
| fcf_ps_slope | 3 | 1.02 [0.98, 1.06] (2234) | 0.99 [0.92, 1.07] (539) | insufficient (40) |
| fcf_ps_slope | 6 | 1.01 [0.97, 1.04] (2177) | 0.97 [0.90, 1.05] (516) | insufficient (44) |
| fcf_ps_slope | 12 | 1.00 [0.96, 1.04] (2118) | 1.00 [0.92, 1.08] (509) | insufficient (26) |
| pegy | 0 | 1.20 [1.12, 1.28] (745) | 1.14 [1.02, 1.28] (240) | insufficient (26) |
| pegy | 3 | 1.17 [1.10, 1.24] (781) | 1.13 [1.00, 1.27] (229) | insufficient (25) |
| pegy | 6 | 1.07 [1.01, 1.15] (742) | 0.99 [0.87, 1.12] (208) | insufficient (20) |
| pegy | 12 | 1.12 [1.06, 1.19] (835) | 1.10 [0.98, 1.24] (235) | insufficient (16) |
| pct_from_52w_high | 0 | 0.70 [0.67, 0.73] (1536) | 0.61 [0.55, 0.67] (333) | insufficient (16) |
| pct_from_52w_high | 3 | 0.70 [0.66, 0.73] (1518) | 0.71 [0.64, 0.78] (380) | insufficient (17) |
| pct_from_52w_high | 6 | 0.75 [0.71, 0.78] (1612) | 0.62 [0.56, 0.68] (326) | insufficient (19) |
| pct_from_52w_high | 12 | 0.75 [0.72, 0.79] (1589) | 0.72 [0.66, 0.80] (364) | insufficient (24) |
| dist_above_30w_sma | 0 | 1.20 [1.16, 1.24] (2649) | 0.97 [0.90, 1.05] (539) | insufficient (35) |
| dist_above_30w_sma | 3 | 1.21 [1.17, 1.25] (2661) | 1.08 [1.00, 1.16] (595) | insufficient (33) |
| dist_above_30w_sma | 6 | 1.25 [1.20, 1.29] (2728) | 1.11 [1.03, 1.20] (607) | insufficient (48) |
| dist_above_30w_sma | 12 | 1.24 [1.20, 1.28] (2667) | 1.08 [1.00, 1.16] (568) | insufficient (33) |
| atr_contraction | 0 | 0.97 [0.93, 1.01] (2150) | 0.84 [0.77, 0.91] (463) | insufficient (23) |
| atr_contraction | 3 | 0.95 [0.91, 0.99] (2102) | 1.02 [0.95, 1.10] (565) | insufficient (29) |
| atr_contraction | 6 | 1.03 [1.00, 1.07] (2286) | 0.97 [0.90, 1.05] (535) | insufficient (32) |
| atr_contraction | 12 | 0.98 [0.94, 1.02] (2139) | 0.97 [0.90, 1.05] (524) | insufficient (42) |
| inst_pct | 0 | 0.96 [0.94, 0.98] (8132) | 0.94 [0.90, 0.98] (2002) | 0.90 [0.77, 1.06] (133) |
| inst_pct | 3 | 0.95 [0.94, 0.97] (8033) | 0.95 [0.91, 0.99] (1977) | 0.94 [0.81, 1.10] (138) |
| inst_pct | 6 | 0.95 [0.93, 0.97] (7995) | 0.96 [0.92, 1.00] (2048) | 0.91 [0.77, 1.06] (131) |
| inst_pct | 12 | 0.95 [0.94, 0.97] (7914) | 0.94 [0.90, 0.97] (1920) | 0.96 [0.82, 1.12] (136) |
| inst_pct_delta_qoq | 0 | 1.08 [1.04, 1.12] (2287) | 1.09 [1.01, 1.17] (578) | insufficient (34) |
| inst_pct_delta_qoq | 3 | 1.15 [1.11, 1.19] (2414) | 1.19 [1.11, 1.28] (621) | insufficient (36) |
| inst_pct_delta_qoq | 6 | 1.13 [1.09, 1.17] (2362) | 1.16 [1.08, 1.24] (610) | insufficient (37) |
| inst_pct_delta_qoq | 12 | 1.15 [1.11, 1.20] (2377) | 1.17 [1.09, 1.26] (591) | insufficient (41) |
| insider_buy_count_90d | 0 | 1.22 [1.17, 1.27] (1714) | 1.06 [0.97, 1.15] (418) | insufficient (28) |
| insider_buy_count_90d | 3 | 1.29 [1.24, 1.34] (1831) | 0.96 [0.87, 1.06] (360) | insufficient (24) |
| insider_buy_count_90d | 6 | 1.15 [1.11, 1.20] (1679) | 1.03 [0.94, 1.12] (393) | insufficient (24) |
| insider_buy_count_90d | 12 | 1.01 [0.97, 1.06] (1606) | 0.91 [0.82, 1.01] (329) | insufficient (20) |
| net_debt_to_ebitda | 0 | 1.08 [1.04, 1.13] (1786) | 0.87 [0.79, 0.96] (356) | insufficient (16) |
| net_debt_to_ebitda | 3 | 1.07 [1.02, 1.11] (1770) | 0.83 [0.75, 0.91] (336) | insufficient (17) |
| net_debt_to_ebitda | 6 | 1.02 [0.98, 1.06] (1690) | 0.79 [0.71, 0.87] (317) | insufficient (14) |
| net_debt_to_ebitda | 12 | 1.02 [0.97, 1.06] (1677) | 0.80 [0.72, 0.89] (316) | insufficient (17) |
| share_count_change_8q | 0 | 1.15 [1.11, 1.19] (2440) | 1.10 [1.02, 1.19] (562) | insufficient (38) |
| share_count_change_8q | 3 | 1.15 [1.11, 1.19] (2415) | 1.07 [0.99, 1.15] (532) | insufficient (30) |
| share_count_change_8q | 6 | 1.15 [1.11, 1.20] (2396) | 1.03 [0.95, 1.11] (501) | insufficient (30) |
| share_count_change_8q | 12 | 1.14 [1.10, 1.18] (2297) | 0.98 [0.90, 1.07] (466) | insufficient (24) |
| shareholder_yield | 0 | 1.15 [1.11, 1.19] (2444) | 0.97 [0.89, 1.05] (493) | insufficient (32) |
| shareholder_yield | 3 | 1.16 [1.12, 1.20] (2431) | 0.93 [0.85, 1.01] (461) | insufficient (30) |
| shareholder_yield | 6 | 1.14 [1.10, 1.18] (2361) | 0.90 [0.82, 0.98] (438) | insufficient (29) |
| shareholder_yield | 12 | 1.12 [1.08, 1.16] (2254) | 0.83 [0.75, 0.91] (391) | insufficient (25) |
| marketcap | 0 | 1.11 [1.07, 1.15] (2460) | 1.14 [1.06, 1.22] (629) | insufficient (44) |
| marketcap | 3 | 1.09 [1.05, 1.13] (2411) | 1.02 [0.94, 1.10] (564) | insufficient (36) |
| marketcap | 6 | 1.06 [1.02, 1.10] (2349) | 0.99 [0.91, 1.06] (545) | insufficient (39) |
| marketcap | 12 | 1.03 [1.00, 1.07] (2268) | 0.98 [0.90, 1.06] (535) | insufficient (34) |
| pb | 0 | 1.36 [1.32, 1.40] (3347) | 1.18 [1.11, 1.26] (704) | insufficient (45) |
| pb | 3 | 1.36 [1.32, 1.40] (3314) | 1.08 [1.01, 1.16] (656) | insufficient (52) |
| pb | 6 | 1.32 [1.28, 1.36] (3182) | 1.13 [1.05, 1.20] (685) | insufficient (43) |
| pb | 12 | 1.26 [1.22, 1.30] (3003) | 1.01 [0.94, 1.09] (589) | insufficient (37) |
| dividend_yield | 0 | 1.08 [1.06, 1.10] (12139) | 1.15 [1.11, 1.18] (3227) | 1.11 [0.98, 1.25] (211) |
| dividend_yield | 3 | 1.08 [1.06, 1.10] (12138) | 1.15 [1.11, 1.18] (3257) | 1.10 [0.98, 1.25] (212) |
| dividend_yield | 6 | 1.08 [1.07, 1.10] (12157) | 1.14 [1.11, 1.18] (3278) | 1.12 [0.99, 1.27] (218) |
| dividend_yield | 12 | 1.09 [1.08, 1.11] (11999) | 1.14 [1.11, 1.18] (3249) | 1.12 [0.99, 1.27] (216) |

## Composite (section 4), build beside holdout

Fewer than 3 features PASS-build on win_50; composite = top 3 by extreme-decile lift, UNCONFIRMED: ret_12m_skip1, pe_vs_5y_median, inst_pct_delta_qoq.
Recipe: mean of oriented raw percentile ranks; pool share = cell rows / all universe rows at that lag.

| lag | label | cell | build pool | build | hold. coverage | hold. pool | hold. rows | holdout | holdout ≥1.5/1.2 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | win_50 | decile 10 | 2.9% | 1.12 [1.06, 1.19] (957) | 60.5% | 6.1% | 10,002 | 1.16 [1.11, 1.21] (1751) |  |
| 0 | win_50 | deciles 8-10 | 8.8% | 1.09 [1.05, 1.13] (2777) | 60.5% | 18.1% | 29,921 | 1.06 [1.04, 1.09] (4809) |  |
| 0 | win_100 | decile 10 | 2.9% | 1.51 [1.29, 1.75] (167) | 60.5% | 6.1% | 10,002 | 1.41 [1.30, 1.53] (569) |  |
| 0 | win_100 | deciles 8-10 | 8.8% | 1.27 [1.16, 1.40] (422) | 60.5% | 18.1% | 29,921 | 1.15 [1.09, 1.21] (1381) |  |
| 0 | launch_300 | decile 10 | 2.9% | insufficient (48) | 59.9% | 6.0% | 8,453 | insufficient (70) |  |
| 0 | launch_300 | deciles 8-10 | 8.8% | 1.28 [1.06, 1.55] (108) | 59.9% | 18.0% | 25,286 | 1.10 [0.94, 1.28] (164) |  |
| 3 | win_50 | decile 10 | 2.8% | 1.16 [1.10, 1.24] (970) | 60.0% | 6.0% | 9,923 | 1.19 [1.14, 1.24] (1796) |  |
| 3 | win_50 | deciles 8-10 | 8.4% | 1.09 [1.05, 1.13] (2717) | 60.0% | 18.0% | 29,684 | 1.08 [1.06, 1.11] (4902) |  |
| 3 | win_100 | decile 10 | 2.8% | 1.28 [1.09, 1.51] (140) | 60.0% | 6.0% | 9,923 | 1.42 [1.31, 1.53] (572) |  |
| 3 | win_100 | deciles 8-10 | 8.4% | 1.21 [1.09, 1.33] (394) | 60.0% | 18.0% | 29,684 | 1.13 [1.08, 1.19] (1369) |  |
| 3 | launch_300 | decile 10 | 2.8% | insufficient (43) | 59.4% | 6.0% | 8,376 | insufficient (51) |  |
| 3 | launch_300 | deciles 8-10 | 8.4% | 1.35 [1.12, 1.63] (108) | 59.4% | 17.8% | 25,055 | 0.91 [0.78, 1.08] (144) |  |
| 6 | win_50 | decile 10 | 2.6% | 1.19 [1.12, 1.26] (951) | 59.6% | 6.0% | 9,865 | 1.12 [1.07, 1.17] (1723) |  |
| 6 | win_50 | deciles 8-10 | 7.9% | 1.09 [1.05, 1.13] (2608) | 59.6% | 17.9% | 29,523 | 1.05 [1.02, 1.08] (4830) |  |
| 6 | win_100 | decile 10 | 2.6% | 1.69 [1.46, 1.95] (180) | 59.6% | 6.0% | 9,865 | 1.29 [1.19, 1.40] (540) |  |
| 6 | win_100 | deciles 8-10 | 7.9% | 1.27 [1.16, 1.40] (406) | 59.6% | 17.9% | 29,523 | 1.11 [1.05, 1.17] (1390) |  |
| 6 | launch_300 | decile 10 | 2.6% | insufficient (56) | 58.9% | 5.9% | 8,306 | insufficient (55) |  |
| 6 | launch_300 | deciles 8-10 | 7.9% | 1.59 [1.34, 1.89] (126) | 58.9% | 17.7% | 24,858 | 0.83 [0.70, 0.98] (140) |  |
| 12 | win_50 | decile 10 | 2.4% | 1.25 [1.18, 1.33] (917) | 58.5% | 5.9% | 9,672 | 1.07 [1.02, 1.12] (1658) |  |
| 12 | win_50 | deciles 8-10 | 7.1% | 1.12 [1.08, 1.16] (2459) | 58.5% | 17.6% | 28,956 | 1.01 [0.98, 1.03] (4675) |  |
| 12 | win_100 | decile 10 | 2.4% | 1.84 [1.60, 2.12] (185) | 58.5% | 5.9% | 9,672 | 1.22 [1.13, 1.33] (523) |  |
| 12 | win_100 | deciles 8-10 | 7.1% | 1.37 [1.24, 1.51] (412) | 58.5% | 17.6% | 28,956 | 1.02 [0.97, 1.08] (1305) |  |
| 12 | launch_300 | decile 10 | 2.4% | insufficient (55) | 57.8% | 5.8% | 8,146 | insufficient (57) |  |
| 12 | launch_300 | deciles 8-10 | 7.1% | 1.43 [1.18, 1.72] (107) | 57.8% | 17.3% | 24,385 | 0.83 [0.71, 0.97] (155) |  |

### Holdout composite by SPY drawdown bucket, lag 0

| label | cell | 0-10 | 10-20 | 20-30 |
| --- | --- | ---: | ---: | ---: |
| win_50 | decile 10 | 1.14 [1.08, 1.19] (1335) | 1.20 [1.09, 1.32] (377) | insufficient (39) |
| win_50 | deciles 8-10 | 1.05 [1.02, 1.08] (3694) | 1.09 [1.03, 1.16] (1025) | insufficient (90) |
| win_100 | decile 10 | 1.38 [1.26, 1.52] (430) | 1.46 [1.24, 1.72] (130) | insufficient (9) |
| win_100 | deciles 8-10 | 1.12 [1.05, 1.18] (1038) | 1.21 [1.09, 1.35] (322) | insufficient (21) |
| launch_300 | decile 10 | insufficient (49) | insufficient (20) | insufficient (1) |
| launch_300 | deciles 8-10 | 1.12 [0.93, 1.35] (110) | insufficient (47) | insufficient (7) |

### Holdout composite by months-since-trough bucket, lag 0

| label | cell | 0-12 | 13-24 |
| --- | --- | ---: | ---: |
| win_50 | decile 10 | 1.15 [1.10, 1.20] (1576) | 1.25 [1.09, 1.42] (175) |
| win_50 | deciles 8-10 | 1.06 [1.03, 1.09] (4338) | 1.12 [1.03, 1.21] (471) |
| win_100 | decile 10 | 1.37 [1.26, 1.49] (517) | insufficient (52) |
| win_100 | deciles 8-10 | 1.11 [1.05, 1.17] (1254) | 1.62 [1.37, 1.92] (127) |
| launch_300 | decile 10 | insufficient (55) | insufficient (15) |
| launch_300 | deciles 8-10 | 1.03 [0.87, 1.23] (126) | insufficient (38) |

## Expected win_50 per ten picks, by regime bucket (holdout)

Cell = 10 x holdout bucket base rate (win_50) x the composite cell's overall holdout lift at lag 0.
Buckets with fewer than 100 wins, or a composite cell under D8, read insufficient.

| composite cell | holdout lift | events | drawdown 0-10 | drawdown 10-20 | drawdown 20-30 | mst 0-12 | mst 13-24 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| decile 10 | 1.16 | 1751 | 2.01 | 1.84 | 1.71 | 1.97 | 1.98 |
| deciles 8-10 | 1.06 | 4809 | 1.84 | 1.69 | 1.57 | 1.81 | 1.82 |

## Exploratory: 12-month realized volatility deciles (outside the pass criteria)

Annualized standard deviation of daily log returns over the 252 trading days ending on the decision trade
date, ranked like every other feature. No direction was declared and no verdict is given. Cell = lift (events).

### realized_vol_12m decile lifts, win_50

| window | lag | coverage | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| build | 0 | 99.3% | 0.24 (1074) | 0.53 (2404) | 0.72 (3293) | 0.79 (3591) | 0.97 (4412) | 1.08 (4939) | 1.25 (5691) | 1.36 (6217) | 1.49 (6814) | 1.57 (7197) |
| build | 3 | 98.3% | 0.26 (1172) | 0.54 (2443) | 0.71 (3202) | 0.79 (3540) | 0.98 (4401) | 1.10 (4968) | 1.25 (5650) | 1.35 (6055) | 1.47 (6626) | 1.55 (6980) |
| build | 6 | 97.1% | 0.29 (1282) | 0.56 (2483) | 0.70 (3125) | 0.79 (3506) | 0.96 (4255) | 1.11 (4925) | 1.28 (5667) | 1.34 (5928) | 1.42 (6292) | 1.55 (6873) |
| build | 12 | 94.8% | 0.31 (1349) | 0.58 (2466) | 0.72 (3068) | 0.80 (3438) | 0.97 (4166) | 1.11 (4759) | 1.25 (5346) | 1.36 (5816) | 1.39 (5944) | 1.50 (6438) |
| holdout | 0 | 98.9% | 0.29 (806) | 0.52 (1449) | 0.73 (2022) | 0.86 (2395) | 1.02 (2823) | 1.16 (3218) | 1.28 (3564) | 1.34 (3716) | 1.43 (3953) | 1.36 (3792) |
| holdout | 3 | 97.8% | 0.32 (867) | 0.56 (1524) | 0.80 (2203) | 0.89 (2451) | 0.99 (2709) | 1.14 (3118) | 1.25 (3430) | 1.32 (3621) | 1.41 (3885) | 1.33 (3659) |
| holdout | 6 | 96.6% | 0.35 (942) | 0.61 (1650) | 0.83 (2253) | 0.91 (2472) | 0.99 (2694) | 1.12 (3054) | 1.21 (3277) | 1.32 (3571) | 1.36 (3686) | 1.31 (3556) |
| holdout | 12 | 94.2% | 0.39 (1047) | 0.68 (1792) | 0.87 (2306) | 0.93 (2469) | 1.03 (2729) | 1.08 (2873) | 1.22 (3226) | 1.24 (3289) | 1.31 (3472) | 1.23 (3271) |

### realized_vol_12m decile lifts, win_100

| window | lag | coverage | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| build | 0 | 99.3% | insuff. (39) | 0.16 (173) | 0.26 (272) | 0.38 (403) | 0.58 (614) | 0.80 (849) | 1.14 (1205) | 1.62 (1711) | 2.10 (2222) | 2.90 (3073) |
| build | 3 | 98.3% | insuff. (61) | 0.17 (181) | 0.31 (321) | 0.41 (421) | 0.63 (655) | 0.84 (877) | 1.16 (1207) | 1.52 (1581) | 2.09 (2173) | 2.79 (2900) |
| build | 6 | 97.1% | insuff. (86) | 0.20 (205) | 0.34 (346) | 0.44 (451) | 0.61 (616) | 0.93 (946) | 1.16 (1181) | 1.51 (1528) | 1.97 (1997) | 2.75 (2796) |
| build | 12 | 94.8% | 0.11 (102) | 0.24 (236) | 0.33 (315) | 0.46 (442) | 0.73 (701) | 0.92 (888) | 1.18 (1139) | 1.51 (1456) | 1.95 (1879) | 2.58 (2492) |
| holdout | 0 | 98.9% | insuff. (55) | 0.17 (158) | 0.29 (274) | 0.44 (415) | 0.73 (697) | 0.96 (916) | 1.33 (1263) | 1.62 (1542) | 2.10 (1998) | 2.31 (2201) |
| holdout | 3 | 97.8% | insuff. (81) | 0.17 (162) | 0.38 (355) | 0.56 (524) | 0.75 (700) | 0.99 (926) | 1.27 (1192) | 1.58 (1486) | 2.03 (1903) | 2.19 (2063) |
| holdout | 6 | 96.6% | 0.12 (108) | 0.17 (162) | 0.42 (385) | 0.61 (563) | 0.77 (711) | 1.02 (950) | 1.23 (1138) | 1.61 (1491) | 1.91 (1767) | 2.15 (1993) |
| holdout | 12 | 94.2% | 0.13 (117) | 0.23 (206) | 0.50 (449) | 0.67 (601) | 0.86 (767) | 0.99 (890) | 1.27 (1136) | 1.56 (1393) | 1.83 (1641) | 1.95 (1753) |

### realized_vol_12m decile lifts, launch_300

| window | lag | coverage | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| build | 0 | 99.3% | insuff. (2) | insuff. (11) | insuff. (27) | insuff. (77) | insuff. (94) | 0.53 (135) | 0.76 (192) | 1.54 (391) | 2.19 (556) | 4.13 (1049) |
| build | 3 | 98.3% | insuff. (4) | insuff. (13) | insuff. (40) | insuff. (72) | 0.44 (109) | 0.49 (121) | 0.86 (211) | 1.40 (344) | 2.23 (548) | 4.06 (1001) |
| build | 6 | 97.1% | insuff. (11) | insuff. (22) | insuff. (44) | insuff. (83) | 0.53 (126) | 0.60 (142) | 0.83 (198) | 1.35 (322) | 2.04 (485) | 3.98 (950) |
| build | 12 | 94.8% | insuff. (22) | insuff. (27) | insuff. (38) | insuff. (85) | 0.59 (131) | 0.64 (143) | 0.91 (202) | 1.33 (294) | 1.98 (440) | 3.76 (837) |
| holdout | 0 | 98.8% | insuff. (15) | insuff. (10) | insuff. (20) | insuff. (62) | insuff. (98) | 0.75 (132) | 0.90 (159) | 1.31 (230) | 2.11 (372) | 3.75 (662) |
| holdout | 3 | 97.6% | insuff. (19) | insuff. (9) | insuff. (22) | insuff. (76) | insuff. (98) | 0.78 (135) | 1.12 (194) | 1.22 (212) | 2.25 (391) | 3.34 (582) |
| holdout | 6 | 96.3% | insuff. (19) | insuff. (16) | insuff. (27) | insuff. (78) | insuff. (89) | 0.87 (149) | 1.09 (188) | 1.29 (222) | 2.24 (385) | 3.17 (545) |
| holdout | 12 | 93.6% | insuff. (15) | insuff. (22) | insuff. (36) | insuff. (74) | 0.78 (129) | 0.96 (159) | 1.09 (180) | 1.57 (260) | 2.11 (349) | 2.59 (428) |

### Spearman correlation of the realized-volatility decile with other feature deciles, lag 0

Computed as the correlation of the two decile ranks over rows where both are non-null.

| window | feature decile | Spearman | rows |
| --- | --- | ---: | ---: |
| build | marketcap | -0.509 | 389,272 |
| build | pct_from_52w_high | 0.484 | 390,504 |
| build | share_count_change_8q | 0.320 | 370,791 |
| holdout | marketcap | -0.474 | 162,709 |
| holdout | pct_from_52w_high | 0.542 | 163,110 |
| holdout | share_count_change_8q | 0.405 | 155,922 |
