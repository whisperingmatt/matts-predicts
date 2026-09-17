"""Spec section 10 — point-in-time join guard. Written before features.py ran.

For a known ticker and decision date, the fundamentals row a feature uses
must be filed (fundamentals.date, the spec's datekey) on or before that
date, and must be the latest such filing. The known case: AAPL's quarter
ending 2019-06-30 was filed 2019-07-31. On 2019-07-30 the feature must
still see the 2019-03-31 quarter; on 2019-07-31 it must see 2019-06-30.

The tests run the same function the pipeline runs
(features.compute_fundamental_features) on a two-row grid, so they test the
code path, not a re-implementation. They need data/raw/fundamentals.parquet
(run src/fetch_bulk.py and src/ingest.py first) and skip without it.
"""
from __future__ import annotations

import datetime as dt

import duckdb
import pytest

from src.config import RAW_DIR
from src import features

FUND = RAW_DIR / "fundamentals.parquet"
TICKER = "AAPL"
QUARTER = dt.date(2019, 6, 30)
KNOWN_FILED = dt.date(2019, 7, 31)
PRIOR_QUARTER = dt.date(2019, 3, 31)

pytestmark = pytest.mark.skipif(not FUND.exists(), reason="fundamentals.parquet not ingested")


@pytest.fixture(scope="module")
def con():
    con = duckdb.connect()
    features.build_arq(con, tickers=[TICKER])
    con.execute("CREATE TABLE grid AS SELECT * FROM (VALUES "
                f"('{TICKER}', DATE '{KNOWN_FILED - dt.timedelta(days=1)}', DATE '{KNOWN_FILED - dt.timedelta(days=1)}'),"
                f"('{TICKER}', DATE '{KNOWN_FILED}', DATE '{KNOWN_FILED}')"
                ") t(ticker, month_end, trade_date)")
    features.compute_fundamental_features(con, grid="grid")
    return con


def test_known_filing_date_is_in_the_data(con):
    filed = con.execute(
        "SELECT filed FROM arq WHERE ticker = ? AND calendardate = ?", [TICKER, QUARTER]).fetchone()
    assert filed is not None and filed[0] == KNOWN_FILED


def test_day_before_filing_uses_prior_quarter(con):
    row = con.execute("""
        SELECT fund_calendardate, fund_filed, eps_q0 FROM fund_feat
        WHERE ticker = ? AND month_end = ?""", [TICKER, KNOWN_FILED - dt.timedelta(days=1)]).fetchone()
    assert row[0] == PRIOR_QUARTER
    assert row[1] <= KNOWN_FILED - dt.timedelta(days=1)
    expected_eps = con.execute("SELECT eps FROM arq WHERE ticker = ? AND calendardate = ?",
                               [TICKER, PRIOR_QUARTER]).fetchone()[0]
    assert row[2] == expected_eps


def test_filing_day_uses_new_quarter(con):
    row = con.execute("""
        SELECT fund_calendardate, fund_filed, eps_q0 FROM fund_feat
        WHERE ticker = ? AND month_end = ?""", [TICKER, KNOWN_FILED]).fetchone()
    assert row[0] == QUARTER
    assert row[1] == KNOWN_FILED
    expected_eps = con.execute("SELECT eps FROM arq WHERE ticker = ? AND calendardate = ?",
                               [TICKER, QUARTER]).fetchone()[0]
    assert row[2] == expected_eps


def test_no_feature_row_uses_a_later_filing(con):
    # Every quarter the feature relies on (q0 through q8) was filed on or before the decision date.
    bad = con.execute("""
        SELECT count(*) FROM fund_feat
        WHERE fund_filed > month_end OR fund_filed_q8 > month_end""").fetchone()[0]
    assert bad == 0
