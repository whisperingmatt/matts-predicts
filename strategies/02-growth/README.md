# Section 2 Growth — multibagger pattern-mining study

Historical study of which signals preceded 300%+ two-year moves
("launches") in US equities, 2006–2019 build window, 2020–2026 holdout,
using Sharadar data via Nasdaq Data Link. Every rule, threshold, and
pass/fail criterion is fixed in the locked spec at
`../../specs/GROWTH-001-multibagger-pattern-mining.md`; this directory
only implements it. Set `NASDAQ_DATA_LINK_API_KEY` in the environment,
install `requirements.txt` into a Python 3.11 virtualenv, and run
`python -m src.sharadar_check` from this directory before anything else.
