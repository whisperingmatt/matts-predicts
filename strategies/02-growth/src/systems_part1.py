"""GROWTH-004 S10 — engine sanity check (section 4) and systems S-A, S-B, S-C (section 2).

    python -m src.systems_part1 [--no-build]

Runs, in order: data prep (src.engine.build_data, skipped with --no-build
when data/processed/bars.parquet exists), the section 4 sanity check
(S-C on AAPL 2010 to 2019 in the engine, split-adjusted raw prices, two
stop conventions), then S-A CANSLIM, S-B Minervini, S-C Weinstein on the
full universe 2006-01 to 2025-06, continuous across build and holdout
(G7), metrics per window (G8), trades with the feature row at entry to
data/processed/trades_<system>.parquet (G9).

Output: reports/engine_sanity.md (+ tradingview/weinstein_stage2_aapl.pine
and the TradingView instructions), reports/systems_part1.md,
reports/s10_*.csv. Every proxy for an "as written" rule is listed in
SUBSTITUTIONS below, in the report, and in decisions.md.

The TradingView leg of section 4 needs Matt's TradingView account; the
engine leg and the Pine script are produced here, and every system
result is labeled PROVISIONAL until the two trade lists are reconciled.
"""
from __future__ import annotations

import sys
import time

import duckdb
import numpy as np
import pandas as pd

from src.config import PROCESSED_DIR, REPORTS_DIR, STRATEGY_DIR
from src.engine import (CAPITAL, WINDOWS, Bars, Engine, Position, System, attach_features, build_data, pq,
                        verdict, window_metrics)
from src.stats import md_table

RUN_START, RUN_END = "2006-01-01", "2025-06-30"
LOAD_START = "2005-01-01"          # bars loaded into memory from here; indicators were computed over full history
SANITY_START, SANITY_END = "2010-01-01", "2019-12-31"
I_TEST_FROM = "2013-01-01"

SUBSTITUTIONS = [
    ("all", "Universe membership at signal", "GROWTH-001 universe by month end", "a stock is eligible on a date when a universe row exists for the latest month end on or before it"),
    ("all", "Next-open fill", "next day's open", "the ticker's next bar after the signal; a ticker with no bar the next day fills at its next bar within five trading days, then the order lapses; a new evaluation replaces unfilled orders"),
    ("all", "Slippage tier", "marketcap >= $2B", "daily.marketcap on the fill day (USD millions); unknown market cap takes the 0.25% tier"),
    ("all", "Equal weight", "equal weight across slots", "each entry sized to equity / slots at the fill, capped by cash; whole shares"),
    ("all", "Candidate order", "not specified", "when candidates exceed free slots, the highest relative-strength rank enters first; ties by ticker"),
    ("all", "Delisting while held", "not specified", "when a held ticker has no further bar in the data it is closed at its last close, small-cap slippage, reason delisted"),
    ("all", "Open positions at 2025-06-30", "not specified", "closed at the last close, reason end_of_test, kept in the trade stats and flagged"),
    ("all", "Expectancy per trade", "expectancy % per trade after costs", "for the pass test: net profit over capital deployed in the window's closed trade rows; the plain mean of row returns is shown beside it (partial sales are separate rows)"),
    ("all", "Trade window", "per window", "a trade belongs to the window of its exit date; the equity curve is continuous across windows"),
    ("S-A", "C quarterly EPS YoY >= 25%, higher than the prior quarter's YoY", "quarterly EPS", "ARQ eps (basic, split-adjusted to today's basis) by filing date; YoY needs a positive year-ago quarter; prior quarter's YoY on the same basis"),
    ("S-A", "A annual EPS growth >= 25% each of the last 3 fiscal years", "3 fiscal years", "12 trailing ARQ quarters summed into three years as the spec directs, which gives two annual growth rates, both >= 25%, with positive bases; quarter spacing checked (q4 at 11-13 months, q8 at 23-25, q11 at 32-34)"),
    ("S-A", "N price within 5% of 52-week high", "52-week high", "implied by the entry: the close is a new 52-week closing high"),
    ("S-A", "S shares not rising over 8 quarters or buyback", "shares outstanding", "ARQ sharesbas now <= sharesbas eight quarters earlier, no tolerance"),
    ("S-A", "L relative strength percentile >= 80", "O'Neil RS rating", "percent rank of the 252-trading-day return among universe members on the evaluation day"),
    ("S-A", "I institutional % rising QoQ (2013+)", "institutional ownership", "features.parquet inst_pct > inst_pct_prev at the latest month end on or before the evaluation day (13F, 45-day lag); the test is skipped before 2013-01-01 and both segments are reported"),
    ("S-A", "M SPY above 50-day and 200-day", "SPY", "funds SPY closeadj above both SMAs on the evaluation day"),
    ("S-A", "Entry: close at a new 52-week high, volume >= 1.5x 50-day average", "new 52-week high", "Friday close above the highest close of the prior 252 bars (closing basis), Friday volume >= 1.5x the 50-day average volume"),
    ("S-A", "3 weeks / week 8", "weeks", "15 and 40 trading days from the entry bar"),
    ("S-A", "Take profit at +20%", "take profit", "a limit at 1.20x entry, filled at the limit or the open if gapped above; reaching it inside 15 bars cancels the limit and switches to the 50-day SMA trailing exit"),
    ("S-B", "VCP breakout (GROWTH-001 H14) then a close above the pivot on volume >= 1.25x 50-day average", "VCP + pivot", "an H14 pattern day (close above the prior 20-day high after three successive 20-day contractions in ATR ratio and average volume) inside the evaluation week with that day's volume >= 1.25x the 50-day average; pivot = the prior 20-day high on that day; Friday close still above the pivot; the trend template checked on the Friday"),
    ("S-B", "200-day SMA rising for >= 1 month", "rising", "SMA200 today above SMA200 22 trading days earlier"),
    ("S-B", "RS percentile >= 70", "RS", "same 252-day return percent rank as S-A"),
    ("S-B", "Trailing exit on the remainder", "remainder", "the 50-day and 20-day SMA exits apply only after the half sale at +14%; before it the 7% stop (and the 10% hard stop) are the only exits"),
    ("S-B", "Close below 20-day SMA on above-average volume", "above average", "volume above the 50-day average"),
    ("S-C", "Weekly bars", "weekly", "Monday-to-Friday weeks from daily bars; close = last trading day, volume = sum"),
    ("S-C", "30-week SMA flattened or turned up", "flattened", "SMA30 this week >= SMA30 four weeks earlier"),
    ("S-C", "Weekly volume >= 2x 26-week average", "26-week average", "26 weeks including the current one (TradingView ta.sma convention)"),
    ("S-C", "RS vs SPY positive and rising", "rising", "26-week relative return above zero and above the prior week's value"),
    ("S-C", "Stage 3/4 exit", "SMA flat or declining", "weekly close below SMA30 with SMA30 <= its value four weeks earlier"),
    ("S-C", "Regime", "SPY below its 30-week SMA", "SPY weekly close (closeadj) below its 30-week SMA on the evaluation week: no new entries"),
]


