# Decile retest — build-window results (GROWTH-002, S6)

Window 2006-01 to 2019-12. 393,429 universe stock-months per lag, four lags. Labels: win_50 and win_100
(12-month forward return >= 50% / >= 100%, E1) with launch_300 (24-month, D1) as reference. Every
number comes from src/decile.py over data/processed/{features,labels12,labels,regime}.parquet. The
holdout was not summarized.

Definitions. Decile = rank within (month_end, lag) among non-null rows, ties sharing the lowest rank,
decile 10 = highest raw value; decile sizes are unequal where a feature has mass points, so each cell
prints its row share. base = events / non-null rows at that lag; lift = cell rate / base; coverage =
non-null rows / all rows. Wilson 95% CI over a fixed base. D8: 100 events per cell. Directions were
declared in spec section 3 before any result. Build-window pass (half of the section 3 criterion) =
extreme-cell lift >= 1.5 with lower bound >= 1.2, and Spearman |rho| >= 0.6 with the declared
sign over the D8-sufficient deciles (at least 5). The holdout half is S7. No recommendations.

## Reading

This section reads the build-window tables below (2006-01 to 2019-12) under GROWTH-002. Directions were declared in spec section 3 before any number was seen; nothing was flipped afterward. A feature can only "PASS-build" here; the full PASS needs the holdout half in S7. No recommendation is made.

**The 12-month label is common enough to read everywhere.** One universe stock-month in nine reached a 50% gain within twelve months (46,046 of 393,429, 11.70%, inside the 3% to 25% gate); one in 37 doubled (2.73%). Every decile cell of every feature at every lag meets D8 on win_50, and all but a few do on win_100. The rarity problem of GROWTH-001 is gone. The regime problem is not: 2009 entries won 50% at 26.68%, 2007 entries at 4.44%, a six-fold spread that no feature below approaches.

**No feature passes on win_50 in its declared direction.** The best extreme-decile lift is 1.48 [1.42, 1.53], the top decile of quarter-on-quarter change in institutional ownership at lag 0, under the 1.5 line; every other feature's declared cell sits between 0.79 and 1.38. Coverage is high for all but the valuation features that need positive earnings (peg, pegy, pe_vs_5y_median at 43% to 70%). The pass criterion also requires a monotone decile curve, and that is where most features fail more clearly than on lift.

**The decile curves are U-shaped, not monotone, for momentum and for most growth measures.** Twelve-month relative strength at lag 0 runs 1.41 in decile 1, down to 0.76 in decile 6, back up to 1.30 in decile 10 (rho −0.04). The six-month flag, distance above the 30-week average, EPS growth, revenue-growth acceleration, operating-margin change, and price-to-earnings all show the same shape: both tails win more than the middle, and the bottom tail wins at least as often as the top. On a twelve-month horizon the worst performers and the cheapest earners rebound as often as the strongest continue. The top decile of 12-month strength still reaches 2.30 on launch_300 at lag 12 (505 events), consistent with GROWTH-001, but its curve on that label is flat in the middle and lifts at both ends (rho −0.02).

**Three declared directions are backward, with near-perfect monotone curves the other way.** Distance from the 52-week high was declared LOW-better; its curve rises from 0.59 in decile 1 (closest to the high) to 1.53 in decile 10 (farthest), rho +1.00, on win_50, and 0.63 to 1.8-fold at the far end on launch_300. Share-count change over eight quarters was declared LOW-better; deciles 7 to 10 (heaviest issuers) run 1.11 to 1.22 and deciles 1 to 3 (buybacks) 0.77 to 0.91, rho +0.83. Shareholder yield was declared HIGH-better; its top deciles are 0.69 to 0.91 and its bottom deciles 1.17 to 1.29, rho −0.83. These repeat what GROWTH-001's flags H15 and H21 found in binary form: the population that goes on to gain 50% or 300% is far from its highs and is issuing shares. Under E6 they fail; they are not re-declared here.

**Four features pass in the build window on the rarer labels, none on win_50.** Market cap, declared LOW-better, is the cleanest result in the study: monotone from 1.31 in the smallest decile to 0.53 in the largest on win_50 (rho −1.00), and on win_100 the smallest decile reaches 2.03 [1.95, 2.11] on 2,178 events at every lag, on launch_300 2.32 [2.14, 2.52] on 605 events, both PASS-build with rho at or below −0.98. It does not pass on win_50 because the lift is 1.31. PEG and PEGY below their first-decile cutoffs are monotone (rho −0.93 and −0.89 on win_50) with lifts of 1.29 to 1.31 on win_50, rising to 1.78 and 1.83 on win_100 (PASS-build at every lag) and 2.35 to 2.43 on launch_300 where too few deciles meet D8 to compute rho. The zero-dividend decile, which holds 49% of rows because dividend yield has a mass point at zero, is 1.30 on win_50 and passes build on win_100 at lags 6 and 12 at 1.56. In every one of these, the lift grows as the label gets rarer: the same cheap, small, non-paying stocks are over-represented among the biggest movers more than among the moderate ones.

**Two features are near misses on win_50 and stronger on the rarer labels.** The top decile of institutional-ownership change is 1.48 on win_50 with a lower bound of 1.42, 2.06 on win_100, and 2.45 on launch_300 (290 events), but its curve is U-shaped (decile 1 at 1.20, rho 0.20), so it would fail the monotonicity test even at lift 1.5. Net debt to EBITDA's lowest decile is 1.29 on win_50 and 1.57 on win_100 with rho −0.12. Institutional level itself (LOW-to-MID, deciles 3 to 6 pooled) is 0.96: the middle of the ownership range wins slightly less than the tails.

**Nothing in three features.** ATR contraction runs 0.95 to 1.14 across deciles with no order. Insider buy count is zero for 79% of rows, so decile 1 is that mass and the non-zero counts fill deciles 7 to 10 at 0.99 to 1.79, with the top decile at 1.12. FCF-per-share slope is highest in its middle deciles (1.18 to 1.23) and 0.91 at the top: the declared direction is not supported.

**Regime.** For win_50 the calm bucket (drawdown under 10%) holds most events and the deep-drawdown bucket reverses momentum: the top strength decile is 1.45 in calm months and 0.53 in months deeper than 30% below the high. Small caps and low PE-versus-history keep their direction in every bucket (1.20 to 1.67 in the deep-drawdown bucket). The ownership-change feature has no events beyond the 10% bucket because holdings start in 2013.

**The composite is unconfirmed by construction.** With no win_50 pass, section 4's fallback applies: the top three by extreme-decile lift on win_50 are ret_12m_skip1, pe_vs_5y_median, and inst_pct_delta_qoq. The recipe is the mean of the three oriented raw percentile ranks (Matt's S7 ruling, replacing the S6 mean of integer deciles, whose few distinct values left 2.4% of rows in decile 10), ranked into deciles per month and lag. The score is non-null for 29% of rows because the ownership term starts in 2014, so composite decile 10 holds 2.9% of all universe rows and deciles 8 to 10 hold 8.8%; that is the candidate-pool size the spec asks for. On win_50 the top decile lifts 1.12 [1.06, 1.19] on 957 events and deciles 8 to 10 lift 1.09; on win_100 the top decile reaches 1.50 [1.30, 1.75] on 167 events; on launch_300 it has 48 events and cannot be read. The composite adds nothing over its best member on win_50 and is a calm-market object: every regime bucket beyond 10% drawdown is empty for it.

**What this report does not say.** It does not rank features for use; S7 holds the other half of every pass criterion. It does not re-declare the three backward features, which E6 forbids. It does not correct for 22 features times 4 lags times 3 labels of cells. Its one clean, declared-direction, monotone finding is size, and size does not clear the win_50 bar.

## Base rates by year (12-month labels), build window

| year | rows | win_50 | rate_50 | win_100 | rate_100 | launch_300 | rate_300 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2006 | 30,752 | 3447 | 11.21% | 756 | 2.46% | 86 | 0.28% |
| 2007 | 31,216 | 1387 | 4.44% | 321 | 1.03% | 5 | 0.02% |
| 2008 | 27,861 | 1998 | 7.17% | 617 | 2.21% | 164 | 0.59% |
| 2009 | 24,501 | 6537 | 26.68% | 1930 | 7.88% | 561 | 2.29% |
| 2010 | 26,486 | 4432 | 16.73% | 939 | 3.55% | 101 | 0.38% |
| 2011 | 26,564 | 2225 | 8.38% | 435 | 1.64% | 126 | 0.47% |
| 2012 | 25,569 | 5364 | 20.98% | 1043 | 4.08% | 180 | 0.70% |
| 2013 | 27,212 | 3566 | 13.10% | 726 | 2.67% | 111 | 0.41% |
| 2014 | 28,980 | 2137 | 7.37% | 473 | 1.63% | 35 | 0.12% |
| 2015 | 29,363 | 1589 | 5.41% | 199 | 0.68% | 76 | 0.26% |
| 2016 | 28,677 | 4868 | 16.98% | 1049 | 3.66% | 274 | 0.96% |
| 2017 | 29,081 | 3642 | 12.52% | 906 | 3.12% | 107 | 0.37% |
| 2018 | 29,085 | 2070 | 7.12% | 435 | 1.50% | 176 | 0.61% |
| 2019 | 28,082 | 2784 | 9.91% | 902 | 3.21% | 601 | 2.14% |

## Extreme-decile cells, win_50, by lag

Extreme = decile 10 for HIGH, decile 1 for LOW, deciles 3-6 pooled for LOW-to-MID (inst_pct).

