"""S2 — Launch labels per spec section 4 and D1.

Input:  data/processed/universe.parquet, data/raw/stocks.parquet
Output: data/processed/labels.parquet (one row per universe row)
        reports/s2_base_rates.md (build window only)

    python -m src.labels

fwd_24m_return = closeadj(t+24m) / closeadj(t) - 1, where t is the
universe row's trade date and t+24m is the last trade on or before the
month end 24 calendar months later (ASOF join on the price table). If the
ticker has no trade in that target month, the last available closeadj is
used and delisted_before_t24 is true: delist is terminal (section 4). If
the target month end is after the last date in the price table, the return
is null (not yet observable). Flags: launch_200/300/500 from
LAUNCH_THRESHOLDS (D1). Base rates use launch_300 and are reported per
year and overall for the build window only (D4); holdout rows are labeled
but nothing about them is printed or written to reports/.

Validity gate (spec section 7): overall build-window base rate must be
between 0.5% and 5% and delisted tickers must appear. Exit 1 otherwise.
"""
from __future__ import annotations

import sys

import duckdb

from src.config import BUILD_END, BUILD_START, LAUNCH_THRESHOLDS, PROCESSED_DIR, RAW_DIR, REPORTS_DIR

BASE_RATE_MIN, BASE_RATE_MAX = 0.005, 0.05


def main() -> int:
    tmp = PROCESSED_DIR / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute("SET memory_limit = '10GB'")
    stocks = f"read_parquet('{(RAW_DIR / 'stocks.parquet').as_posix()}')"
    universe = f"read_parquet('{(PROCESSED_DIR / 'universe.parquet').as_posix()}')"
    out = PROCESSED_DIR / "labels.parquet"
    report = REPORTS_DIR / "s2_base_rates.md"

    data_max = con.execute(f"SELECT max(date) FROM {stocks}").fetchone()[0]
    flags = ", ".join(
        f"CASE WHEN fwd_24m_return IS NULL THEN NULL ELSE fwd_24m_return >= {thr} END AS {name}"
        for name, thr in LAUNCH_THRESHOLDS.items())
    con.execute(f"""
        CREATE TABLE labels AS
        WITH u AS (
            SELECT ticker, month_end, trade_date, closeadj AS closeadj_t, isdelisted,
                   last_day(month_end + INTERVAL 24 MONTH) AS month_end_t24
            FROM {universe}
        ),
        px AS (SELECT ticker, date, closeadj FROM {stocks} WHERE ticker IN (SELECT ticker FROM u)),
        joined AS (
            SELECT u.*, px.date AS trade_date_t24, px.closeadj AS closeadj_t24
            FROM u ASOF LEFT JOIN px ON px.ticker = u.ticker AND px.date <= u.month_end_t24
        ),
        ret AS (
            SELECT *,
                   CASE WHEN month_end_t24 > DATE '{data_max}' THEN NULL
                        ELSE closeadj_t24 / closeadj_t - 1 END AS fwd_24m_return,
                   CASE WHEN month_end_t24 > DATE '{data_max}' THEN NULL
                        ELSE trade_date_t24 < date_trunc('month', month_end_t24) END AS delisted_before_t24
            FROM joined
        )
        SELECT ticker, month_end, trade_date, closeadj_t, month_end_t24, trade_date_t24, closeadj_t24,
               fwd_24m_return, delisted_before_t24, {flags}, isdelisted
        FROM ret ORDER BY month_end, ticker
    """)
    con.execute(f"COPY labels TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")

    total, labeled, unlabeled = con.execute(
        "SELECT count(*), count(fwd_24m_return), count(*) - count(fwd_24m_return) FROM labels").fetchone()
    print(f"labels: {total:,} rows, {labeled:,} with a 24m return, {unlabeled:,} not yet observable -> {out}")
    build_null = con.execute(f"""
        SELECT count(*) FROM labels WHERE month_end <= DATE '{BUILD_END}' AND fwd_24m_return IS NULL
    """).fetchone()[0]
    print(f"build-window rows without a return: {build_null:,}")

    yearly = con.execute(f"""
        SELECT year(month_end) AS y, count(*) AS rows_,
               count(*) FILTER (WHERE launch_200) AS l200,
               count(*) FILTER (WHERE launch_300) AS l300,
               count(*) FILTER (WHERE launch_500) AS l500,
               count(*) FILTER (WHERE delisted_before_t24) AS delisted_by_t24,
               count(DISTINCT ticker) FILTER (WHERE launch_300) AS l300_tickers
        FROM labels
        WHERE month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}'
        GROUP BY 1 ORDER BY 1
    """).fetchall()
    overall = con.execute(f"""
        SELECT count(*), count(*) FILTER (WHERE launch_200), count(*) FILTER (WHERE launch_300),
               count(*) FILTER (WHERE launch_500), count(*) FILTER (WHERE delisted_before_t24),
               count(DISTINCT ticker) FILTER (WHERE launch_300), count(DISTINCT ticker)
        FROM labels WHERE month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}'
    """).fetchone()
    rows_all, l200, l300, l500, del24, l300_t, tick_all = overall
    base = l300 / rows_all if rows_all else float("nan")

    lines = [
        "# S2 base rates — build window 2006-01 to 2019-12",
        "",
        "Source: src/labels.py over data/processed/universe.parquet and data/raw/stocks.parquet.",
        "A row is one (ticker, month_end) in the universe. A launch is fwd_24m_return >= 300%",
        "(D1); the 200% and 500% flags are alongside. Delist is terminal: the last available",
        "closeadj stands in for close(t+24m).",
        "",
        "| year | universe rows | launch_300 | rate_300 | launch_200 | rate_200 | launch_500 | rate_500 | delisted by t+24 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for y, r, a, b, c, d, _ in yearly:
        lines.append(f"| {y} | {r:,} | {b:,} | {b / r:.2%} | {a:,} | {a / r:.2%} | {c:,} | {c / r:.2%} | {d:,} |")
    lines.append(f"| **overall** | {rows_all:,} | {l300:,} | {base:.2%} | {l200:,} | {l200 / rows_all:.2%} "
                 f"| {l500:,} | {l500 / rows_all:.2%} | {del24:,} |")
    lines += [
        "",
        f"Distinct tickers in the build-window universe: {tick_all:,}. Distinct tickers with at least",
        f"one launch_300 row: {l300_t:,}.",
        "",
        f"Validity gate (spec section 7): overall rate_300 {base:.2%} must lie in [0.50%, 5.00%].",
    ]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"-> {report}")

    ok = BASE_RATE_MIN <= base <= BASE_RATE_MAX and build_null == 0
    print("RESULT:", "PASS — base rate inside [0.5%, 5%], every build-window row labeled" if ok
          else "FAIL — see the gate line above")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
