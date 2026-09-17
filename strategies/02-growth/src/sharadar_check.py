"""S1 gate — Sharadar authentication test and table-name verification.

Calls the Sharadar direct API (api.sharadar.com), not Nasdaq Data Link.
See decisions.md, 2026-09-17 "D6 superseded" entry, for the table and
column name mapping.

Run from strategies/02-growth/ with the key in the environment:

    SHARADAR_API_KEY=... python -m src.sharadar_check

Request format, verified against sharadar.com/docs/getting-started and
each table's docs page on 2026-09-17:

    https://api.sharadar.com/v1.0/data/<table>?api_key=<key>&<filters>

    format=json returns {"count": N, "data": [ {column: value, ...}, ... ]}
    from= / to= bound the table's date column (filing date on fundamentals
    and insiders, trade date on stocks and daily, quarter-end on holdings,
    action date on sp500). They default to one year ago and yesterday.
    Other columns filter with =, .gt=, .gte=, .lt=, .lte=. limit= caps rows.

Why every probe below asks for 2006-2013 data: the API serves the trailing
year for any ticker with a bad key, or no key at all (verified 2026-09-17
against stocks and tickers for AAPL and MSFT). Only rows older than that
prove the key was accepted and the subscription covers the table. tickers
has no date column, so it can only prove the table and columns exist.

Exit code 0 only if every table returns at least one row and no required
column is missing. The key is never printed; it is redacted from any
exception text before printing.
"""
from __future__ import annotations

import json
import os
import sys

import requests

from src.config import API_KEY_ENV, API_KEY_ENV_FALLBACK, SHARADAR_API_BASE, TABLES

TICKER = "MSFT"  # not AAPL: AAPL is the public sample and proves nothing

# One small filtered query per table, in a window inside the build window
# (D4: 2006-01 onward) or the table's own history start where later
# (insiders 2008-01, holdings 2013-06). Keys are direct-API table names.
QUERIES: dict[str, dict[str, str]] = {
    "tickers": {"ticker": TICKER},
    "fundamentals": {"ticker": TICKER, "dimension": "ARQ",
                     "from": "2006-01-01", "to": "2006-06-30"},
    "stocks": {"ticker": TICKER, "from": "2006-01-03", "to": "2006-01-10"},
    "daily": {"ticker": TICKER, "from": "2006-01-03", "to": "2006-01-10"},
    "insiders": {"ticker": TICKER, "from": "2008-07-01", "to": "2008-12-31"},
    "holdings": {"ticker": TICKER, "securitytype": "SHR",
                 "from": "2013-07-01", "to": "2013-12-31"},
    "sp500": {"ticker": TICKER, "from": "2006-01-01", "to": "2006-06-30"},
}

# Columns each spec feature depends on, in direct-API names. Where the spec
# or the NDL feed used a different name, the NDL name is in the comment.
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "tickers": ["ticker", "permaticker", "table", "exchange", "category", "isdelisted",
                "sector", "industry", "firstpricedate", "lastpricedate"],
    "fundamentals": ["ticker", "dimension", "calendardate",
                     "date",  # NDL SF1: datekey (filing date, D2)
                     "reportperiod", "revenue", "opinc", "eps", "fcf", "fcfps",
                     "sharesbas", "debt", "cashneq", "ebitda", "pe", "pb", "divyield",
                     "marketcap", "price"],
    "stocks": ["ticker", "date", "close", "closeadj", "volume"],
    "daily": ["ticker", "date", "marketcap", "pe", "pb", "ev"],
    "insiders": ["ticker",
                 "date",  # NDL SF2: filingdate
                 "transactiondate", "transactioncode", "ownername", "transactionshares"],
    "holdings": ["ticker",
                 "investorid",  # NDL SF3: investorname (no name column here)
                 "securitytype",
                 "date",  # NDL SF3: calendardate
                 "value", "units"],
    "sp500": ["date", "action", "ticker"],
}

# Fields the spec asks for that Sharadar does not carry. Reported, not substituted.
KNOWN_GAPS = {
    "daily": "no short-interest field — H12 short_fuel is UNAVAILABLE",
    "tickers": "no analyst-count field — H7 records marketcap only",
}


def redact(text: str, key: str) -> str:
    return text.replace(key, "<api_key>") if key else text


def fetch(table: str, filters: dict[str, str], key: str) -> tuple[int, list[str], str]:
    """Return (row_count, columns, note). Raises on transport or non-JSON errors."""
    params = {"api_key": key, "format": "json", "limit": "5", **filters}
    resp = requests.get(f"{SHARADAR_API_BASE}/{table}", params=params, timeout=60)
    try:
        body = resp.json()
    except json.JSONDecodeError:
        raise RuntimeError(f"HTTP {resp.status_code}, non-JSON body: {resp.text[:200]!r}")
    if resp.status_code != 200 or "error" in body:
        raise RuntimeError(f"HTTP {resp.status_code}: {json.dumps(body)[:300]}")
    rows = body.get("data", [])
    cols = list(rows[0].keys()) if rows else []
    note = ""
    if not rows and table != "tickers":
        note = ("0 rows in a historical window — key not accepted, or the "
                "subscription does not include this table or this history")
    return len(rows), cols, note


def main() -> int:
    key = os.environ.get(API_KEY_ENV)
    key_source = API_KEY_ENV
    if not key:
        key = os.environ.get(API_KEY_ENV_FALLBACK)
        key_source = API_KEY_ENV_FALLBACK
    if not key:
        print(f"FAIL: neither {API_KEY_ENV} nor {API_KEY_ENV_FALLBACK} is set. "
              "Nothing was queried.")
        return 1
    print(f"key source: environment variable {key_source} (value not shown)")
    print(f"endpoint: {SHARADAR_API_BASE}/<table>   probe ticker: {TICKER}")

    all_ok = True
    for table in TABLES:
        filters = QUERIES[table]
        try:
            rows, cols, note = fetch(table, filters, key)
        except Exception as exc:  # noqa: BLE001 — report every failure mode verbatim
            print(f"FAIL {table}: {type(exc).__name__}: {redact(str(exc), key)}")
            all_ok = False
            continue
        missing = [c for c in REQUIRED_COLUMNS[table] if c not in cols]
        status = "OK" if rows > 0 and not missing else "FAIL"
        if status == "FAIL":
            all_ok = False
        window = (f"{filters['from']}..{filters['to']}" if "from" in filters else "no date filter")
        print(f"{status} {table}: {rows} rows, {len(cols)} columns ({window})")
        if cols:
            print(f"     columns: {', '.join(cols)}")
        if note:
            print(f"     {note}")
        if missing:
            print(f"     MISSING required columns: {', '.join(missing)}")
        if table in KNOWN_GAPS:
            print(f"     known gap: {KNOWN_GAPS[table]}")

    print("RESULT:", "PASS — all tables reachable with history, all required columns present"
          if all_ok else "FAIL — see lines above")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