| feature | dir | lag | coverage | cell share | rows | events | rate | lift | CI low | CI high | rho | cell |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 0 | 99.9% | 10.0% | 39,379 | 5927 | 15.05% | 1.29 | 1.26 | 1.32 | -0.20 |  |
| ret_6m_skip1 | HIGH | 3 | 99.7% | 10.0% | 39,297 | 6136 | 15.61% | 1.33 | 1.30 | 1.37 | -0.12 |  |
| ret_6m_skip1 | HIGH | 6 | 99.0% | 10.0% | 39,007 | 6069 | 15.56% | 1.33 | 1.30 | 1.36 | 0.08 |  |
| ret_6m_skip1 | HIGH | 12 | 96.8% | 10.0% | 38,140 | 5852 | 15.34% | 1.33 | 1.29 | 1.36 | -0.18 |  |
| ret_12m_skip1 | HIGH | 0 | 99.0% | 10.0% | 39,007 | 5915 | 15.16% | 1.30 | 1.27 | 1.33 | -0.18 |  |
| ret_12m_skip1 | HIGH | 3 | 97.9% | 10.0% | 38,600 | 6105 | 15.82% | 1.36 | 1.33 | 1.39 | -0.15 |  |
| ret_12m_skip1 | HIGH | 6 | 96.8% | 10.0% | 38,140 | 6114 | 16.03% | 1.38 | 1.35 | 1.42 | -0.04 |  |
| ret_12m_skip1 | HIGH | 12 | 94.5% | 10.0% | 37,236 | 5754 | 15.45% | 1.35 | 1.32 | 1.38 | -0.07 |  |
| eps_growth_q0 | HIGH | 0 | 78.0% | 10.0% | 30,546 | 3570 | 11.69% | 1.09 | 1.06 | 1.13 | -0.25 |  |
| eps_growth_q0 | HIGH | 3 | 77.1% | 10.0% | 30,211 | 3606 | 11.94% | 1.12 | 1.09 | 1.15 | -0.25 |  |
| eps_growth_q0 | HIGH | 6 | 76.2% | 10.0% | 29,849 | 3721 | 12.47% | 1.17 | 1.13 | 1.20 | -0.09 |  |
| eps_growth_q0 | HIGH | 12 | 74.7% | 10.0% | 29,257 | 3834 | 13.10% | 1.24 | 1.20 | 1.27 | 0.15 |  |
| rev_growth_accel | HIGH | 0 | 92.8% | 10.0% | 36,569 | 4722 | 12.91% | 1.13 | 1.10 | 1.16 | -0.39 |  |
| rev_growth_accel | HIGH | 3 | 91.5% | 10.0% | 36,090 | 4527 | 12.54% | 1.10 | 1.08 | 1.14 | -0.36 |  |
| rev_growth_accel | HIGH | 6 | 90.4% | 10.0% | 35,623 | 4369 | 12.26% | 1.09 | 1.06 | 1.12 | -0.54 |  |
| rev_growth_accel | HIGH | 12 | 88.1% | 10.0% | 34,752 | 4498 | 12.94% | 1.16 | 1.13 | 1.19 | -0.09 |  |
| op_margin_delta | HIGH | 0 | 96.9% | 10.0% | 38,199 | 5155 | 13.50% | 1.16 | 1.13 | 1.19 | -0.14 |  |
| op_margin_delta | HIGH | 3 | 95.8% | 10.0% | 37,756 | 5132 | 13.59% | 1.18 | 1.15 | 1.21 | -0.20 |  |
| op_margin_delta | HIGH | 6 | 94.6% | 10.0% | 37,286 | 5091 | 13.65% | 1.19 | 1.16 | 1.22 | -0.09 |  |
| op_margin_delta | HIGH | 12 | 92.3% | 10.0% | 36,384 | 5172 | 14.22% | 1.25 | 1.22 | 1.28 | 0.18 |  |
| peg | LOW | 0 | 43.5% | 10.0% | 17,179 | 2072 | 12.06% | 1.29 | 1.24 | 1.34 | -0.99 |  |
| peg | LOW | 3 | 43.6% | 10.0% | 17,194 | 2134 | 12.41% | 1.29 | 1.24 | 1.34 | -0.93 |  |
| peg | LOW | 6 | 43.3% | 10.0% | 17,089 | 2142 | 12.53% | 1.27 | 1.22 | 1.32 | -0.92 |  |
| peg | LOW | 12 | 42.6% | 10.0% | 16,810 | 2114 | 12.58% | 1.23 | 1.18 | 1.28 | -0.95 |  |
| pe | LOW | 0 | 80.0% | 10.2% | 32,004 | 4059 | 12.68% | 1.23 | 1.19 | 1.26 | 0.14 |  |
| pe | LOW | 3 | 80.1% | 10.2% | 31,992 | 3969 | 12.41% | 1.19 | 1.16 | 1.22 | 0.26 |  |
| pe | LOW | 6 | 79.9% | 10.2% | 31,969 | 3973 | 12.43% | 1.18 | 1.15 | 1.22 | 0.30 |  |
| pe | LOW | 12 | 79.1% | 10.2% | 31,617 | 3931 | 12.43% | 1.17 | 1.13 | 1.20 | 0.30 |  |
| pe_vs_5y_median | LOW | 0 | 69.9% | 10.0% | 27,545 | 3659 | 13.28% | 1.35 | 1.31 | 1.39 | -0.39 |  |
| pe_vs_5y_median | LOW | 3 | 69.4% | 10.0% | 27,364 | 3620 | 13.23% | 1.33 | 1.29 | 1.37 | -0.41 |  |
| pe_vs_5y_median | LOW | 6 | 68.7% | 10.0% | 27,092 | 3567 | 13.17% | 1.32 | 1.28 | 1.36 | -0.39 |  |
| pe_vs_5y_median | LOW | 12 | 67.4% | 10.0% | 26,561 | 3624 | 13.64% | 1.35 | 1.31 | 1.39 | -0.41 |  |
| fcf_ps_slope | HIGH | 0 | 99.4% | 10.0% | 39,178 | 4156 | 10.61% | 0.91 | 0.88 | 0.93 | 0.18 |  |
| fcf_ps_slope | HIGH | 3 | 98.2% | 10.0% | 38,730 | 3892 | 10.05% | 0.86 | 0.84 | 0.89 | -0.04 |  |
| fcf_ps_slope | HIGH | 6 | 97.0% | 10.0% | 38,241 | 3839 | 10.04% | 0.86 | 0.84 | 0.89 | -0.18 |  |
| fcf_ps_slope | HIGH | 12 | 94.5% | 10.0% | 37,264 | 3726 | 10.00% | 0.87 | 0.84 | 0.90 | 0.04 |  |
| pegy | LOW | 0 | 45.1% | 10.0% | 17,801 | 2147 | 12.06% | 1.30 | 1.25 | 1.35 | -0.98 |  |
| pegy | LOW | 3 | 45.1% | 10.0% | 17,801 | 2213 | 12.43% | 1.31 | 1.26 | 1.36 | -0.89 |  |
| pegy | LOW | 6 | 44.8% | 10.0% | 17,686 | 2219 | 12.55% | 1.29 | 1.24 | 1.34 | -0.90 |  |
| pegy | LOW | 12 | 44.1% | 10.0% | 17,410 | 2203 | 12.65% | 1.25 | 1.21 | 1.30 | -0.92 |  |
| pct_from_52w_high | LOW | 0 | 99.3% | 10.0% | 39,113 | 2686 | 6.87% | 0.59 | 0.57 | 0.61 | 1.00 |  |
| pct_from_52w_high | LOW | 3 | 98.3% | 10.0% | 38,728 | 3058 | 7.90% | 0.68 | 0.66 | 0.70 | 0.99 |  |
| pct_from_52w_high | LOW | 6 | 97.2% | 10.0% | 38,281 | 3349 | 8.75% | 0.75 | 0.73 | 0.78 | 1.00 |  |
| pct_from_52w_high | LOW | 12 | 94.9% | 10.0% | 37,379 | 3378 | 9.04% | 0.79 | 0.76 | 0.81 | 1.00 |  |
| dist_above_30w_sma | HIGH | 0 | 99.9% | 10.0% | 39,382 | 5784 | 14.69% | 1.25 | 1.23 | 1.28 | -0.22 |  |
| dist_above_30w_sma | HIGH | 3 | 99.7% | 10.0% | 39,307 | 6039 | 15.36% | 1.31 | 1.28 | 1.34 | -0.15 |  |
| dist_above_30w_sma | HIGH | 6 | 99.0% | 10.0% | 39,045 | 6091 | 15.60% | 1.34 | 1.31 | 1.37 | 0.15 |  |
| dist_above_30w_sma | HIGH | 12 | 96.9% | 10.0% | 38,187 | 5884 | 15.41% | 1.33 | 1.30 | 1.36 | 0.03 |  |
| atr_contraction | HIGH | 0 | 100.0% | 10.0% | 39,413 | 4555 | 11.56% | 0.99 | 0.96 | 1.01 | -0.14 |  |
| atr_contraction | HIGH | 3 | 99.9% | 10.0% | 39,391 | 4743 | 12.04% | 1.03 | 1.00 | 1.06 | -0.28 |  |
| atr_contraction | HIGH | 6 | 99.8% | 10.0% | 39,335 | 4910 | 12.48% | 1.07 | 1.04 | 1.09 | -0.03 |  |
| atr_contraction | HIGH | 12 | 98.3% | 10.0% | 38,752 | 4909 | 12.67% | 1.09 | 1.06 | 1.12 | -0.13 |  |
| inst_pct | LOWMID | 0 | 45.0% | 40.0% | 70,809 | 6523 | 9.21% | 0.95 | 0.93 | 0.97 | 0.32 |  |
| inst_pct | LOWMID | 3 | 43.2% | 40.0% | 67,930 | 6306 | 9.28% | 0.96 | 0.93 | 0.98 | 0.27 |  |
| inst_pct | LOWMID | 6 | 41.3% | 40.0% | 65,032 | 6103 | 9.38% | 0.96 | 0.94 | 0.98 | 0.18 |  |
| inst_pct | LOWMID | 12 | 37.2% | 40.0% | 58,526 | 5397 | 9.22% | 0.94 | 0.92 | 0.97 | -0.01 |  |
| inst_pct_delta_qoq | HIGH | 0 | 43.3% | 10.0% | 17,054 | 2448 | 14.35% | 1.48 | 1.42 | 1.53 | 0.22 |  |
| inst_pct_delta_qoq | HIGH | 3 | 41.4% | 10.0% | 16,304 | 2292 | 14.06% | 1.43 | 1.38 | 1.48 | 0.28 |  |
| inst_pct_delta_qoq | HIGH | 6 | 39.3% | 10.0% | 15,489 | 2106 | 13.60% | 1.38 | 1.33 | 1.44 | 0.37 |  |
| inst_pct_delta_qoq | HIGH | 12 | 35.0% | 10.0% | 13,787 | 1934 | 14.03% | 1.42 | 1.36 | 1.48 | 0.20 |  |
| insider_buy_count_90d | HIGH | 0 | 82.4% | 6.9% | 22,203 | 3153 | 14.20% | 1.12 | 1.08 | 1.16 | 0.10 |  |
| insider_buy_count_90d | HIGH | 3 | 80.5% | 6.8% | 21,472 | 2923 | 13.61% | 1.05 | 1.02 | 1.09 | 0.10 |  |
| insider_buy_count_90d | HIGH | 6 | 78.7% | 6.9% | 21,497 | 2896 | 13.47% | 1.02 | 0.99 | 1.06 | -0.20 |  |
| insider_buy_count_90d | HIGH | 12 | 75.3% | 7.2% | 21,245 | 2761 | 13.00% | 1.06 | 1.02 | 1.10 | 0.00 |  |
| net_debt_to_ebitda | LOW | 0 | 88.2% | 10.0% | 34,774 | 4847 | 13.94% | 1.29 | 1.25 | 1.32 | -0.56 |  |
| net_debt_to_ebitda | LOW | 3 | 87.3% | 10.0% | 34,403 | 4771 | 13.87% | 1.28 | 1.24 | 1.31 | -0.61 |  |
| net_debt_to_ebitda | LOW | 6 | 86.3% | 10.0% | 33,999 | 4702 | 13.83% | 1.27 | 1.24 | 1.31 | -0.75 |  |
| net_debt_to_ebitda | LOW | 12 | 84.2% | 10.0% | 33,190 | 4637 | 13.97% | 1.29 | 1.25 | 1.32 | -0.85 |  |
| share_count_change_8q | LOW | 0 | 94.3% | 10.0% | 37,173 | 3898 | 10.49% | 0.91 | 0.89 | 0.94 | 0.77 |  |
| share_count_change_8q | LOW | 3 | 93.1% | 10.0% | 36,679 | 3822 | 10.42% | 0.91 | 0.89 | 0.94 | 0.77 |  |
| share_count_change_8q | LOW | 6 | 91.9% | 10.0% | 36,192 | 3747 | 10.35% | 0.92 | 0.89 | 0.94 | 0.76 |  |
| share_count_change_8q | LOW | 12 | 89.5% | 10.0% | 35,290 | 3683 | 10.44% | 0.93 | 0.91 | 0.96 | 0.83 |  |
| shareholder_yield | HIGH | 0 | 94.3% | 10.0% | 37,183 | 3866 | 10.40% | 0.91 | 0.88 | 0.93 | -0.83 |  |
| shareholder_yield | HIGH | 3 | 93.1% | 10.0% | 36,693 | 3681 | 10.03% | 0.88 | 0.85 | 0.91 | -0.83 |  |
| shareholder_yield | HIGH | 6 | 91.8% | 10.0% | 36,202 | 3501 | 9.67% | 0.85 | 0.83 | 0.88 | -0.83 |  |
| shareholder_yield | HIGH | 12 | 89.5% | 10.0% | 35,301 | 3350 | 9.49% | 0.85 | 0.82 | 0.88 | -0.84 |  |
| marketcap | LOW | 0 | 99.7% | 10.0% | 39,285 | 6033 | 15.36% | 1.31 | 1.28 | 1.34 | -1.00 |  |
| marketcap | LOW | 3 | 100.0% | 10.0% | 39,404 | 5888 | 14.94% | 1.28 | 1.25 | 1.31 | -0.99 |  |
| marketcap | LOW | 6 | 99.9% | 10.0% | 39,376 | 5866 | 14.90% | 1.27 | 1.24 | 1.30 | -1.00 |  |
| marketcap | LOW | 12 | 99.2% | 10.0% | 39,102 | 5802 | 14.84% | 1.27 | 1.24 | 1.30 | -1.00 |  |
| pb | LOW | 0 | 96.6% | 11.7% | 44,536 | 5430 | 12.19% | 1.05 | 1.02 | 1.08 | 0.65 |  |
| pb | LOW | 3 | 96.9% | 11.8% | 45,059 | 5095 | 11.31% | 0.98 | 0.95 | 1.00 | 0.79 |  |
| pb | LOW | 6 | 96.8% | 11.7% | 44,501 | 4862 | 10.93% | 0.94 | 0.92 | 0.97 | 0.87 |  |
| pb | LOW | 12 | 95.8% | 11.7% | 44,068 | 4823 | 10.94% | 0.95 | 0.92 | 0.97 | 0.88 |  |
| dividend_yield | LOW | 0 | 100.0% | 48.8% | 192,049 | 29113 | 15.16% | 1.30 | 1.28 | 1.31 | -0.79 |  |
| dividend_yield | LOW | 3 | 99.9% | 49.1% | 193,098 | 29263 | 15.15% | 1.29 | 1.28 | 1.31 | -0.79 |  |
| dividend_yield | LOW | 6 | 99.9% | 49.4% | 194,211 | 29381 | 15.13% | 1.29 | 1.28 | 1.31 | -0.89 |  |
| dividend_yield | LOW | 12 | 98.7% | 49.8% | 193,391 | 29068 | 15.03% | 1.29 | 1.28 | 1.30 | -0.93 |  |

