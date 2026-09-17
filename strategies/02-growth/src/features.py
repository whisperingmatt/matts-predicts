"""S3 — Features per spec section 5 at lags 0, 3, 6, 12 months.

Input:  data/raw/{fundamentals,stocks,daily,holdings,insiders}.parquet,
        data/processed/universe.parquet
Output: data/processed/features.parquet — one row per (ticker, month_end, lag)
        reports/s3_feature_coverage.md — non-null share per feature per year

    python -m src.features

Every feature is first computed on a base grid: every (ticker, month_end)
for tickers that ever enter the universe, month ends from 2005-01 on, using
the ticker's last trade on or before the month end. The lag-L row of a
universe (ticker, month_end) is the base row at last_day(month_end - L
months): the feature as it stood that many months earlier. Fundamentals
are joined point in time on the filing date (fundamentals.date, the spec's
datekey) <= decision date; tests/test_point_in_time.py guards this.

Interpretations that the spec text leaves open are listed in decisions.md
(2026-09-17, "S3 feature interpretations"). Unavailable hypotheses are
present as all-null columns so S4 can report them as unavailable:
H2, H3, H17, H18 (deferred), H12 (no short-interest field), H16 (no ETF
shares-outstanding field in any Sharadar table).

Nulls mean insufficient data. Nothing is filled.
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from src.config import BUILD_END, BUILD_START, HOLDOUT_END, LAGS, PROCESSED_DIR, RAW_DIR, REPORTS_DIR

GRID_START = "2003-01-31"  # BUILD_START minus the longest lag minus the 13 months H9 looks back

FEATURE_STATUS = {
    "h1_eps_accel": "available", "h4_op_leverage": "available",
    "h5_peg_lt_1": "available", "h5_peg_lt_05": "available",
    "h6_compressed_multiple": "available", "h7_neglect": "available",
    "h8_fcf_divergence": "available",
    "h9_rs6_top_decile": "available", "h9_rs12_top_decile": "available",
    "h10_sponsorship": "available (holdings from 2013-06-30)",
    "h11_insider_cluster": "available (insiders from 2008-01-02)",
    "h12_short_fuel": "UNAVAILABLE — no short-interest field in Sharadar",
    "h13_stage2": "available", "h14_vol_contraction": "available", "h15_near_high": "available",
    "h16_sector_flow": "UNAVAILABLE — no ETF shares-outstanding field in Sharadar (funds is OHLCV only)",
    "h2_surprise_streak": "DEFERRED (D7)", "h3_estimate_revisions": "DEFERRED (D7)",
    "h17_sector_surprise": "DEFERRED", "h18_attention": "DEFERRED",
    "h20_leverage_ok": "available", "h21_no_dilution": "available",
    "ctl_pe_lt_15": "available", "ctl_pb_lt_15": "available", "ctl_divyield_gt_2": "available",
}
FLAG_COLUMNS = list(FEATURE_STATUS)
VALUE_COLUMNS = ["eps_growth_q0", "eps_ttm_growth", "peg", "marketcap", "pe", "pb",
                 "rs6_return", "rs12_return", "rs6_pct", "rs12_pct", "inst_pct", "inst_pct_prev",
                 "insider_buyers_90d", "fcf_slope_num", "fcf_period_return", "high52_ratio",
                 "net_debt_to_ebitda_ttm", "divyield", "fund_calendardate", "fund_filed"]


def P(name: str) -> str:
    return f"read_parquet('{(RAW_DIR / name).as_posix()}')"


def connect() -> duckdb.DuckDBPyConnection:
    tmp = PROCESSED_DIR / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute("SET memory_limit = '10GB'")
    con.execute("SET preserve_insertion_order = false")
    return con


def log(con: duckdb.DuckDBPyConnection, table: str, note: str = "") -> None:
    n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {n:,} rows {note}", flush=True)


# ---------------------------------------------------------------- grid

def build_grid(con: duckdb.DuckDBPyConnection) -> None:
    """grid(ticker, month_end, trade_date, close, closeadj, closeunadj, volume, in_universe)."""
    con.execute(f"""
        CREATE TABLE utick AS SELECT DISTINCT ticker FROM read_parquet('{(PROCESSED_DIR / 'universe.parquet').as_posix()}')
    """)
    con.execute(f"""
        CREATE TABLE grid AS
        WITH px AS (
            SELECT ticker, date, close, closeadj, closeunadj, volume, last_day(date) AS month_end
            FROM {P('stocks.parquet')} WHERE ticker IN (SELECT ticker FROM utick)
            QUALIFY row_number() OVER (PARTITION BY ticker, last_day(date) ORDER BY date DESC) = 1
        )
        SELECT p.ticker, p.month_end, p.date AS trade_date, p.close, p.closeadj, p.closeunadj, p.volume,
               (u.ticker IS NOT NULL) AS in_universe
        FROM px p
        LEFT JOIN read_parquet('{(PROCESSED_DIR / 'universe.parquet').as_posix()}') u
               ON u.ticker = p.ticker AND u.month_end = p.month_end
        WHERE p.month_end BETWEEN DATE '{GRID_START}' AND DATE '{HOLDOUT_END}'
    """)
    log(con, "grid")


# ---------------------------------------------------------- fundamentals

def build_arq(con: duckdb.DuckDBPyConnection, tickers: list[str] | None = None) -> None:
    """arq: one row per (ticker, calendardate), dimension ARQ, earliest filing kept.

    Re-filings of the same quarter (10-K repeating a 10-Q, amendments) carry
    identical figures on later dates; the earliest filing is when the figures
    became public, so it is the point-in-time row.
    """
    scope = ("ticker IN (SELECT ticker FROM utick)" if tickers is None
             else "ticker IN (" + ",".join(f"'{t}'" for t in tickers) + ")")
    con.execute(f"""
        CREATE TABLE arq AS
        SELECT ticker, calendardate, date AS filed, eps, revenue, opinc, fcfps, sharesbas, debt, cashneq,
               ebitda, CASE WHEN pe > 0 THEN pe END AS pe, divyield, marketcap, price
        FROM {P('fundamentals.parquet')}
        WHERE dimension = 'ARQ' AND {scope}
        QUALIFY row_number() OVER (PARTITION BY ticker, calendardate ORDER BY date) = 1
    """)


def build_fund_seq(con: duckdb.DuckDBPyConnection) -> None:
    """fund_seq: per arq row, everything section 5 derives from the quarter sequence.

    Lags are previous quarters in calendardate order. Each use checks the
    month distance so a missing quarter yields null instead of a wrong pair.
    """
    con.execute("""
        CREATE TABLE fund_seq AS
        WITH s1 AS (
            SELECT *,
                lag(calendardate, 1) OVER w AS cd_q1, lag(calendardate, 2) OVER w AS cd_q2,
                lag(calendardate, 3) OVER w AS cd_q3, lag(calendardate, 4) OVER w AS cd_q4,
                lag(calendardate, 5) OVER w AS cd_q5, lag(calendardate, 6) OVER w AS cd_q6,
                lag(calendardate, 7) OVER w AS cd_q7, lag(calendardate, 8) OVER w AS cd_q8,
                lag(calendardate, 19) OVER w AS cd_q19,
                lag(filed, 8) OVER w AS filed_q8,
                lag(eps, 1) OVER w AS eps_q1, lag(eps, 2) OVER w AS eps_q2, lag(eps, 3) OVER w AS eps_q3,
                lag(eps, 4) OVER w AS eps_q4, lag(eps, 5) OVER w AS eps_q5, lag(eps, 6) OVER w AS eps_q6,
                lag(eps, 7) OVER w AS eps_q7,
                lag(revenue, 1) OVER w AS rev_q1, lag(revenue, 2) OVER w AS rev_q2, lag(revenue, 3) OVER w AS rev_q3,
                lag(revenue, 4) OVER w AS rev_q4, lag(revenue, 5) OVER w AS rev_q5, lag(revenue, 6) OVER w AS rev_q6,
                lag(revenue, 7) OVER w AS rev_q7,
                lag(opinc, 4) OVER w AS opinc_q4,
                lag(fcfps, 1) OVER w AS fcfps_q1, lag(fcfps, 2) OVER w AS fcfps_q2, lag(fcfps, 3) OVER w AS fcfps_q3,
                lag(ebitda, 1) OVER w AS ebitda_q1, lag(ebitda, 2) OVER w AS ebitda_q2, lag(ebitda, 3) OVER w AS ebitda_q3,
                lag(sharesbas, 8) OVER w AS sharesbas_q8
            FROM arq
            WINDOW w AS (PARTITION BY ticker ORDER BY calendardate)
        ),
        s2 AS (
            SELECT *,
                -- month distances guard against missing quarters
                date_diff('month', cd_q3, calendardate) = 9   AS ok_q3,
                date_diff('month', cd_q4, calendardate) = 12  AS ok_q4,
                date_diff('month', cd_q5, calendardate) = 15  AS ok_q5,
                date_diff('month', cd_q6, calendardate) = 18  AS ok_q6,
                date_diff('month', cd_q7, calendardate) = 21  AS ok_q7,
                date_diff('month', cd_q8, calendardate) = 24  AS ok_q8,
                -- EPS growth YoY; null when the base quarter's EPS is not positive
                CASE WHEN eps_q4 > 0 THEN eps / eps_q4 - 1 END AS g0,
                CASE WHEN eps_q5 > 0 THEN eps_q1 / eps_q5 - 1 END AS g1,
                CASE WHEN eps_q6 > 0 THEN eps_q2 / eps_q6 - 1 END AS g2,
                -- revenue growth YoY
                CASE WHEN rev_q4 > 0 THEN revenue / rev_q4 - 1 END AS rg0,
                CASE WHEN rev_q5 > 0 THEN rev_q1 / rev_q5 - 1 END AS rg1,
                CASE WHEN rev_q6 > 0 THEN rev_q2 / rev_q6 - 1 END AS rg2,
                CASE WHEN rev_q7 > 0 THEN rev_q3 / rev_q7 - 1 END AS rg3,
                eps + eps_q1 + eps_q2 + eps_q3 AS eps_ttm,
                eps_q4 + eps_q5 + eps_q6 + eps_q7 AS eps_ttm_prev,
                ebitda + ebitda_q1 + ebitda_q2 + ebitda_q3 AS ebitda_ttm,
                -- least-squares slope sign of fcfps over q3..q0 (x = 0..3): 3*q0 + q1 - q2 - 3*q3
                3 * fcfps + fcfps_q1 - fcfps_q2 - 3 * fcfps_q3 AS fcf_slope_num
            FROM s1
        ),
        s3 AS (
            SELECT *,
                median(pe) OVER w20 AS pe_med20,
                median(CASE WHEN ok_q4 THEN g0 END) OVER w20 AS g_med20,
                count(*) OVER w20 AS n20
            FROM s2
            WINDOW w20 AS (PARTITION BY ticker ORDER BY calendardate ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        )
        SELECT ticker, calendardate, filed, filed_q8, eps, sharesbas, debt, cashneq, divyield, pe AS pe_sf1,
               cd_q4,
               CASE WHEN ok_q4 THEN g0 END AS eps_growth_q0,
               CASE WHEN ok_q6 AND g0 IS NOT NULL AND g1 IS NOT NULL AND g2 IS NOT NULL
                    THEN g0 > g1 AND g1 > g2 AND g0 >= 0.25 END AS h1_eps_accel,
               CASE WHEN ok_q7 AND rg0 IS NOT NULL AND rg1 IS NOT NULL AND rg2 IS NOT NULL AND rg3 IS NOT NULL
                         AND revenue > 0 AND rev_q4 > 0 AND opinc IS NOT NULL AND opinc_q4 IS NOT NULL
                    THEN rg0 > rg1 AND rg1 > rg2 AND rg2 > rg3 AND opinc / revenue > opinc_q4 / rev_q4 END AS h4_op_leverage,
               CASE WHEN ok_q7 AND eps_ttm > 0 AND eps_ttm_prev > 0 THEN eps_ttm / eps_ttm_prev - 1 END AS eps_ttm_growth,
               CASE WHEN ok_q7 THEN eps_ttm END AS eps_ttm,
               CASE WHEN n20 = 20 THEN pe_med20 END AS pe_med20,
               CASE WHEN n20 = 20 THEN g_med20 END AS g_med20,
               CASE WHEN ok_q3 THEN fcf_slope_num END AS fcf_slope_num,
               CASE WHEN ok_q3 THEN ebitda_ttm END AS ebitda_ttm,
               CASE WHEN debt IS NULL OR cashneq IS NULL THEN NULL
                    WHEN debt - cashneq <= 0 THEN TRUE
                    WHEN ok_q3 AND ebitda_ttm > 0 THEN (debt - cashneq) / ebitda_ttm < 2
                    WHEN ok_q3 AND ebitda_ttm <= 0 THEN FALSE END AS h20_leverage_ok,
               CASE WHEN ok_q3 AND ebitda_ttm > 0 AND debt IS NOT NULL AND cashneq IS NOT NULL
                    THEN (debt - cashneq) / ebitda_ttm END AS net_debt_to_ebitda_ttm,
               CASE WHEN ok_q8 AND sharesbas IS NOT NULL AND sharesbas_q8 IS NOT NULL
                    THEN sharesbas <= sharesbas_q8 * 1.02 END AS h21_no_dilution
        FROM s3
    """)


def compute_fundamental_features(con: duckdb.DuckDBPyConnection, grid: str = "grid") -> None:
    """fund_feat: the grid joined point in time to the latest quarter filed on or before month_end."""
    if not con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'fund_seq'").fetchone()[0]:
        build_fund_seq(con)
    con.execute(f"""
        CREATE TABLE fund_feat AS
        SELECT g.ticker, g.month_end,
               f.calendardate AS fund_calendardate, f.filed AS fund_filed, f.filed_q8 AS fund_filed_q8,
               f.eps AS eps_q0, f.divyield, f.cd_q4, f.eps_growth_q0, f.h1_eps_accel, f.h4_op_leverage,
               f.eps_ttm, f.eps_ttm_growth, f.pe_med20, f.g_med20, f.fcf_slope_num, f.ebitda_ttm,
               f.h20_leverage_ok, f.net_debt_to_ebitda_ttm, f.h21_no_dilution
        FROM {grid} g
        ASOF LEFT JOIN fund_seq f ON f.ticker = g.ticker AND f.filed <= g.month_end
    """)


# ----------------------------------------------------------- prices

def build_price_features(con: duckdb.DuckDBPyConnection) -> None:
    # Daily rows for universe tickers, with the windows H14 and H15 need.
    con.execute(f"""
        CREATE TABLE daily_px AS
        WITH d AS (
            SELECT ticker, date, open, high, low, close, volume,
                   lag(close) OVER w AS prev_close,
                   row_number() OVER w AS rn
            FROM {P('stocks.parquet')} WHERE ticker IN (SELECT ticker FROM utick)
            WINDOW w AS (PARTITION BY ticker ORDER BY date)
        ),
        d2 AS (
            SELECT *,
                   greatest(high - low, abs(high - prev_close), abs(low - prev_close)) AS tr
            FROM d
        ),
        d3 AS (
            SELECT *,
                   avg(tr) OVER w20 / nullif(close, 0) AS atr_ratio,
                   avg(volume) OVER w20 AS vol20,
                   max(high) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS high20_prev,
                   max(high) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS high252,
                   count(*) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS n252
            FROM d2
            WINDOW w20 AS (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        )
        SELECT ticker, date, close, volume, rn, high252, n252,
               CASE WHEN rn >= 62 THEN
                    close > high20_prev
                    AND lag(atr_ratio, 1) OVER w < lag(atr_ratio, 21) OVER w
                    AND lag(atr_ratio, 21) OVER w < lag(atr_ratio, 41) OVER w
                    AND lag(vol20, 1) OVER w < lag(vol20, 21) OVER w
                    AND lag(vol20, 21) OVER w < lag(vol20, 41) OVER w
               END AS h14_pattern_day
        FROM d3
        WINDOW w AS (PARTITION BY ticker ORDER BY date)
    """)
    log(con, "daily_px")
    con.execute("CREATE TABLE h14_days AS SELECT ticker, date FROM daily_px WHERE h14_pattern_day")
    log(con, "h14_days", "(completed vol-contraction breakouts)")

    # Weekly bars for H13.
    con.execute("""
        CREATE TABLE weekly AS
        WITH wk AS (
            SELECT ticker, date_trunc('week', date) AS week_start, max(date) AS week_end,
                   arg_max(close, date) AS close, sum(volume) AS volume, count(*) AS n_days
            FROM daily_px GROUP BY 1, 2
        ),
        w1 AS (
            SELECT *,
                   row_number() OVER w AS wn,
                   avg(close) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS sma30,
                   lag(close) OVER w AS prev_close,
                   max(close) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 26 PRECEDING AND 1 PRECEDING) AS base_max,
                   min(close) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 26 PRECEDING AND 1 PRECEDING) AS base_min,
                   sum(volume) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING)
                     / nullif(sum(n_days) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING), 0) AS adv50_prior
            FROM wk WINDOW w AS (PARTITION BY ticker ORDER BY week_start)
        ),
        w2 AS (
            SELECT *, lag(sma30) OVER w AS prev_sma30, lag(sma30, 4) OVER w AS sma30_lag4
            FROM w1 WINDOW w AS (PARTITION BY ticker ORDER BY week_start)
        )
        SELECT ticker, week_start, week_end, wn,
               CASE WHEN wn >= 34 THEN
                    close > sma30 AND prev_close <= prev_sma30
                    AND sma30 > sma30_lag4
                    AND (base_max - base_min) / nullif((base_max + base_min) / 2, 0) <= 0.4
                    AND volume / n_days > 1.5 * adv50_prior
               END AS h13_cross_week
        FROM w2
    """)
    con.execute("CREATE TABLE h13_weeks AS SELECT ticker, week_end FROM weekly WHERE h13_cross_week")
    log(con, "h13_weeks", "(qualifying stage-2 crosses)")

    # Per grid row: H13, H14, H15 and history sufficiency.
    con.execute("""
        CREATE TABLE px_feat AS
        SELECT g.ticker, g.month_end,
               CASE WHEN d.n252 = 252 THEN g.close / d.high252 END AS high52_ratio,
               CASE WHEN d.n252 = 252 THEN g.close >= 0.85 * d.high252 END AS h15_near_high,
               CASE WHEN d.rn >= 62 THEN
                    EXISTS (SELECT 1 FROM h14_days h WHERE h.ticker = g.ticker
                            AND h.date > g.trade_date - INTERVAL 28 DAY AND h.date <= g.trade_date) END AS h14_vol_contraction,
               CASE WHEN (SELECT max(wn) FROM weekly w WHERE w.ticker = g.ticker AND w.week_end <= g.trade_date) >= 34 THEN
                    EXISTS (SELECT 1 FROM h13_weeks h WHERE h.ticker = g.ticker
                            AND h.week_end > g.trade_date - INTERVAL 56 DAY AND h.week_end <= g.trade_date) END AS h13_stage2
        FROM grid g
        LEFT JOIN daily_px d ON d.ticker = g.ticker AND d.date = g.trade_date
    """)
    log(con, "px_feat")

    # H9 relative strength: returns skipping the most recent month, ranked within the universe that month.
    con.execute("""
        CREATE TABLE rs_feat AS
        WITH r AS (
            SELECT g.ticker, g.month_end, g.in_universe,
                   p1.closeadj / p7.closeadj - 1  AS rs6_return,
                   p1.closeadj / p13.closeadj - 1 AS rs12_return
            FROM grid g
            LEFT JOIN grid p1  ON p1.ticker = g.ticker  AND p1.month_end  = last_day(g.month_end - INTERVAL 1 MONTH)
            LEFT JOIN grid p7  ON p7.ticker = g.ticker  AND p7.month_end  = last_day(g.month_end - INTERVAL 7 MONTH)
            LEFT JOIN grid p13 ON p13.ticker = g.ticker AND p13.month_end = last_day(g.month_end - INTERVAL 13 MONTH)
        )
        SELECT ticker, month_end, rs6_return, rs12_return,
               CASE WHEN in_universe AND rs6_return IS NOT NULL THEN
                    percent_rank() OVER (PARTITION BY month_end, in_universe, rs6_return IS NOT NULL ORDER BY rs6_return) END AS rs6_pct,
               CASE WHEN in_universe AND rs12_return IS NOT NULL THEN
                    percent_rank() OVER (PARTITION BY month_end, in_universe, rs12_return IS NOT NULL ORDER BY rs12_return) END AS rs12_pct
        FROM r
    """)
    log(con, "rs_feat")


# ------------------------------------------------ daily valuation, holdings, insiders

def build_other_features(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(f"""
        CREATE TABLE val_feat AS
        SELECT g.ticker, g.month_end, d.marketcap, CASE WHEN d.pe > 0 THEN d.pe END AS pe, CASE WHEN d.pb > 0 THEN d.pb END AS pb
        FROM grid g
        ASOF LEFT JOIN (SELECT ticker, date, marketcap, pe, pb FROM {P('daily.parquet')}
                        WHERE ticker IN (SELECT ticker FROM utick)) d
             ON d.ticker = g.ticker AND d.date <= g.month_end
        WHERE d.date IS NULL OR d.date > g.month_end - INTERVAL 7 DAY
    """)
    log(con, "val_feat")

    # H10: 13F holdings become public 45 days after the quarter end. Units are
    # as reported (not split adjusted); sharesbas is on today's basis, so it is
    # rescaled by close/closeunadj at the quarter end.
    con.execute(f"""
        CREATE TABLE inst_q AS
        SELECT ticker, date AS qdate, sum(units) * 1000 AS inst_shares
        FROM {P('holdings.parquet')} WHERE securitytype = 'SHR' AND ticker IN (SELECT ticker FROM utick)
        GROUP BY 1, 2
    """)
    con.execute("""
        CREATE TABLE inst_feat AS
        WITH q AS (
            SELECT ticker, month_end,
                   (date_trunc('quarter', month_end - INTERVAL 45 DAY) - INTERVAL 1 DAY)::DATE AS q0,
                   last_day((date_trunc('quarter', month_end - INTERVAL 45 DAY) - INTERVAL 1 DAY)::DATE - INTERVAL 3 MONTH) AS q1
            FROM grid
        ),
        lvl AS (
            SELECT q.ticker, q.month_end, q.q0, q.q1,
                   i0.inst_shares / (a0.sharesbas * g0.close / g0.closeunadj) AS inst_pct,
                   i1.inst_shares / (a1.sharesbas * g1.close / g1.closeunadj) AS inst_pct_prev
            FROM q
            LEFT JOIN inst_q i0 ON i0.ticker = q.ticker AND i0.qdate = q.q0
            LEFT JOIN inst_q i1 ON i1.ticker = q.ticker AND i1.qdate = q.q1
            LEFT JOIN arq a0 ON a0.ticker = q.ticker AND a0.calendardate = q.q0 AND a0.filed <= q.month_end AND a0.sharesbas > 0
            LEFT JOIN arq a1 ON a1.ticker = q.ticker AND a1.calendardate = q.q1 AND a1.filed <= q.month_end AND a1.sharesbas > 0
            LEFT JOIN grid g0 ON g0.ticker = q.ticker AND g0.month_end = q.q0 AND g0.closeunadj > 0
            LEFT JOIN grid g1 ON g1.ticker = q.ticker AND g1.month_end = q.q1 AND g1.closeunadj > 0
        )
        SELECT ticker, month_end, inst_pct, inst_pct_prev,
               CASE WHEN inst_pct IS NOT NULL AND inst_pct_prev IS NOT NULL
                    THEN inst_pct > inst_pct_prev AND inst_pct < 0.40 END AS h10_sponsorship
        FROM lvl
    """)
    log(con, "inst_feat")

    # H11: distinct insiders with an open-market purchase (P, non-derivative) filed in the trailing 90 days.
    con.execute(f"""
        CREATE TABLE buys AS
        SELECT ticker, date AS filed, ownername FROM {P('insiders.parquet')}
        WHERE transactioncode = 'P' AND securityadcode = 'NA' AND ticker IN (SELECT ticker FROM utick)
    """)
    con.execute("""
        CREATE TABLE ins_feat AS
        SELECT g.ticker, g.month_end,
               CASE WHEN g.month_end >= DATE '2008-04-01' THEN coalesce(b.n, 0) END AS insider_buyers_90d,
               CASE WHEN g.month_end >= DATE '2008-04-01' THEN coalesce(b.n, 0) >= 3 END AS h11_insider_cluster
        FROM grid g
        LEFT JOIN (
            SELECT g2.ticker, g2.month_end, count(DISTINCT b.ownername) AS n
            FROM grid g2 JOIN buys b ON b.ticker = g2.ticker
                 AND b.filed > g2.month_end - INTERVAL 90 DAY AND b.filed <= g2.month_end
            GROUP BY 1, 2
        ) b ON b.ticker = g.ticker AND b.month_end = g.month_end
    """)
    log(con, "ins_feat")


# ----------------------------------------------------------- assemble

def assemble(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE base AS
        WITH b0 AS (
        SELECT g.ticker, g.month_end, g.trade_date, g.in_universe,
               f.fund_calendardate, f.fund_filed, f.eps_growth_q0, f.h1_eps_accel, f.h4_op_leverage,
               f.eps_ttm_growth,
               CASE WHEN v.pe > 0 AND f.eps_ttm > 0 AND f.eps_ttm_growth > 0
                    THEN v.pe / (f.eps_ttm_growth * 100) END AS peg,
               v.marketcap, v.pe, v.pb, f.divyield,
               CASE WHEN v.pe IS NOT NULL AND f.pe_med20 IS NOT NULL AND f.eps_growth_q0 IS NOT NULL AND f.g_med20 IS NOT NULL
                    THEN v.pe < f.pe_med20 AND f.eps_growth_q0 > f.g_med20 END AS h6_compressed_multiple,
               CASE WHEN v.marketcap IS NOT NULL THEN v.marketcap < 2000 END AS h7_neglect,
               f.fcf_slope_num,
               p0.closeadj / p4.closeadj - 1 AS fcf_period_return,
               CASE WHEN f.fcf_slope_num IS NOT NULL AND p0.closeadj IS NOT NULL AND p4.closeadj IS NOT NULL
                    THEN f.fcf_slope_num > 0 AND (p0.closeadj / p4.closeadj - 1) BETWEEN -0.10 AND 0.10 END AS h8_fcf_divergence,
               r.rs6_return, r.rs12_return, r.rs6_pct, r.rs12_pct,
               CASE WHEN r.rs6_pct IS NOT NULL THEN r.rs6_pct >= 0.9 END AS h9_rs6_top_decile,
               CASE WHEN r.rs12_pct IS NOT NULL THEN r.rs12_pct >= 0.9 END AS h9_rs12_top_decile,
               i.inst_pct, i.inst_pct_prev, i.h10_sponsorship,
               n.insider_buyers_90d, n.h11_insider_cluster,
               x.h13_stage2, x.h14_vol_contraction, x.high52_ratio, x.h15_near_high,
               f.net_debt_to_ebitda_ttm, f.h20_leverage_ok, f.h21_no_dilution,
               CASE WHEN v.pe IS NOT NULL THEN v.pe < 15 END AS ctl_pe_lt_15,
               CASE WHEN v.pb IS NOT NULL THEN v.pb < 1.5 END AS ctl_pb_lt_15,
               CASE WHEN f.divyield IS NOT NULL THEN f.divyield > 0.02 END AS ctl_divyield_gt_2
        FROM grid g
        LEFT JOIN fund_feat f USING (ticker, month_end)
        LEFT JOIN val_feat v USING (ticker, month_end)
        LEFT JOIN rs_feat r USING (ticker, month_end)
        LEFT JOIN inst_feat i USING (ticker, month_end)
        LEFT JOIN ins_feat n USING (ticker, month_end)
        LEFT JOIN px_feat x USING (ticker, month_end)
        LEFT JOIN grid p0 ON p0.ticker = g.ticker AND p0.month_end = f.fund_calendardate
        LEFT JOIN grid p4 ON p4.ticker = g.ticker AND p4.month_end = f.cd_q4
        )
        SELECT b0.*,
               CASE WHEN peg IS NOT NULL THEN peg < 1.0 END AS h5_peg_lt_1,
               CASE WHEN peg IS NOT NULL THEN peg < 0.5 END AS h5_peg_lt_05
        FROM b0
    """)
    log(con, "base")
    unavailable = ["h12_short_fuel", "h16_sector_flow", "h2_surprise_streak", "h3_estimate_revisions",
                   "h17_sector_surprise", "h18_attention"]
    null_cols = ", ".join(f"NULL::BOOLEAN AS {c}" for c in unavailable)
    lag_union = " UNION ALL ".join(f"SELECT {L} AS lag" for L in LAGS)
    con.execute(f"""
        CREATE TABLE features AS
        SELECT u.ticker, u.month_end, l.lag, last_day(u.month_end - to_months(l.lag)) AS asof_month_end,
               b.* EXCLUDE (ticker, month_end, in_universe), {null_cols}
        FROM read_parquet('{(PROCESSED_DIR / 'universe.parquet').as_posix()}') u
        CROSS JOIN ({lag_union}) l
        LEFT JOIN base b ON b.ticker = u.ticker AND b.month_end = last_day(u.month_end - to_months(l.lag))
        ORDER BY u.month_end, u.ticker, l.lag
    """)
    log(con, "features")