def wk(d: np.datetime64) -> np.datetime64:
    return d


# ------------------------------------------------------------------ signals

def build_signals(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("SET threads = 1")
    con.execute(f"CREATE TABLE cal AS SELECT date FROM {pq('spy.parquet')} WHERE date >= DATE '{LOAD_START}' ORDER BY date")
    con.execute("CREATE TABLE week_ends AS SELECT max(date) AS date FROM cal GROUP BY date_trunc('week', date)")
    con.execute("CREATE TABLE wmap AS SELECT date AS cal_week_end, date_trunc('week', date)::DATE AS week_start FROM week_ends")
    con.execute(f"""
        CREATE TABLE spy AS SELECT s.*, (c > sma50 AND c > sma200) AS canslim_m FROM {pq('spy.parquet')} s
    """)
    # relative strength: 252-bar return percent rank among members, on every week end
    con.execute(f"""
        CREATE TABLE rs AS
        WITH r AS (
            SELECT ticker, date, member, c / lag(c, 252) OVER (PARTITION BY ticker ORDER BY date) - 1 AS ret252
            FROM {pq('bars.parquet')}
        )
        SELECT ticker, date, ret252,
               percent_rank() OVER (PARTITION BY date ORDER BY ret252) AS rs_pct
        FROM r WHERE member AND ret252 IS NOT NULL AND date IN (SELECT date FROM week_ends)
    """)
    # S-A fundamentals by filing date
    con.execute(f"""
        CREATE TABLE arq AS
        SELECT ticker, calendardate, date AS filed, eps, sharesbas
        FROM read_parquet('{(STRATEGY_DIR / 'data' / 'raw' / 'fundamentals.parquet').as_posix()}')
        WHERE dimension = 'ARQ' AND ticker IN (SELECT DISTINCT ticker FROM {pq('universe.parquet')})
        QUALIFY row_number() OVER (PARTITION BY ticker, calendardate ORDER BY date) = 1
    """)
    lags = ", ".join(f"lag(eps, {j}) OVER w AS e{j}" for j in range(1, 12))
    con.execute(f"""
        CREATE TABLE fund AS
        WITH s AS (
            SELECT *, {lags}, lag(sharesbas, 8) OVER w AS sh8,
                   lag(calendardate, 4) OVER w AS cd4, lag(calendardate, 8) OVER w AS cd8, lag(calendardate, 11) OVER w AS cd11,
                   lag(calendardate, 5) OVER w AS cd5
            FROM arq WINDOW w AS (PARTITION BY ticker ORDER BY calendardate)
        )
        SELECT ticker, calendardate, filed,
               (e4 > 0 AND eps / e4 - 1 >= 0.25 AND e5 > 0 AND e1 / e5 - 1 < eps / e4 - 1
                AND datediff('month', cd4, calendardate) BETWEEN 11 AND 13 AND datediff('month', cd5, calendardate) BETWEEN 14 AND 16) AS c_ok,
               (e8 IS NOT NULL AND e11 IS NOT NULL AND (e4 + e5 + e6 + e7) > 0 AND (e8 + e9 + e10 + e11) > 0
                AND (eps + e1 + e2 + e3) / (e4 + e5 + e6 + e7) - 1 >= 0.25
                AND (e4 + e5 + e6 + e7) / (e8 + e9 + e10 + e11) - 1 >= 0.25
                AND datediff('month', cd4, calendardate) BETWEEN 11 AND 13 AND datediff('month', cd8, calendardate) BETWEEN 23 AND 25
                AND datediff('month', cd11, calendardate) BETWEEN 32 AND 34) AS a_ok,
               (sh8 > 0 AND sharesbas <= sh8 AND datediff('month', cd8, calendardate) BETWEEN 23 AND 25) AS s_ok
        FROM s
    """)
    con.execute(f"""
        CREATE TABLE inst AS SELECT ticker, month_end, inst_pct > inst_pct_prev AS i_ok
        FROM {pq('features.parquet')} WHERE lag = 0 AND inst_pct IS NOT NULL AND inst_pct_prev IS NOT NULL
    """)
    con.execute(f"""
        CREATE TABLE sig_a AS
        SELECT b.date, b.ticker, r.rs_pct AS rank,
               CASE WHEN b.date >= DATE '{I_TEST_FROM}' THEN 'with_I' ELSE 'no_I' END AS segment
        FROM {pq('bars.parquet')} b
        JOIN rs r USING (ticker, date)
        JOIN spy s ON s.date = b.date
        ASOF LEFT JOIN fund f ON f.ticker = b.ticker AND f.filed <= b.date
        ASOF LEFT JOIN inst i ON i.ticker = b.ticker AND i.month_end <= b.date
        WHERE b.member AND b.n252 = 252 AND b.c > b.chigh252_prev AND b.v >= 1.5 * b.vol50
          AND r.rs_pct >= 0.80 AND s.canslim_m
          AND coalesce(f.c_ok, FALSE) AND coalesce(f.a_ok, FALSE) AND coalesce(f.s_ok, FALSE)
          AND f.filed > b.date - INTERVAL 16 MONTH
          AND (b.date < DATE '{I_TEST_FROM}' OR (coalesce(i.i_ok, FALSE) AND i.month_end > b.date - INTERVAL 45 DAY))
    """)
    # S-B: template on the Friday, H14 day inside the week with volume >= 1.25x vol50, Friday close above the pivot
    con.execute(f"""
        CREATE TABLE sig_b AS
        WITH h AS (
            SELECT ticker, date AS h14_date, high20_prev AS pivot_px FROM {pq('bars.parquet')}
            WHERE h14_day AND v >= 1.25 * vol50
        )
        SELECT b.date, b.ticker, r.rs_pct AS rank, max(h.pivot_px) AS pivot_px, max(h.h14_date) AS h14_date
        FROM {pq('bars.parquet')} b
        JOIN rs r USING (ticker, date)
        JOIN h ON h.ticker = b.ticker AND h.h14_date > b.date - INTERVAL 7 DAY AND h.h14_date <= b.date
        WHERE b.member AND b.n252 = 252 AND b.rn >= 223
          AND b.c > b.sma150 AND b.c > b.sma200 AND b.sma150 > b.sma200 AND b.sma200 > b.sma200_lag22
          AND b.sma50 > b.sma150 AND b.sma50 > b.sma200 AND b.c > b.sma50
          AND b.c >= 1.30 * b.low252 AND b.c >= 0.75 * b.high252 AND r.rs_pct >= 0.70
          AND b.c > h.pivot_px
        GROUP BY 1, 2, 3
    """)
    for name, wtable, spycol in [("sig_c", "weekly.parquet", "sma30"), ("sig_c_raw", "weekly_raw.parquet", "sma30_raw")]:
        con.execute(f"""
            CREATE TABLE {name} AS
            SELECT m.cal_week_end AS date, w.ticker, w.rs26 AS rank
            FROM {pq(wtable)} w
            JOIN wmap m ON m.week_start = w.week_start
            JOIN {pq('bars.parquet')} b ON b.ticker = w.ticker AND b.date = w.week_end
            WHERE b.member AND w.wn >= 34
              AND w.wclose > w.sma30 AND w.prev_close <= w.prev_sma30
              AND w.sma30 >= w.sma30_lag4 AND w.wclose > w.base_high
              AND w.wvol >= 2 * w.vol26 AND w.rs26 > 0 AND w.rs26 > w.rs26_prev
        """)
    for t in ["rs", "sig_a", "sig_b", "sig_c", "sig_c_raw"]:
        print(f"  {t}: {con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:,} rows", flush=True)


def signal_dict(con, table: str, extra: list[str] | None = None) -> dict:
    cols = ", ".join(["date", "ticker", "rank"] + (extra or []))
    df = con.execute(f"SELECT {cols} FROM {table} ORDER BY date, ticker").fetchdf()
    out: dict = {}
    for row in df.itertuples(index=False):
        out.setdefault(np.datetime64(row.date, "D"), []).append(tuple(row)[1:])
    return out


# ------------------------------------------------------------------ systems

class Canslim(System):
    name, slots = "S-A_canslim", 10

    def __init__(self, signals: dict, week_ends: set, spy_m: dict):
        self.signals, self.week_ends, self.spy_m = signals, week_ends, spy_m

    def eval_days(self, calendar):
        return {d for d in calendar if d in self.week_ends}

    def regime_ok(self, d):
        return bool(self.spy_m.get(d, False))

    def candidates(self, d, held):
        return [(t, r) for t, r, *_ in self.signals.get(d, []) if t not in held]

    def on_entry(self, pos, bars, i):
        pos.stop, pos.target = pos.entry_price * 0.92, pos.entry_price * 1.20
        pos.state = {"trail": False}

    def intraday(self, pos, bars, i):
        o, h, l = bars.cols["o"][i], bars.cols["h"][i], bars.cols["l"][i]
        if l <= pos.stop:
            return [("stop_8pct", min(pos.stop, o), 1.0)]
        if pos.target is not None and h >= pos.target:
            if pos.bars_held < 15:
                pos.target, pos.state["trail"] = None, True   # +20% inside 3 weeks: hold, trail on the 50-day
                return []
            return [("take_profit_20pct", max(pos.target, o), 1.0)]
        return []

    def on_close(self, pos, bars, i, d):
        if (pos.state.get("trail") or pos.bars_held > 40) and bars.cols["c"][i] < bars.cols["sma50"][i]:
            return "close_below_sma50"
        return None


class Minervini(System):
    name, slots = "S-B_minervini", 10

    def __init__(self, signals: dict, week_ends: set):
        self.signals, self.week_ends = signals, week_ends

    def eval_days(self, calendar):
        return {d for d in calendar if d in self.week_ends}

    def candidates(self, d, held):
        return [(t, r) for t, r, *_ in self.signals.get(d, []) if t not in held]

    def on_entry(self, pos, bars, i):
        pos.stop, pos.stop2, pos.target = pos.entry_price * 0.93, pos.entry_price * 0.90, pos.entry_price * 1.14
        pos.state = {"partial": False}

    def intraday(self, pos, bars, i):
        o, h, l = bars.cols["o"][i], bars.cols["h"][i], bars.cols["l"][i]
        eff = max(pos.stop, pos.stop2)
        if l <= eff:
            reason = "breakeven_stop" if pos.state["partial"] else "stop_7pct"
            return [(reason, min(eff, o), 1.0)]
        if not pos.state["partial"] and h >= pos.target:
            pos.state["partial"], pos.stop = True, pos.entry_price
            return [("half_at_2R", max(pos.target, o), 0.5)]
        return []

    def on_close(self, pos, bars, i, d):
        if not pos.state["partial"]:
            return None
        c, v = bars.cols["c"][i], bars.cols["v"][i]
        if c < bars.cols["sma50"][i]:
            return "close_below_sma50"
        if c < bars.cols["sma20"][i] and v > bars.cols["vol50"][i]:
            return "close_below_sma20_volume"
        return None


class Weinstein(System):
    name, slots = "S-C_weinstein", 10

    def __init__(self, signals: dict, week_ends: set, weekly: dict, spy_ok: dict, raw: bool = False, weekly_stops: bool = False,
                 slots: int = 10, name: str | None = None):
        self.signals, self.week_ends, self.weekly, self.spy_ok = signals, week_ends, weekly, spy_ok
        self.raw, self.weekly_stops, self.slots = raw, weekly_stops, slots
        if name:
            self.name = name

    def eval_days(self, calendar):
        return {d for d in calendar if d in self.week_ends}

    def regime_ok(self, d):
        return bool(self.spy_ok.get(d, False))

    def candidates(self, d, held):
        return [(t, r) for t, r, *_ in self.signals.get(d, []) if t not in held]

    def on_entry(self, pos, bars, i):
        pos.stop = pos.entry_price * 0.90

    def intraday(self, pos, bars, i):
        d = bars.date[i]
        if self.weekly_stops:
            if d not in self.week_ends:
                return []
            w = self.weekly.get((pos.ticker, d))
            if w is None:
                return []
            wlow, wopen = w[3], w[4]
            if wlow <= pos.stop:
                return [("stop_10pct", min(pos.stop, wopen), 1.0)]
            return []
        return self._daily_stop(pos, bars, i)

    def _daily_stop(self, pos, bars, i):
        sfx = "_raw" if self.raw else ""
        o, l = bars.cols["o" + sfx][i], bars.cols["l" + sfx][i]
        if l <= pos.stop:
            return [("stop_10pct", min(pos.stop, o), 1.0)]
        return []

    def on_close(self, pos, bars, i, d):
        if d not in self.week_ends:
            return None
        w = self.weekly.get((pos.ticker, d))
        if w is None or np.isnan(w[1]) or np.isnan(w[2]):
            return None
        if w[0] < w[1] and w[1] <= w[2]:
            return "stage3_close_below_sma30"
        return None


def weekly_dict(con, table: str, tickers: list[str] | None = None) -> dict:
    """(ticker, calendar week end) -> (wclose, sma30, sma30_lag4, wlow, wopen), weeks from LOAD_START."""
    where = "AND w.ticker IN (" + ",".join(f"'{t}'" for t in tickers) + ")" if tickers else ""
    res = con.execute(f"""
        SELECT w.ticker, m.cal_week_end, w.wclose, w.sma30, w.sma30_lag4, w.wlow, w.wopen
        FROM {pq(table)} w JOIN wmap m ON m.week_start = w.week_start
        WHERE w.week_end >= DATE '{LOAD_START}' {where}
    """).fetchnumpy()
    keys = zip(np.asarray(res["ticker"]).astype(str), np.asarray(res["cal_week_end"]).astype("datetime64[D]"))
    vals = zip(*(np.ma.filled(res[c], np.nan) if np.ma.isMaskedArray(res[c]) else res[c]
                 for c in ("wclose", "sma30", "sma30_lag4", "wlow", "wopen")))
    return {k: tuple(float(x) for x in v) for k, v in zip(keys, vals)}


# ------------------------------------------------------------------ report helpers

def pct(x, nd=1):
    return "n/a" if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))) else f"{100 * x:.{nd}f}%"