## Extreme-decile cells, win_100, by lag

Extreme = decile 10 for HIGH, decile 1 for LOW, deciles 3-6 pooled for LOW-to-MID (inst_pct).

| feature | dir | lag | coverage | cell share | rows | events | rate | lift | CI low | CI high | rho | cell |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 0 | 99.9% | 10.0% | 39,379 | 1875 | 4.76% | 1.75 | 1.67 | 1.83 | -0.22 |  |
| ret_6m_skip1 | HIGH | 3 | 99.7% | 10.0% | 39,297 | 1861 | 4.74% | 1.74 | 1.67 | 1.82 | -0.15 |  |
| ret_6m_skip1 | HIGH | 6 | 99.0% | 10.0% | 39,007 | 1871 | 4.80% | 1.78 | 1.70 | 1.86 | -0.15 |  |
| ret_6m_skip1 | HIGH | 12 | 96.8% | 10.0% | 38,140 | 1723 | 4.52% | 1.71 | 1.63 | 1.79 | -0.22 |  |
| ret_12m_skip1 | HIGH | 0 | 99.0% | 10.0% | 39,007 | 1824 | 4.68% | 1.73 | 1.66 | 1.81 | -0.18 |  |
| ret_12m_skip1 | HIGH | 3 | 97.9% | 10.0% | 38,600 | 1792 | 4.64% | 1.74 | 1.66 | 1.82 | -0.22 |  |
| ret_12m_skip1 | HIGH | 6 | 96.8% | 10.0% | 38,140 | 1798 | 4.71% | 1.78 | 1.70 | 1.86 | -0.20 |  |
| ret_12m_skip1 | HIGH | 12 | 94.5% | 10.0% | 37,236 | 1649 | 4.43% | 1.72 | 1.64 | 1.80 | -0.18 |  |
| eps_growth_q0 | HIGH | 0 | 78.0% | 10.0% | 30,546 | 775 | 2.54% | 1.24 | 1.16 | 1.33 | -0.25 |  |
| eps_growth_q0 | HIGH | 3 | 77.1% | 10.0% | 30,211 | 838 | 2.77% | 1.36 | 1.27 | 1.45 | -0.27 |  |
| eps_growth_q0 | HIGH | 6 | 76.2% | 10.0% | 29,849 | 796 | 2.67% | 1.29 | 1.21 | 1.38 | -0.27 |  |
| eps_growth_q0 | HIGH | 12 | 74.7% | 10.0% | 29,257 | 815 | 2.79% | 1.42 | 1.32 | 1.52 | -0.05 |  |
| rev_growth_accel | HIGH | 0 | 92.8% | 10.0% | 36,569 | 1256 | 3.43% | 1.36 | 1.29 | 1.44 | -0.27 |  |
| rev_growth_accel | HIGH | 3 | 91.5% | 10.0% | 36,090 | 1219 | 3.38% | 1.36 | 1.29 | 1.44 | -0.26 |  |
| rev_growth_accel | HIGH | 6 | 90.4% | 10.0% | 35,623 | 1203 | 3.38% | 1.38 | 1.30 | 1.46 | -0.22 |  |
| rev_growth_accel | HIGH | 12 | 88.1% | 10.0% | 34,752 | 1220 | 3.51% | 1.46 | 1.39 | 1.55 | -0.19 |  |
| op_margin_delta | HIGH | 0 | 96.9% | 10.0% | 38,199 | 1585 | 4.15% | 1.59 | 1.52 | 1.67 | -0.15 |  |
| op_margin_delta | HIGH | 3 | 95.8% | 10.0% | 37,756 | 1531 | 4.05% | 1.57 | 1.49 | 1.65 | -0.07 |  |
| op_margin_delta | HIGH | 6 | 94.6% | 10.0% | 37,286 | 1462 | 3.92% | 1.53 | 1.46 | 1.61 | -0.07 |  |
| op_margin_delta | HIGH | 12 | 92.3% | 10.0% | 36,384 | 1472 | 4.05% | 1.63 | 1.55 | 1.71 | 0.15 |  |
| peg | LOW | 0 | 43.5% | 10.0% | 17,179 | 452 | 2.63% | 1.71 | 1.56 | 1.87 | -0.77 | PASS-build |
| peg | LOW | 3 | 43.6% | 10.0% | 17,194 | 479 | 2.79% | 1.71 | 1.57 | 1.87 | -0.96 | PASS-build |
| peg | LOW | 6 | 43.3% | 10.0% | 17,089 | 460 | 2.69% | 1.63 | 1.49 | 1.79 | -0.87 | PASS-build |
| peg | LOW | 12 | 42.6% | 10.0% | 16,810 | 503 | 2.99% | 1.78 | 1.63 | 1.94 | -0.81 | PASS-build |
| pe | LOW | 0 | 80.0% | 10.2% | 32,004 | 994 | 3.11% | 1.66 | 1.56 | 1.76 | 0.27 |  |
| pe | LOW | 3 | 80.1% | 10.2% | 31,992 | 990 | 3.09% | 1.60 | 1.51 | 1.71 | 0.19 |  |
| pe | LOW | 6 | 79.9% | 10.2% | 31,969 | 929 | 2.91% | 1.49 | 1.40 | 1.59 | 0.20 |  |
| pe | LOW | 12 | 79.1% | 10.2% | 31,617 | 911 | 2.88% | 1.43 | 1.34 | 1.53 | 0.20 |  |
| pe_vs_5y_median | LOW | 0 | 69.9% | 10.0% | 27,545 | 838 | 3.04% | 1.82 | 1.70 | 1.95 | -0.27 |  |
| pe_vs_5y_median | LOW | 3 | 69.4% | 10.0% | 27,364 | 823 | 3.01% | 1.76 | 1.64 | 1.88 | -0.27 |  |
| pe_vs_5y_median | LOW | 6 | 68.7% | 10.0% | 27,092 | 809 | 2.99% | 1.73 | 1.61 | 1.85 | -0.26 |  |
| pe_vs_5y_median | LOW | 12 | 67.4% | 10.0% | 26,561 | 791 | 2.98% | 1.68 | 1.57 | 1.80 | -0.22 |  |
| fcf_ps_slope | HIGH | 0 | 99.4% | 10.0% | 39,178 | 929 | 2.37% | 0.87 | 0.81 | 0.93 | -0.02 |  |
| fcf_ps_slope | HIGH | 3 | 98.2% | 10.0% | 38,730 | 897 | 2.32% | 0.86 | 0.80 | 0.92 | -0.04 |  |
| fcf_ps_slope | HIGH | 6 | 97.0% | 10.0% | 38,241 | 877 | 2.29% | 0.86 | 0.80 | 0.92 | -0.26 |  |
| fcf_ps_slope | HIGH | 12 | 94.5% | 10.0% | 37,264 | 829 | 2.22% | 0.86 | 0.80 | 0.92 | -0.16 |  |
| pegy | LOW | 0 | 45.1% | 10.0% | 17,801 | 467 | 2.62% | 1.73 | 1.58 | 1.89 | -0.77 | PASS-build |
| pegy | LOW | 3 | 45.1% | 10.0% | 17,801 | 495 | 2.78% | 1.73 | 1.59 | 1.89 | -0.95 | PASS-build |
| pegy | LOW | 6 | 44.8% | 10.0% | 17,686 | 472 | 2.67% | 1.64 | 1.50 | 1.80 | -0.79 | PASS-build |
| pegy | LOW | 12 | 44.1% | 10.0% | 17,410 | 526 | 3.02% | 1.83 | 1.68 | 1.99 | -0.75 | PASS-build |
| pct_from_52w_high | LOW | 0 | 99.3% | 10.0% | 39,113 | 488 | 1.25% | 0.46 | 0.42 | 0.50 | 1.00 |  |
| pct_from_52w_high | LOW | 3 | 98.3% | 10.0% | 38,728 | 514 | 1.33% | 0.49 | 0.45 | 0.54 | 1.00 |  |
| pct_from_52w_high | LOW | 6 | 97.2% | 10.0% | 38,281 | 565 | 1.48% | 0.56 | 0.51 | 0.60 | 1.00 |  |
| pct_from_52w_high | LOW | 12 | 94.9% | 10.0% | 37,379 | 626 | 1.67% | 0.65 | 0.60 | 0.70 | 0.96 |  |
| dist_above_30w_sma | HIGH | 0 | 99.9% | 10.0% | 39,382 | 1861 | 4.73% | 1.73 | 1.66 | 1.81 | -0.22 |  |
| dist_above_30w_sma | HIGH | 3 | 99.7% | 10.0% | 39,307 | 1816 | 4.62% | 1.70 | 1.62 | 1.78 | -0.25 |  |
| dist_above_30w_sma | HIGH | 6 | 99.0% | 10.0% | 39,045 | 1793 | 4.59% | 1.70 | 1.63 | 1.78 | -0.15 |  |
| dist_above_30w_sma | HIGH | 12 | 96.9% | 10.0% | 38,187 | 1718 | 4.50% | 1.70 | 1.62 | 1.78 | -0.18 |  |
| atr_contraction | HIGH | 0 | 100.0% | 10.0% | 39,413 | 1157 | 2.94% | 1.08 | 1.02 | 1.14 | -0.15 |  |
| atr_contraction | HIGH | 3 | 99.9% | 10.0% | 39,391 | 1211 | 3.07% | 1.13 | 1.07 | 1.19 | -0.16 |  |
| atr_contraction | HIGH | 6 | 99.8% | 10.0% | 39,335 | 1267 | 3.22% | 1.18 | 1.12 | 1.25 | -0.15 |  |
| atr_contraction | HIGH | 12 | 98.3% | 10.0% | 38,752 | 1237 | 3.19% | 1.19 | 1.13 | 1.26 | -0.32 |  |
| inst_pct | LOWMID | 0 | 45.0% | 40.0% | 70,809 | 1474 | 2.08% | 0.93 | 0.89 | 0.98 | -0.71 |  |
| inst_pct | LOWMID | 3 | 43.2% | 40.0% | 67,930 | 1429 | 2.10% | 0.95 | 0.90 | 1.00 | -0.68 |  |
| inst_pct | LOWMID | 6 | 41.3% | 40.0% | 65,032 | 1336 | 2.05% | 0.91 | 0.87 | 0.96 | -0.66 |  |
| inst_pct | LOWMID | 12 | 37.2% | 40.0% | 58,526 | 1181 | 2.02% | 0.91 | 0.86 | 0.96 | -0.58 |  |
| inst_pct_delta_qoq | HIGH | 0 | 43.3% | 10.0% | 17,054 | 785 | 4.60% | 2.06 | 1.92 | 2.20 | 0.20 |  |
| inst_pct_delta_qoq | HIGH | 3 | 41.4% | 10.0% | 16,304 | 719 | 4.41% | 1.95 | 1.82 | 2.10 | 0.31 |  |
| inst_pct_delta_qoq | HIGH | 6 | 39.3% | 10.0% | 15,489 | 664 | 4.29% | 1.90 | 1.77 | 2.05 | 0.25 |  |
| inst_pct_delta_qoq | HIGH | 12 | 35.0% | 10.0% | 13,787 | 598 | 4.34% | 1.95 | 1.81 | 2.11 | 0.32 |  |
| insider_buy_count_90d | HIGH | 0 | 82.4% | 6.9% | 22,203 | 893 | 4.02% | 1.35 | 1.27 | 1.44 | 0.30 |  |
| insider_buy_count_90d | HIGH | 3 | 80.5% | 6.8% | 21,472 | 892 | 4.15% | 1.37 | 1.28 | 1.46 | 0.30 |  |
| insider_buy_count_90d | HIGH | 6 | 78.7% | 6.9% | 21,497 | 813 | 3.78% | 1.23 | 1.15 | 1.31 | 0.10 |  |
| insider_buy_count_90d | HIGH | 12 | 75.3% | 7.2% | 21,245 | 732 | 3.45% | 1.30 | 1.21 | 1.40 | 0.40 |  |
| net_debt_to_ebitda | LOW | 0 | 88.2% | 10.0% | 34,774 | 1173 | 3.37% | 1.57 | 1.48 | 1.66 | -0.12 |  |
| net_debt_to_ebitda | LOW | 3 | 87.3% | 10.0% | 34,403 | 1133 | 3.29% | 1.53 | 1.44 | 1.61 | -0.19 |  |
| net_debt_to_ebitda | LOW | 6 | 86.3% | 10.0% | 33,999 | 1129 | 3.32% | 1.54 | 1.45 | 1.63 | -0.21 |  |
| net_debt_to_ebitda | LOW | 12 | 84.2% | 10.0% | 33,190 | 1105 | 3.33% | 1.55 | 1.46 | 1.64 | -0.22 |  |
| share_count_change_8q | LOW | 0 | 94.3% | 10.0% | 37,173 | 616 | 1.66% | 0.64 | 0.59 | 0.69 | 0.95 |  |
| share_count_change_8q | LOW | 3 | 93.1% | 10.0% | 36,679 | 606 | 1.65% | 0.65 | 0.60 | 0.70 | 0.95 |  |
| share_count_change_8q | LOW | 6 | 91.9% | 10.0% | 36,192 | 609 | 1.68% | 0.67 | 0.62 | 0.72 | 0.95 |  |
| share_count_change_8q | LOW | 12 | 89.5% | 10.0% | 35,290 | 600 | 1.70% | 0.69 | 0.64 | 0.75 | 0.95 |  |
| shareholder_yield | HIGH | 0 | 94.3% | 10.0% | 37,183 | 721 | 1.94% | 0.75 | 0.70 | 0.81 | -0.88 |  |
| shareholder_yield | HIGH | 3 | 93.1% | 10.0% | 36,693 | 670 | 1.83% | 0.72 | 0.66 | 0.77 | -0.93 |  |
| shareholder_yield | HIGH | 6 | 91.8% | 10.0% | 36,202 | 631 | 1.74% | 0.69 | 0.64 | 0.75 | -0.93 |  |
| shareholder_yield | HIGH | 12 | 89.5% | 10.0% | 35,301 | 577 | 1.63% | 0.67 | 0.62 | 0.72 | -0.93 |  |
| marketcap | LOW | 0 | 99.7% | 10.0% | 39,285 | 2178 | 5.54% | 2.03 | 1.95 | 2.11 | -1.00 | PASS-build |
| marketcap | LOW | 3 | 100.0% | 10.0% | 39,404 | 2108 | 5.35% | 1.96 | 1.88 | 2.04 | -1.00 | PASS-build |
| marketcap | LOW | 6 | 99.9% | 10.0% | 39,376 | 2044 | 5.19% | 1.90 | 1.83 | 1.99 | -1.00 | PASS-build |
| marketcap | LOW | 12 | 99.2% | 10.0% | 39,102 | 1975 | 5.05% | 1.87 | 1.79 | 1.95 | -1.00 | PASS-build |
| pb | LOW | 0 | 96.6% | 11.7% | 44,536 | 1571 | 3.53% | 1.33 | 1.26 | 1.39 | 0.48 |  |
| pb | LOW | 3 | 96.9% | 11.8% | 45,059 | 1465 | 3.25% | 1.23 | 1.17 | 1.29 | 0.59 |  |
| pb | LOW | 6 | 96.8% | 11.7% | 44,501 | 1302 | 2.93% | 1.10 | 1.05 | 1.16 | 0.58 |  |
| pb | LOW | 12 | 95.8% | 11.7% | 44,068 | 1225 | 2.78% | 1.06 | 1.01 | 1.12 | 0.61 |  |
| dividend_yield | LOW | 0 | 100.0% | 48.8% | 192,049 | 8165 | 4.25% | 1.56 | 1.53 | 1.59 | -0.32 |  |
| dividend_yield | LOW | 3 | 99.9% | 49.1% | 193,098 | 8167 | 4.23% | 1.55 | 1.52 | 1.58 | -0.43 |  |
| dividend_yield | LOW | 6 | 99.9% | 49.4% | 194,211 | 8183 | 4.21% | 1.55 | 1.51 | 1.58 | -0.64 | PASS-build |
| dividend_yield | LOW | 12 | 98.7% | 49.8% | 193,391 | 7973 | 4.12% | 1.53 | 1.50 | 1.56 | -0.79 | PASS-build |

