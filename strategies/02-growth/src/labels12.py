"""S6 — 12-month labels per GROWTH-002 E1.

Input:  data/processed/universe.parquet, data/raw/stocks.parquet
Output: data/processed/labels12.parquet, one row per universe row

    python -m src.labels12

fwd_12m_return = closeadj(t+12m) / closeadj(t) - 1 with t the universe row's
trade date and t+12m the last trade on or before the month end 12 calendar
months later (ASOF join, as src/labels.py does for 24 months). No trade in
that month means the last available closeadj stands in and
delisted_before_t12 is true (delist is terminal, D1/E1). A target month end
after the last price date gives a null return. Flags win_50 (>= 50%) and
win_100 (>= 100%). launch_300 is not recomputed; S6 joins it from
labels.parquet as the reference column.

Validity gate (GROWTH-002 section 3): build-window win_50 base rate must be
between 3% and 25%. Exit 1 otherwise.
"""
from __future__ import annotations

import sys

import duckdb

from src.config import BUILD_END, BUILD_START, PROCESSED_DIR, RAW_DIR

WIN_THRESHOLDS = {"win_50": 0.5, "win_100": 1.0}
BASE_RATE_MIN, BASE_RATE_MAX = 0.03, 0.25


def main() -> int:
    tmp = PROCESSED_DIR / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute("SET memory_limit = '10GB'")
    stocks = f"read_parquet('{(RAW_DIR / 'stocks.parquet').as_posix()}')"
    universe = f"read_parquet('{(PROCESSED_DIR / 'universe.parquet').as_posix()}')"
    out = PROCESSED_DIR / "labels12.parquet"
    data_max = con.execute(f"SELECT max(date) FROM {stocks}").fetchone()[0]
    flags = ", ".join(
        f"CASE WHEN fwd_12m_return IS NULL THEN NULL ELSE fwd_12m_return >= {thr} END AS {name}"
        for name, thr in WIN_THRESHOLDS.items())
    con.execute(f"""
        CREATE TABLE labels12 AS
        WITH u AS (
            SELECT ticker, month_end, trade_date, closeadj AS closeadj_t,
                   last_day(month_end + INTERVAL 12 MONTH) AS month_end_t12
            FROM {universe}
        ),
        px AS (SELECT ticker, date, closeadj FROM {stocks} WHERE ticker IN (SELECT ticker FROM u)),
        joined AS (
            SELECT u.*, px.date AS trade_date_t12, px.closeadj AS closeadj_t12
            FROM u ASOF LEFT JOIN px ON px.ticker = u.ticker AND px.date <= u.month_end_t12
        ),
        ret AS (
            SELECT *,
                   CASE WHEN month_end_t12 > DATE '{data_max}' THEN NULL
                        ELSE closeadj_t12 / closeadj_t - 1 END AS fwd_12m_return,
                   CASE WHEN month_end_t12 > DATE '{data_max}' THEN NULL
                        ELSE trade_date_t12 < date_trunc('month', month_end_t12) END AS delisted_before_t12
            FROM joined
        )
        SELECT ticker, month_end, trade_date, closeadj_t, month_end_t12, trade_date_t12, closeadj_t12,
               fwd_12m_return, delisted_before_t12, {flags}
        FROM ret ORDER BY month_end, ticker
    """)
    con.execute(f"COPY labels12 TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    total, labeled = con.execute("SELECT count(*), count(fwd_12m_return) FROM labels12").fetchone()
    last = con.execute("SELECT max(month_end) FROM labels12 WHERE fwd_12m_return IS NOT NULL").fetchone()[0]
    print(f"labels12: {total:,} rows, {labeled:,} with a 12m return, last observable month end {last} -> {out}")
    print("build window by year: rows, win_50, rate_50, win_100, rate_100, delisted by t+12")
    for y, r, a, b, d in con.execute(f"""
        SELECT year(month_end), count(*), count(*) FILTER (WHERE win_50), count(*) FILTER (WHERE win_100),
               count(*) FILTER (WHERE delisted_before_t12)
        FROM labels12 WHERE month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}' GROUP BY 1 ORDER BY 1
    """).fetchall():
        print(f"  {y}: {r:>7,}  {a:>6,} {a / r:6.2%}  {b:>6,} {b / r:6.2%}  {d:>6,}")
    n, k50, k100, nnull = con.execute(f"""
        SELECT count(*), count(*) FILTER (WHERE win_50), count(*) FILTER (WHERE win_100),
               count(*) - count(fwd_12m_return)
        FROM labels12 WHERE month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}'
    """).fetchone()
    base = k50 / n
    print(f"build window overall: {n:,} rows, win_50 {k50:,} ({base:.2%}), win_100 {k100:,} ({k100 / n:.2%}), unlabeled {nnull:,}")
    ok = BASE_RATE_MIN <= base <= BASE_RATE_MAX and nnull == 0
    print("RESULT:", "PASS — win_50 base rate inside [3%, 25%], every build-window row labeled" if ok else "FAIL — see above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
