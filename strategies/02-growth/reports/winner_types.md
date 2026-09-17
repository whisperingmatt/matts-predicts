# Winner types — Section 2 Growth, GROWTH-003 session 9 (end of chunk 4c)

Descriptive clustering of the winners described in reports/anatomy_tables.md. Inputs are the section-2
numeric fields at T-0 plus the 23 GROWTH-002 percentile ranks at lag 0, winners only, standardized on the
winners (decisions.md "Chunk 4c", S9 rulings: T-0 only; the 5.02 proxy dropped, and ev_total_t12 with it;
scalemarketcap excluded in favor of the point-in-time market cap; dollar fields as log1p; fields under 50%
winner coverage left out per label; nulls filled with the winners' median). k-means for k 2 to 6 with
silhouette, k chosen by silhouette; HDBSCAN as a check. No cluster was dropped or merged. Population
frequency assigns every population row (winners included, F3) to its nearest k-means centroid in the same
standardized space; lift = the cluster's share of winners / its share of population rows. Every number
comes from src/winner_types.py; unrounded tables in reports/s9_*.csv, the per-winner assignment in
reports/s9_winner_clusters.csv. Seeds fixed (0); single-threaded so the outputs reproduce.

Everything measured after T-0 (the T+k half of a timeline, every _f12 column) is FORWARD-LOOKING and
describes the move; it was not a clustering input and cannot enter a later scoring model.

## launch_300

4,301 winners in 529,158 population rows; 51 inputs used (51 of 56 candidates).
Left out for coverage under 50%: pr_eps_growth_q0 (46%), pr_peg (18%), pr_pe (42%), pr_pe_vs_5y_median (31%), pr_pegy (18%).
Inputs with more than 5% of winners imputed: drawdown_from_3y_high (21%), months_since_3y_low (21%), rev_growth_yoy (8%), gross_margin (6%), op_margin (6%), capex_to_rev (6%), rnd_to_rev (6%), shares_chg_8q (11%), rev_growth_streak (8%), inst_pct (35%), inst_pct_delta_4q (40%), pr_rev_growth_accel (18%), pr_op_margin_delta (9%), pr_inst_pct (35%), pr_inst_pct_delta_qoq (35%), pr_net_debt_to_ebitda (43%), pr_share_count_change_8q (11%), pr_shareholder_yield (11%), pr_pb (8%).

### k-means sweep

| k | silhouette | inertia | cluster sizes (largest first) |
| --- | ---: | ---: | ---: |
| 2 | 0.0829 | 202,161 | 2209/2092 |
| 3 | 0.0721 | 192,428 | 1935/1381/985 |
| 4 | 0.0740 | 184,580 | 1912/1361/1006/22 |
| 5 | 0.0507 | 182,825 | 1357/1192/793/641/318 |
| 6 | 0.0446 | 178,570 | 1211/1034/655/612/536/253 |

Chosen k = 2 (highest silhouette). Clusters are numbered by size, 1 = largest.

### HDBSCAN check

min_cluster_size 43 (1% of winners). The first row is scikit-learn's default
min_samples; the others are the sensitivity check. ARI = adjusted Rand index against the chosen k-means labels.

| min_samples | clusters | sizes | noise share | ARI all | ARI excluding noise |
| --- | ---: | ---: | ---: | ---: | ---: |
| 43 | 0 | none | 100.0% | 0.000 | n/a |
| 25 | 0 | none | 100.0% | 0.000 | n/a |
| 10 | 2 | 328/75 | 90.6% | 0.005 | -0.016 |
| 5 | 2 | 508/60 | 86.8% | 0.003 | -0.010 |

Overlap with the k-means clusters (first setting that found any cluster, else all noise):

| k-means \ HDBSCAN | noise | h0 | h1 |
| --- | ---: | ---: | ---: |
| c1 | 2,060 | 149 | 0 |
| c2 | 1,838 | 179 | 75 |

### Clusters

| cluster | winners | winner share | population rows | population share | lift | winner rate | most distinguishing fields (mean z within cluster) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c1 | 2,209 | 51.4% | 99,765 | 18.9% | 2.72 | 2.21% | drawdown_from_3y_high (-0.66 sd); pr_pct_from_52w_high (+0.64 sd); pr_ret_12m_skip1 (-0.62 sd) |
| c2 | 2,092 | 48.6% | 429,393 | 81.1% | 0.60 | 0.49% | drawdown_from_3y_high (+0.69 sd); pr_pct_from_52w_high (-0.68 sd); pr_ret_12m_skip1 (+0.65 sd) |

Base winner rate over the population: 0.81%. Winner rate in a cluster = winners in it / population rows assigned to it (winners included).

### Median of every field by cluster (raw values, nulls excluded; ranks are GROWTH-002 percentile ranks at lag 0)

| field | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| years_since_first_price | 8.3 | 8.5 | 8.4 | 16.3 |
| drawdown_from_3y_high | -74.3% | -27.3% | -55.3% | -19.4% |
| months_since_3y_low | 3 | 25 | 12 | 26 |
| realized_vol_12m | 78.7% | 55.0% | 66.0% | 37.1% |
| avg_dollar_volume_20d | 7 | 15 | 10 | 16 |
| price | 9.20 | 22.77 | 13.39 | 30.20 |
| marketcap_musd | 523 | 1,407 | 790 | 1,869 |
| rev_growth_yoy | -2.0% | 17.3% | 6.6% | 7.3% |
| gross_margin | 38.1% | 48.1% | 42.6% | 44.1% |
| op_margin | -3.2% | 3.5% | -0.3% | 10.3% |
| cash_to_mcap | 17.4% | 7.5% | 11.3% | 7.3% |
| net_debt_to_mcap | 35.0% | -0.2% | 5.2% | 11.4% |
| capex_to_rev | 4.2% | 2.9% | 3.5% | 3.2% |
| rnd_to_rev | 0.0% | 9.6% | 3.8% | 0.0% |
| shares_chg_4q | 1.4% | 2.3% | 1.8% | 0.5% |
| shares_chg_8q | 4.1% | 5.7% | 4.9% | 1.1% |
| rev_growth_streak | 0 | 3 | 1 | 3 |
| quarters_since_loss | 0 | 1 | 0 | 7 |
| ev11_t12 | 1.0 | 1.0 | 1.0 | 1.0 |
| ev12_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev21_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev22_t12 | 4.0 | 4.0 | 4.0 | 4.0 |
| ev23_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev32_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev53_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev71_t12 | 2.0 | 1.0 | 1.0 | 1.0 |
| ev81_t12 | 2.0 | 2.0 | 2.0 | 2.0 |
| insider_net_buys_12m | 3.0 | 1.0 | 2.0 | 0.0 |
| officer_buys_12m | 0.0 | 0.0 | 0.0 | 0.0 |
| inst_pct | 75.2% | 74.8% | 74.9% | 82.3% |
| inst_pct_delta_4q | -0.0% | 2.6% | 1.6% | 0.9% |
| spy_drawdown | -6.6% | -3.2% | -4.9% | -2.0% |
| months_since_trough | 2 | 3 | 2 | 3 |
| ev52_t12 | 3.0 | 2.0 | 2.0 | 2.0 |
| ev_total_t12 | 15.0 | 13.0 | 14.0 | 14.0 |
| pr_ret_6m_skip1 | 0.115 | 0.757 | 0.363 | 0.500 |
| pr_ret_12m_skip1 | 0.089 | 0.742 | 0.337 | 0.500 |
| pr_eps_growth_q0 | 0.146 | 0.654 | 0.310 | 0.499 |
| pr_rev_growth_accel | 0.342 | 0.579 | 0.440 | 0.500 |
| pr_op_margin_delta | 0.282 | 0.704 | 0.489 | 0.500 |
| pr_peg | 0.222 | 0.447 | 0.366 | 0.500 |
| pr_pe | 0.207 | 0.702 | 0.505 | 0.498 |
| pr_pe_vs_5y_median | 0.217 | 0.577 | 0.462 | 0.500 |
| pr_fcf_ps_slope | 0.512 | 0.515 | 0.513 | 0.500 |
| pr_pegy | 0.216 | 0.443 | 0.364 | 0.500 |
| pr_pct_from_52w_high | 0.928 | 0.516 | 0.799 | 0.500 |
| pr_dist_above_30w_sma | 0.121 | 0.736 | 0.377 | 0.500 |
| pr_atr_contraction | 0.443 | 0.502 | 0.475 | 0.500 |
| pr_inst_pct | 0.384 | 0.376 | 0.378 | 0.500 |
| pr_inst_pct_delta_qoq | 0.379 | 0.618 | 0.532 | 0.500 |
| pr_insider_buy_count_90d | 0.000 | 0.000 | 0.000 | 0.000 |
| pr_net_debt_to_ebitda | 0.675 | 0.349 | 0.523 | 0.500 |
| pr_share_count_change_8q | 0.699 | 0.731 | 0.721 | 0.500 |
| pr_shareholder_yield | 0.277 | 0.243 | 0.257 | 0.500 |
| pr_marketcap | 0.183 | 0.391 | 0.273 | 0.500 |
| pr_pb | 0.250 | 0.783 | 0.545 | 0.490 |
| pr_dividend_yield | 0.000 | 0.000 | 0.000 | 0.469 |
| pr_realized_vol_12m | 0.910 | 0.792 | 0.864 | 0.500 |

### 8-K, insider and share-count fingerprint (mean for counts, median for share changes; _f12 rows are forward-looking)

| field | stat | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: | ---: |
| ev11_t12 | mean | 1.90 | 1.94 | 1.92 | 1.75 |
| ev12_t12 | mean | 0.19 | 0.18 | 0.18 | 0.17 |
| ev21_t12 | mean | 0.18 | 0.16 | 0.17 | 0.23 |
| ev22_t12 | mean | 4.21 | 4.14 | 4.18 | 4.09 |
| ev23_t12 | mean | 0.64 | 0.69 | 0.66 | 0.64 |
| ev32_t12 | mean | 0.25 | 0.23 | 0.24 | 0.17 |
| ev53_t12 | mean | 0.42 | 0.25 | 0.34 | 0.37 |
| ev71_t12 | mean | 2.95 | 2.23 | 2.60 | 2.75 |
| ev81_t12 | mean | 2.99 | 2.62 | 2.81 | 3.05 |
| insider_net_buys_12m | mean | 10.82 | 4.87 | 7.92 | 5.80 |
| officer_buys_12m | mean | 3.89 | 1.05 | 2.51 | 1.77 |
| ev11_f12 | mean | 1.86 | 1.97 | 1.92 | 1.54 |
| ev12_f12 | mean | 0.21 | 0.23 | 0.22 | 0.17 |
| ev21_f12 | mean | 0.18 | 0.21 | 0.19 | 0.23 |
| ev22_f12 | mean | 4.29 | 4.23 | 4.26 | 3.98 |
| ev23_f12 | mean | 0.70 | 0.79 | 0.74 | 0.63 |
| ev32_f12 | mean | 0.26 | 0.34 | 0.29 | 0.15 |
| ev52_f12 | mean | 2.58 | 2.26 | 2.42 | 2.42 |
| ev53_f12 | mean | 0.35 | 0.32 | 0.33 | 0.39 |
| ev71_f12 | mean | 2.91 | 2.51 | 2.71 | 2.71 |
| ev81_f12 | mean | 3.31 | 3.23 | 3.28 | 2.98 |
| ev_total_f12 | mean | 16.65 | 16.07 | 16.37 | 15.20 |
| shares_chg_4q | median | 1.4% | 2.3% | 1.8% | 0.5% |
| shares_chg_8q | median | 4.1% | 5.7% | 4.9% | 1.1% |
| shares_change_f12 | median | 1.9% | 3.4% | 2.5% | 0.4% |

### Sector and regime mix (share of the cluster's winners in each bucket)

sector

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| Basic Materials | 8.4% | 4.9% | 6.7% | 5.8% |
| Communication Services | 2.8% | 5.7% | 4.2% | 4.2% |
| Consumer Cyclical | 17.5% | 9.7% | 13.7% | 12.8% |
| Consumer Defensive | 2.1% | 3.9% | 3.0% | 5.1% |
| Energy | 13.1% | 2.5% | 7.9% | 7.2% |
| Financial Services | 4.7% | 3.2% | 4.0% | 15.6% |
| Healthcare | 27.3% | 27.7% | 27.5% | 15.3% |
| Industrials | 11.3% | 13.9% | 12.6% | 14.6% |
| Real Estate | 0.6% | 0.5% | 0.6% | 0.6% |
| Technology | 12.0% | 26.4% | 19.0% | 15.6% |
| Unknown | 0.0% | 0.0% | 0.0% | 0.0% |
| Utilities | 0.2% | 1.6% | 0.9% | 3.2% |

drawdown_bucket

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| 0-10 | 59.4% | 73.0% | 66.0% | 76.1% |
| 10-20 | 13.6% | 16.1% | 14.8% | 13.9% |
| 20-30 | 3.6% | 4.3% | 4.0% | 5.8% |
| >30 | 23.4% | 6.5% | 15.2% | 4.2% |

mst_bucket

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| 0-12 | 89.1% | 79.3% | 84.4% | 79.2% |
| 13-24 | 7.9% | 12.4% | 10.1% | 9.1% |
| >24 | 2.9% | 8.3% | 5.5% | 11.7% |

price_bucket

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| 1 5-10 | 55.0% | 16.4% | 36.2% | 11.2% |
| 2 10-20 | 33.5% | 26.9% | 30.3% | 21.7% |
| 3 20-50 | 10.7% | 36.4% | 23.2% | 38.8% |
| 4 50+ | 0.9% | 20.3% | 10.3% | 28.2% |

profitable

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| False | 68.9% | 47.5% | 58.5% | 23.3% |
| True | 31.1% | 52.5% | 41.5% | 76.7% |

ipo_lt_3y

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| False | 78.6% | 77.3% | 78.0% | 89.8% |
| True | 21.4% | 22.7% | 22.0% | 10.2% |

### Timeline by cluster (winner median at T+k; population overlay = median over the cluster's winners of the population median at the same calendar month)

c1

| k | price_return W | price_return P | rev_growth_yoy W | rev_growth_yoy P | shares_change W | shares_change P | insider_net_buys_12m W | insider_net_buys_12m P | ev_total_t12 W | ev_total_t12 P |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -24 | 133.5% (88%) | -3.7% | 10.8% (73%) | 9.9% | -3.9% (89%) | -0.7% | 0.0 (72%) | 0.0 | 14.0 (99%) | 13.0 |
| -21 | 130.4% (90%) | -2.2% | 10.1% (75%) | 9.9% | -3.0% (91%) | -0.5% | 1.0 (72%) | 0.0 | 15.0 (99%) | 13.0 |
| -18 | 120.2% (93%) | -0.4% | 10.7% (78%) | 9.9% | -2.4% (94%) | -0.4% | 1.0 (73%) | 0.0 | 15.0 (99%) | 13.0 |
| -15 | 107.5% (95%) | 1.7% | 10.1% (80%) | 9.9% | -1.8% (96%) | -0.4% | 1.0 (73%) | 0.0 | 15.0 (99%) | 14.0 |
| -12 | 96.1% (97%) | 3.5% | 9.1% (81%) | 9.9% | -1.4% (98%) | -0.3% | 1.0 (74%) | 0.0 | 15.0 (99%) | 14.0 |
| -9 | 76.2% (99%) | 3.2% | 7.2% (83%) | 9.0% | -0.8% (100%) | -0.2% | 1.0 (74%) | 0.0 | 15.0 (100%) | 14.0 |
| -6 | 47.2% (99%) | 0.2% | 4.8% (86%) | 7.4% | -0.4% (100%) | -0.1% | 2.0 (77%) | 0.0 | 15.0 (100%) | 14.0 |
| -3 | 19.0% (100%) | -0.8% | 3.5% (88%) | 5.1% | -0.1% (100%) | -0.1% | 2.0 (85%) | 0.0 | 15.0 (100%) | 14.0 |
| +0 | 0.0% (100%) | 0.0% | -2.0% (90%) | 4.5% | 0.0% (100%) | 0.0% | 3.0 (95%) | 1.0 | 15.0 (100%) | 14.0 |
| +3 | 30.0% (100%) | 7.1% | -4.4% (93%) | 3.3% | 0.1% (100%) | 0.1% | 3.0 (98%) | 1.0 | 15.0 (100%) | 14.0 |
| +6 | 67.4% (100%) | 10.8% | -4.1% (92%) | 3.8% | 0.4% (100%) | 0.2% | 3.0 (98%) | 0.0 | 15.0 (100%) | 14.0 |
| +9 | 113.9% (100%) | 15.5% | 0.5% (92%) | 4.0% | 1.0% (100%) | 0.3% | 2.0 (99%) | 0.0 | 15.0 (100%) | 14.0 |
| +12 | 160.7% (99%) | 18.8% | 10.8% (93%) | 4.4% | 1.9% (100%) | 0.5% | 1.0 (99%) | 0.0 | 15.0 (100%) | 14.0 |
| +15 | 208.5% (98%) | 21.4% | 19.8% (93%) | 6.0% | 3.0% (100%) | 0.6% | 1.0 (99%) | 0.0 | 15.0 (100%) | 13.0 |
| +18 | 266.5% (96%) | 27.5% | 26.8% (93%) | 7.2% | 4.3% (100%) | 0.7% | 0.0 (99%) | 0.0 | 15.0 (100%) | 13.0 |
| +21 | 342.0% (95%) | 27.9% | 27.8% (93%) | 9.1% | 5.5% (100%) | 0.8% | 0.0 (99%) | 0.0 | 16.0 (100%) | 13.0 |
| +24 | 406.7% (93%) | 29.3% | 28.3% (93%) | 9.8% | 7.0% (100%) | 0.9% | 0.0 (99%) | 0.0 | 15.0 (100%) | 13.0 |

c2

| k | price_return W | price_return P | rev_growth_yoy W | rev_growth_yoy P | shares_change W | shares_change P | insider_net_buys_12m W | insider_net_buys_12m P | ev_total_t12 W | ev_total_t12 P |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -24 | -26.7% (88%) | -11.2% | 13.6% (72%) | 7.4% | -5.2% (90%) | -0.8% | 0.0 (86%) | 0.0 | 12.0 (97%) | 13.0 |
| -21 | -26.5% (91%) | -8.5% | 13.8% (74%) | 9.5% | -4.4% (92%) | -0.6% | 0.0 (87%) | 0.0 | 12.0 (97%) | 13.0 |
| -18 | -24.9% (93%) | -6.4% | 14.9% (76%) | 10.0% | -3.8% (94%) | -0.5% | 0.0 (88%) | 0.0 | 13.0 (97%) | 13.0 |
| -15 | -24.4% (96%) | -4.7% | 13.8% (79%) | 10.1% | -2.9% (97%) | -0.4% | 0.0 (88%) | 0.0 | 12.0 (97%) | 14.0 |
| -12 | -22.0% (98%) | -5.8% | 13.4% (82%) | 9.6% | -2.3% (99%) | -0.3% | 1.0 (89%) | 0.0 | 13.0 (97%) | 14.0 |
| -9 | -19.0% (99%) | -4.4% | 14.2% (85%) | 9.0% | -1.5% (100%) | -0.3% | 1.0 (90%) | 0.0 | 13.0 (99%) | 14.0 |
| -6 | -16.0% (100%) | -3.0% | 16.0% (88%) | 8.3% | -0.9% (100%) | -0.2% | 1.0 (92%) | 0.0 | 13.0 (100%) | 14.0 |
| -3 | -9.1% (100%) | -2.7% | 16.0% (91%) | 6.8% | -0.3% (100%) | -0.0% | 1.0 (94%) | 0.0 | 13.0 (100%) | 14.0 |
| +0 | 0.0% (100%) | 0.0% | 17.3% (93%) | 5.0% | 0.0% (100%) | 0.0% | 1.0 (96%) | 0.0 | 13.0 (100%) | 14.0 |
| +3 | 21.2% (100%) | 3.1% | 17.9% (95%) | 4.5% | 0.4% (100%) | 0.0% | 0.0 (96%) | 0.0 | 13.0 (100%) | 14.0 |
| +6 | 48.5% (100%) | 6.3% | 18.9% (95%) | 4.3% | 1.2% (100%) | 0.2% | 0.0 (97%) | 0.0 | 14.0 (100%) | 14.0 |
| +9 | 82.2% (99%) | 7.8% | 21.0% (95%) | 4.2% | 2.2% (100%) | 0.3% | 0.0 (97%) | 0.0 | 14.0 (100%) | 14.0 |
| +12 | 121.6% (98%) | 7.9% | 24.3% (95%) | 4.3% | 3.4% (100%) | 0.3% | 0.0 (97%) | 0.0 | 15.0 (100%) | 14.0 |
| +15 | 168.6% (97%) | 11.8% | 26.8% (95%) | 4.4% | 4.9% (100%) | 0.4% | 0.0 (97%) | 0.0 | 15.0 (100%) | 13.0 |
| +18 | 239.3% (96%) | 12.7% | 30.7% (95%) | 4.9% | 6.3% (100%) | 0.5% | 0.0 (97%) | 0.0 | 15.0 (100%) | 13.0 |
| +21 | 313.0% (94%) | 17.9% | 32.8% (94%) | 5.7% | 7.6% (100%) | 0.6% | 0.0 (97%) | 0.0 | 15.0 (100%) | 13.0 |
| +24 | 390.1% (92%) | 19.8% | 35.2% (94%) | 6.2% | 8.6% (99%) | 0.7% | 0.0 (97%) | 0.0 | 14.0 (100%) | 13.0 |

## win_100

20,367 winners in 558,318 population rows; 53 inputs used (53 of 56 candidates).
Left out for coverage under 50%: pr_peg (23%), pr_pe_vs_5y_median (43%), pr_pegy (24%).
Inputs with more than 5% of winners imputed: drawdown_from_3y_high (16%), months_since_3y_low (16%), rev_growth_yoy (7%), gross_margin (5%), op_margin (5%), capex_to_rev (5%), rnd_to_rev (5%), shares_chg_8q (8%), rev_growth_streak (7%), insider_net_buys_12m (7%), officer_buys_12m (7%), inst_pct (36%), inst_pct_delta_4q (41%), pr_eps_growth_q0 (44%), pr_rev_growth_accel (14%), pr_op_margin_delta (8%), pr_pe (47%), pr_inst_pct (36%), pr_inst_pct_delta_qoq (36%), pr_insider_buy_count_90d (5%), pr_net_debt_to_ebitda (32%), pr_share_count_change_8q (8%), pr_shareholder_yield (8%), pr_pb (6%).

### k-means sweep

| k | silhouette | inertia | cluster sizes (largest first) |
| --- | ---: | ---: | ---: |
| 2 | 0.0854 | 999,615 | 10617/9750 |
| 3 | 0.0695 | 959,544 | 7655/6778/5934 |
| 4 | 0.0697 | 918,926 | 7798/6517/6047/5 |
| 5 | 0.0602 | 894,984 | 5903/5741/4629/4089/5 |
| 6 | 0.0498 | 877,239 | 5403/5221/4225/3882/1631/5 |

Chosen k = 2 (highest silhouette). Clusters are numbered by size, 1 = largest.

### HDBSCAN check

min_cluster_size 204 (1% of winners). The first row is scikit-learn's default
min_samples; the others are the sensitivity check. ARI = adjusted Rand index against the chosen k-means labels.

| min_samples | clusters | sizes | noise share | ARI all | ARI excluding noise |
| --- | ---: | ---: | ---: | ---: | ---: |
| 204 | 0 | none | 100.0% | 0.000 | n/a |
| 25 | 0 | none | 100.0% | 0.000 | n/a |
| 10 | 0 | none | 100.0% | 0.000 | n/a |
| 5 | 0 | none | 100.0% | 0.000 | n/a |

Overlap with the k-means clusters (first setting that found any cluster, else all noise):

| k-means \ HDBSCAN | noise |
| --- | ---: |
| c1 | 10,617 |
| c2 | 9,750 |

### Clusters

| cluster | winners | winner share | population rows | population share | lift | winner rate | most distinguishing fields (mean z within cluster) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c1 | 10,617 | 52.1% | 144,748 | 25.9% | 2.01 | 7.33% | drawdown_from_3y_high (-0.65 sd); pr_pct_from_52w_high (+0.64 sd); pr_ret_12m_skip1 (-0.59 sd) |
| c2 | 9,750 | 47.9% | 413,570 | 74.1% | 0.65 | 2.36% | drawdown_from_3y_high (+0.71 sd); pr_pct_from_52w_high (-0.69 sd); pr_ret_12m_skip1 (+0.64 sd) |

Base winner rate over the population: 3.65%. Winner rate in a cluster = winners in it / population rows assigned to it (winners included).

### Median of every field by cluster (raw values, nulls excluded; ranks are GROWTH-002 percentile ranks at lag 0)

| field | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| years_since_first_price | 10.7 | 11.5 | 11.0 | 16.4 |
| drawdown_from_3y_high | -64.9% | -21.6% | -45.0% | -19.6% |
| months_since_3y_low | 4 | 26 | 14 | 26 |
| realized_vol_12m | 70.7% | 50.3% | 59.9% | 37.2% |
| avg_dollar_volume_20d | 8 | 20 | 12 | 17 |
| price | 11.42 | 28.80 | 16.85 | 30.53 |
| marketcap_musd | 620 | 1,750 | 980 | 1,914 |
| rev_growth_yoy | -1.4% | 15.9% | 6.7% | 7.2% |
| gross_margin | 39.8% | 47.9% | 44.0% | 44.3% |
| op_margin | 0.2% | 7.4% | 3.6% | 10.3% |
| cash_to_mcap | 16.2% | 7.0% | 10.5% | 7.3% |
| net_debt_to_mcap | 35.2% | 1.0% | 8.1% | 11.5% |
| capex_to_rev | 3.6% | 3.2% | 3.4% | 3.1% |
| rnd_to_rev | 0.0% | 3.4% | 0.0% | 0.0% |
| shares_chg_4q | 0.9% | 1.5% | 1.2% | 0.5% |
| shares_chg_8q | 2.5% | 2.9% | 2.7% | 1.1% |
| rev_growth_streak | 0 | 4 | 2 | 3 |
| quarters_since_loss | 0 | 3 | 1 | 7 |
| ev11_t12 | 1.0 | 1.0 | 1.0 | 1.0 |
| ev12_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev21_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev22_t12 | 4.0 | 4.0 | 4.0 | 4.0 |
| ev23_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev32_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev53_t12 | 0.0 | 0.0 | 0.0 | 0.0 |
| ev71_t12 | 2.0 | 1.0 | 1.0 | 1.0 |
| ev81_t12 | 2.0 | 2.0 | 2.0 | 2.0 |
| insider_net_buys_12m | 2.0 | 0.0 | 1.0 | 0.0 |
| officer_buys_12m | 0.0 | 0.0 | 0.0 | 0.0 |
| inst_pct | 80.3% | 80.8% | 80.5% | 82.4% |
| inst_pct_delta_4q | 0.5% | 2.1% | 1.3% | 0.9% |
| spy_drawdown | -6.1% | -2.0% | -3.7% | -2.0% |
| months_since_trough | 2 | 3 | 2 | 3 |
| ev52_t12 | 2.0 | 2.0 | 2.0 | 2.0 |
| ev_total_t12 | 15.0 | 13.0 | 14.0 | 14.0 |
| pr_ret_6m_skip1 | 0.171 | 0.732 | 0.418 | 0.500 |
| pr_ret_12m_skip1 | 0.148 | 0.755 | 0.411 | 0.500 |
| pr_eps_growth_q0 | 0.196 | 0.674 | 0.386 | 0.499 |
| pr_rev_growth_accel | 0.367 | 0.579 | 0.467 | 0.500 |
| pr_op_margin_delta | 0.319 | 0.649 | 0.494 | 0.500 |
| pr_peg | 0.266 | 0.417 | 0.373 | 0.500 |
| pr_pe | 0.241 | 0.667 | 0.493 | 0.498 |
| pr_pe_vs_5y_median | 0.246 | 0.530 | 0.423 | 0.500 |
| pr_fcf_ps_slope | 0.478 | 0.526 | 0.506 | 0.500 |
| pr_pegy | 0.274 | 0.414 | 0.370 | 0.500 |
| pr_pct_from_52w_high | 0.880 | 0.453 | 0.726 | 0.500 |
| pr_dist_above_30w_sma | 0.182 | 0.724 | 0.426 | 0.500 |
| pr_atr_contraction | 0.463 | 0.503 | 0.484 | 0.500 |
| pr_inst_pct | 0.459 | 0.463 | 0.462 | 0.500 |
| pr_inst_pct_delta_qoq | 0.417 | 0.615 | 0.530 | 0.500 |
| pr_insider_buy_count_90d | 0.000 | 0.000 | 0.000 | 0.000 |
| pr_net_debt_to_ebitda | 0.687 | 0.357 | 0.516 | 0.500 |
| pr_share_count_change_8q | 0.634 | 0.644 | 0.638 | 0.500 |
| pr_shareholder_yield | 0.347 | 0.324 | 0.336 | 0.500 |
| pr_marketcap | 0.223 | 0.462 | 0.326 | 0.500 |
| pr_pb | 0.281 | 0.727 | 0.510 | 0.490 |
| pr_dividend_yield | 0.000 | 0.000 | 0.000 | 0.472 |
| pr_realized_vol_12m | 0.848 | 0.703 | 0.785 | 0.500 |

### 8-K, insider and share-count fingerprint (mean for counts, median for share changes; _f12 rows are forward-looking)

| field | stat | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: | ---: |
| ev11_t12 | mean | 1.81 | 1.71 | 1.76 | 1.73 |
| ev12_t12 | mean | 0.17 | 0.18 | 0.18 | 0.16 |
| ev21_t12 | mean | 0.20 | 0.21 | 0.20 | 0.22 |
| ev22_t12 | mean | 4.22 | 4.07 | 4.15 | 4.09 |
| ev23_t12 | mean | 0.73 | 0.63 | 0.68 | 0.64 |
| ev32_t12 | mean | 0.26 | 0.23 | 0.24 | 0.17 |
| ev53_t12 | mean | 0.39 | 0.29 | 0.34 | 0.37 |
| ev71_t12 | mean | 3.04 | 2.30 | 2.68 | 2.77 |
| ev81_t12 | mean | 3.07 | 2.76 | 2.92 | 3.02 |
| insider_net_buys_12m | mean | 10.29 | 4.19 | 7.42 | 5.63 |
| officer_buys_12m | mean | 3.67 | 0.99 | 2.41 | 1.72 |
| ev11_f12 | mean | 1.99 | 1.82 | 1.91 | 1.53 |
| ev12_f12 | mean | 0.21 | 0.20 | 0.20 | 0.17 |
| ev21_f12 | mean | 0.24 | 0.25 | 0.25 | 0.23 |
| ev22_f12 | mean | 4.15 | 4.07 | 4.11 | 3.99 |
| ev23_f12 | mean | 0.73 | 0.69 | 0.71 | 0.63 |
| ev32_f12 | mean | 0.27 | 0.32 | 0.29 | 0.15 |
| ev52_f12 | mean | 2.55 | 2.24 | 2.40 | 2.41 |
| ev53_f12 | mean | 0.36 | 0.34 | 0.35 | 0.39 |
| ev71_f12 | mean | 3.03 | 2.53 | 2.79 | 2.73 |
| ev81_f12 | mean | 3.41 | 3.22 | 3.32 | 2.96 |
| ev_total_f12 | mean | 16.94 | 15.68 | 16.34 | 15.19 |
| shares_chg_4q | median | 0.9% | 1.5% | 1.2% | 0.5% |
| shares_chg_8q | median | 2.5% | 2.9% | 2.7% | 1.1% |
| shares_change_f12 | median | 1.5% | 2.2% | 1.8% | 0.4% |

### Sector and regime mix (share of the cluster's winners in each bucket)

sector

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| Basic Materials | 7.7% | 6.3% | 7.0% | 5.8% |
| Communication Services | 4.1% | 4.2% | 4.1% | 4.2% |
| Consumer Cyclical | 16.8% | 11.7% | 14.3% | 12.8% |
| Consumer Defensive | 2.3% | 4.2% | 3.3% | 5.1% |
| Energy | 10.5% | 4.9% | 7.8% | 7.1% |
| Financial Services | 9.6% | 5.8% | 7.8% | 15.7% |
| Healthcare | 23.1% | 24.2% | 23.6% | 15.4% |
| Industrials | 12.7% | 13.5% | 13.1% | 14.6% |
| Real Estate | 0.5% | 0.5% | 0.5% | 0.6% |
| Technology | 12.5% | 24.1% | 18.0% | 15.6% |
| Unknown | 0.0% | 0.0% | 0.0% | 0.0% |
| Utilities | 0.4% | 0.6% | 0.5% | 3.2% |

drawdown_bucket

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| 0-10 | 65.1% | 78.2% | 71.4% | 77.3% |
| 10-20 | 12.6% | 11.6% | 12.1% | 13.2% |
| 20-30 | 5.6% | 6.2% | 5.9% | 5.5% |
| >30 | 16.7% | 4.0% | 10.6% | 3.9% |

mst_bucket

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| 0-12 | 89.8% | 81.6% | 85.9% | 80.3% |
| 13-24 | 6.0% | 9.4% | 7.7% | 8.6% |
| >24 | 4.2% | 8.9% | 6.5% | 11.1% |

price_bucket

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| 1 5-10 | 41.7% | 9.4% | 26.2% | 11.3% |
| 2 10-20 | 37.9% | 24.0% | 31.2% | 21.5% |
| 3 20-50 | 18.1% | 39.2% | 28.2% | 38.3% |
| 4 50+ | 2.3% | 27.5% | 14.3% | 29.0% |

profitable

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| False | 59.9% | 33.4% | 47.2% | 23.5% |
| True | 40.1% | 66.6% | 52.8% | 76.4% |

ipo_lt_3y

| bucket | c1 | c2 | all winners | population |
| --- | ---: | ---: | ---: | ---: |
| False | 82.9% | 84.9% | 83.9% | 90.1% |
| True | 17.1% | 15.1% | 16.1% | 9.9% |

### Timeline by cluster (winner median at T+k; population overlay = median over the cluster's winners of the population median at the same calendar month)

c1

| k | price_return W | price_return P | rev_growth_yoy W | rev_growth_yoy P | shares_change W | shares_change P | insider_net_buys_12m W | insider_net_buys_12m P | ev_total_t12 W | ev_total_t12 P |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -24 | 84.2% (91%) | -1.1% | 11.1% (77%) | 10.0% | -2.4% (91%) | -0.7% | 0.0 (75%) | 0.0 | 14.0 (98%) | 13.0 |
| -21 | 79.9% (93%) | -3.1% | 10.3% (79%) | 9.9% | -2.0% (94%) | -0.5% | 1.0 (75%) | 0.0 | 14.0 (98%) | 13.0 |
| -18 | 73.0% (95%) | -0.5% | 9.2% (80%) | 9.2% | -1.6% (96%) | -0.5% | 1.0 (76%) | 0.0 | 14.0 (98%) | 13.0 |
| -15 | 63.1% (97%) | 0.9% | 7.9% (82%) | 8.6% | -1.3% (97%) | -0.4% | 1.0 (77%) | 0.0 | 14.0 (98%) | 13.0 |
| -12 | 55.7% (99%) | 0.4% | 7.1% (84%) | 7.0% | -0.9% (99%) | -0.3% | 1.0 (79%) | 0.0 | 14.0 (99%) | 13.0 |
| -9 | 46.9% (100%) | 2.9% | 5.5% (86%) | 5.2% | -0.6% (100%) | -0.2% | 1.0 (80%) | 0.0 | 15.0 (100%) | 14.0 |
| -6 | 33.8% (100%) | 0.2% | 4.0% (88%) | 4.9% | -0.4% (100%) | -0.2% | 2.0 (81%) | 0.0 | 15.0 (100%) | 14.0 |
| -3 | 13.7% (100%) | -1.4% | 2.2% (90%) | 5.0% | -0.1% (100%) | -0.1% | 2.0 (88%) | 0.0 | 15.0 (100%) | 14.0 |
| +0 | 0.0% (100%) | 0.0% | -1.4% (91%) | 4.6% | 0.0% (100%) | 0.0% | 2.0 (94%) | 1.0 | 15.0 (100%) | 14.0 |
| +3 | 30.8% (100%) | 7.2% | -2.4% (93%) | 3.4% | 0.1% (100%) | 0.1% | 2.0 (97%) | 1.0 | 15.0 (100%) | 14.0 |
| +6 | 67.2% (99%) | 11.4% | -0.2% (93%) | 4.2% | 0.4% (100%) | 0.2% | 2.0 (97%) | 0.0 | 16.0 (100%) | 14.0 |
| +9 | 108.4% (98%) | 17.7% | 5.0% (93%) | 4.8% | 0.9% (100%) | 0.3% | 1.0 (97%) | 0.0 | 15.0 (100%) | 14.0 |
| +12 | 142.2% (95%) | 22.8% | 12.8% (93%) | 6.2% | 1.5% (100%) | 0.5% | 0.0 (97%) | 0.0 | 15.0 (100%) | 14.0 |
| +15 | 149.2% (93%) | 26.5% | 19.0% (93%) | 8.1% | 2.2% (100%) | 0.6% | 0.0 (97%) | 0.0 | 15.0 (100%) | 14.0 |
| +18 | 148.9% (87%) | 28.6% | 20.3% (93%) | 9.0% | 2.8% (100%) | 0.7% | 0.0 (98%) | 0.0 | 14.0 (100%) | 13.0 |
| +21 | 155.0% (84%) | 27.7% | 17.2% (93%) | 9.2% | 3.4% (98%) | 0.8% | 0.0 (98%) | 0.0 | 14.0 (100%) | 13.0 |
| +24 | 156.3% (82%) | 28.4% | 14.7% (91%) | 9.3% | 4.0% (97%) | 0.9% | 0.0 (98%) | 0.0 | 13.0 (100%) | 13.0 |

c2

| k | price_return W | price_return P | rev_growth_yoy W | rev_growth_yoy P | shares_change W | shares_change P | insider_net_buys_12m W | insider_net_buys_12m P | ev_total_t12 W | ev_total_t12 P |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| -24 | -30.0% (92%) | -13.0% | 13.6% (81%) | 9.9% | -2.8% (93%) | -0.8% | 0.0 (81%) | 0.0 | 12.0 (92%) | 13.0 |
| -21 | -28.5% (94%) | -9.8% | 13.5% (83%) | 10.0% | -2.4% (94%) | -0.6% | 0.0 (82%) | 0.0 | 12.0 (93%) | 13.0 |
| -18 | -28.5% (96%) | -9.0% | 13.4% (84%) | 9.2% | -2.1% (96%) | -0.5% | 0.0 (84%) | 0.0 | 12.0 (94%) | 13.0 |
| -15 | -27.8% (97%) | -7.6% | 12.4% (86%) | 8.6% | -1.7% (98%) | -0.5% | 0.0 (85%) | 0.0 | 13.0 (96%) | 13.0 |
| -12 | -25.0% (99%) | -8.6% | 11.6% (88%) | 7.0% | -1.4% (99%) | -0.4% | 1.0 (87%) | 0.0 | 13.0 (98%) | 13.0 |
| -9 | -20.3% (100%) | -5.8% | 11.8% (90%) | 5.3% | -1.0% (100%) | -0.3% | 1.0 (88%) | 0.0 | 13.0 (99%) | 13.0 |
| -6 | -15.5% (100%) | -3.9% | 12.5% (91%) | 5.1% | -0.6% (100%) | -0.2% | 1.0 (88%) | 0.0 | 13.0 (100%) | 14.0 |
| -3 | -8.6% (100%) | -2.7% | 13.9% (93%) | 5.1% | -0.2% (100%) | -0.1% | 0.0 (90%) | 0.0 | 13.0 (100%) | 14.0 |
| +0 | 0.0% (100%) | 0.0% | 15.9% (94%) | 5.0% | 0.0% (100%) | 0.0% | 0.0 (91%) | 0.0 | 13.0 (100%) | 14.0 |
| +3 | 25.6% (100%) | 4.9% | 17.5% (96%) | 5.0% | 0.2% (100%) | 0.1% | 0.0 (92%) | 0.0 | 13.0 (100%) | 14.0 |
| +6 | 56.3% (99%) | 8.4% | 19.9% (96%) | 5.4% | 0.8% (100%) | 0.2% | 0.0 (92%) | 0.0 | 14.0 (100%) | 14.0 |
| +9 | 92.6% (98%) | 12.2% | 23.7% (96%) | 6.0% | 1.4% (100%) | 0.3% | 0.0 (92%) | 0.0 | 14.0 (100%) | 14.0 |
| +12 | 130.5% (96%) | 14.9% | 26.9% (96%) | 6.4% | 2.2% (100%) | 0.4% | 0.0 (92%) | 0.0 | 14.0 (100%) | 14.0 |
| +15 | 137.1% (94%) | 16.5% | 28.8% (96%) | 7.6% | 3.0% (100%) | 0.5% | 0.0 (92%) | 0.0 | 14.0 (100%) | 14.0 |
| +18 | 136.2% (88%) | 17.5% | 27.4% (96%) | 8.0% | 3.6% (100%) | 0.6% | 0.0 (93%) | 0.0 | 13.0 (100%) | 13.0 |
| +21 | 129.5% (85%) | 21.3% | 24.1% (96%) | 8.0% | 4.1% (99%) | 0.7% | 0.0 (94%) | 0.0 | 13.0 (100%) | 13.0 |
| +24 | 122.1% (83%) | 20.1% | 20.9% (94%) | 7.8% | 4.5% (97%) | 0.8% | 0.0 (95%) | 0.0 | 12.0 (100%) | 13.0 |


## Reading

This describes what the algorithms found. It names each cluster, gives the two or three fields that most distinguish it, and says which kinds of field carry it. No recommendation is made.

### What the algorithms found

For both labels the silhouette peaks at k = 2 and is small: 0.083 for launch_300 and 0.085 for win_100, falling to 0.045 to 0.050 at k = 6. A silhouette near zero means the winners do not sit in separated groups; k-means is cutting a continuum. HDBSCAN, which looks for density rather than cutting, finds no cluster at all at its default setting for either label, and no cluster at any looser setting for win_100. For launch_300 the two loosest settings find two small clusters (328 and 75 winners, then 508 and 60) with 87 to 91% of winners left as noise and an adjusted Rand index against the k-means split of 0.003 to 0.005, so they are not the k-means types seen again. At k = 4 and above, k-means also splits off outlier clusters of 22 (launch_300) and 5 (win_100) winners. The honest summary is that winners form one population stretched along a single axis, not a set of types. The two k-means halves are the two ends of that axis, and the description below is of the ends, not of separated groups.

### The axis and its two ends

The fields that separate the two halves are the same for both labels and in the same order: drawdown from the three-year high (about 1.35 standard deviations between the cluster means), the GROWTH-002 rank of distance from the 52-week high (1.3), the twelve- and six-month momentum ranks (1.1 to 1.3), distance above the 30-week average (1.0 to 1.1), months since the three-year low (1.0), the price-to-book rank (1.0), price (1.0), realized volatility (0.8 to 0.9) and market cap (0.8). Fundamentals follow behind: the revenue-growth streak, operating-margin change, net debt, cash and quarters since the last loss all sit at 0.4 to 0.5. 8-K counts and 13F level separate almost nothing.

Cluster 1, the larger half in both labels, is the crashed end. For launch_300 (2,209 winners, 51%) its median winner is 74% below its three-year high, three months from its three-year low, at 79% realized volatility, priced at $9.20 with a $523 million market cap, with revenue shrinking 2% a year, a 3% operating loss, net debt at 35% of market cap and cash at 17%, and insiders buying (mean 10.8 net buy rows against 5.8 for the population). Its momentum ranks are near the bottom (0.09 to 0.12). It leans to Energy (13% against 7%), Consumer Cyclical (18%) and Basic Materials (8%), and 23% of it sits in SPY drawdowns over 30% against 4% of the population. Its timeline is a collapse and a rebound: the median winner's price at T-24 was 134% above its T-0 price, so it lost more than half its value in the two years before the move, while revenue growth fell from 11% to −2%; after T-0 revenue growth is still negative at T+6 and recovers to 28% by T+24. The win_100 cluster 1 (10,617 winners, 52%) is the same shape at 65% below the high, four months from the low, 71% volatility, $11.42, $620 million, revenue −1%, net debt 35% of market cap, and 17% in deep SPY drawdowns.

Cluster 2 is the strong end. For launch_300 (2,092 winners, 49%) its median winner is 27% below its three-year high, 25 months from the low, at 55% volatility, priced at $22.77 with a $1.4 billion market cap, growing revenue 17% a year with a three-quarter growth streak, 48% gross margin, R&D at 10% of revenue, no net debt, and momentum ranks near the top (0.74 to 0.76). It leans to Technology (26% against 16%) and Healthcare (28%), is 52% profitable against 31% for cluster 1, and sits in calm markets (73% in the 0 to 10% SPY bucket). Its timeline is a pullback inside an uptrend: the price at T-24 was 27% below the T-0 price, so it rose over the two years before the move, and revenue growth runs 13 to 17% throughout, reaching 35% at T+24. The win_100 cluster 2 (9,750 winners, 48%) matches: 22% below the high, 26 months from the low, 50% volatility, $28.80, $1.75 billion, revenue growth 16%, 67% profitable, momentum ranks 0.73 to 0.76.

### Rough lift

Assigning every population row to its nearest centroid puts 19% of launch_300 population rows and 26% of win_100 rows in cluster 1, against 51 to 52% of winners, a rough lift of 2.7 (launch_300) and 2.0 (win_100); the winner rate inside cluster 1 is 2.2% against a 0.8% base for launch_300 and 7.3% against 3.7% for win_100. Cluster 2 holds 74 to 81% of population rows and 48 to 49% of winners, a lift of 0.60 to 0.65. Section 3.5 of reports/anatomy_tables.md already showed that the fields carrying cluster 1 (drawdown, volatility, small size, losses) raise the loss_50 rate more than the win_100 rate, so the lift of cluster 1 is a lift in both directions and is not a return expectation.

### Which kind of field carries each type

Cluster 1 is mostly regime and size-volatility. Its defining fields are the stock's own drawdown and volatility, its price and size, and the market's drawdown at T-0; its fundamental fingerprint is distress (losses, debt, shrinking revenue, insider buying into the fall) rather than a growth pattern. Cluster 2 is mostly momentum and size, with a fundamental fingerprint of growth: revenue growing in the mid teens with a streak, high gross margin, R&D spend, no net debt. Neither is a regime-only type: the SPY drawdown bucket tilts cluster 1 but 59 to 65% of cluster 1 still sits in calm markets. No cluster has an 8-K fingerprint; the item counts before T-0 are within 0.3 filings a year of each other across clusters and the population.

### Names

Cluster 1, both labels: "the crash rebound", distinguished by drawdown from the three-year high, months since the three-year low, and realized volatility. Cluster 2, both labels: "the pullback in an uptrend", distinguished by the twelve-month momentum rank, revenue growth, and distance above the 30-week average. These are the two ends of one axis, not two populations.