## Extreme-decile cells, launch_300, by lag

Extreme = decile 10 for HIGH, decile 1 for LOW, deciles 3-6 pooled for LOW-to-MID (inst_pct).

| feature | dir | lag | coverage | cell share | rows | events | rate | lift | CI low | CI high | rho | cell |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 0 | 99.9% | 10.0% | 39,379 | 482 | 1.22% | 1.86 | 1.70 | 2.03 | -0.30 |  |
| ret_6m_skip1 | HIGH | 3 | 99.7% | 10.0% | 39,297 | 496 | 1.26% | 1.93 | 1.76 | 2.10 | -0.22 |  |
| ret_6m_skip1 | HIGH | 6 | 99.0% | 10.0% | 39,007 | 528 | 1.35% | 2.09 | 1.92 | 2.28 | -0.12 |  |
| ret_6m_skip1 | HIGH | 12 | 96.8% | 10.0% | 38,140 | 503 | 1.32% | 2.13 | 1.96 | 2.33 | -0.18 |  |
| ret_12m_skip1 | HIGH | 0 | 99.0% | 10.0% | 39,007 | 478 | 1.23% | 1.90 | 1.73 | 2.07 | -0.35 |  |
| ret_12m_skip1 | HIGH | 3 | 97.9% | 10.0% | 38,600 | 491 | 1.27% | 2.01 | 1.84 | 2.20 | -0.28 |  |
| ret_12m_skip1 | HIGH | 6 | 96.8% | 10.0% | 38,140 | 511 | 1.34% | 2.17 | 1.99 | 2.36 | -0.15 |  |
| ret_12m_skip1 | HIGH | 12 | 94.5% | 10.0% | 37,236 | 505 | 1.36% | 2.30 | 2.10 | 2.50 | -0.02 |  |
| eps_growth_q0 | HIGH | 0 | 78.0% | 10.0% | 30,546 | 154 | 0.50% | 1.23 | 1.05 | 1.44 | -0.60 |  |
| eps_growth_q0 | HIGH | 3 | 77.1% | 10.0% | 30,211 | 192 | 0.64% | 1.58 | 1.37 | 1.82 | -0.30 |  |
| eps_growth_q0 | HIGH | 6 | 76.2% | 10.0% | 29,849 | 178 | 0.60% | 1.51 | 1.31 | 1.75 | -0.10 |  |
| eps_growth_q0 | HIGH | 12 | 74.7% | 10.0% | 29,257 | 154 | 0.53% | 1.36 | 1.16 | 1.59 | -0.30 |  |
| rev_growth_accel | HIGH | 0 | 92.8% | 10.0% | 36,569 | 352 | 0.96% | 1.67 | 1.50 | 1.85 | -0.37 |  |
| rev_growth_accel | HIGH | 3 | 91.5% | 10.0% | 36,090 | 349 | 0.97% | 1.72 | 1.55 | 1.91 | -0.21 |  |
| rev_growth_accel | HIGH | 6 | 90.4% | 10.0% | 35,623 | 346 | 0.97% | 1.76 | 1.59 | 1.96 | -0.04 |  |
| rev_growth_accel | HIGH | 12 | 88.1% | 10.0% | 34,752 | 287 | 0.83% | 1.54 | 1.37 | 1.73 | -0.03 |  |
| op_margin_delta | HIGH | 0 | 96.9% | 10.0% | 38,199 | 502 | 1.31% | 2.11 | 1.93 | 2.30 | -0.10 |  |
| op_margin_delta | HIGH | 3 | 95.8% | 10.0% | 37,756 | 462 | 1.22% | 2.01 | 1.84 | 2.20 | 0.00 |  |
| op_margin_delta | HIGH | 6 | 94.6% | 10.0% | 37,286 | 435 | 1.17% | 1.96 | 1.79 | 2.15 | 0.08 |  |
| op_margin_delta | HIGH | 12 | 92.3% | 10.0% | 36,384 | 409 | 1.12% | 1.99 | 1.80 | 2.19 | 0.08 |  |
| peg | LOW | 0 | 43.5% | 10.0% | 17,179 | 108 | 0.63% | 2.19 | 1.81 | 2.64 | n/a |  |
| peg | LOW | 3 | 43.6% | 10.0% | 17,194 | 125 | 0.73% | 2.35 | 1.98 | 2.80 | n/a |  |
| peg | LOW | 6 | 43.3% | 10.0% | 17,089 | 113 | 0.66% | 2.08 | 1.73 | 2.50 | n/a |  |
| peg | LOW | 12 | 42.6% | 10.0% | 16,810 | 108 | 0.64% | 2.06 | 1.71 | 2.48 | n/a |  |
| pe | LOW | 0 | 80.0% | 10.2% | 32,004 | 243 | 0.76% | 2.07 | 1.82 | 2.34 | 0.00 |  |
| pe | LOW | 3 | 80.1% | 10.2% | 31,992 | 248 | 0.78% | 2.02 | 1.79 | 2.29 | -0.10 |  |
| pe | LOW | 6 | 79.9% | 10.2% | 31,969 | 206 | 0.64% | 1.63 | 1.43 | 1.87 | 0.30 |  |
| pe | LOW | 12 | 79.1% | 10.2% | 31,617 | 193 | 0.61% | 1.52 | 1.32 | 1.75 | 0.37 |  |
| pe_vs_5y_median | LOW | 0 | 69.9% | 10.0% | 27,545 | 195 | 0.71% | 2.36 | 2.06 | 2.72 | n/a |  |
| pe_vs_5y_median | LOW | 3 | 69.4% | 10.0% | 27,364 | 186 | 0.68% | 2.18 | 1.89 | 2.51 | n/a |  |
| pe_vs_5y_median | LOW | 6 | 68.7% | 10.0% | 27,092 | 156 | 0.58% | 1.80 | 1.54 | 2.11 | n/a |  |
| pe_vs_5y_median | LOW | 12 | 67.4% | 10.0% | 26,561 | 148 | 0.56% | 1.75 | 1.49 | 2.05 | n/a |  |
| fcf_ps_slope | HIGH | 0 | 99.4% | 10.0% | 39,178 | 226 | 0.58% | 0.87 | 0.77 | 0.99 | 0.33 |  |
| fcf_ps_slope | HIGH | 3 | 98.2% | 10.0% | 38,730 | 209 | 0.54% | 0.83 | 0.73 | 0.95 | -0.01 |  |
| fcf_ps_slope | HIGH | 6 | 97.0% | 10.0% | 38,241 | 184 | 0.48% | 0.76 | 0.66 | 0.87 | -0.27 |  |
| fcf_ps_slope | HIGH | 12 | 94.5% | 10.0% | 37,264 | 180 | 0.48% | 0.80 | 0.69 | 0.93 | 0.08 |  |
| pegy | LOW | 0 | 45.1% | 10.0% | 17,801 | 110 | 0.62% | 2.19 | 1.82 | 2.64 | n/a |  |
| pegy | LOW | 3 | 45.1% | 10.0% | 17,801 | 131 | 0.74% | 2.43 | 2.05 | 2.88 | n/a |  |
| pegy | LOW | 6 | 44.8% | 10.0% | 17,686 | 114 | 0.64% | 2.09 | 1.74 | 2.51 | n/a |  |
| pegy | LOW | 12 | 44.1% | 10.0% | 17,410 | 112 | 0.64% | 2.08 | 1.73 | 2.50 | n/a |  |
| pct_from_52w_high | LOW | 0 | 99.3% | 10.0% | 39,113 | 101 | 0.26% | 0.40 | 0.33 | 0.48 | 1.00 |  |
| pct_from_52w_high | LOW | 3 | 98.3% | 10.0% | 38,728 | 100 | 0.26% | 0.41 | 0.33 | 0.49 | 1.00 |  |
| pct_from_52w_high | LOW | 6 | 97.2% | 10.0% | 38,281 | 114 | 0.30% | 0.48 | 0.40 | 0.57 | 0.99 |  |
| pct_from_52w_high | LOW | 12 | 94.9% | 10.0% | 37,379 | 141 | 0.38% | 0.63 | 0.54 | 0.75 | 0.92 |  |
| dist_above_30w_sma | HIGH | 0 | 99.9% | 10.0% | 39,382 | 485 | 1.23% | 1.87 | 1.71 | 2.04 | -0.27 |  |
| dist_above_30w_sma | HIGH | 3 | 99.7% | 10.0% | 39,307 | 482 | 1.23% | 1.87 | 1.71 | 2.04 | -0.32 |  |
| dist_above_30w_sma | HIGH | 6 | 99.0% | 10.0% | 39,045 | 485 | 1.24% | 1.92 | 1.76 | 2.10 | -0.22 |  |
| dist_above_30w_sma | HIGH | 12 | 96.9% | 10.0% | 38,187 | 472 | 1.24% | 2.00 | 1.83 | 2.19 | -0.10 |  |
| atr_contraction | HIGH | 0 | 100.0% | 10.0% | 39,413 | 298 | 0.76% | 1.15 | 1.02 | 1.28 | -0.03 |  |
| atr_contraction | HIGH | 3 | 99.9% | 10.0% | 39,391 | 343 | 0.87% | 1.32 | 1.19 | 1.47 | 0.07 |  |
| atr_contraction | HIGH | 6 | 99.8% | 10.0% | 39,335 | 335 | 0.85% | 1.30 | 1.16 | 1.44 | -0.45 |  |
| atr_contraction | HIGH | 12 | 98.3% | 10.0% | 38,752 | 324 | 0.84% | 1.31 | 1.18 | 1.46 | -0.07 |  |
| inst_pct | LOWMID | 0 | 45.0% | 40.0% | 70,809 | 423 | 0.60% | 0.88 | 0.80 | 0.97 | -1.00 |  |
| inst_pct | LOWMID | 3 | 43.2% | 40.0% | 67,930 | 408 | 0.60% | 0.87 | 0.79 | 0.96 | -1.00 |  |
| inst_pct | LOWMID | 6 | 41.3% | 40.0% | 65,032 | 400 | 0.62% | 0.87 | 0.79 | 0.96 | n/a |  |
| inst_pct | LOWMID | 12 | 37.2% | 40.0% | 58,526 | 358 | 0.61% | 0.85 | 0.76 | 0.94 | n/a |  |
| inst_pct_delta_qoq | HIGH | 0 | 43.3% | 10.0% | 17,054 | 290 | 1.70% | 2.45 | 2.19 | 2.75 | n/a |  |
| inst_pct_delta_qoq | HIGH | 3 | 41.4% | 10.0% | 16,304 | 269 | 1.65% | 2.33 | 2.07 | 2.62 | 0.30 |  |
| inst_pct_delta_qoq | HIGH | 6 | 39.3% | 10.0% | 15,489 | 245 | 1.58% | 2.18 | 1.92 | 2.47 | n/a |  |
| inst_pct_delta_qoq | HIGH | 12 | 35.0% | 10.0% | 13,787 | 214 | 1.55% | 2.11 | 1.85 | 2.41 | n/a |  |
| insider_buy_count_90d | HIGH | 0 | 82.4% | 6.9% | 22,203 | 309 | 1.39% | 1.80 | 1.61 | 2.01 | n/a |  |
| insider_buy_count_90d | HIGH | 3 | 80.5% | 6.8% | 21,472 | 256 | 1.19% | 1.52 | 1.34 | 1.71 | n/a |  |
| insider_buy_count_90d | HIGH | 6 | 78.7% | 6.9% | 21,497 | 201 | 0.94% | 1.17 | 1.02 | 1.34 | n/a |  |
| insider_buy_count_90d | HIGH | 12 | 75.3% | 7.2% | 21,245 | 153 | 0.72% | 1.08 | 0.92 | 1.26 | n/a |  |
| net_debt_to_ebitda | LOW | 0 | 88.2% | 10.0% | 34,774 | 264 | 0.76% | 1.76 | 1.56 | 1.99 | -0.14 |  |
| net_debt_to_ebitda | LOW | 3 | 87.3% | 10.0% | 34,403 | 258 | 0.75% | 1.73 | 1.53 | 1.95 | -0.16 |  |
| net_debt_to_ebitda | LOW | 6 | 86.3% | 10.0% | 33,999 | 253 | 0.74% | 1.72 | 1.52 | 1.94 | -0.19 |  |
| net_debt_to_ebitda | LOW | 12 | 84.2% | 10.0% | 33,190 | 208 | 0.63% | 1.47 | 1.28 | 1.68 | -0.30 |  |
| share_count_change_8q | LOW | 0 | 94.3% | 10.0% | 37,173 | 124 | 0.33% | 0.55 | 0.46 | 0.66 | 0.98 |  |
| share_count_change_8q | LOW | 3 | 93.1% | 10.0% | 36,679 | 123 | 0.34% | 0.57 | 0.47 | 0.67 | 0.98 |  |
| share_count_change_8q | LOW | 6 | 91.9% | 10.0% | 36,192 | 130 | 0.36% | 0.62 | 0.52 | 0.73 | 1.00 |  |
| share_count_change_8q | LOW | 12 | 89.5% | 10.0% | 35,290 | 147 | 0.42% | 0.75 | 0.64 | 0.88 | 0.93 |  |
| shareholder_yield | HIGH | 0 | 94.3% | 10.0% | 37,183 | 148 | 0.40% | 0.66 | 0.56 | 0.77 | -0.86 |  |
| shareholder_yield | HIGH | 3 | 93.1% | 10.0% | 36,693 | 147 | 0.40% | 0.68 | 0.58 | 0.79 | -0.89 |  |
| shareholder_yield | HIGH | 6 | 91.8% | 10.0% | 36,202 | 141 | 0.39% | 0.67 | 0.57 | 0.79 | -1.00 |  |
| shareholder_yield | HIGH | 12 | 89.5% | 10.0% | 35,301 | 143 | 0.41% | 0.73 | 0.62 | 0.86 | -0.96 |  |
| marketcap | LOW | 0 | 99.7% | 10.0% | 39,285 | 605 | 1.54% | 2.32 | 2.14 | 2.51 | -0.98 | PASS-build |
| marketcap | LOW | 3 | 100.0% | 10.0% | 39,404 | 575 | 1.46% | 2.21 | 2.04 | 2.40 | -1.00 | PASS-build |
| marketcap | LOW | 6 | 99.9% | 10.0% | 39,376 | 553 | 1.40% | 2.13 | 1.96 | 2.31 | -1.00 | PASS-build |
| marketcap | LOW | 12 | 99.2% | 10.0% | 39,102 | 529 | 1.35% | 2.08 | 1.92 | 2.27 | -0.97 | PASS-build |
| pb | LOW | 0 | 96.6% | 11.7% | 44,536 | 399 | 0.90% | 1.42 | 1.29 | 1.57 | 0.48 |  |
| pb | LOW | 3 | 96.9% | 11.8% | 45,059 | 350 | 0.78% | 1.24 | 1.12 | 1.38 | 0.58 |  |
| pb | LOW | 6 | 96.8% | 11.7% | 44,501 | 254 | 0.57% | 0.91 | 0.80 | 1.03 | 0.66 |  |
| pb | LOW | 12 | 95.8% | 11.7% | 44,068 | 209 | 0.47% | 0.78 | 0.68 | 0.89 | 0.88 |  |
| dividend_yield | LOW | 0 | 100.0% | 48.8% | 192,049 | 2126 | 1.11% | 1.67 | 1.60 | 1.75 | n/a |  |
| dividend_yield | LOW | 3 | 99.9% | 49.1% | 193,098 | 2119 | 1.10% | 1.66 | 1.59 | 1.73 | n/a |  |
| dividend_yield | LOW | 6 | 99.9% | 49.4% | 194,211 | 2113 | 1.09% | 1.65 | 1.58 | 1.72 | n/a |  |
| dividend_yield | LOW | 12 | 98.7% | 49.8% | 193,391 | 2026 | 1.05% | 1.63 | 1.56 | 1.70 | n/a |  |

