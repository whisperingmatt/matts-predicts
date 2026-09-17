# S3 feature coverage — build window 2006-01 to 2019-12, universe rows

Source: src/features.py over data/processed/features.parquet. Cell = percent of universe
rows whose flag is non-null (data sufficient). Nulls are never filled.

## Availability

- h1_eps_accel: available
- h4_op_leverage: available
- h5_peg_lt_1: available
- h5_peg_lt_05: available
- h6_compressed_multiple: available
- h7_neglect: available
- h8_fcf_divergence: available
- h9_rs6_top_decile: available
- h9_rs12_top_decile: available
- h10_sponsorship: available (holdings from 2013-06-30)
- h11_insider_cluster: available (insiders from 2008-01-02)
- h12_short_fuel: UNAVAILABLE — no short-interest field in Sharadar
- h13_stage2: available
- h14_vol_contraction: available
- h15_near_high: available
- h16_sector_flow: UNAVAILABLE — no ETF shares-outstanding field in Sharadar (funds is OHLCV only)
- h2_surprise_streak: DEFERRED (D7)
- h3_estimate_revisions: DEFERRED (D7)
- h17_sector_surprise: DEFERRED
- h18_attention: DEFERRED
- h20_leverage_ok: available
- h21_no_dilution: available
- ctl_pe_lt_15: available
- ctl_pb_lt_15: available
- ctl_divyield_gt_2: available

## Non-null percent per flag per year, lag 0

| year | rows | h1_eps_accel | h4_op_leverage | h5_peg_lt_1 | h5_peg_lt_05 | h6_cmult | h7_neglect | h8_fcf_divergence | h9_rs6 | h9_rs12 | h10_sponsorship | h11_insider_cluster | h12_short_fuel | h13_stage2 | h14_volc | h15_near_high | h16_sector_flow | h2_surprise_streak | h3_estimate_revisions | h17_sector_surprise | h18_attention | h20_leverage_ok | h21_no_dilution | ctl_pe_lt_15 | ctl_pb_lt_15 | ctl_divyield_gt_2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2006 | 30,752 | 68.9 | 92.3 | 51.3 | 51.3 | 67.2 | 99.7 | 97.4 | 99.9 | 98.8 | 0.0 | 0.0 | 0.0 | 99.8 | 100.0 | 99.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.4 | 93.2 | 85.5 | 97.6 | 100.0 |
| 2007 | 31,216 | 68.4 | 91.3 | 48.9 | 48.9 | 65.4 | 99.5 | 97.2 | 99.8 | 98.8 | 0.0 | 0.0 | 0.0 | 99.8 | 99.9 | 99.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.4 | 92.1 | 84.6 | 97.1 | 100.0 |
| 2008 | 27,861 | 72.3 | 90.6 | 45.2 | 45.2 | 65.9 | 99.7 | 97.3 | 99.9 | 98.7 | 0.0 | 73.7 | 0.0 | 99.9 | 100.0 | 99.1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.6 | 91.4 | 85.0 | 97.7 | 100.0 |
| 2009 | 24,501 | 71.6 | 93.6 | 31.1 | 31.1 | 58.3 | 99.8 | 98.9 | 99.9 | 99.6 | 0.0 | 100.0 | 0.0 | 99.9 | 100.0 | 99.7 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.8 | 94.6 | 74.5 | 97.2 | 100.0 |
| 2010 | 26,486 | 53.7 | 94.9 | 34.6 | 34.6 | 56.2 | 99.7 | 98.8 | 99.9 | 99.3 | 0.0 | 100.0 | 0.0 | 99.9 | 100.0 | 99.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.8 | 97.7 | 79.0 | 97.0 | 100.0 |
| 2011 | 26,564 | 62.7 | 94.3 | 50.8 | 50.8 | 67.7 | 99.7 | 98.4 | 100.0 | 99.3 | 0.0 | 100.0 | 0.0 | 100.0 | 100.0 | 99.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.7 | 96.2 | 84.6 | 97.2 | 100.0 |
| 2012 | 25,569 | 68.9 | 94.3 | 48.9 | 48.9 | 70.7 | 99.7 | 98.4 | 99.9 | 99.2 | 0.0 | 100.0 | 0.0 | 99.9 | 100.0 | 99.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.8 | 95.9 | 85.3 | 97.4 | 100.0 |
| 2013 | 27,212 | 66.1 | 93.7 | 44.3 | 44.3 | 67.2 | 99.7 | 98.2 | 99.9 | 99.1 | 16.6 | 100.0 | 0.0 | 99.9 | 100.0 | 99.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.8 | 95.4 | 81.2 | 97.1 | 100.0 |
| 2014 | 28,980 | 63.5 | 92.4 | 44.2 | 44.2 | 64.2 | 99.8 | 97.4 | 99.9 | 98.6 | 95.1 | 100.0 | 0.0 | 99.8 | 100.0 | 99.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.6 | 94.1 | 79.9 | 96.9 | 100.0 |
| 2015 | 29,363 | 63.8 | 90.7 | 42.5 | 42.5 | 62.5 | 99.7 | 97.1 | 99.9 | 98.5 | 95.2 | 100.0 | 0.0 | 99.9 | 100.0 | 99.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.7 | 92.3 | 78.7 | 96.6 | 100.0 |
| 2016 | 28,677 | 62.7 | 92.2 | 38.6 | 38.6 | 59.4 | 99.6 | 98.0 | 100.0 | 99.0 | 96.3 | 100.0 | 0.0 | 100.0 | 100.0 | 99.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.7 | 94.0 | 75.0 | 95.5 | 100.0 |
| 2017 | 29,081 | 59.7 | 92.8 | 42.5 | 42.5 | 59.1 | 99.6 | 98.2 | 99.9 | 99.1 | 95.6 | 100.0 | 0.0 | 99.9 | 100.0 | 99.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.6 | 95.3 | 76.1 | 95.2 | 100.0 |
| 2018 | 29,085 | 59.8 | 91.6 | 42.8 | 42.8 | 58.9 | 99.7 | 97.9 | 99.9 | 99.0 | 95.6 | 100.0 | 0.0 | 99.9 | 100.0 | 99.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.7 | 95.0 | 74.9 | 95.3 | 100.0 |
| 2019 | 28,082 | 54.5 | 91.0 | 41.3 | 41.3 | 59.5 | 99.7 | 97.7 | 99.9 | 98.8 | 96.0 | 100.0 | 0.0 | 99.9 | 100.0 | 99.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.7 | 94.6 | 75.6 | 95.4 | 100.0 |