def f2(x):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else ("inf" if isinstance(x, float) and np.isinf(x) else f"{x:.2f}")


def metrics_rows(m: dict) -> list[list[str]]:
    return [["trades", str(m["trades"])], ["win rate", pct(m["win_rate"])], ["avg winner", pct(m["avg_winner"])],
            ["avg loser", pct(m["avg_loser"])], ["expectancy per trade row (mean return)", pct(m["expectancy"], 2)],
            ["expectancy per dollar (net profit / capital deployed, the pass test)", pct(m["expectancy_dollar"], 2)],
            ["profit factor", f2(m["profit_factor"])], ["CAGR", pct(m["cagr"])], ["total return", pct(m["total_return"])],
            ["max drawdown", pct(m["max_drawdown"])], ["worst 12-month", pct(m["worst_12m"])], ["Sharpe (rf 0)", f2(m["sharpe"])],
            ["turnover (annual)", f2(m["turnover"])], ["avg holding days", f2(m["avg_holding_days"])],
            ["SPY CAGR", pct(m["spy_cagr"])], ["SPY max drawdown", pct(m["spy_max_drawdown"])],
            ["equity start / end", f"{m['equity_start']:,.0f} / {m['equity_end']:,.0f}"]]


def trade_table(tr: pd.DataFrame, raw_cols=True) -> list[str]:
    rows = [[str(r.entry_date)[:10], f"{r.entry_price:.2f}", str(r.exit_date)[:10], f"{r.exit_price:.2f}", r.exit_reason,
             pct(r.ret, 2), str(int(r.holding_days))] for r in tr.itertuples(index=False)]
    return md_table(["entry", "entry px", "exit", "exit px", "reason", "return", "days"], rows)


