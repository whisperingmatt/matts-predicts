"""S8 — GROWTH-003 winner anatomy, session 8 (spec sections 2 and 3, plus 3.5).

Descriptive only: no directions, no pass criteria (F1). Build and holdout
pooled (F2): 2006-01 to 2025-06 for win_100, 2006-01 to 2024-06 for
launch_300. Every comparison is winner versus population at the same
month (F3). D8 (100 events) applies to every cell reported as a ratio
(F4). Narrative qualities are out of scope; 8-K item codes are the proxy
(F5).

Input:  data/processed/{universe,labels,labels12,features,deciles,regime}.parquet
        data/raw/{tickers,stocks,daily,fundamentals,events,insiders}.parquet
Output: data/processed/anatomy_fields.parquet — every section-2 field per
        (ticker, month) on a dense monthly grid 2003-01 to 2027-06 for every
        ticker ever in the universe (regenerable)
        reports/anatomy_tables.md (+ reports/anatomy_reading.md inserted
        verbatim when present)
        reports/s8_*.csv — every table, unrounded

    python -m src.anatomy

Section 3.5 (Matt's S8 addition, decisions.md 2026-09-17): loss_50 =
fwd_12m_return <= -50% on the existing grid; for every GROWTH-002 feature
decile plus the realized-volatility decile, the win_100 rate, the loss_50
rate, their ratio, and the median 12-month forward return, pooled
2006-01 to 2025-06, coverage beside each; the ratio is "insufficient" when
either count is under D8.

"After T-0" fields (event counts in the 12 months after T-0, share count
change to T+12, the T+k half of the timeline) are FORWARD-LOOKING. They
describe the move. They cannot enter any later scoring model. Column
names carry the suffix _f12 or a positive k so the label travels with the
number. No random element anywhere in this session.
"""
from __future__ import annotations

import sys

import duckdb
import pandas as pd

from src.config import MIN_EVENTS_PER_CELL, PROCESSED_DIR, RAW_DIR, REPORTS_DIR
from src.decile import EXPLORATORY, FEATURES
from src.stats import md_table

# label -> (labels file, window start, window end). F2.
LABELS = {
    "launch_300": ("labels.parquet", "2006-01-31", "2024-06-30"),
    "win_100": ("labels12.parquet", "2006-01-31", "2025-06-30"),
}
LOSS_WINDOW = ("2006-01-31", "2025-06-30")
PROFILE_LAGS = [0, 6, 12]
STEPS = list(range(-24, 25, 3))
GRID_START, GRID_END = "2003-01-01", "2027-06-01"

# Sharadar events.eventcodes stores 8-K item X.0Y as the two-digit code "XY"
# (descriptions table, table = eventcodes, read 2026-09-17). Spec order.
CODES = {
    "11": "1.01 material agreement", "12": "1.02 termination of agreement",
    "21": "2.01 acquisition or disposition completed", "22": "2.02 results of operations",
    "23": "2.03 new financial obligation", "32": "3.02 unregistered equity sale",
    "52": "5.02 officer or director change", "53": "5.03 charter or bylaw change",
    "71": "7.01 Reg FD", "81": "8.01 other events",
}
# Modern 8-K item numbering began 2004-08-23 (first code 22 in the table); a
# trailing 12-month count is complete from 2005-08-31. The forward 12-month
# count is complete while T+12 is inside the data (events to 2026-09-16).
EV_TRAIL_FROM, EV_FWD_TO = "2005-08-31", "2025-08-31"
# Insiders begin 2008-01-02; a trailing 12-month count is complete from 2008-12-31.
INS_TRAIL_FROM = "2008-12-31"

# Numeric section-2 fields: column in anatomy_fields -> (format, description).
NUMERIC: dict[str, tuple[str, str]] = {
    "years_since_first_price": ("yrs", "years from tickers.firstpricedate to the month end"),
    "drawdown_from_3y_high": ("pct", "month-end closeadj / highest daily closeadj in the trailing 36 months - 1"),
    "months_since_3y_low": ("int", "months since the month holding the lowest daily closeadj of the trailing 36"),
    "realized_vol_12m": ("pct", "annualized std of daily log returns, 252 trading days to the last trade date"),
    "avg_dollar_volume_20d": ("musd", "mean close x volume over the 20 trading days to the last trade date, USD millions"),
    "price": ("usd", "closeunadj at the last trade date of the month"),
    "marketcap_musd": ("musd", "daily.marketcap at the last trade date, USD millions"),
    "rev_growth_yoy": ("pct", "ARQ revenue / revenue four quarters earlier - 1"),
    "gross_margin": ("pct", "ARQ grossmargin"),
    "op_margin": ("pct", "ARQ opinc / revenue"),
    "cash_to_mcap": ("pct", "ARQ cashnequsd / market cap"),
    "net_debt_to_mcap": ("pct", "ARQ (debtusd - cashnequsd) / market cap"),
    "capex_to_rev": ("pct", "ARQ -capex / revenue (outflow positive)"),
    "rnd_to_rev": ("pct", "ARQ rnd / revenue"),
    "shares_chg_4q": ("pct", "ARQ sharesbas / sharesbas four quarters earlier - 1"),
    "shares_chg_8q": ("pct", "ARQ sharesbas / sharesbas eight quarters earlier - 1"),
    "rev_growth_streak": ("int", "consecutive ARQ quarters with revenue above the year-earlier quarter, capped at 12"),
    "quarters_since_loss": ("int", "consecutive ARQ quarters with netinc > 0 ending at the latest, capped at 12 (0 = latest is a loss)"),
    **{f"ev{c}_t12": ("cnt", f"8-K {CODES[c]} filings in the trailing 12 months") for c in CODES},
    "ev_total_t12": ("cnt", "the ten codes summed, trailing 12 months"),
    "insider_net_buys_12m": ("cnt", "open-market purchase rows minus sale rows filed in the trailing 12 months (Form 4, non-derivative)"),
    "officer_buys_12m": ("cnt", "open-market purchase rows by officers filed in the trailing 12 months"),
    "inst_pct": ("pct", "13F institutional share of shares outstanding (features.py rules)"),
    "inst_pct_delta_4q": ("pct", "inst_pct minus inst_pct twelve months earlier"),
    "spy_drawdown": ("pct", "SPY drawdown from its all-time high at the month end (regime.parquet)"),
    "months_since_trough": ("int", "months since the SPY trough (regime.parquet)"),
}
CATEGORICAL = ["sector", "exchange", "price_bucket", "profitable", "ceo_change_12m", "financing_12m",
               "deal_12m", "ipo_lt_3y", "scalemarketcap", "drawdown_bucket", "mst_bucket"]