## Non-null percent per flag per lag, build window overall

| lag | rows | h1_eps_accel | h4_op_leverage | h5_peg_lt_1 | h5_peg_lt_05 | h6_cmult | h7_neglect | h8_fcf_divergence | h9_rs6 | h9_rs12 | h10_sponsorship | h11_insider_cluster | h12_short_fuel | h13_stage2 | h14_volc | h15_near_high | h16_sector_flow | h2_surprise_streak | h3_estimate_revisions | h17_sector_surprise | h18_attention | h20_leverage_ok | h21_no_dilution | ctl_pe_lt_15 | ctl_pb_lt_15 | ctl_divyield_gt_2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 393,429 | 64.0 | 92.5 | 43.5 | 43.5 | 63.0 | 99.7 | 97.9 | 99.9 | 99.0 | 43.3 | 82.4 | 0.0 | 99.9 | 100.0 | 99.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.7 | 94.4 | 80.0 | 96.6 | 100.0 |
| 3 | 393,429 | 63.4 | 91.3 | 43.6 | 43.6 | 62.5 | 100.0 | 96.6 | 92.0 | 91.2 | 41.4 | 80.5 | 0.0 | 99.6 | 99.9 | 98.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 99.1 | 93.1 | 80.1 | 96.9 | 99.9 |
| 6 | 393,429 | 62.9 | 90.1 | 43.3 | 43.3 | 61.9 | 99.9 | 95.3 | 87.7 | 87.0 | 39.3 | 78.7 | 0.0 | 98.8 | 99.8 | 97.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 98.5 | 91.9 | 79.9 | 96.8 | 99.9 |
| 12 | 393,429 | 61.7 | 87.9 | 42.6 | 42.6 | 60.8 | 99.2 | 92.8 | 80.6 | 79.9 | 35.0 | 75.3 | 0.0 | 96.5 | 98.3 | 94.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 96.8 | 89.6 | 79.1 | 95.8 | 98.7 |

## Percent TRUE among non-null, lag 0, build window (context only, no lifts here)

| h1_eps_accel | h4_op_leverage | h5_peg_lt_1 | h5_peg_lt_05 | h6_cmult | h7_neglect | h8_fcf_divergence | h9_rs6 | h9_rs12 | h10_sponsorship | h11_insider_cluster | h12_short_fuel | h13_stage2 | h14_volc | h15_near_high | h16_sector_flow | h2_surprise_streak | h3_estimate_revisions | h17_sector_surprise | h18_attention | h20_leverage_ok | h21_no_dilution | ctl_pe_lt_15 | ctl_pb_lt_15 | ctl_divyield_gt_2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10.1 | 6.9 | 62.7 | 42.2 | 22.6 | 54.6 | 11.9 | 10.0 | 10.0 | 4.8 | 4.0 | n/a | 2.5 | 9.8 | 51.9 | n/a | n/a | n/a | n/a | n/a | 61.3 | 56.3 | 30.4 | 24.0 | 25.2 |