PINE = '''//@version=5
// GROWTH-004 section 4 sanity check: S-C Weinstein Stage 2 on AAPL, weekly chart.
// Cost model: 0.10% commission + 0.10% slippage per side folded into a 0.20% commission; slippage 0 ticks.
strategy("GROWTH-004 S-C Weinstein sanity", overlay=true, initial_capital=100000,
     default_qty_type=strategy.percent_of_equity, default_qty_value=100,
     commission_type=strategy.commission.percent, commission_value=0.2, slippage=0,
     process_orders_on_close=false, calc_on_every_tick=false, pyramiding=0)
startDate = input.time(timestamp("2010-01-01T00:00:00"), "Start")
endDate   = input.time(timestamp("2019-12-31T23:59:00"), "End")
inRange   = time >= startDate and time <= endDate
sma30     = ta.sma(close, 30)
spyClose  = request.security("AMEX:SPY", "W", close)
spySma30  = request.security("AMEX:SPY", "W", ta.sma(close, 30))
rs26      = (close / close[26]) / (spyClose / spyClose[26]) - 1
baseHigh  = ta.highest(close[1], 26)
vol26     = ta.sma(volume, 26)
entrySig  = ta.crossover(close, sma30) and sma30 >= sma30[4] and close > baseHigh and volume >= 2 * vol26 and rs26 > 0 and rs26 > rs26[1] and spyClose > spySma30
exitSig   = close < sma30 and sma30 <= sma30[4]
if inRange and entrySig and strategy.position_size == 0
    strategy.entry("L", strategy.long)
if strategy.position_size > 0
    strategy.exit("stop", "L", stop=strategy.position_avg_price * 0.90)
    if exitSig
        strategy.close("L", comment="stage3")
plot(sma30, color=color.orange)
'''