def write_outputs(con: duckdb.DuckDBPyConnection) -> Path:
    out = PROCESSED_DIR / "features.parquet"
    con.execute(f"COPY features TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    cols = [c for c in FLAG_COLUMNS]
    # Coverage: non-null share per flag per year, lag 0, build window; then per lag overall.
    yearly = con.execute(f"""
        SELECT year(month_end) AS y, count(*) AS n,
               {", ".join(f"round(100.0 * count({c}) / count(*), 1) AS {c}" for c in cols)}
        FROM features WHERE lag = 0 AND month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}'
        GROUP BY 1 ORDER BY 1
    """).fetchall()
    bylag = con.execute(f"""
        SELECT lag, count(*) AS n,
               {", ".join(f"round(100.0 * count({c}) / count(*), 1) AS {c}" for c in cols)}
        FROM features WHERE month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}'
        GROUP BY 1 ORDER BY 1
    """).fetchall()
    truerate = con.execute(f"""
        SELECT {", ".join(f"round(100.0 * count(*) FILTER (WHERE {c}) / nullif(count({c}), 0), 1) AS {c}" for c in cols)}
        FROM features WHERE lag = 0 AND month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}'
    """).fetchone()
    short = {c: c.replace("_top_decile", "").replace("compressed_multiple", "cmult").replace("vol_contraction", "volc")
             for c in cols}
    lines = ["# S3 feature coverage — build window 2006-01 to 2019-12, universe rows",
             "",
             "Source: src/features.py over data/processed/features.parquet. Cell = percent of universe",
             "rows whose flag is non-null (data sufficient). Nulls are never filled.",
             "",
             "## Availability", ""]
    lines += [f"- {c}: {s}" for c, s in FEATURE_STATUS.items()]
    lines += ["", "## Non-null percent per flag per year, lag 0", "",
              "| year | rows | " + " | ".join(short[c] for c in cols) + " |",
              "| --- | ---: | " + " | ".join("---:" for _ in cols) + " |"]
    for row in yearly:
        lines.append(f"| {row[0]} | {row[1]:,} | " + " | ".join(f"{v:.1f}" if v is not None else "0.0" for v in row[2:]) + " |")
    lines += ["", "## Non-null percent per flag per lag, build window overall", "",
              "| lag | rows | " + " | ".join(short[c] for c in cols) + " |",
              "| --- | ---: | " + " | ".join("---:" for _ in cols) + " |"]
    for row in bylag:
        lines.append(f"| {row[0]} | {row[1]:,} | " + " | ".join(f"{v:.1f}" if v is not None else "0.0" for v in row[2:]) + " |")
    lines += ["", "## Percent TRUE among non-null, lag 0, build window (context only, no lifts here)", "",
              "| " + " | ".join(short[c] for c in cols) + " |",
              "| " + " | ".join("---:" for _ in cols) + " |",
              "| " + " | ".join(f"{v:.1f}" if v is not None else "n/a" for v in truerate) + " |", ""]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORTS_DIR / "s3_feature_coverage.md"
    report.write_text("\n".join(lines))
    print("\n".join(lines))
    return out


def main() -> int:
    con = connect()
    print("grid"); build_grid(con)
    print("fundamentals"); build_arq(con); build_fund_seq(con); compute_fundamental_features(con)
    log(con, "fund_feat")
    print("prices"); build_price_features(con)
    print("valuation, holdings, insiders"); build_other_features(con)
    print("assemble"); assemble(con)
    out = write_outputs(con)
    n, nt, nm = con.execute("SELECT count(*), count(DISTINCT ticker), count(DISTINCT month_end) FROM features").fetchone()
    print(f"features.parquet: {n:,} rows ({nt:,} tickers x {nm:,} month ends x {len(LAGS)} lags) -> {out}")
    pit = con.execute("SELECT count(*) FROM features WHERE fund_filed > asof_month_end").fetchone()[0]
    print(f"rows whose fundamentals were filed after their as-of date: {pit:,}")
    print("RESULT:", "PASS — features written, point-in-time clean" if pit == 0 else "FAIL — look-ahead rows present")
    return 0 if pit == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
