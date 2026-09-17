# S2 base rates — build window 2006-01 to 2019-12

Source: src/labels.py over data/processed/universe.parquet and data/raw/stocks.parquet.
A row is one (ticker, month_end) in the universe. A launch is fwd_24m_return >= 300%
(D1); the 200% and 500% flags are alongside. Delist is terminal: the last available
closeadj stands in for close(t+24m).

| year | universe rows | launch_300 | rate_300 | launch_200 | rate_200 | launch_500 | rate_500 | delisted by t+24 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2006 | 30,752 | 86 | 0.28% | 198 | 0.64% | 21 | 0.07% | 4,062 |
| 2007 | 31,216 | 5 | 0.02% | 24 | 0.08% | 0 | 0.00% | 3,305 |
| 2008 | 27,861 | 164 | 0.59% | 491 | 1.76% | 22 | 0.08% | 1,960 |
| 2009 | 24,501 | 561 | 2.29% | 1,540 | 6.29% | 113 | 0.46% | 1,875 |
| 2010 | 26,486 | 101 | 0.38% | 362 | 1.37% | 34 | 0.13% | 2,487 |
| 2011 | 26,564 | 126 | 0.47% | 439 | 1.65% | 41 | 0.15% | 2,205 |
| 2012 | 25,569 | 180 | 0.70% | 604 | 2.36% | 46 | 0.18% | 2,057 |
| 2013 | 27,212 | 111 | 0.41% | 389 | 1.43% | 23 | 0.08% | 2,304 |
| 2014 | 28,980 | 35 | 0.12% | 125 | 0.43% | 3 | 0.01% | 2,810 |
| 2015 | 29,363 | 76 | 0.26% | 239 | 0.81% | 17 | 0.06% | 3,177 |
| 2016 | 28,677 | 274 | 0.96% | 737 | 2.57% | 60 | 0.21% | 3,038 |
| 2017 | 29,081 | 107 | 0.37% | 376 | 1.29% | 16 | 0.06% | 3,068 |
| 2018 | 29,085 | 176 | 0.61% | 477 | 1.64% | 47 | 0.16% | 2,817 |
| 2019 | 28,082 | 601 | 2.14% | 1,407 | 5.01% | 186 | 0.66% | 2,295 |
| **overall** | 393,429 | 2,603 | 0.66% | 7,408 | 1.88% | 629 | 0.16% | 37,460 |

Distinct tickers in the build-window universe: 6,168. Distinct tickers with at least
one launch_300 row: 576.

Validity gate (spec section 7): overall rate_300 0.66% must lie in [0.50%, 5.00%].