SUPPLEMENTARY = "ACN"   # large cap with an S-C signal in 2010-2019, alphabetically first among those; fills get tested here


def funnel(con, ticker: str) -> pd.DataFrame:
    """Every weekly crossover above the 30-week SMA for the ticker in the sanity window, with each entry condition."""
    return con.execute(f"""
        SELECT w.week_end, m.cal_week_end, round(w.wclose, 2) AS close, round(w.sma30, 2) AS sma30, round(w.sma30_lag4, 2) AS sma30_4w_ago,
               round(w.base_high, 2) AS base_high, round(w.wvol / w.vol26, 2) AS vol_x_26w, round(w.rs26, 3) AS rs26, round(w.rs26_prev, 3) AS rs26_prev,
               s.wclose_raw > s.sma30_raw AS spy_above_30w,
               (w.sma30 >= w.sma30_lag4 AND w.wclose > w.base_high AND w.wvol >= 2 * w.vol26 AND w.rs26 > 0 AND w.rs26 > w.rs26_prev
                AND s.wclose_raw > s.sma30_raw) AS entry
        FROM {pq('weekly_raw.parquet')} w
        JOIN wmap m ON m.week_start = w.week_start
        JOIN {pq('spy_weekly.parquet')} s ON s.week_start = w.week_start
        WHERE w.ticker = '{ticker}' AND w.week_end BETWEEN DATE '{SANITY_START}' AND DATE '{SANITY_END}'
          AND w.wclose > w.sma30 AND w.prev_close <= w.prev_sma30
        ORDER BY 1
    """).fetchdf()