## Verdicts (build-window half of section 3), all labels

| feature | dir | label | verdict | passing lags | best lag | lift | CI low | rho | events | regime-dependent |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | win_50 | FAIL | - | 3 | 1.33 | 1.30 | -0.12 | 6136 | - |
| ret_6m_skip1 | HIGH | win_100 | FAIL | - | 6 | 1.78 | 1.70 | -0.15 | 1871 | - |
| ret_6m_skip1 | HIGH | launch_300 | FAIL | - | 12 | 2.13 | 1.96 | -0.18 | 503 | - |
| ret_12m_skip1 | HIGH | win_50 | FAIL | - | 6 | 1.38 | 1.35 | -0.04 | 6114 | - |
| ret_12m_skip1 | HIGH | win_100 | FAIL | - | 6 | 1.78 | 1.70 | -0.20 | 1798 | - |
| ret_12m_skip1 | HIGH | launch_300 | FAIL | - | 12 | 2.30 | 2.10 | -0.02 | 505 | - |
| eps_growth_q0 | HIGH | win_50 | FAIL | - | 12 | 1.24 | 1.20 | 0.15 | 3834 | - |
| eps_growth_q0 | HIGH | win_100 | FAIL | - | 12 | 1.42 | 1.32 | -0.05 | 815 | - |
| eps_growth_q0 | HIGH | launch_300 | FAIL | - | 3 | 1.58 | 1.37 | -0.30 | 192 | - |
| rev_growth_accel | HIGH | win_50 | FAIL | - | 12 | 1.16 | 1.13 | -0.09 | 4498 | - |
| rev_growth_accel | HIGH | win_100 | FAIL | - | 12 | 1.46 | 1.39 | -0.19 | 1220 | - |
| rev_growth_accel | HIGH | launch_300 | FAIL | - | 6 | 1.76 | 1.59 | -0.04 | 346 | - |
| op_margin_delta | HIGH | win_50 | FAIL | - | 12 | 1.25 | 1.22 | 0.18 | 5172 | - |
| op_margin_delta | HIGH | win_100 | FAIL | - | 12 | 1.63 | 1.55 | 0.15 | 1472 | - |
| op_margin_delta | HIGH | launch_300 | FAIL | - | 0 | 2.11 | 1.93 | -0.10 | 502 | - |
| peg | LOW | win_50 | FAIL | - | 3 | 1.29 | 1.24 | -0.93 | 2134 | - |
| peg | LOW | win_100 | PASS-build | 0,3,6,12 | 12 | 1.78 | 1.63 | -0.81 | 503 | no |
| peg | LOW | launch_300 | FAIL | - | 3 | 2.35 | 1.98 | n/a | 125 | - |
| pe | LOW | win_50 | FAIL | - | 0 | 1.23 | 1.19 | 0.14 | 4059 | - |
| pe | LOW | win_100 | FAIL | - | 0 | 1.66 | 1.56 | 0.27 | 994 | - |
| pe | LOW | launch_300 | FAIL | - | 0 | 2.07 | 1.82 | 0.00 | 243 | - |
| pe_vs_5y_median | LOW | win_50 | FAIL | - | 12 | 1.35 | 1.31 | -0.41 | 3624 | - |
| pe_vs_5y_median | LOW | win_100 | FAIL | - | 0 | 1.82 | 1.70 | -0.27 | 838 | - |
| pe_vs_5y_median | LOW | launch_300 | FAIL | - | 0 | 2.36 | 2.06 | n/a | 195 | - |
| fcf_ps_slope | HIGH | win_50 | FAIL | - | 0 | 0.91 | 0.88 | 0.18 | 4156 | - |
| fcf_ps_slope | HIGH | win_100 | FAIL | - | 0 | 0.87 | 0.81 | -0.02 | 929 | - |
| fcf_ps_slope | HIGH | launch_300 | FAIL | - | 0 | 0.87 | 0.77 | 0.33 | 226 | - |
| pegy | LOW | win_50 | FAIL | - | 3 | 1.31 | 1.26 | -0.89 | 2213 | - |
| pegy | LOW | win_100 | PASS-build | 0,3,6,12 | 12 | 1.83 | 1.68 | -0.75 | 526 | no |
| pegy | LOW | launch_300 | FAIL | - | 3 | 2.43 | 2.05 | n/a | 131 | - |
| pct_from_52w_high | LOW | win_50 | FAIL | - | 12 | 0.79 | 0.76 | 1.00 | 3378 | - |
| pct_from_52w_high | LOW | win_100 | FAIL | - | 12 | 0.65 | 0.60 | 0.96 | 626 | - |
| pct_from_52w_high | LOW | launch_300 | FAIL | - | 12 | 0.63 | 0.54 | 0.92 | 141 | - |
| dist_above_30w_sma | HIGH | win_50 | FAIL | - | 6 | 1.34 | 1.31 | 0.15 | 6091 | - |
| dist_above_30w_sma | HIGH | win_100 | FAIL | - | 0 | 1.73 | 1.66 | -0.22 | 1861 | - |
| dist_above_30w_sma | HIGH | launch_300 | FAIL | - | 12 | 2.00 | 1.83 | -0.10 | 472 | - |
| atr_contraction | HIGH | win_50 | FAIL | - | 12 | 1.09 | 1.06 | -0.13 | 4909 | - |
| atr_contraction | HIGH | win_100 | FAIL | - | 12 | 1.19 | 1.13 | -0.32 | 1237 | - |
| atr_contraction | HIGH | launch_300 | FAIL | - | 3 | 1.32 | 1.19 | 0.07 | 343 | - |
| inst_pct | LOWMID | win_50 | FAIL | - | 6 | 0.96 | 0.94 | 0.18 | 6103 | - |
| inst_pct | LOWMID | win_100 | FAIL | - | 3 | 0.95 | 0.90 | -0.68 | 1429 | - |
| inst_pct | LOWMID | launch_300 | FAIL | - | 0 | 0.88 | 0.80 | -1.00 | 423 | - |
| inst_pct_delta_qoq | HIGH | win_50 | FAIL | - | 0 | 1.48 | 1.42 | 0.22 | 2448 | - |
| inst_pct_delta_qoq | HIGH | win_100 | FAIL | - | 0 | 2.06 | 1.92 | 0.20 | 785 | - |
| inst_pct_delta_qoq | HIGH | launch_300 | FAIL | - | 0 | 2.45 | 2.19 | n/a | 290 | - |
| insider_buy_count_90d | HIGH | win_50 | FAIL | - | 0 | 1.12 | 1.08 | 0.10 | 3153 | - |
| insider_buy_count_90d | HIGH | win_100 | FAIL | - | 3 | 1.37 | 1.28 | 0.30 | 892 | - |
| insider_buy_count_90d | HIGH | launch_300 | FAIL | - | 0 | 1.80 | 1.61 | n/a | 309 | - |
| net_debt_to_ebitda | LOW | win_50 | FAIL | - | 0 | 1.29 | 1.25 | -0.56 | 4847 | - |
| net_debt_to_ebitda | LOW | win_100 | FAIL | - | 0 | 1.57 | 1.48 | -0.12 | 1173 | - |
| net_debt_to_ebitda | LOW | launch_300 | FAIL | - | 0 | 1.76 | 1.56 | -0.14 | 264 | - |
| share_count_change_8q | LOW | win_50 | FAIL | - | 12 | 0.93 | 0.91 | 0.83 | 3683 | - |
| share_count_change_8q | LOW | win_100 | FAIL | - | 12 | 0.69 | 0.64 | 0.95 | 600 | - |
| share_count_change_8q | LOW | launch_300 | FAIL | - | 12 | 0.75 | 0.64 | 0.93 | 147 | - |
| shareholder_yield | HIGH | win_50 | FAIL | - | 0 | 0.91 | 0.88 | -0.83 | 3866 | - |
| shareholder_yield | HIGH | win_100 | FAIL | - | 0 | 0.75 | 0.70 | -0.88 | 721 | - |
| shareholder_yield | HIGH | launch_300 | FAIL | - | 12 | 0.73 | 0.62 | -0.96 | 143 | - |
| marketcap | LOW | win_50 | FAIL | - | 0 | 1.31 | 1.28 | -1.00 | 6033 | - |
| marketcap | LOW | win_100 | PASS-build | 0,3,6,12 | 0 | 2.03 | 1.95 | -1.00 | 2178 | no |
| marketcap | LOW | launch_300 | PASS-build | 0,3,6,12 | 0 | 2.32 | 2.14 | -0.98 | 605 | no |
| pb | LOW | win_50 | FAIL | - | 0 | 1.05 | 1.02 | 0.65 | 5430 | - |
| pb | LOW | win_100 | FAIL | - | 0 | 1.33 | 1.26 | 0.48 | 1571 | - |
| pb | LOW | launch_300 | FAIL | - | 0 | 1.42 | 1.29 | 0.48 | 399 | - |
| dividend_yield | LOW | win_50 | FAIL | - | 0 | 1.30 | 1.28 | -0.79 | 29113 | - |
| dividend_yield | LOW | win_100 | PASS-build | 6,12 | 0 | 1.56 | 1.53 | -0.32 | 8165 | no |
| dividend_yield | LOW | launch_300 | FAIL | - | 0 | 1.67 | 1.60 | n/a | 2126 | - |

