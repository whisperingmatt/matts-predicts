"""S2 — Monthly universe per spec section 3 and D3 floors.

Output: data/processed/universe.parquet, one row per (ticker, month_end)
that qualifies, for every month end from BUILD_START to HOLDOUT_END.

    python -m src.universe

Rules as implemented (decisions.md 2026-09-17 "Universe rules mapping"):

* Membership from the tickers table's price-table row ("table" = SEP; the
  bulk file uses legacy codes, the paged API says stocks). category in
  {Domestic Common Stock, Domestic Common Stock Primary Class}; exchange in
  {NYSE, NASDAQ, NYSEMKT}. ADRs, Canadian, preferred, CEF, ETF are other
  categories and drop out. SPACs are industry = 'Shell Companies'. REITs are
  industry starting 'REIT'. Secondary share classes are excluded so one
  issuer is one launch. category, exchange, and industry are the current
  values in the securities master; Sharadar keeps no history for them.
* Decision date = calendar month end; the row uses the ticker's last trade
  on or before it in that month.
* D3 floors on that trade date: closeunadj >= MIN_PRICE (the price actually
  traded, not split-adjusted), and the mean of close*volume over the
  trailing 20 trading days >= MIN_AVG_DOLLAR_VOLUME_20D (both split
  adjusted; the product is invariant). Fewer than 20 prior trading days
  disqualifies the month.
* EPS history: at least four distinct fiscal quarters (calendardate) with a
  non-null eps in fundamentals dimension ARQ, filed (fundamentals.date, the
  spec's datekey) on or before the decision date, with quarter ends inside
  the trailing 16 months. 12 months of quarter ends plus one quarter of
  filing lag, so a 10-K filed up to 90 days after year end still counts.
* Delisted tickers are kept. The script stops with exit 1 if the price
  table carries no delisted ticker (spec section 3).

Every printed number comes from the SQL below.
"""
from __future__ import annotations

import sys

import duckdb

from src.config import (BUILD_END, BUILD_START, HOLDOUT_END, MIN_AVG_DOLLAR_VOLUME_20D,
                        MIN_PRICE, PROCESSED_DIR, RAW_DIR)

EPS_WINDOW_MONTHS = 16
EPS_MIN_QUARTERS = 4
INCLUDED_CATEGORIES = ("Domestic Common Stock", "Domestic Common Stock Primary Class")
INCLUDED_EXCHANGES = ("NYSE", "NASDAQ", "NYSEMKT")
SPAC_INDUSTRY = "Shell Companies"
REIT_INDUSTRY_PREFIX = "REIT"


def connect() -> duckdb.DuckDBPyConnection:
    tmp = PROCESSED_DIR / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute("SET memory_limit = '10GB'")
    con.execute("SET preserve_insertion_order = false")
    return con