def write_sanity(tr_weekly: pd.DataFrame, tr_daily: pd.DataFrame, n_sig: int, sig_dates: list, fun: pd.DataFrame,
                 sup: dict) -> None:
    (STRATEGY_DIR / "tradingview").mkdir(exist_ok=True)
    (STRATEGY_DIR / "tradingview" / "weinstein_stage2_aapl.pine").write_text(PINE)
    L = ["# Engine sanity check — GROWTH-004 section 4 (S-C Weinstein on AAPL, 2010-01 to 2019-12)", "",
         "Status: ENGINE LEG COMPLETE, TRADINGVIEW LEG PENDING. The TradingView Strategy Tester cannot be run from",
         "Claude Code on the web (it needs Matt's TradingView login in a browser). The engine trade list, the Pine",
         "script, and the exact settings are below; the reconciliation section at the end is to be filled after the",
         "TradingView run. Until it is, every result in reports/systems_part1.md is PROVISIONAL.", "",
         "## Engine run", "",
         "Split-adjusted raw prices (Sharadar open, high, low, close, the same basis as TradingView's default,",
         "dividends unadjusted), weekly bars Monday to Friday, one slot, $100,000, 100% of equity per trade, costs",
         "0.10% commission + 0.10% slippage per side (AAPL is above $2B throughout). Entry on the week's close when",
         "the weekly close crosses above the 30-week SMA, the SMA is at or above its value four weeks earlier, the",
         "close is above the highest close of the prior 26 weeks, weekly volume is at least twice the 26-week",
         "average (current week included), the 26-week relative return against SPY is positive and above the prior",
         "week's, and SPY's weekly close is above its own 30-week SMA. Fill at the next Monday open. Exit at the",
         "next open after a weekly close below the 30-week SMA with the SMA at or below its value four weeks",
         "earlier; protective stop 10% below the fill.", "",
         f"Entry signals on AAPL in the window (position or not): {n_sig}" + (" — " + ", ".join(str(d) for d in sig_dates) if sig_dates else "") + ".", "",
         "### Crossover weeks and why they did or did not enter", "",
         "Every week in which AAPL's weekly close crossed above its 30-week SMA, with each entry condition. This is",
         "the table to compare against TradingView bar by bar when the trade lists are empty: the SMA, the prior",
         "26-week high close, the volume multiple of the 26-week average, the 26-week relative return against SPY.", ""]
    L += md_table(["week end", "close", "SMA30", "SMA30 4w ago", "26w high close", "vol / 26w avg", "RS26", "RS26 prev", "SPY > 30w", "entry"],
                  [[str(r.week_end)[:10], f"{r.close:.2f}", f"{r.sma30:.2f}", f"{r.sma30_4w_ago:.2f}", f"{r.base_high:.2f}", f"{r.vol_x_26w:.2f}",
                    f"{r.rs26:.3f}", f"{r.rs26_prev:.3f}", str(bool(r.spy_above_30w)), str(bool(r.entry))] for r in fun.itertuples(index=False)])
    L += ["### Trade list A — stop evaluated on weekly bars (TradingView weekly-chart convention: the stop fills at the",
          "stop price when the week's low crosses it, or at the week's open when the week opens below it)", ""]
    L += trade_table(tr_weekly)
    L += ["### Trade list B — stop evaluated daily (the production engine, G3: the stop fills at the stop price or the",
          "day's open if gapped through)", ""]
    L += trade_table(tr_daily)
    L += [f"## Supplementary ticker — {SUPPLEMENTARY} (fills get tested where AAPL takes no trade)", "",
          f"Same rules, same window, same settings; in TradingView change the symbol to NYSE:{SUPPLEMENTARY}. Not part of",
          "the spec's pass criterion, which names AAPL; reported so a fill, a stop and a Stage 3 exit can be compared.", "",
          "Trade list A (weekly-bar stop):", ""]
    L += trade_table(sup["weekly"])
    L += ["Trade list B (daily stop, production engine):", ""]
    L += trade_table(sup["daily"])
    L += ["Crossover weeks:", ""]
    L += md_table(["week end", "close", "SMA30", "SMA30 4w ago", "26w high close", "vol / 26w avg", "RS26", "RS26 prev", "SPY > 30w", "entry"],
                  [[str(r.week_end)[:10], f"{r.close:.2f}", f"{r.sma30:.2f}", f"{r.sma30_4w_ago:.2f}", f"{r.base_high:.2f}", f"{r.vol_x_26w:.2f}",
                    f"{r.rs26:.3f}", f"{r.rs26_prev:.3f}", str(bool(r.spy_above_30w)), str(bool(r.entry))] for r in sup["funnel"].itertuples(index=False)])
    L += ["## TradingView leg — what Matt runs", "",
          "Warnings before step 1: leave dividend adjustment OFF on the chart (Sharadar's split-adjusted series is the",
          "TradingView default); do not enable the bar magnifier; the date range is set inside the script. TradingView",
          "has no percent slippage, so the 0.10% slippage is folded into a 0.20% commission.", "",
          "1. TradingView, chart NASDAQ:AAPL, interval W (weekly).",
          "2. Pine Editor, paste strategies/02-growth/tradingview/weinstein_stage2_aapl.pine, Add to chart.",
          "3. Strategy Tester tab, Properties: initial capital 100000, order size 100% of equity, commission 0.2% (already",
          "   set by the script), slippage 0, verify \"Recalculate after order is filled\" is off.",
          "4. List of Trades tab: export (the download icon) and paste the entry date, entry price, exit date, exit price",
          "   and exit type for every trade into the reconciliation section below, or into the chat.",
          "5. Also note the Strategy Tester's total trade count and net profit.", "",
          "## Reconciliation (to fill after the TradingView run)", "",
          "Pass criterion (section 4): entry dates match trade list A within one bar and the trade counts match. With",
          "zero engine trades on AAPL, the check is that TradingView also takes zero and that its indicator values on",
          "the crossover weeks above agree (in particular the volume multiples of 1.30 and 1.57 on the two weeks that",
          "cleared the 26-week base); the ACN list tests the fills.",
          "Known sources of small differences to check first: TradingView's weekly volume against Sharadar's daily",
          "sum; a week where AAPL's data ends on a Thursday holiday; SPY from AMEX:SPY against Sharadar funds.", "",
          "| ticker | engine entry | TradingView entry | match | note |", "| --- | --- | --- | --- | --- |"]
    L += [f"| AAPL | {str(r.entry_date)[:10]} | | | |" for r in tr_weekly.itertuples(index=False)] or ["| AAPL | (no trades) | | | |"]
    L += [f"| {SUPPLEMENTARY} | {str(r.entry_date)[:10]} | | | |" for r in sup["weekly"].itertuples(index=False)]
    L.append("")
    (REPORTS_DIR / "engine_sanity.md").write_text("\n".join(L))