## Decile lift curves, win_50, lag 0

Cell = lift (events); insufficient cells show the event count only.

| feature | dir | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | HIGH | 1.41 (6510) | 1.12 (5152) | 0.97 (4466) | 0.89 (4078) | 0.81 (3703) | 0.80 (3686) | 0.83 (3807) | 0.86 (3966) | 1.02 (4714) | 1.29 (5927) |
| ret_12m_skip1 | HIGH | 1.41 (6407) | 1.13 (5134) | 0.96 (4359) | 0.85 (3883) | 0.83 (3779) | 0.76 (3463) | 0.82 (3709) | 0.90 (4099) | 1.04 (4710) | 1.30 (5915) |
| eps_growth_q0 | HIGH | 1.34 (4423) | 1.21 (3966) | 1.02 (3347) | 0.89 (2969) | 0.79 (2590) | 0.79 (2564) | 0.85 (2785) | 0.94 (3078) | 1.06 (3473) | 1.09 (3570) |
| rev_growth_accel | HIGH | 1.18 (4931) | 1.06 (4411) | 1.04 (4336) | 0.98 (4095) | 0.94 (3916) | 0.87 (3606) | 0.90 (3741) | 0.93 (3872) | 0.97 (4046) | 1.13 (4722) |
| op_margin_delta | HIGH | 1.23 (5436) | 1.06 (4667) | 1.00 (4415) | 0.94 (4143) | 0.86 (3811) | 0.87 (3848) | 0.91 (4034) | 0.94 (4160) | 1.02 (4529) | 1.16 (5155) |
| peg | LOW | 1.29 (2072) | 1.13 (1812) | 1.08 (1726) | 1.08 (1728) | 1.03 (1649) | 0.92 (1473) | 0.90 (1441) | 0.88 (1404) | 0.87 (1401) | 0.84 (1351) |
| pe | LOW | 1.23 (4059) | 1.02 (3327) | 0.88 (2882) | 0.84 (2738) | 0.81 (2639) | 0.80 (2595) | 0.88 (2839) | 1.00 (3240) | 1.20 (3873) | 1.32 (4300) |
| pe_vs_5y_median | LOW | 1.35 (3659) | 1.19 (3214) | 1.05 (2846) | 0.93 (2528) | 0.86 (2325) | 0.81 (2204) | 0.85 (2300) | 0.86 (2331) | 0.96 (2612) | 1.14 (3102) |
| fcf_ps_slope | HIGH | 0.82 (3745) | 0.91 (4145) | 0.94 (4321) | 1.05 (4813) | 1.18 (5407) | 1.23 (5617) | 1.09 (4985) | 0.97 (4423) | 0.91 (4141) | 0.91 (4156) |
| pegy | LOW | 1.30 (2147) | 1.14 (1869) | 1.08 (1780) | 1.06 (1739) | 1.04 (1708) | 0.89 (1466) | 0.90 (1473) | 0.87 (1421) | 0.88 (1444) | 0.85 (1397) |
| pct_from_52w_high | LOW | 0.59 (2686) | 0.71 (3245) | 0.79 (3627) | 0.86 (3903) | 0.91 (4133) | 0.99 (4521) | 1.07 (4896) | 1.21 (5522) | 1.34 (6125) | 1.53 (6979) |
| dist_above_30w_sma | HIGH | 1.43 (6586) | 1.12 (5168) | 0.97 (4451) | 0.88 (4059) | 0.83 (3828) | 0.81 (3741) | 0.82 (3757) | 0.88 (4032) | 1.00 (4609) | 1.25 (5784) |
| atr_contraction | HIGH | 1.14 (5248) | 1.03 (4741) | 0.99 (4535) | 0.95 (4372) | 0.97 (4457) | 0.97 (4476) | 0.98 (4491) | 0.99 (4558) | 1.00 (4606) | 0.99 (4555) |
| inst_pct | LOWMID | 1.05 (1800) | 1.01 (1739) | 0.94 (1615) | 0.92 (1572) | 0.97 (1665) | 0.97 (1671) | 0.95 (1638) | 1.04 (1793) | 1.03 (1773) | 1.11 (1908) |
| inst_pct_delta_qoq | HIGH | 1.20 (1980) | 1.02 (1680) | 0.87 (1440) | 0.82 (1350) | 0.77 (1273) | 0.84 (1388) | 0.89 (1477) | 0.95 (1566) | 1.17 (1935) | 1.48 (2448) |
| insider_buy_count_90d | HIGH | 0.97 (31568) | - | - | - | - | - | 1.79 (995) | 1.12 (2295) | 0.99 (3090) | 1.12 (3153) |
| net_debt_to_ebitda | LOW | 1.29 (4847) | 1.15 (4328) | 1.03 (3859) | 0.92 (3467) | 0.95 (3580) | 0.89 (3360) | 0.92 (3460) | 0.89 (3364) | 0.95 (3568) | 1.00 (3787) |
| share_count_change_8q | LOW | 0.91 (3898) | 0.84 (3587) | 0.77 (3306) | 0.90 (3835) | 0.90 (3824) | 1.01 (4296) | 1.19 (5066) | 1.22 (5208) | 1.11 (4725) | 1.14 (4853) |
| shareholder_yield | HIGH | 1.17 (4977) | 1.24 (5272) | 1.29 (5498) | 1.23 (5230) | 1.01 (4284) | 0.97 (4115) | 0.79 (3364) | 0.69 (2919) | 0.72 (3068) | 0.91 (3866) |
| marketcap | LOW | 1.31 (6033) | 1.30 (5982) | 1.15 (5283) | 1.11 (5104) | 1.03 (4738) | 1.00 (4618) | 0.93 (4278) | 0.85 (3919) | 0.79 (3626) | 0.53 (2465) |
| pb | LOW | 1.05 (5430) | 0.84 (3723) | 0.89 (3971) | 0.86 (3649) | 0.92 (3943) | 0.94 (4102) | 0.95 (4072) | 0.99 (4255) | 1.15 (4968) | 1.38 (6069) |
| dividend_yield | LOW | 1.30 (29113) | - | - | - | 0.88 (1045) | 0.81 (3508) | 0.72 (3288) | 0.68 (3054) | 0.57 (2534) | 0.78 (3499) |

## Extreme-cell lift by SPY drawdown bucket, win_50 (regime-dependence check)

