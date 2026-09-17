"""S1 gate — Sharadar authentication test and table-name verification.

Run from strategies/02-growth/:

    NASDAQ_DATA_LINK_API_KEY=... python -m src.sharadar_check

For each table in D6 (plus SP500, needed for H16) it requests a handful of
rows for one ticker, reports whether the request succeeded, prints the
columns returned, and checks that the columns the spec's features depend on
are present. Exit code 0 only if every table returns at least one row and no
required column is missing. The key is never printed.
"""
from __future__ import annotations

import os
import sys

from src.config import API_KEY_ENV

# One small filtered query per table. Filters chosen so each returns a few rows.
QUERIES: dict[str, dict] = {
    "TICKERS": {"ticker": "AAPL"},
    "SF1": {"ticker": "AAPL", "dimension": "ARQ", "calendardate": "2019-12-31"},
    "SEP": {"ticker": "AAPL", "date": "2019-12-31"},
    "DAILY": {"ticker": "AAPL", "date": "2019-12-31"},
    "SF2": {"ticker": "AAPL", "filingdate": {"gte": "2019-01-01", "lte": "2019-12-31"}},
    "SF3": {"ticker": "AAPL", "calendardate": "2019-12-31", "securitytype": "SHR"},
    "SP500": {"ticker": "AAPL"},
}

# Columns each spec feature depends on. Names are Nasdaq Data Link names
# (datekey, filingdate), not the newer api.sharadar.com names (date).
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "TICKERS": ["ticker", "permaticker", "exchange", "category", "isdelisted",
                "sector", "industry", "firstpricedate", "lastpricedate"],
    "SF1": ["ticker", "dimension", "calendardate", "datekey", "reportperiod",
            "revenue", "opinc", "eps", "fcf", "fcfps", "sharesbas", "debt",
            "cashneq", "ebitda", "pe", "pb", "divyield", "marketcap", "price"],
    "SEP": ["ticker", "date", "close", "closeadj", "volume"],
    "DAILY": ["ticker", "date", "marketcap", "pe", "pb", "ev"],
    "SF2": ["ticker", "filingdate", "transactiondate", "transactioncode",
            "ownername", "transactionshares"],
    "SF3": ["ticker", "investorname", "securitytype", "calendardate", "value", "units"],
    "SP500": ["date", "action", "ticker"],
}

# Fields the spec asks for that Sharadar does not carry. Reported, not substituted.
KNOWN_GAPS = {
    "DAILY": "no short-interest field — H12 short_fuel is UNAVAILABLE",
    "TICKERS": "no analyst-count field — H7 records marketcap only",
}


def main() -> int:
    key = os.environ.get(API_KEY_ENV)
    if not key:
        print(f"FAIL: environment variable {API_KEY_ENV} is not set. Nothing was queried.")
        return 1

    import nasdaqdatalink  # imported late so the missing-key message is clean

    nasdaqdatalink.ApiConfig.api_key = key
    all_ok = True
    for table, filters in QUERIES.items():
        name = f"SHARADAR/{table}"
        try:
            df = nasdaqdatalink.get_table(name, paginate=False, qopts={"per_page": 5}, **filters)
        except Exception as exc:  # noqa: BLE001 — report every failure mode verbatim
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
            all_ok = False
            continue
        rows = len(df)
        cols = list(df.columns)
        missing = [c for c in REQUIRED_COLUMNS[table] if c not in cols]
        status = "OK" if rows > 0 and not missing else "FAIL"
        if status == "FAIL":
            all_ok = False
        print(f"{status} {name}: {rows} rows, {len(cols)} columns")
        print(f"     columns: {', '.join(cols)}")
        if missing:
            print(f"     MISSING required columns: {', '.join(missing)}")
        if table in KNOWN_GAPS:
            print(f"     known gap: {KNOWN_GAPS[table]}")

    print("RESULT:", "PASS — all tables reachable, all required columns present" if all_ok
          else "FAIL — see lines above")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