def write_part1(results: dict, seg: dict, sanity_status: str) -> None:
    L = ["# Systems part 1 — GROWTH-004 S10: S-A CANSLIM, S-B Minervini, S-C Weinstein", "",
         f"STATUS: {sanity_status}", "",
         "Engine per spec section 1 (src/engine.py): daily event loop on the GROWTH-001 universe, fills at the next",
         "open, stops at the stop or the gapped open, 0.10% commission plus 0.10% / 0.25% slippage per side by market",
         "cap, $100,000, no leverage, equal weight across ten slots, cash when nothing qualifies, continuous 2006-01",
         "to 2025-06 with results per window (build 2006-01 to 2019-12, holdout 2020-01 to 2025-06). Every rule is",
         "run as written or by the proxy listed in the substitution table; nothing was tuned. Every number comes",
         "from src/systems_part1.py; trades with the full feature row at entry are in",
         "data/processed/trades_<system>.parquet (regenerable) and the core trade columns in reports/s10_trades_*.csv.", "",
         "## Pass criteria (section 3, fixed before results)", "",
         "PASS: in both windows, expectancy per trade > 0 after costs, CAGR above SPY's, and max drawdown no worse",
         "than 1.5x SPY's. MARGINAL: CAGR above SPY's in both windows but one of the other four checks fails. Expectancy",
         "for the pass test is per dollar deployed (net profit / capital put into trades in the window), because a",
         "half-position sale is its own row and the plain mean of row returns overweights it; both are shown. Rank by",
         "holdout CAGR / holdout max drawdown. The three systems below are ranked; S-D to S-F join the board in S11.", ""]
    rows = []
    for name, r in results.items():
        h = r["holdout"]
        ratio = h["cagr"] / abs(h["max_drawdown"]) if h["max_drawdown"] < 0 else float("nan")
        rows.append([name, r["verdict"], pct(r["build"]["cagr"]), pct(r["build"]["spy_cagr"]), pct(r["build"]["max_drawdown"]),
                     pct(r["build"]["expectancy_dollar"], 2), pct(h["cagr"]), pct(h["spy_cagr"]), pct(h["max_drawdown"]), pct(h["expectancy_dollar"], 2),
                     f2(ratio), str(r["build"]["trades"] + h["trades"])])
    rows.sort(key=lambda x: -float(x[10]) if x[10] not in ("n/a",) else 1e9)
    L += md_table(["system", "verdict", "build CAGR", "SPY", "build maxDD", "build exp.", "holdout CAGR", "SPY", "holdout maxDD",
                   "holdout exp.", "holdout CAGR/DD", "trades"], rows)
    L += ["## Substitutions (every proxy for an as-written rule; also in decisions.md)", ""]
    L += md_table(["system", "rule as written", "original term", "what runs"], [list(s) for s in SUBSTITUTIONS])
    for name, r in results.items():
        L += [f"## {name}", ""]
        L += md_table(["metric", "build 2006-01 to 2019-12", "holdout 2020-01 to 2025-06"],
                      [[a, b, c] for (a, b), (_, c) in zip(metrics_rows(r["build"]), metrics_rows(r["holdout"]))])
        L += ["Per-year return against SPY (calendar years; a year's return is equity at its last close over the prior", "year's last close):", ""]
        yrs = sorted(set(r["build"]["per_year"]) | set(r["holdout"]["per_year"]))
        py = {**r["build"]["per_year"], **r["holdout"]["per_year"]}
        sy = {**r["build"]["spy_per_year"], **r["holdout"]["spy_per_year"]}
        L += md_table(["year", "system", "SPY"], [[str(y), pct(py[y]), pct(sy[y])] for y in yrs])
        ex = r["exit_reasons"]
        L += ["Exit reasons (all closed trades, both windows):", ""]
        L += md_table(["reason", "trades", "share", "mean return"], [[k, str(v["n"]), pct(v["share"]), pct(v["mean_ret"], 2)] for k, v in ex.items()])
        if name in seg:
            L += ["S-A segments (spec section 6): the I test is skipped before 2013 and applied from 2013; the run is", "continuous and the segments are cut from it:", ""]
            L += md_table(["metric", "2006-01 to 2012-12 (no I test)", "2013-01 to 2019-12 (with I test)"],
                          [[a, b, c] for (a, b), (_, c) in zip(metrics_rows(seg[name]["no_I"]), metrics_rows(seg[name]["with_I"]))])
    reading = REPORTS_DIR / "systems_part1_reading.md"
    if reading.exists():
        L += ["", reading.read_text().rstrip(), ""]
    (REPORTS_DIR / "systems_part1.md").write_text("\n".join(L))


def exit_reasons(tr: pd.DataFrame) -> dict:
    out = {}
    if not len(tr):
        return out
    for k, g in tr.groupby("exit_reason", sort=True):
        out[k] = {"n": len(g), "share": len(g) / len(tr), "mean_ret": g["ret"].mean()}
    return out


# ------------------------------------------------------------------ main