| feature | lag | 0-10 | 10-20 | 20-30 | >30 |
| --- | --- | ---: | ---: | ---: | ---: |
| ret_6m_skip1 | 0 | 1.42 [1.38, 1.46] (4425) | 1.31 [1.19, 1.43] (407) | 1.31 [1.23, 1.40] (696) | 0.61 [0.56, 0.67] (399) |
| ret_6m_skip1 | 3 | 1.45 [1.41, 1.49] (4507) | 1.38 [1.26, 1.51] (428) | 1.41 [1.32, 1.50] (748) | 0.70 [0.64, 0.75] (453) |
| ret_6m_skip1 | 6 | 1.42 [1.38, 1.46] (4346) | 1.36 [1.24, 1.49] (419) | 1.31 [1.23, 1.40] (695) | 0.94 [0.88, 1.00] (609) |
| ret_6m_skip1 | 12 | 1.43 [1.39, 1.47] (4213) | 1.21 [1.10, 1.34] (368) | 1.06 [0.99, 1.14] (558) | 1.13 [1.06, 1.19] (713) |
| ret_12m_skip1 | 0 | 1.45 [1.41, 1.49] (4435) | 1.40 [1.28, 1.53] (431) | 1.33 [1.25, 1.42] (706) | 0.53 [0.48, 0.58] (343) |
| ret_12m_skip1 | 3 | 1.50 [1.46, 1.54] (4522) | 1.41 [1.29, 1.54] (432) | 1.30 [1.21, 1.38] (684) | 0.73 [0.67, 0.79] (467) |
| ret_12m_skip1 | 6 | 1.49 [1.45, 1.53] (4400) | 1.33 [1.21, 1.46] (403) | 1.21 [1.13, 1.29] (636) | 1.07 [1.00, 1.13] (675) |
| ret_12m_skip1 | 12 | 1.47 [1.42, 1.51] (4156) | 1.20 [1.08, 1.32] (354) | 1.03 [0.95, 1.11] (529) | 1.17 [1.10, 1.24] (715) |
| eps_growth_q0 | 0 | 1.11 [1.07, 1.16] (2362) | 0.99 [0.86, 1.12] (209) | 1.12 [1.03, 1.22] (423) | 1.04 [0.97, 1.11] (576) |
| eps_growth_q0 | 3 | 1.15 [1.11, 1.19] (2388) | 1.05 [0.93, 1.19] (225) | 0.99 [0.90, 1.09] (380) | 1.13 [1.05, 1.20] (613) |
| eps_growth_q0 | 6 | 1.20 [1.15, 1.24] (2445) | 1.17 [1.03, 1.31] (244) | 1.04 [0.95, 1.13] (417) | 1.15 [1.08, 1.23] (615) |
| eps_growth_q0 | 12 | 1.27 [1.22, 1.32] (2502) | 1.26 [1.12, 1.41] (269) | 1.17 [1.08, 1.26] (470) | 1.17 [1.09, 1.24] (593) |
| rev_growth_accel | 0 | 1.19 [1.16, 1.23] (3322) | 1.08 [0.98, 1.20] (315) | 1.07 [0.99, 1.15] (537) | 0.91 [0.85, 0.98] (548) |
| rev_growth_accel | 3 | 1.17 [1.13, 1.21] (3189) | 0.97 [0.87, 1.09] (277) | 0.93 [0.85, 1.01] (459) | 1.03 [0.96, 1.10] (602) |
| rev_growth_accel | 6 | 1.16 [1.12, 1.20] (3107) | 0.89 [0.79, 1.00] (250) | 0.84 [0.77, 0.92] (411) | 1.05 [0.98, 1.12] (601) |
| rev_growth_accel | 12 | 1.25 [1.21, 1.29] (3226) | 0.98 [0.87, 1.10] (264) | 0.88 [0.81, 0.96] (408) | 1.09 [1.01, 1.16] (600) |
| op_margin_delta | 0 | 1.22 [1.18, 1.26] (3613) | 1.10 [0.99, 1.22] (333) | 1.14 [1.06, 1.22] (593) | 0.97 [0.90, 1.03] (616) |
| op_margin_delta | 3 | 1.23 [1.20, 1.27] (3591) | 1.04 [0.93, 1.16] (312) | 1.15 [1.07, 1.24] (597) | 1.01 [0.94, 1.07] (632) |
| op_margin_delta | 6 | 1.26 [1.22, 1.30] (3605) | 1.16 [1.04, 1.28] (342) | 0.98 [0.91, 1.06] (503) | 1.03 [0.97, 1.10] (641) |
| op_margin_delta | 12 | 1.33 [1.29, 1.37] (3653) | 1.25 [1.13, 1.38] (359) | 1.02 [0.94, 1.10] (511) | 1.10 [1.03, 1.17] (649) |
| peg | 0 | 1.30 [1.24, 1.36] (1445) | 1.22 [1.04, 1.42] (141) | 0.99 [0.85, 1.14] (149) | 1.46 [1.34, 1.58] (337) |
| peg | 3 | 1.31 [1.25, 1.37] (1472) | 1.17 [0.99, 1.38] (128) | 1.05 [0.91, 1.21] (152) | 1.39 [1.28, 1.50] (382) |
| peg | 6 | 1.30 [1.24, 1.37] (1487) | 1.15 [0.97, 1.36] (121) | 1.12 [0.97, 1.28] (158) | 1.28 [1.18, 1.39] (376) |
| peg | 12 | 1.26 [1.20, 1.33] (1434) | 1.16 [0.97, 1.38] (114) | 1.21 [1.07, 1.36] (213) | 1.16 [1.06, 1.26] (353) |
| pe | 0 | 1.15 [1.11, 1.19] (2510) | 1.23 [1.10, 1.38] (282) | 1.06 [0.97, 1.16] (403) | 1.68 [1.60, 1.76] (864) |
| pe | 3 | 1.13 [1.09, 1.17] (2479) | 1.18 [1.05, 1.33] (264) | 1.09 [1.00, 1.19] (392) | 1.50 [1.42, 1.58] (834) |
| pe | 6 | 1.18 [1.13, 1.22] (2601) | 1.13 [1.01, 1.28] (247) | 1.19 [1.10, 1.30] (422) | 1.23 [1.15, 1.30] (703) |
| pe | 12 | 1.16 [1.12, 1.20] (2530) | 1.23 [1.10, 1.38] (267) | 1.38 [1.29, 1.49] (544) | 1.03 [0.96, 1.10] (590) |
| pe_vs_5y_median | 0 | 1.31 [1.26, 1.36] (2386) | 1.36 [1.21, 1.52] (255) | 1.12 [1.01, 1.23] (341) | 1.67 [1.57, 1.76] (677) |
| pe_vs_5y_median | 3 | 1.31 [1.26, 1.36] (2380) | 1.28 [1.13, 1.44] (230) | 1.16 [1.05, 1.28] (332) | 1.56 [1.47, 1.65] (678) |
| pe_vs_5y_median | 6 | 1.31 [1.26, 1.36] (2366) | 1.36 [1.21, 1.54] (236) | 1.28 [1.17, 1.41] (352) | 1.38 [1.29, 1.46] (613) |
| pe_vs_5y_median | 12 | 1.33 [1.28, 1.38] (2358) | 1.53 [1.36, 1.72] (258) | 1.49 [1.37, 1.61] (446) | 1.25 [1.17, 1.34] (562) |
| fcf_ps_slope | 0 | 0.85 [0.82, 0.88] (2639) | 0.89 [0.80, 1.00] (277) | 0.97 [0.89, 1.04] (511) | 1.12 [1.06, 1.19] (729) |
| fcf_ps_slope | 3 | 0.82 [0.79, 0.85] (2489) | 0.88 [0.78, 0.98] (269) | 0.95 [0.87, 1.02] (500) | 0.99 [0.92, 1.05] (634) |
| fcf_ps_slope | 6 | 0.82 [0.79, 0.86] (2457) | 0.93 [0.83, 1.04] (281) | 0.91 [0.83, 0.98] (476) | 0.99 [0.93, 1.06] (625) |
| fcf_ps_slope | 12 | 0.82 [0.79, 0.85] (2353) | 0.84 [0.74, 0.95] (249) | 0.90 [0.83, 0.98] (461) | 1.09 [1.02, 1.16] (663) |
| pegy | 0 | 1.32 [1.25, 1.38] (1496) | 1.22 [1.04, 1.43] (144) | 0.96 [0.83, 1.11] (149) | 1.48 [1.36, 1.60] (358) |
| pegy | 3 | 1.32 [1.26, 1.39] (1523) | 1.19 [1.00, 1.40] (131) | 1.06 [0.92, 1.22] (157) | 1.41 [1.30, 1.52] (402) |
| pegy | 6 | 1.32 [1.26, 1.38] (1537) | 1.17 [0.99, 1.38] (125) | 1.13 [0.99, 1.30] (165) | 1.30 [1.20, 1.40] (392) |
| pegy | 12 | 1.29 [1.23, 1.35] (1492) | 1.24 [1.05, 1.47] (125) | 1.22 [1.08, 1.37] (222) | 1.16 [1.07, 1.26] (364) |
| pct_from_52w_high | 0 | 0.62 [0.60, 0.65] (1917) | 0.55 [0.47, 0.64] (170) | 0.63 [0.57, 0.70] (336) | 0.40 [0.36, 0.45] (263) |
| pct_from_52w_high | 3 | 0.69 [0.66, 0.72] (2098) | 0.68 [0.59, 0.77] (207) | 0.88 [0.81, 0.96] (467) | 0.44 [0.40, 0.49] (286) |
| pct_from_52w_high | 6 | 0.73 [0.70, 0.76] (2164) | 0.82 [0.72, 0.92] (248) | 0.98 [0.90, 1.05] (513) | 0.66 [0.61, 0.72] (424) |
| pct_from_52w_high | 12 | 0.77 [0.74, 0.80] (2204) | 0.79 [0.70, 0.89] (235) | 0.79 [0.72, 0.86] (407) | 0.86 [0.80, 0.93] (532) |
| dist_above_30w_sma | 0 | 1.39 [1.35, 1.43] (4322) | 1.18 [1.07, 1.30] (368) | 1.18 [1.10, 1.27] (630) | 0.71 [0.66, 0.77] (464) |
| dist_above_30w_sma | 3 | 1.45 [1.41, 1.49] (4490) | 1.30 [1.18, 1.42] (404) | 1.39 [1.31, 1.48] (740) | 0.62 [0.57, 0.68] (405) |
| dist_above_30w_sma | 6 | 1.43 [1.39, 1.47] (4396) | 1.30 [1.19, 1.43] (403) | 1.41 [1.32, 1.50] (746) | 0.84 [0.78, 0.90] (546) |
| dist_above_30w_sma | 12 | 1.42 [1.38, 1.46] (4190) | 1.30 [1.19, 1.43] (395) | 1.09 [1.01, 1.17] (571) | 1.15 [1.08, 1.22] (728) |
| atr_contraction | 0 | 0.99 [0.96, 1.03] (3098) | 0.97 [0.87, 1.08] (303) | 0.97 [0.90, 1.05] (517) | 0.98 [0.91, 1.04] (637) |
| atr_contraction | 3 | 1.06 [1.02, 1.09] (3296) | 1.07 [0.97, 1.19] (334) | 0.91 [0.84, 0.99] (486) | 0.96 [0.90, 1.03] (627) |
| atr_contraction | 6 | 1.09 [1.06, 1.13] (3390) | 1.10 [1.00, 1.22] (343) | 1.06 [0.99, 1.14] (564) | 0.94 [0.88, 1.01] (613) |
| atr_contraction | 12 | 1.13 [1.09, 1.16] (3414) | 1.17 [1.06, 1.29] (358) | 0.95 [0.88, 1.03] (503) | 0.98 [0.92, 1.05] (634) |
| inst_pct | 0 | 0.95 [0.93, 0.97] (6367) | 0.86 [0.75, 0.99] (156) | insufficient (0) | insufficient (0) |
| inst_pct | 3 | 0.96 [0.94, 0.98] (6150) | 0.87 [0.75, 1.00] (156) | insufficient (0) | insufficient (0) |
| inst_pct | 6 | 0.96 [0.94, 0.98] (5944) | 0.88 [0.76, 1.01] (159) | insufficient (0) | insufficient (0) |
| inst_pct | 12 | 0.95 [0.92, 0.97] (5239) | 0.89 [0.77, 1.03] (158) | insufficient (0) | insufficient (0) |
| inst_pct_delta_qoq | 0 | 1.48 [1.42, 1.53] (2380) | insufficient (68) | insufficient (0) | insufficient (0) |
| inst_pct_delta_qoq | 3 | 1.44 [1.39, 1.50] (2244) | insufficient (48) | insufficient (0) | insufficient (0) |
| inst_pct_delta_qoq | 6 | 1.39 [1.34, 1.45] (2063) | insufficient (43) | insufficient (0) | insufficient (0) |
| inst_pct_delta_qoq | 12 | 1.43 [1.37, 1.49] (1881) | insufficient (53) | insufficient (0) | insufficient (0) |
| insider_buy_count_90d | 0 | 1.11 [1.07, 1.16] (1972) | 1.12 [0.99, 1.26] (237) | 0.86 [0.77, 0.94] (323) | 1.27 [1.19, 1.35] (621) |
| insider_buy_count_90d | 3 | 1.11 [1.06, 1.15] (1952) | 0.89 [0.78, 1.01] (197) | 0.86 [0.78, 0.95] (300) | 1.12 [1.04, 1.20] (474) |
| insider_buy_count_90d | 6 | 1.06 [1.02, 1.11] (1943) | 0.96 [0.84, 1.10] (185) | 0.88 [0.79, 0.97] (310) | 1.00 [0.92, 1.08] (458) |
| insider_buy_count_90d | 12 | 1.08 [1.04, 1.12] (2009) | 0.93 [0.81, 1.07] (179) | 1.06 [0.97, 1.15] (404) | 0.98 [0.86, 1.12] (169) |
| net_debt_to_ebitda | 0 | 1.39 [1.35, 1.43] (3472) | 1.16 [1.04, 1.29] (302) | 1.15 [1.06, 1.24] (508) | 1.00 [0.93, 1.07] (565) |
| net_debt_to_ebitda | 3 | 1.39 [1.34, 1.43] (3431) | 1.16 [1.04, 1.29] (290) | 1.14 [1.05, 1.23] (488) | 0.96 [0.90, 1.03] (562) |
| net_debt_to_ebitda | 6 | 1.39 [1.35, 1.44] (3396) | 1.10 [0.98, 1.23] (274) | 1.17 [1.08, 1.26] (482) | 0.93 [0.87, 1.00] (550) |
| net_debt_to_ebitda | 12 | 1.40 [1.36, 1.45] (3302) | 1.16 [1.04, 1.30] (280) | 1.17 [1.09, 1.27] (509) | 0.95 [0.89, 1.02] (546) |
| share_count_change_8q | 0 | 0.86 [0.83, 0.89] (2461) | 1.04 [0.94, 1.16] (308) | 0.98 [0.91, 1.06] (502) | 1.04 [0.98, 1.11] (627) |
| share_count_change_8q | 3 | 0.85 [0.82, 0.88] (2372) | 1.10 [0.99, 1.22] (321) | 0.98 [0.90, 1.06] (491) | 1.09 [1.02, 1.16] (638) |
| share_count_change_8q | 6 | 0.84 [0.81, 0.88] (2314) | 1.04 [0.94, 1.16] (299) | 1.00 [0.92, 1.08] (493) | 1.12 [1.05, 1.19] (641) |
| share_count_change_8q | 12 | 0.87 [0.84, 0.90] (2300) | 0.99 [0.88, 1.10] (273) | 1.06 [0.98, 1.15] (496) | 1.11 [1.04, 1.19] (614) |
| shareholder_yield | 0 | 0.84 [0.81, 0.88] (2411) | 0.88 [0.78, 0.99] (261) | 0.94 [0.86, 1.01] (479) | 1.19 [1.12, 1.26] (715) |
| shareholder_yield | 3 | 0.80 [0.77, 0.84] (2251) | 0.93 [0.83, 1.04] (272) | 0.91 [0.84, 0.99] (459) | 1.19 [1.12, 1.27] (699) |
| shareholder_yield | 6 | 0.78 [0.75, 0.81] (2134) | 0.91 [0.81, 1.02] (260) | 0.93 [0.85, 1.01] (456) | 1.14 [1.07, 1.21] (651) |
| shareholder_yield | 12 | 0.80 [0.77, 0.83] (2115) | 0.87 [0.77, 0.99] (242) | 0.95 [0.87, 1.03] (443) | 1.00 [0.93, 1.07] (550) |
| marketcap | 0 | 1.37 [1.34, 1.41] (4282) | 1.38 [1.26, 1.51] (430) | 1.01 [0.94, 1.09] (538) | 1.20 [1.13, 1.27] (783) |
| marketcap | 3 | 1.35 [1.31, 1.39] (4197) | 1.37 [1.25, 1.50] (426) | 1.01 [0.94, 1.09] (538) | 1.11 [1.05, 1.18] (727) |
| marketcap | 6 | 1.36 [1.32, 1.40] (4236) | 1.36 [1.25, 1.49] (425) | 1.10 [1.03, 1.19] (587) | 0.95 [0.89, 1.01] (618) |
| marketcap | 12 | 1.36 [1.32, 1.40] (4196) | 1.45 [1.33, 1.58] (448) | 1.17 [1.10, 1.26] (623) | 0.82 [0.76, 0.89] (535) |
| pb | 0 | 0.94 [0.91, 0.97] (3246) | 0.90 [0.81, 1.00] (318) | 0.97 [0.90, 1.04] (593) | 1.56 [1.50, 1.63] (1273) |
| pb | 3 | 0.89 [0.86, 0.92] (3090) | 0.90 [0.81, 1.00] (315) | 0.91 [0.84, 0.98] (563) | 1.40 [1.33, 1.46] (1127) |
| pb | 6 | 0.89 [0.86, 0.92] (3094) | 0.90 [0.80, 1.00] (310) | 1.00 [0.93, 1.07] (602) | 1.20 [1.14, 1.26] (856) |
| pb | 12 | 0.90 [0.87, 0.93] (3066) | 1.02 [0.93, 1.13] (351) | 1.13 [1.06, 1.21] (675) | 0.97 [0.92, 1.04] (731) |
| dividend_yield | 0 | 1.35 [1.33, 1.37] (20241) | 1.30 [1.25, 1.35] (2074) | 1.21 [1.18, 1.25] (3385) | 1.07 [1.04, 1.10] (3413) |
| dividend_yield | 3 | 1.35 [1.34, 1.37] (20405) | 1.30 [1.25, 1.35] (2084) | 1.21 [1.17, 1.24] (3363) | 1.08 [1.05, 1.11] (3411) |
| dividend_yield | 6 | 1.35 [1.33, 1.37] (20519) | 1.30 [1.25, 1.35] (2098) | 1.21 [1.17, 1.24] (3347) | 1.08 [1.05, 1.11] (3417) |
| dividend_yield | 12 | 1.35 [1.33, 1.37] (20290) | 1.28 [1.23, 1.34] (2061) | 1.21 [1.18, 1.25] (3310) | 1.08 [1.05, 1.11] (3407) |