def main() -> int:
    con = connect()
    stocks = f"read_parquet('{(RAW_DIR / 'stocks.parquet').as_posix()}')"
    tickers = f"read_parquet('{(RAW_DIR / 'tickers.parquet').as_posix()}')"
    fundamentals = f"read_parquet('{(RAW_DIR / 'fundamentals.parquet').as_posix()}')"
    out = PROCESSED_DIR / "universe.parquet"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Section 3 stop condition: the price table must contain delistings.
    n_delisted_priced, n_priced = con.execute(f"""
        SELECT count(*) FILTER (WHERE t.isdelisted = 'Y'), count(*)
        FROM (SELECT DISTINCT ticker FROM {stocks}) s
        JOIN {tickers} t ON t.ticker = s.ticker AND t."table" IN ('SEP', 'stocks')
    """).fetchone()
    print(f"price table: {n_priced:,} tickers, {n_delisted_priced:,} delisted")
    if n_delisted_priced == 0:
        print("STOP: the price table contains no delisted tickers — data is wrong (spec section 3)")
        return 1

    con.execute(f"""
        CREATE TABLE eligible AS
        SELECT ticker, permaticker, category, exchange, industry, sector, isdelisted,
               firstpricedate, lastpricedate
        FROM {tickers}
        WHERE "table" IN ('SEP', 'stocks')
          AND category IN {INCLUDED_CATEGORIES}
          AND exchange IN {INCLUDED_EXCHANGES}
          AND (industry IS NULL OR industry <> '{SPAC_INDUSTRY}')
          AND (industry IS NULL OR industry NOT LIKE '{REIT_INDUSTRY_PREFIX}%')
    """)
    funnel = con.execute(f"""
        SELECT
          count(*) FILTER (WHERE "table" IN ('SEP','stocks')) AS priced,
          count(*) FILTER (WHERE "table" IN ('SEP','stocks') AND category IN {INCLUDED_CATEGORIES}) AS domestic_common,
          count(*) FILTER (WHERE "table" IN ('SEP','stocks') AND category IN {INCLUDED_CATEGORIES}
                             AND exchange IN {INCLUDED_EXCHANGES}) AS on_exchanges,
          count(*) FILTER (WHERE "table" IN ('SEP','stocks') AND category IN {INCLUDED_CATEGORIES}
                             AND exchange IN {INCLUDED_EXCHANGES} AND industry = '{SPAC_INDUSTRY}') AS spacs_removed,
          count(*) FILTER (WHERE "table" IN ('SEP','stocks') AND category IN {INCLUDED_CATEGORIES}
                             AND exchange IN {INCLUDED_EXCHANGES} AND industry LIKE '{REIT_INDUSTRY_PREFIX}%') AS reits_removed,
          (SELECT count(*) FROM eligible) AS eligible,
          (SELECT count(*) FROM eligible WHERE isdelisted = 'Y') AS eligible_delisted
        FROM {tickers}
    """).fetchone()
    names = ["priced", "domestic_common", "on_exchanges", "spacs_removed", "reits_removed",
             "eligible", "eligible_delisted"]
    print("ticker funnel: " + ", ".join(f"{n}={v:,}" for n, v in zip(names, funnel)))

    # Month-end rows with D3 floors.
    con.execute(f"""
        CREATE TABLE month_rows AS
        WITH px AS (
            SELECT s.ticker, s.date, s.close, s.closeadj, s.closeunadj, s.volume,
                   last_day(s.date) AS month_end,
                   avg(s.close * s.volume) OVER w AS adv20,
                   count(*) OVER w AS n20
            FROM {stocks} s
            WHERE s.ticker IN (SELECT ticker FROM eligible)
            WINDOW w AS (PARTITION BY s.ticker ORDER BY s.date
                         ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        ),
        last_in_month AS (
            SELECT * FROM px
            QUALIFY row_number() OVER (PARTITION BY ticker, month_end ORDER BY date DESC) = 1
        )
        SELECT ticker, month_end, date AS trade_date, close, closeadj, closeunadj, volume, adv20, n20
        FROM last_in_month
        WHERE month_end BETWEEN DATE '{BUILD_START}' AND DATE '{HOLDOUT_END}'
    """)
    floors = con.execute(f"""
        SELECT count(*) AS candidate_rows,
               count(*) FILTER (WHERE n20 = 20) AS with_20d_history,
               count(*) FILTER (WHERE n20 = 20 AND closeunadj >= {MIN_PRICE}) AS pass_price,
               count(*) FILTER (WHERE n20 = 20 AND closeunadj >= {MIN_PRICE}
                                  AND adv20 >= {MIN_AVG_DOLLAR_VOLUME_20D}) AS pass_floors
        FROM month_rows
    """).fetchone()
    print("month-end funnel: " + ", ".join(
        f"{n}={v:,}" for n, v in zip(["candidate_rows", "with_20d_history", "pass_price", "pass_floors"], floors)))

    # EPS history filter, point in time on the filing date.
    con.execute(f"""
        CREATE TABLE eps_q AS
        SELECT ticker, calendardate, date AS filed
        FROM {fundamentals}
        WHERE dimension = 'ARQ' AND eps IS NOT NULL
          AND ticker IN (SELECT ticker FROM eligible)
    """)
    con.execute(f"""
        CREATE TABLE universe AS
        WITH cand AS (
            SELECT * FROM month_rows
            WHERE n20 = 20 AND closeunadj >= {MIN_PRICE} AND adv20 >= {MIN_AVG_DOLLAR_VOLUME_20D}
        ),
        eps_counts AS (
            SELECT c.ticker, c.month_end, count(DISTINCT q.calendardate) AS eps_quarters
            FROM cand c
            JOIN eps_q q ON q.ticker = c.ticker
                        AND q.filed <= c.month_end
                        AND q.calendardate <= c.month_end
                        AND q.calendardate > c.month_end - INTERVAL {EPS_WINDOW_MONTHS} MONTH
            GROUP BY 1, 2
        )
        SELECT c.ticker, c.month_end, c.trade_date, c.close, c.closeadj, c.closeunadj, c.volume,
               c.adv20 AS avg_dollar_volume_20d, e.eps_quarters,
               t.permaticker, t.category, t.exchange, t.industry, t.sector, t.isdelisted, t.lastpricedate
        FROM cand c
        JOIN eps_counts e USING (ticker, month_end)
        JOIN eligible t USING (ticker)
        WHERE e.eps_quarters >= {EPS_MIN_QUARTERS}
        ORDER BY c.month_end, c.ticker
    """)
    con.execute(f"COPY universe TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    rows, n_tickers, n_del = con.execute(
        "SELECT count(*), count(DISTINCT ticker), count(DISTINCT ticker) FILTER (WHERE isdelisted='Y') FROM universe"
    ).fetchone()
    print(f"universe: {rows:,} rows, {n_tickers:,} tickers, {n_del:,} of them delisted -> {out}")
    print("rows per year (build window), distinct tickers, delisted tickers:")
    for y, r, t, d in con.execute(f"""
        SELECT year(month_end), count(*), count(DISTINCT ticker),
               count(DISTINCT ticker) FILTER (WHERE isdelisted = 'Y')
        FROM universe WHERE month_end <= DATE '{BUILD_END}' GROUP BY 1 ORDER BY 1
    """).fetchall():
        print(f"  {y}: {r:>7,} rows  {t:>6,} tickers  {d:>6,} delisted")
    if n_del == 0:
        print("STOP: no delisted ticker survived into the universe (spec section 3)")
        return 1
    print("RESULT: PASS — universe written; delisted tickers present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