def main(argv: list[str]) -> int:
    t0 = time.time()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET threads = 1")
    if "--no-build" not in argv or not (PROCESSED_DIR / "bars.parquet").exists():
        print("build_data", flush=True)
        build_data(con)
    print("signals", flush=True)
    build_signals(con)
    cal = np.asarray(con.execute("SELECT date FROM cal ORDER BY date").fetchnumpy()["date"]).astype("datetime64[D]")
    week_ends = set(np.asarray(con.execute("SELECT date FROM week_ends").fetchnumpy()["date"]).astype("datetime64[D]"))
    spy = con.execute("SELECT date, c, c_raw, canslim_m FROM spy ORDER BY date").fetchdf()
    spy["date"] = pd.to_datetime(spy["date"])
    spy_m = {np.datetime64(d, "D"): bool(m) for d, m in zip(spy["date"].values.astype("datetime64[D]"), spy["canslim_m"])}
    spyw = con.execute(f"SELECT week_end, wclose, sma30, wclose_raw, sma30_raw FROM {pq('spy_weekly.parquet')}").fetchdf()
    spy_ok = {np.datetime64(r.week_end, "D"): bool(r.wclose > r.sma30) for r in spyw.itertuples(index=False)}
    spy_ok_raw = {np.datetime64(r.week_end, "D"): bool(r.wclose_raw > r.sma30_raw) for r in spyw.itertuples(index=False)}

    # ---- section 4: sanity check on AAPL
    print("sanity check", flush=True)
    bars_aapl = Bars(con, "2009-01-01", ["AAPL"], raw=True)
    eng_a = Engine(bars_aapl, cal)
    sig_raw = signal_dict(con, "sig_c_raw WHERE ticker = 'AAPL'")
    wk_raw = weekly_dict(con, "weekly_raw.parquet", ["AAPL"])
    sys_tv = Weinstein(sig_raw, week_ends, wk_raw, spy_ok_raw, raw=True, weekly_stops=True, slots=1, name="sanity_weekly_stop")
    sys_dl = Weinstein(sig_raw, week_ends, wk_raw, spy_ok_raw, raw=True, weekly_stops=False, slots=1, name="sanity_daily_stop")
    _, tr_tv = eng_a.run(sys_tv, SANITY_START, SANITY_END)
    _, tr_dl = eng_a.run(sys_dl, SANITY_START, SANITY_END)
    sig_dates = sorted(d for d in sig_raw if np.datetime64(SANITY_START) <= d <= np.datetime64(SANITY_END))
    bars_sup = Bars(con, "2009-01-01", [SUPPLEMENTARY], raw=True)
    eng_s = Engine(bars_sup, cal)
    sig_sup = signal_dict(con, f"sig_c_raw WHERE ticker = '{SUPPLEMENTARY}'")
    wk_sup = weekly_dict(con, "weekly_raw.parquet", [SUPPLEMENTARY])
    _, sup_tv = eng_s.run(Weinstein(sig_sup, week_ends, wk_sup, spy_ok_raw, raw=True, weekly_stops=True, slots=1, name="sup_weekly"), SANITY_START, SANITY_END)
    _, sup_dl = eng_s.run(Weinstein(sig_sup, week_ends, wk_sup, spy_ok_raw, raw=True, weekly_stops=False, slots=1, name="sup_daily"), SANITY_START, SANITY_END)
    write_sanity(tr_tv, tr_dl, len(sig_dates), sig_dates, funnel(con, "AAPL"),
                 {"weekly": sup_tv, "daily": sup_dl, "funnel": funnel(con, SUPPLEMENTARY)})
    sup_tv.to_csv(REPORTS_DIR / f"s10_sanity_{SUPPLEMENTARY}_weekly_stop.csv", index=False)
    funnel(con, "AAPL").to_csv(REPORTS_DIR / "s10_sanity_aapl_crossovers.csv", index=False)
    tr_tv.to_csv(REPORTS_DIR / "s10_sanity_aapl_weekly_stop.csv", index=False)
    tr_dl.to_csv(REPORTS_DIR / "s10_sanity_aapl_daily_stop.csv", index=False)
    print(f"  AAPL signals {len(sig_dates)}, trades weekly-stop {len(tr_tv)}, daily-stop {len(tr_dl)}; {SUPPLEMENTARY} trades {len(sup_tv)} / {len(sup_dl)}", flush=True)

    # ---- the three systems
    print("loading bars", flush=True)
    bars = Bars(con, LOAD_START)
    eng = Engine(bars, cal)
    print(f"  {len(bars.slices):,} tickers, {len(bars.date):,} rows ({time.time() - t0:.0f}s)", flush=True)
    systems = {
        "S-A_canslim": Canslim(signal_dict(con, "sig_a", ["segment"]), week_ends, spy_m),
        "S-B_minervini": Minervini(signal_dict(con, "sig_b", ["pivot_px"]), week_ends),
        "S-C_weinstein": Weinstein(signal_dict(con, "sig_c"), week_ends, weekly_dict(con, "weekly.parquet"), spy_ok),
    }
    results, seg, metrics_rows_csv, years_csv = {}, {}, [], []
    for name, sysm in systems.items():
        t1 = time.time()
        curve, tr = eng.run(sysm, RUN_START, RUN_END)
        tr.insert(0, "system", name)
        curve.insert(0, "system", name)
        full = attach_features(con, tr)
        full.to_parquet(PROCESSED_DIR / f"trades_{name}.parquet", index=False)
        tr.to_csv(REPORTS_DIR / f"s10_trades_{name}.csv", index=False)
        curve.to_csv(REPORTS_DIR / f"s10_equity_{name}.csv", index=False)
        curve["date"] = pd.to_datetime(curve["date"])
        tr["exit_date"] = pd.to_datetime(tr["exit_date"]) if len(tr) else tr.get("exit_date")
        tr["entry_date"] = pd.to_datetime(tr["entry_date"]) if len(tr) else tr.get("entry_date")
        res = {w: window_metrics(curve, tr, spy, *WINDOWS[w]) for w in WINDOWS}
        res["verdict"] = verdict(res["build"], res["holdout"])
        res["exit_reasons"] = exit_reasons(tr)
        results[name] = res
        if name == "S-A_canslim":
            seg[name] = {"no_I": window_metrics(curve, tr, spy, "2006-01-01", "2012-12-31"),
                         "with_I": window_metrics(curve, tr, spy, "2013-01-01", "2019-12-31")}
        for w in WINDOWS:
            m = res[w]
            metrics_rows_csv.append({"system": name, "window": w, **{k: v for k, v in m.items() if k not in ("per_year", "spy_per_year")}})
            for y, v in m["per_year"].items():
                years_csv.append({"system": name, "window": w, "year": y, "system_return": v, "spy_return": m["spy_per_year"][y]})
        print(f"  {name}: {len(tr):,} trades; build CAGR {100 * res['build']['cagr']:.1f}% maxDD {100 * res['build']['max_drawdown']:.1f}%; "
              f"holdout CAGR {100 * res['holdout']['cagr']:.1f}% maxDD {100 * res['holdout']['max_drawdown']:.1f}%; {res['verdict']} ({time.time() - t1:.0f}s)", flush=True)
    pd.DataFrame(metrics_rows_csv).to_csv(REPORTS_DIR / "s10_metrics.csv", index=False)
    pd.DataFrame(years_csv).to_csv(REPORTS_DIR / "s10_per_year.csv", index=False)
    pd.DataFrame(SUBSTITUTIONS, columns=["system", "rule", "original", "proxy"]).to_csv(REPORTS_DIR / "s10_substitutions.csv", index=False)
    status = ("PROVISIONAL — the section 4 sanity check is half complete: the engine leg is in reports/engine_sanity.md, "
              "the TradingView leg is pending Matt's run. Verdicts stand only once the two AAPL trade lists reconcile.")
    write_part1(results, seg, status)
    print(f"RESULT: PASS (provisional) — {REPORTS_DIR / 'systems_part1.md'} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