## Composite (section 4)

Fewer than 3 features PASS-build on win_50; composite built from the top 3 by extreme-decile lift, UNCONFIRMED: ret_12m_skip1, pe_vs_5y_median, inst_pct_delta_qoq.
Composite = mean oriented raw percentile rank (1 - rank for LOW features) over rows where every member is
non-null, ranked into deciles per (month_end, lag). pool share = rows in the cell / all universe rows at that lag.

| lag | label | cell | coverage | pool share | rows | events | rate | lift | CI low | CI high |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | win_50 | decile 10 | 29.2% | 2.9% | 11,542 | 957 | 8.29% | 1.12 | 1.06 | 1.19 |
| 0 | win_50 | deciles 8-10 | 29.2% | 8.8% | 34,536 | 2777 | 8.04% | 1.09 | 1.05 | 1.13 |
| 0 | win_100 | decile 10 | 29.2% | 2.9% | 11,542 | 167 | 1.45% | 1.51 | 1.29 | 1.75 |
| 0 | win_100 | deciles 8-10 | 29.2% | 8.8% | 34,536 | 422 | 1.22% | 1.27 | 1.16 | 1.40 |
| 0 | launch_300 | decile 10 | 29.2% | 2.9% | 11,542 | 48 | insufficient | insufficient | insufficient | insufficient |
| 0 | launch_300 | deciles 8-10 | 29.2% | 8.8% | 34,536 | 108 | 0.31% | 1.28 | 1.06 | 1.55 |
| 3 | win_50 | decile 10 | 27.8% | 2.8% | 10,992 | 970 | 8.82% | 1.16 | 1.10 | 1.24 |
| 3 | win_50 | deciles 8-10 | 27.8% | 8.4% | 32,881 | 2717 | 8.26% | 1.09 | 1.05 | 1.13 |
| 3 | win_100 | decile 10 | 27.8% | 2.8% | 10,992 | 140 | 1.27% | 1.28 | 1.09 | 1.51 |
| 3 | win_100 | deciles 8-10 | 27.8% | 8.4% | 32,881 | 394 | 1.20% | 1.21 | 1.09 | 1.33 |
| 3 | launch_300 | decile 10 | 27.8% | 2.8% | 10,992 | 43 | insufficient | insufficient | insufficient | insufficient |
| 3 | launch_300 | deciles 8-10 | 27.8% | 8.4% | 32,881 | 108 | 0.33% | 1.35 | 1.12 | 1.63 |
| 6 | win_50 | decile 10 | 26.4% | 2.6% | 10,407 | 951 | 9.14% | 1.19 | 1.12 | 1.26 |
| 6 | win_50 | deciles 8-10 | 26.4% | 7.9% | 31,138 | 2608 | 8.38% | 1.09 | 1.05 | 1.13 |
| 6 | win_100 | decile 10 | 26.4% | 2.6% | 10,407 | 180 | 1.73% | 1.69 | 1.46 | 1.95 |
| 6 | win_100 | deciles 8-10 | 26.4% | 7.9% | 31,138 | 406 | 1.30% | 1.27 | 1.16 | 1.40 |
| 6 | launch_300 | decile 10 | 26.4% | 2.6% | 10,407 | 56 | insufficient | insufficient | insufficient | insufficient |
| 6 | launch_300 | deciles 8-10 | 26.4% | 7.9% | 31,138 | 126 | 0.40% | 1.59 | 1.34 | 1.89 |
| 12 | win_50 | decile 10 | 23.6% | 2.4% | 9,299 | 917 | 9.86% | 1.25 | 1.18 | 1.33 |
| 12 | win_50 | deciles 8-10 | 23.6% | 7.1% | 27,826 | 2459 | 8.84% | 1.12 | 1.08 | 1.16 |
| 12 | win_100 | decile 10 | 23.6% | 2.4% | 9,299 | 185 | 1.99% | 1.84 | 1.60 | 2.12 |
| 12 | win_100 | deciles 8-10 | 23.6% | 7.1% | 27,826 | 412 | 1.48% | 1.37 | 1.24 | 1.51 |
| 12 | launch_300 | decile 10 | 23.6% | 2.4% | 9,299 | 55 | insufficient | insufficient | insufficient | insufficient |
| 12 | launch_300 | deciles 8-10 | 23.6% | 7.1% | 27,826 | 107 | 0.38% | 1.43 | 1.18 | 1.72 |

### Composite by SPY drawdown bucket, lag 0

| label | cell | 0-10 | 10-20 | 20-30 | >30 |
| --- | --- | ---: | ---: | ---: | ---: |
| win_50 | decile 10 | 1.13 [1.06, 1.20] (927) | insufficient (30) | insufficient (0) | insufficient (0) |
| win_50 | deciles 8-10 | 1.09 [1.05, 1.13] (2684) | insufficient (93) | insufficient (0) | insufficient (0) |
| win_100 | decile 10 | 1.51 [1.30, 1.76] (163) | insufficient (4) | insufficient (0) | insufficient (0) |
| win_100 | deciles 8-10 | 1.29 [1.17, 1.42] (415) | insufficient (7) | insufficient (0) | insufficient (0) |
| launch_300 | decile 10 | insufficient (46) | insufficient (2) | insufficient (0) | insufficient (0) |
| launch_300 | deciles 8-10 | 1.28 [1.05, 1.54] (105) | insufficient (3) | insufficient (0) | insufficient (0) |

### Composite by months-since-trough bucket, lag 0

| label | cell | 0-12 | 13-24 | >24 |
| --- | --- | ---: | ---: | ---: |
| win_50 | decile 10 | 1.13 [1.06, 1.20] (940) | insufficient (17) | insufficient (0) |
| win_50 | deciles 8-10 | 1.09 [1.05, 1.13] (2731) | insufficient (46) | insufficient (0) |
| win_100 | decile 10 | 1.51 [1.30, 1.75] (165) | insufficient (2) | insufficient (0) |
| win_100 | deciles 8-10 | 1.27 [1.15, 1.40] (416) | insufficient (6) | insufficient (0) |
| launch_300 | decile 10 | insufficient (48) | insufficient (0) | insufficient (0) |
| launch_300 | deciles 8-10 | 1.29 [1.06, 1.55] (108) | insufficient (0) | insufficient (0) |