# sector, industry, exchange and scalemarketcap come from the tickers table as it stands today, not point in
# time. scalemarketcap in particular reflects the company's size AFTER any move, so its winner ratio is not
# a pre-move description; the point-in-time size fields are marketcap_musd and the marketcap decile.
CATEGORICAL_NOTE = ("sector, exchange and scalemarketcap are the tickers table's current values, not point in time. "
                    "scalemarketcap is the size category today, after any move, so its ratios describe where winners "
                    "ended up, not where they started; use marketcap_musd and the marketcap decile for size at T-0.")
DECILE_FEATURES = list(FEATURES) + list(EXPLORATORY)
FORWARD = {f"ev{c}_f12": f"8-K {CODES[c]} filings in the 12 months after T-0" for c in CODES}
FORWARD["ev_total_f12"] = "the ten codes summed, 12 months after T-0"


def P(name: str) -> str:
    return f"read_parquet('{(RAW_DIR / name).as_posix()}')"


def pq(name: str) -> str:
    return f"read_parquet('{(PROCESSED_DIR / name).as_posix()}')"


def log(con, table: str) -> None:
    n = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {n:,} rows", flush=True)


# ------------------------------------------------------------------ fields

def build_fields(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(f"""
        CREATE TABLE months AS
        SELECT last_day(d::DATE)::DATE AS month_end
        FROM generate_series(DATE '{GRID_START}', DATE '{GRID_END}', INTERVAL 1 MONTH) t(d)
    """)
    con.execute(f"CREATE TABLE utick AS SELECT DISTINCT ticker FROM {pq('universe.parquet')}")
    con.execute("CREATE TABLE grid AS SELECT ticker, month_end FROM utick CROSS JOIN months")
    log(con, "grid")

    # prices: month-end row, monthly high/low, 20-day dollar volume, realized vol (decile.py definition)
    con.execute(f"""
        CREATE TABLE px AS
        WITH s AS (
            SELECT ticker, date, close, closeadj, closeunadj, volume FROM {P('stocks.parquet')}
            WHERE closeadj > 0 AND ticker IN (SELECT ticker FROM utick)
        ), d AS (
            SELECT *, avg(close * volume) OVER w20 AS adv20, count(*) OVER w20 AS n20,
                   ln(closeadj / lag(closeadj) OVER (PARTITION BY ticker ORDER BY date)) AS lr
            FROM s WINDOW w20 AS (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
        ), d2 AS (
            SELECT *, CASE WHEN count(lr) OVER w252 = 252 THEN stddev_samp(lr) OVER w252 * sqrt(252) END AS rv
            FROM d WINDOW w252 AS (PARTITION BY ticker ORDER BY date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)
        ), last AS (
            SELECT ticker, last_day(date)::DATE AS month_end, date AS trade_date, closeadj, closeunadj,
                   CASE WHEN n20 = 20 THEN adv20 END AS adv20, rv
            FROM d2 QUALIFY row_number() OVER (PARTITION BY ticker, last_day(date) ORDER BY date DESC) = 1
        ), agg AS (
            SELECT ticker, last_day(date)::DATE AS month_end, max(closeadj) AS hi, min(closeadj) AS lo
            FROM s GROUP BY 1, 2
        )
        SELECT l.*, a.hi, a.lo FROM last l JOIN agg a USING (ticker, month_end)
    """)
    con.execute("""
        CREATE TABLE pxg AS
        SELECT g.ticker, g.month_end, p.trade_date, p.closeadj, p.closeunadj AS price, p.adv20 / 1e6 AS avg_dollar_volume_20d,
               p.rv AS realized_vol_12m,
               CASE WHEN count(p.hi) OVER w36 = 36 THEN p.closeadj / max(p.hi) OVER w36 - 1 END AS drawdown_from_3y_high,
               CASE WHEN count(p.lo) OVER w36 = 36
                    THEN datediff('month', arg_min(g.month_end, p.lo) OVER w36, g.month_end) END AS months_since_3y_low
        FROM grid g LEFT JOIN px p USING (ticker, month_end)
        WINDOW w36 AS (PARTITION BY g.ticker ORDER BY g.month_end ROWS BETWEEN 35 PRECEDING AND CURRENT ROW)
    """)
    log(con, "pxg")

    # market cap at the last trade date (daily, within 7 days, as features.py)
    con.execute(f"""
        CREATE TABLE mc AS
        SELECT g.ticker, g.month_end, CASE WHEN d.date > g.trade_date - INTERVAL 7 DAY THEN d.marketcap END AS marketcap_musd
        FROM pxg g
        ASOF LEFT JOIN (SELECT ticker, date, marketcap FROM {P('daily.parquet')} WHERE ticker IN (SELECT ticker FROM utick)) d
             ON d.ticker = g.ticker AND d.date <= g.trade_date
    """)
    log(con, "mc")

    # fundamentals, ARQ, earliest filing per quarter (features.py rule), quarter sequence
    con.execute(f"""
        CREATE TABLE arq AS
        SELECT ticker, calendardate, date AS filed, netinc, revenue, grossmargin, opinc, cashnequsd, debtusd,
               capex, rnd, sharesbas
        FROM {P('fundamentals.parquet')}
        WHERE dimension = 'ARQ' AND ticker IN (SELECT ticker FROM utick)
        QUALIFY row_number() OVER (PARTITION BY ticker, calendardate ORDER BY date) = 1
    """)
    lags_u = ", ".join(f"lag(rev_up, {j}) OVER w AS u{j}" for j in range(1, 12))
    lags_p = ", ".join(f"lag(profitable, {j}) OVER w AS p{j}" for j in range(1, 12))
    streak_u = " ".join(f"WHEN NOT coalesce(u{j}, FALSE) THEN {j}" for j in range(1, 12))
    streak_p = " ".join(f"WHEN NOT coalesce(p{j}, FALSE) THEN {j}" for j in range(1, 12))
    con.execute(f"""
        CREATE TABLE aseq AS
        WITH s1 AS (
            SELECT *, lag(calendardate, 4) OVER w AS cd4, lag(revenue, 4) OVER w AS rev4, lag(sharesbas, 4) OVER w AS sh4,
                   lag(calendardate, 8) OVER w AS cd8, lag(sharesbas, 8) OVER w AS sh8
            FROM arq WINDOW w AS (PARTITION BY ticker ORDER BY calendardate)
        ), s2 AS (
            SELECT *,
                CASE WHEN rev4 > 0 AND datediff('month', cd4, calendardate) BETWEEN 11 AND 13 THEN revenue / rev4 - 1 END AS rev_growth_yoy,
                CASE WHEN sh4 > 0 AND datediff('month', cd4, calendardate) BETWEEN 11 AND 13 THEN sharesbas / sh4 - 1 END AS shares_chg_4q,
                CASE WHEN sh8 > 0 AND datediff('month', cd8, calendardate) BETWEEN 23 AND 25 THEN sharesbas / sh8 - 1 END AS shares_chg_8q,
                CASE WHEN netinc IS NOT NULL THEN netinc > 0 END AS profitable
            FROM s1
        ), s3 AS (
            SELECT *, CASE WHEN rev_growth_yoy IS NOT NULL THEN rev_growth_yoy > 0 END AS rev_up, {lags_u}, {lags_p}
            FROM s2 WINDOW w AS (PARTITION BY ticker ORDER BY calendardate)
        )
        SELECT ticker, calendardate, filed, profitable, rev_growth_yoy, grossmargin AS gross_margin,
               CASE WHEN revenue > 0 THEN opinc / revenue END AS op_margin,
               cashnequsd, debtusd,
               CASE WHEN revenue > 0 THEN -capex / revenue END AS capex_to_rev,
               CASE WHEN revenue > 0 THEN rnd / revenue END AS rnd_to_rev,
               shares_chg_4q, shares_chg_8q, sharesbas,
               CASE WHEN rev_up IS NULL THEN NULL WHEN NOT rev_up THEN 0 {streak_u} ELSE 12 END AS rev_growth_streak,
               CASE WHEN profitable IS NULL THEN NULL WHEN NOT profitable THEN 0 {streak_p} ELSE 12 END AS quarters_since_loss
        FROM s3
    """)
    # point in time: latest quarter filed on or before the month end, filed within 16 months (universe staleness rule)
    con.execute("""
        CREATE TABLE fg AS
        SELECT g.ticker, g.month_end, a.calendardate AS fund_calendardate, a.filed AS fund_filed,
               a.profitable, a.rev_growth_yoy, a.gross_margin, a.op_margin, a.cashnequsd, a.debtusd,
               a.capex_to_rev, a.rnd_to_rev, a.shares_chg_4q, a.shares_chg_8q, a.sharesbas,
               a.rev_growth_streak, a.quarters_since_loss
        FROM grid g
        ASOF LEFT JOIN aseq a ON a.ticker = g.ticker AND a.filed <= g.month_end
        WHERE a.filed IS NULL OR a.filed > g.month_end - INTERVAL 16 MONTH
    """)
    log(con, "fg")

    # 8-K item codes: trailing 12 months (months m-11..m) and the 12 months after (m+1..m+12, forward-looking)
    con.execute(f"""
        CREATE TABLE evx AS
        SELECT ticker, date, unnest(string_split(eventcodes, '|')) AS code
        FROM {P('events.parquet')} WHERE ticker IN (SELECT ticker FROM utick)
    """)
    counts = ", ".join(f"count(*) FILTER (WHERE code = '{c}') AS c{c}" for c in CODES)
    con.execute(f"CREATE TABLE evm AS SELECT ticker, last_day(date)::DATE AS month_end, {counts} FROM evx GROUP BY 1, 2")
    trail = ", ".join(f"CASE WHEN g.month_end >= DATE '{EV_TRAIL_FROM}' THEN sum(coalesce(e.c{c}, 0)) OVER wt END AS ev{c}_t12"
                      for c in CODES)
    fwd = ", ".join(f"CASE WHEN g.month_end <= DATE '{EV_FWD_TO}' THEN sum(coalesce(e.c{c}, 0)) OVER wf END AS ev{c}_f12"
                    for c in CODES)
    con.execute(f"""
        CREATE TABLE evg AS
        SELECT g.ticker, g.month_end, {trail}, {fwd}
        FROM grid g LEFT JOIN evm e USING (ticker, month_end)
        WINDOW wt AS (PARTITION BY g.ticker ORDER BY g.month_end ROWS BETWEEN 11 PRECEDING AND CURRENT ROW),
               wf AS (PARTITION BY g.ticker ORDER BY g.month_end ROWS BETWEEN 1 FOLLOWING AND 12 FOLLOWING)
    """)
    log(con, "evg")

    # insiders: Form 4 rows, non-derivative, open-market purchase (P) and sale (S), by filing date
    con.execute(f"""
        CREATE TABLE insm AS
        SELECT ticker, last_day(date)::DATE AS month_end,
               count(*) FILTER (WHERE transactioncode = 'P') AS buys,
               count(*) FILTER (WHERE transactioncode = 'S') AS sells,
               count(*) FILTER (WHERE transactioncode = 'P' AND isofficer = 'Y') AS obuys
        FROM {P('insiders.parquet')}
        WHERE securityadcode = 'NA' AND transactioncode IN ('P', 'S') AND ticker IN (SELECT ticker FROM utick)
        GROUP BY 1, 2
    """)
    con.execute(f"""
        CREATE TABLE insg AS
        SELECT g.ticker, g.month_end,
               CASE WHEN g.month_end >= DATE '{INS_TRAIL_FROM}'
                    THEN sum(coalesce(i.buys, 0)) OVER wt - sum(coalesce(i.sells, 0)) OVER wt END AS insider_net_buys_12m,
               CASE WHEN g.month_end >= DATE '{INS_TRAIL_FROM}' THEN sum(coalesce(i.obuys, 0)) OVER wt END AS officer_buys_12m
        FROM grid g LEFT JOIN insm i USING (ticker, month_end)
        WINDOW wt AS (PARTITION BY g.ticker ORDER BY g.month_end ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
    """)
    log(con, "insg")

    # 13F level from features.py (every (ticker, as-of month) it computed, any lag), 4-quarter delta by self join
    con.execute(f"""
        CREATE TABLE instm AS
        SELECT ticker, asof_month_end AS month_end, max(inst_pct) AS inst_pct
        FROM {pq('features.parquet')} GROUP BY 1, 2
    """)
    con.execute("""
        CREATE TABLE instg AS
        SELECT a.ticker, a.month_end, a.inst_pct, a.inst_pct - b.inst_pct AS inst_pct_delta_4q
        FROM instm a LEFT JOIN instm b ON b.ticker = a.ticker AND b.month_end = last_day(a.month_end - INTERVAL 12 MONTH)
    """)
    log(con, "instg")

    con.execute(f"""
        CREATE TABLE tk AS
        SELECT ticker, firstpricedate, sector, industry, exchange, scalemarketcap
        FROM {P('tickers.parquet')} WHERE "table" = 'SEP' AND ticker IN (SELECT ticker FROM utick)
        QUALIFY row_number() OVER (PARTITION BY ticker ORDER BY lastpricedate DESC) = 1
    """)

    con.execute(f"""
        CREATE TABLE fields AS
        SELECT g.ticker, g.month_end, p.trade_date, p.closeadj,
               datediff('day', t.firstpricedate, g.month_end) / 365.25 AS years_since_first_price,
               t.sector, t.industry, t.exchange, t.scalemarketcap,
               p.drawdown_from_3y_high, p.months_since_3y_low, p.realized_vol_12m, p.avg_dollar_volume_20d, p.price,
               CASE WHEN p.price IS NULL THEN NULL WHEN p.price < 5 THEN '0 under 5' WHEN p.price < 10 THEN '1 5-10'
                    WHEN p.price < 20 THEN '2 10-20' WHEN p.price < 50 THEN '3 20-50' ELSE '4 50+' END AS price_bucket,
               m.marketcap_musd,
               f.fund_calendardate, f.fund_filed, f.profitable, f.rev_growth_yoy, f.gross_margin, f.op_margin,
               CASE WHEN m.marketcap_musd > 0 THEN f.cashnequsd / (m.marketcap_musd * 1e6) END AS cash_to_mcap,
               CASE WHEN m.marketcap_musd > 0 THEN (f.debtusd - f.cashnequsd) / (m.marketcap_musd * 1e6) END AS net_debt_to_mcap,
               f.capex_to_rev, f.rnd_to_rev, f.shares_chg_4q, f.shares_chg_8q, f.sharesbas,
               f.rev_growth_streak, f.quarters_since_loss,
               e.* EXCLUDE (ticker, month_end),
               {" + ".join(f"e.ev{c}_t12" for c in CODES)} AS ev_total_t12,
               {" + ".join(f"e.ev{c}_f12" for c in CODES)} AS ev_total_f12,
               e.ev52_t12 > 0 AS ceo_change_12m,
               (e.ev23_t12 + e.ev32_t12) > 0 AS financing_12m,
               e.ev21_t12 > 0 AS deal_12m,
               CASE WHEN t.firstpricedate IS NOT NULL THEN datediff('day', t.firstpricedate, g.month_end) / 365.25 < 3 END AS ipo_lt_3y,
               i.insider_net_buys_12m, i.officer_buys_12m,
               h.inst_pct, h.inst_pct_delta_4q,
               r.drawdown AS spy_drawdown, r.drawdown_bucket, r.months_since_trough, r.mst_bucket
        FROM grid g
        JOIN tk t USING (ticker)
        LEFT JOIN pxg p USING (ticker, month_end)
        LEFT JOIN mc m USING (ticker, month_end)
        LEFT JOIN fg f USING (ticker, month_end)
        LEFT JOIN evg e USING (ticker, month_end)
        LEFT JOIN insg i USING (ticker, month_end)
        LEFT JOIN instg h USING (ticker, month_end)
        LEFT JOIN {pq('regime.parquet')} r USING (month_end)
    """)
    log(con, "fields")
    out = PROCESSED_DIR / "anatomy_fields.parquet"
    con.execute(f"COPY (SELECT * FROM fields ORDER BY ticker, month_end) TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    print(f"  -> {out}")


# --------------------------------------------------------------- populations

def build_populations(con) -> None:
    for label, (lfile, start, end) in LABELS.items():
        con.execute(f"""
            CREATE TABLE pop_{label} AS
            SELECT u.ticker, u.month_end, l.{label} AS winner, coalesce(u.sector, 'Unknown') AS sector,
                   r.drawdown_bucket, r.mst_bucket
            FROM {pq('universe.parquet')} u
            JOIN {pq(lfile)} l USING (ticker, month_end)
            JOIN {pq('regime.parquet')} r USING (month_end)
            WHERE u.month_end BETWEEN DATE '{start}' AND DATE '{end}' AND l.{label} IS NOT NULL
        """)
        log(con, f"pop_{label}")


def events_coverage(con) -> pd.DataFrame:
    """Per year: universe tickers, and per code the share of them with at least one filing that year."""
    shares = ", ".join(f"count(DISTINCT CASE WHEN code = '{c}' THEN ticker END) AS t{c}" for c in CODES)
    return con.execute(f"""
        WITH uy AS (SELECT DISTINCT year(month_end) AS year, ticker FROM {pq('universe.parquet')}
                    UNION
                    SELECT y.year, u.ticker FROM (VALUES (2004), (2005)) y(year)
                    CROSS JOIN (SELECT DISTINCT ticker FROM {pq('universe.parquet')} WHERE year(month_end) = 2006) u),
        ey AS (SELECT year(date) AS year, ticker, code FROM evx),
        j AS (SELECT uy.year, uy.ticker, ey.code FROM uy LEFT JOIN ey USING (year, ticker))
        SELECT year, count(DISTINCT ticker) AS tickers, count(DISTINCT CASE WHEN code IS NOT NULL THEN ticker END) AS any_event,
               {shares}
        FROM j GROUP BY 1 ORDER BY 1
    """).fetchdf()


# --------------------------------------------------------------- 3.5 loss_50

def loss_table(con) -> pd.DataFrame:
    start, end = LOSS_WINDOW
    frames = []
    for name in DECILE_FEATURES:
        df = con.execute(f"""
            WITH b AS (
                SELECT d.lag, d.dec_{name} AS decile, l.win_100, l.fwd_12m_return <= -0.5 AS loss_50, l.fwd_12m_return
                FROM {pq('deciles.parquet')} d JOIN {pq('labels12.parquet')} l USING (ticker, month_end)
                WHERE d.month_end BETWEEN DATE '{start}' AND DATE '{end}' AND l.win_100 IS NOT NULL
            ), tot AS (SELECT lag, count(*) AS rows_all, count(decile) AS rows_nn FROM b GROUP BY 1)
            SELECT b.lag, b.decile, count(*) AS rows, count(*) FILTER (WHERE win_100) AS k_win,
                   count(*) FILTER (WHERE loss_50) AS k_loss, median(fwd_12m_return) AS median_fwd_12m,
                   any_value(t.rows_nn) / any_value(t.rows_all) AS coverage
            FROM b JOIN tot t USING (lag) WHERE b.decile IS NOT NULL GROUP BY 1, 2 ORDER BY 1, 2
        """).fetchdf()
        df.insert(0, "feature", name)
        frames.append(df)
    t = pd.concat(frames, ignore_index=True)
    t["win_100_rate"] = t["k_win"] / t["rows"]
    t["loss_50_rate"] = t["k_loss"] / t["rows"]
    t["ratio"] = t["win_100_rate"] / t["loss_50_rate"]
    t["sufficient"] = (t["k_win"] >= MIN_EVENTS_PER_CELL) & (t["k_loss"] >= MIN_EVENTS_PER_CELL)
    return t


def loss_base(con) -> pd.DataFrame:
    start, end = LOSS_WINDOW
    return con.execute(f"""
        SELECT count(*) AS rows, count(*) FILTER (WHERE win_100) AS k_win,
               count(*) FILTER (WHERE fwd_12m_return <= -0.5) AS k_loss, median(fwd_12m_return) AS median_fwd_12m
        FROM {pq('labels12.parquet')}
        WHERE month_end BETWEEN DATE '{start}' AND DATE '{end}' AND win_100 IS NOT NULL
    """).fetchdf()


# --------------------------------------------------------------- 3.1 profile

def profile_numeric(con) -> pd.DataFrame:
    out = []
    for label in LABELS:
        for lag in PROFILE_LAGS:
            aggs = ", ".join(
                f"median({c}) FILTER (WHERE winner) AS w_{c}, count({c}) FILTER (WHERE winner) AS wc_{c}, "
                f"median({c}) AS p_{c}, count({c}) AS pc_{c}, "
                f"avg({c}) FILTER (WHERE winner) AS wa_{c}, avg({c}) AS pa_{c}" for c in NUMERIC)
            r = con.execute(f"""
                SELECT count(*) FILTER (WHERE winner) AS nw, count(*) AS np, {aggs}
                FROM pop_{label} p
                LEFT JOIN fields f ON f.ticker = p.ticker AND f.month_end = last_day(p.month_end - INTERVAL {lag} MONTH)
            """).fetchdf().iloc[0]
            for c in NUMERIC:
                out.append({"label": label, "lag": lag, "field": c, "winners": int(r["nw"]), "population": int(r["np"]),
                            "winner_median": r[f"w_{c}"], "winner_coverage": r[f"wc_{c}"] / r["nw"],
                            "population_median": r[f"p_{c}"], "population_coverage": r[f"pc_{c}"] / r["np"],
                            "winner_mean": r[f"wa_{c}"], "population_mean": r[f"pa_{c}"]})
    return pd.DataFrame(out)


def profile_deciles(con) -> pd.DataFrame:
    out = []
    for label in LABELS:
        for lag in PROFILE_LAGS:
            aggs = ", ".join(
                f"median(dec_{c}) FILTER (WHERE winner) AS wm_{c}, avg(dec_{c}) FILTER (WHERE winner) AS wa_{c}, "
                f"count(dec_{c}) FILTER (WHERE winner) AS wc_{c}, median(dec_{c}) AS pm_{c}, avg(dec_{c}) AS pa_{c}, "
                f"count(dec_{c}) AS pc_{c}" for c in DECILE_FEATURES)
            r = con.execute(f"""
                SELECT count(*) FILTER (WHERE winner) AS nw, count(*) AS np, {aggs}
                FROM pop_{label} p
                LEFT JOIN {pq('deciles.parquet')} d ON d.ticker = p.ticker AND d.month_end = p.month_end AND d.lag = {lag}
            """).fetchdf().iloc[0]
            for c in DECILE_FEATURES:
                out.append({"label": label, "lag": lag, "feature": c, "winners": int(r["nw"]), "population": int(r["np"]),
                            "winner_median_decile": r[f"wm_{c}"], "winner_mean_decile": r[f"wa_{c}"],
                            "winner_coverage": r[f"wc_{c}"] / r["nw"], "population_median_decile": r[f"pm_{c}"],
                            "population_mean_decile": r[f"pa_{c}"], "population_coverage": r[f"pc_{c}"] / r["np"]})
    return pd.DataFrame(out)


def profile_categorical(con) -> pd.DataFrame:
    out = []
    for label in LABELS:
        for cat in CATEGORICAL:
            df = con.execute(f"""
                WITH j AS (SELECT p.winner, f.{cat}::VARCHAR AS bucket FROM pop_{label} p
                           LEFT JOIN fields f ON f.ticker = p.ticker AND f.month_end = p.month_end),
                tot AS (SELECT count(*) FILTER (WHERE winner) AS nw, count(*) AS np,
                               count(bucket) FILTER (WHERE winner) AS nw_nn, count(bucket) AS np_nn FROM j)
                SELECT bucket, count(*) FILTER (WHERE winner) AS winners, count(*) AS population,
                       any_value(t.nw) AS nw, any_value(t.np) AS np, any_value(t.nw_nn) AS nw_nn, any_value(t.np_nn) AS np_nn
                FROM j CROSS JOIN tot t WHERE bucket IS NOT NULL GROUP BY 1 ORDER BY 1
            """).fetchdf()
            df["winner_share"] = df["winners"] / df["nw_nn"]
            df["population_share"] = df["population"] / df["np_nn"]
            df["ratio"] = df["winner_share"] / df["population_share"]
            df["sufficient"] = df["winners"] >= MIN_EVENTS_PER_CELL
            df["winner_coverage"] = df["nw_nn"] / df["nw"]
            df["population_coverage"] = df["np_nn"] / df["np"]
            df.insert(0, "category", cat)
            df.insert(0, "label", label)
            out.append(df.drop(columns=["nw", "np", "nw_nn", "np_nn"]))
    return pd.concat(out, ignore_index=True)


# --------------------------------------------------------------- 3.2 timeline

TL_MEASURES = {
    "price_return": "closeadj at T+k / closeadj at T-0 - 1",
    "rev_growth_yoy": "ARQ revenue growth YoY as of T+k",
    "shares_change": "ARQ sharesbas as of T+k / sharesbas as of T-0 - 1",
    "insider_net_buys_12m": "trailing 12-month net insider buy rows at T+k",
    "ev_total_t12": "trailing 12-month count of the ten 8-K codes at T+k",
}


def timeline(con) -> pd.DataFrame:
    con.execute(f"CREATE TABLE steps AS SELECT unnest([{', '.join(str(k) for k in STEPS)}])::INTEGER AS k")
    out = []
    for label in LABELS:
        con.execute(f"""
            CREATE OR REPLACE TABLE tl AS
            SELECT p.ticker, p.month_end, p.winner, s.k,
                   f.closeadj / f0.closeadj - 1 AS price_return, f.rev_growth_yoy,
                   CASE WHEN f0.sharesbas > 0 THEN f.sharesbas / f0.sharesbas - 1 END AS shares_change, f.insider_net_buys_12m, f.ev_total_t12
            FROM pop_{label} p CROSS JOIN steps s
            JOIN fields f0 ON f0.ticker = p.ticker AND f0.month_end = p.month_end
            LEFT JOIN fields f ON f.ticker = p.ticker AND f.month_end = last_day(p.month_end + to_months(s.k))
        """)
        # population median per calendar month and step, then the median of that over winners' months (aligned on
        # calendar month, weighted by where the winners sit in time)
        for m in TL_MEASURES:
            df = con.execute(f"""
                WITH pm AS (SELECT month_end, k, median({m}) AS pmed, avg({m}) AS pavg, count({m}) AS pn FROM tl GROUP BY 1, 2),
                w AS (SELECT t.k, median(t.{m}) AS wmed, avg(t.{m}) AS wavg, count(t.{m}) AS wn, count(*) AS wrows,
                             median(pm.pmed) AS pop_med, median(pm.pavg) AS pop_avg,
                             count(*) FILTER (WHERE pm.pn > 0) AS pop_months
                      FROM tl t JOIN pm USING (month_end, k) WHERE t.winner GROUP BY 1)
                SELECT k, wmed, wavg, wn, wrows, pop_med, pop_avg, pop_months FROM w ORDER BY k
            """).fetchdf()
            df.insert(0, "measure", m)
            df.insert(0, "label", label)
            out.append(df)
    t = pd.concat(out, ignore_index=True)
    t["winner_coverage"] = t["wn"] / t["wrows"]
    return t.rename(columns={"wmed": "winner_median", "wavg": "winner_mean", "wn": "winner_n", "wrows": "winners",
                             "pop_med": "population_median", "pop_avg": "population_mean",
                             "pop_months": "population_months"})


# --------------------------------------------------------------- 3.3 during move

def during_move(con) -> pd.DataFrame:
    out = []
    for label in LABELS:
        con.execute(f"""
            CREATE OR REPLACE TABLE dm AS
            SELECT p.winner, {", ".join(f"f.ev{c}_f12" for c in CODES)}, f.ev_total_f12,
                   CASE WHEN f.sharesbas > 0 THEN f12.sharesbas / f.sharesbas - 1 END AS shares_change_f12
            FROM pop_{label} p
            LEFT JOIN fields f ON f.ticker = p.ticker AND f.month_end = p.month_end
            LEFT JOIN fields f12 ON f12.ticker = p.ticker AND f12.month_end = last_day(p.month_end + INTERVAL 12 MONTH)
        """)
        for c in [*(f"ev{c}_f12" for c in CODES), "ev_total_f12"]:
            r = con.execute(f"""
                SELECT count(*) FILTER (WHERE winner) AS nw, count(*) AS np,
                       count({c}) FILTER (WHERE winner) AS wc, count({c}) AS pc,
                       avg({c}) FILTER (WHERE winner) AS w_mean, avg({c}) AS p_mean,
                       count(*) FILTER (WHERE winner AND {c} > 0) AS w_any, count(*) FILTER (WHERE {c} > 0) AS p_any
                FROM dm
            """).fetchdf().iloc[0]
            out.append({"label": label, "measure": c, "winners": int(r["nw"]), "population": int(r["np"]),
                        "winner_coverage": r["wc"] / r["nw"], "population_coverage": r["pc"] / r["np"],
                        "winner_mean": r["w_mean"], "population_mean": r["p_mean"],
                        "winner_any_share": r["w_any"] / r["wc"] if r["wc"] else float("nan"),
                        "population_any_share": r["p_any"] / r["pc"] if r["pc"] else float("nan"),
                        "winner_any_events": int(r["w_any"])})
        r = con.execute("""
            SELECT count(*) FILTER (WHERE winner) AS nw, count(*) AS np,
                   count(shares_change_f12) FILTER (WHERE winner) AS wc, count(shares_change_f12) AS pc,
                   median(shares_change_f12) FILTER (WHERE winner) AS w_med, median(shares_change_f12) AS p_med,
                   count(*) FILTER (WHERE winner AND shares_change_f12 > 0.10) AS w_any,
                   count(*) FILTER (WHERE shares_change_f12 > 0.10) AS p_any
            FROM dm
        """).fetchdf().iloc[0]
        out.append({"label": label, "measure": "shares_change_f12", "winners": int(r["nw"]), "population": int(r["np"]),
                    "winner_coverage": r["wc"] / r["nw"], "population_coverage": r["pc"] / r["np"],
                    "winner_mean": r["w_med"], "population_mean": r["p_med"],
                    "winner_any_share": r["w_any"] / r["wc"] if r["wc"] else float("nan"),
                    "population_any_share": r["p_any"] / r["pc"] if r["pc"] else float("nan"),
                    "winner_any_events": int(r["w_any"])})
    t = pd.DataFrame(out)
    t["any_ratio"] = t["winner_any_share"] / t["population_any_share"]
    t["sufficient"] = t["winner_any_events"] >= MIN_EVENTS_PER_CELL
    return t


# --------------------------------------------------------------- 3.4 sector x regime

def sector_regime(con) -> pd.DataFrame:
    out = []
    for label in LABELS:
        df = con.execute(f"""
            WITH c AS (
                SELECT drawdown_bucket, sector, count(*) AS rows, count(*) FILTER (WHERE winner) AS winners FROM pop_{label} GROUP BY 1, 2
            ), b AS (
                SELECT drawdown_bucket, sum(rows) AS b_rows, sum(winners) AS b_winners FROM c GROUP BY 1
            )
            SELECT c.drawdown_bucket, c.sector, c.rows, c.winners, b.b_rows, b.b_winners FROM c JOIN b USING (drawdown_bucket)
            ORDER BY 1, 2
        """).fetchdf()
        df.insert(0, "label", label)
        out.append(df)
    t = pd.concat(out, ignore_index=True)
    t["winner_rate"] = t["winners"] / t["rows"]
    t["bucket_rate"] = t["b_winners"] / t["b_rows"]
    t["winner_share"] = t["winners"] / t["b_winners"]
    t["population_share"] = t["rows"] / t["b_rows"]
    t["ratio"] = t["winner_share"] / t["population_share"]
    t["sufficient"] = t["winners"] >= MIN_EVENTS_PER_CELL
    return t


# --------------------------------------------------------------- report

def fmt(x, kind: str) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    if kind == "pct":
        return f"{100 * x:.1f}%"
    if kind == "musd":
        return f"{x:,.0f}"
    if kind == "usd":
        return f"{x:.2f}"
    if kind == "int":
        return f"{x:.0f}"
    if kind == "cnt":
        return f"{x:.1f}"
    if kind == "yrs":
        return f"{x:.1f}"
    return f"{x:.3f}"


def cov(x) -> str:
    return f"{100 * x:.0f}%"


def ratio_str(r, ok) -> str:
    return f"{r:.2f}" if ok and not pd.isna(r) else "insufficient"


BUCKET_ORDER = ["0-10", "10-20", "20-30", ">30"]


def write_report(evc, lb, lt, pn, pdc, pc, tl, dm, sr, pops) -> None:
    L = ["# Winner anatomy tables — Section 2 Growth, GROWTH-003 session 8", "",
         "Descriptive only (F1): no directions were declared and nothing here passes or fails. Build and holdout",
         "are pooled (F2): 2006-01 to 2024-06 for launch_300 (300% in 24 months), 2006-01 to 2025-06 for win_100",
         "(100% in 12 months). Every comparison is winner versus population at the same month (F3); the population",
         "is every universe stock-month in the window whose label is observable, winners included. D8 (100 winner",
         "events) applies to every ratio; a cell below it says \"insufficient\" (F4). Narrative qualities are out of",
         "scope; 8-K item codes are the recorded proxy (F5). Every number comes from src/anatomy.py over",
         "data/processed/anatomy_fields.parquet, deciles.parquet, labels.parquet, labels12.parquet and",
         "regime.parquet; the unrounded tables are in reports/s8_*.csv. No random element was used.", "",
         "Fields measured in the 12 months AFTER T-0 (section 3.3, the T+k half of the timeline, every column",
         "ending in _f12) are FORWARD-LOOKING. They describe the move. They cannot enter any later scoring model.", ""]
    for label, (_, s, e) in LABELS.items():
        L.append(f"- {label}: window {s[:7]} to {e[:7]}, {pops[label][1]:,} population rows, {pops[label][0]:,} winners "
                 f"({100 * pops[label][0] / pops[label][1]:.2f}%).")
    L.append("")

    # 8-K coverage
    L += ["## 8-K item coverage per code per year", "",
          "Share of universe tickers active in the year with at least one filing carrying the code that year",
          "(events.parquet, Sharadar codes 11, 12, 21, 22, 23, 32, 52, 53, 71, 81 = items 1.01, 1.02, 2.01, 2.02,",
          "2.03, 3.02, 5.02, 5.03, 7.01, 8.01). The modern item numbering starts 2004-08-23, so trailing 12-month",
          "counts are null before 2005-08 and forward 12-month counts are null after 2025-08. The universe starts",
          "2006; the 2004 and 2005 rows use the tickers of the 2006 universe because the T-12 and T-24 windows",
          "reach back into them. \"any\" counts any code in the events table, the ten above or not.", ""]
    hdr = ["year", "tickers", "any"] + list(CODES)
    rows = []
    for _, r in evc.iterrows():
        if r["year"] < 2004:
            continue
        rows.append([int(r["year"]), f"{int(r['tickers']):,}", cov(r["any_event"] / r["tickers"])]
                    + [cov(r[f"t{c}"] / r["tickers"]) for c in CODES])
    L += md_table(hdr, rows)

    # 3.5
    b = lb.iloc[0]
    L += ["## Section 3.5 — win_100 against loss_50 by decile (Matt's S8 addition)", "",
          f"loss_50 = 12-month forward return of -50% or worse, on the existing grid. Pooled {LOSS_WINDOW[0][:7]} to",
          f"{LOSS_WINDOW[1][:7]}, decision month T-0 (lag 0; lags 3, 6, 12 are in reports/s8_loss50_deciles.csv). Base over",
          f"{int(b['rows']):,} rows: win_100 {100 * b['k_win'] / b['rows']:.2f}%, loss_50 {100 * b['k_loss'] / b['rows']:.2f}%, ratio "
          f"{(b['k_win'] / b['k_loss']):.2f}, median 12-month return {100 * b['median_fwd_12m']:.1f}%. Ratio = win_100 rate / loss_50 rate;",
          "\"insufficient\" when either count in the cell is under 100. Coverage = rows with the feature non-null over",
          "all rows at that lag. Decile 1 is the lowest raw value; the direction declared in GROWTH-002 is shown",
          "for orientation only and plays no part here.", ""]
    for name in DECILE_FEATURES:
        t = lt[(lt["feature"] == name) & (lt["lag"] == 0)]
        if t.empty:
            continue
        direction = {**FEATURES, **EXPLORATORY}[name][1]
        L += [f"### {name} (GROWTH-002 direction {direction}; coverage {cov(t['coverage'].iloc[0])})", ""]
        rows = [[int(r["decile"]), f"{int(r['rows']):,}", f"{100 * r['win_100_rate']:.2f}%", int(r["k_win"]),
                 f"{100 * r['loss_50_rate']:.2f}%", int(r["k_loss"]), ratio_str(r["ratio"], r["sufficient"]),
                 f"{100 * r['median_fwd_12m']:.1f}%"] for _, r in t.iterrows()]
        L += md_table(["decile", "rows", "win_100", "k", "loss_50", "k", "ratio", "median 12m"], rows)

    # 3.1 numeric
    L += ["## 3.1 Profile — numeric fields, winner median against population median", "",
          "T-0 is the decision month; T-6 and T-12 are the same tickers six and twelve months earlier, compared with",
          "the population at that earlier month. Coverage (in brackets) is the share of winners, or of the population,",
          "with the field non-null. Field definitions follow the tables.", ""]
    for label in LABELS:
        L += [f"### {label}", ""]
        rows = []
        for c, (kind, _) in NUMERIC.items():
            row = [c]
            for lag in PROFILE_LAGS:
                r = pn[(pn["label"] == label) & (pn["lag"] == lag) & (pn["field"] == c)].iloc[0]
                row += [f"{fmt(r['winner_median'], kind)} ({cov(r['winner_coverage'])})",
                        f"{fmt(r['population_median'], kind)} ({cov(r['population_coverage'])})"]
            rows.append(row)
        L += md_table(["field", "T-0 winners", "T-0 population", "T-6 winners", "T-6 population",
                       "T-12 winners", "T-12 population"], rows)
        L += ["Count fields, mean instead of median (medians of small counts tie; same rows and coverage as above):", ""]
        rows = []
        for c, (kind, _) in NUMERIC.items():
            if kind != "cnt":
                continue
            row = [c]
            for lag in PROFILE_LAGS:
                r = pn[(pn["label"] == label) & (pn["lag"] == lag) & (pn["field"] == c)].iloc[0]
                row += [f"{r['winner_mean']:.2f}", f"{r['population_mean']:.2f}"]
            rows.append(row)
        L += md_table(["field", "T-0 winners", "T-0 population", "T-6 winners", "T-6 population",
                       "T-12 winners", "T-12 population"], rows)
    L += ["Definitions:", ""] + [f"- {c}: {d}" for c, (_, d) in NUMERIC.items()] + [""]

    # 3.1 deciles
    L += ["## 3.1 Profile — GROWTH-002 decile ranks", "",
          "Decile 1 is the lowest raw value within the month and lag (GROWTH-002 rule). The population median is",
          "near 5.5 by construction and is shown because the spec asks for it; the mean carries the same",
          "information with more resolution. Cells read winner / population; coverage in brackets is",
          "winners / population.", ""]
    for label in LABELS:
        L += [f"### {label}", ""]
        rows = []
        for c in DECILE_FEATURES:
            row = [c]
            for lag in PROFILE_LAGS:
                r = pdc[(pdc["label"] == label) & (pdc["lag"] == lag) & (pdc["feature"] == c)].iloc[0]
                row += [f"{fmt(r['winner_median_decile'], 'cnt')} / {fmt(r['population_median_decile'], 'cnt')}",
                        f"{fmt(r['winner_mean_decile'], 'x')} / {fmt(r['population_mean_decile'], 'x')}",
                        f"{cov(r['winner_coverage'])} / {cov(r['population_coverage'])}"]
            rows.append(row)
        L += md_table(["feature", "T-0 median", "T-0 mean", "T-0 cov", "T-6 median", "T-6 mean", "T-6 cov",
                       "T-12 median", "T-12 mean", "T-12 cov"], rows)

    # 3.1 categorical
    L += ["## 3.1 Profile — categorical buckets at T-0", "",
          "Ratio = winner share of the bucket / population share of the bucket, among rows with the field non-null.",
          "D8 on the winners in the bucket. Coverage is stated per category. " + CATEGORICAL_NOTE,
          "ceo_change_12m is any 5.02 filing, which also covers director elections and compensation arrangements,",
          "so it is true for most rows in most years; the spec names it a proxy and it is a weak one.", ""]
    for label in LABELS:
        L += [f"### {label}", ""]
        for cat in CATEGORICAL:
            t = pc[(pc["label"] == label) & (pc["category"] == cat)]
            if t.empty:
                continue
            L += [f"{cat} (coverage winners {cov(t['winner_coverage'].iloc[0])}, population {cov(t['population_coverage'].iloc[0])})", ""]
            rows = [[r["bucket"], int(r["winners"]), f"{100 * r['winner_share']:.1f}%", f"{int(r['population']):,}",
                     f"{100 * r['population_share']:.1f}%", ratio_str(r["ratio"], r["sufficient"])] for _, r in t.iterrows()]
            L += md_table(["bucket", "winners", "winner share", "population", "population share", "ratio"], rows)

    # 3.2 timeline
    L += ["## 3.2 Timeline — winners' median path, T-24 to T+24 in 3-month steps", "",
          "Winner cell = median over winners of the measure at T+k for that ticker. Population cell = the population",
          "median at the same calendar month, taken as the median over winners of the population median at each",
          "winner's month + k (aligned on calendar month, so the overlay carries the winners' distribution in time).",
          "Price return and share change are relative to the ticker's own T-0. Steps with k > 0 are forward-looking.",
          "Coverage table: winners with the measure non-null at that step; population months = winner months with a",
          "population value.", ""]
    for label in LABELS:
        L += [f"### {label}", ""]
        rows, crow = [], []
        for k in STEPS:
            row, cr = [f"{k:+d}"], [f"{k:+d}"]
            for m in TL_MEASURES:
                r = tl[(tl["label"] == label) & (tl["measure"] == m) & (tl["k"] == k)].iloc[0]
                kind = "pct" if m in ("price_return", "rev_growth_yoy", "shares_change") else "cnt"
                row += [fmt(r["winner_median"], kind), fmt(r["population_median"], kind)]
                cr += [f"{int(r['winner_n']):,} ({cov(r['winner_coverage'])})"]
            rows.append(row)
            crow.append(cr)
        hdr = ["k"] + [f"{m} W" if i == 0 else f"{m} P" for m in TL_MEASURES for i in (0, 1)]
        L += md_table(hdr, rows)
        L += ["Count measures, mean path (winner mean; population = median over winners of the population mean at",
              "the same calendar month):", ""]
        rows = []
        for k in STEPS:
            row = [f"{k:+d}"]
            for m in ("insider_net_buys_12m", "ev_total_t12"):
                r = tl[(tl["label"] == label) & (tl["measure"] == m) & (tl["k"] == k)].iloc[0]
                row += [f"{r['winner_mean']:.2f}", f"{r['population_mean']:.2f}"]
            rows.append(row)
        L += md_table(["k", "insider_net_buys_12m W", "insider_net_buys_12m P", "ev_total_t12 W", "ev_total_t12 P"], rows)
        L += ["Coverage (winners non-null, share of winners):", ""]
        L += md_table(["k"] + list(TL_MEASURES), crow)
    L += ["Measures:", ""] + [f"- {m}: {d}" for m, d in TL_MEASURES.items()] + [""]

    # 3.3 during move
    L += ["## 3.3 During the move — 8-K counts and share count change in the 12 months after T-0 (FORWARD-LOOKING)", "",
          "Mean filings per row and the share of rows with at least one, winners against population; ratio = winner",
          "share with at least one / population share, D8 on the winners with at least one. The last row is the",
          "change in ARQ shares outstanding from the quarter known at T-0 to the quarter known at T+12; its cells are",
          "the median change and the share of rows with more than 10% growth. Coverage in brackets.", ""]
    for label in LABELS:
        L += [f"### {label}", ""]
        rows = []
        for _, r in dm[dm["label"] == label].iterrows():
            is_sh = r["measure"] == "shares_change_f12"
            kind = "pct" if is_sh else "cnt"
            rows.append([r["measure"], f"{fmt(r['winner_mean'], kind)} ({cov(r['winner_coverage'])})",
                         f"{fmt(r['population_mean'], kind)} ({cov(r['population_coverage'])})",
                         f"{100 * r['winner_any_share']:.1f}%", f"{100 * r['population_any_share']:.1f}%",
                         ratio_str(r["any_ratio"], r["sufficient"])])
        L += md_table(["measure", "winners mean (median for shares)", "population", "winners >=1 (>10% for shares)",
                       "population", "ratio"], rows)

    # 3.4 sector x regime
    L += ["## 3.4 Sector x regime — winner rate by sector within each SPY drawdown bucket", "",
          "Rate = winners / population rows in the cell; share ratio = the sector's share of the bucket's winners /",
          "its share of the bucket's rows. D8 on the cell's winners. The bucket line gives the bucket's own rate.", ""]
    for label in LABELS:
        L += [f"### {label}", ""]
        t = sr[sr["label"] == label]
        for bkt in BUCKET_ORDER:
            tb = t[t["drawdown_bucket"] == bkt]
            if tb.empty:
                continue
            L += [f"Drawdown {bkt}: {int(tb['b_rows'].iloc[0]):,} rows, {int(tb['b_winners'].iloc[0]):,} winners, "
                  f"rate {100 * tb['bucket_rate'].iloc[0]:.2f}%", ""]
            rows = [[r["sector"], f"{int(r['rows']):,}", int(r["winners"]),
                     f"{100 * r['winner_rate']:.2f}%" if r["sufficient"] else "insufficient",
                     ratio_str(r["ratio"], r["sufficient"])] for _, r in tb.iterrows()]
            L += md_table(["sector", "rows", "winners", "rate", "share ratio"], rows)

    reading = REPORTS_DIR / "anatomy_reading.md"
    if reading.exists():
        L += ["", reading.read_text().rstrip(), ""]
    (REPORTS_DIR / "anatomy_tables.md").write_text("\n".join(L))


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET threads = 1")  # deterministic floating sums in avg(); 4 threads moved means by ~1e-13
    print("fields", flush=True)
    build_fields(con)
    print("populations", flush=True)
    build_populations(con)
    pops = {label: tuple(con.execute(f"SELECT count(*) FILTER (WHERE winner), count(*) FROM pop_{label}").fetchone())
            for label in LABELS}
    print("tables", flush=True)
    evc = events_coverage(con)
    lb, lt = loss_base(con), loss_table(con)
    pn, pdc, pc = profile_numeric(con), profile_deciles(con), profile_categorical(con)
    tl, dm, sr = timeline(con), during_move(con), sector_regime(con)
    for name, df in [("s8_events_coverage", evc), ("s8_loss50_base", lb), ("s8_loss50_deciles", lt),
                     ("s8_profile_numeric", pn), ("s8_profile_deciles", pdc), ("s8_profile_categorical", pc),
                     ("s8_timeline", tl), ("s8_during_move", dm), ("s8_sector_regime", sr)]:
        df.to_csv(REPORTS_DIR / f"{name}.csv", index=False)
    write_report(evc, lb, lt, pn, pdc, pc, tl, dm, sr, pops)
    for label in LABELS:
        print(f"{label}: {pops[label][0]:,} winners in {pops[label][1]:,} rows")
    print(f"RESULT: PASS — {REPORTS_DIR / 'anatomy_tables.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
