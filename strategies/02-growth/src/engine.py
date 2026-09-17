"""GROWTH-004 section 1 — the shared backtest engine (S10).

Data prep (duckdb, once per container):
    data/processed/bars.parquet     daily bars for every ticker ever in the
                                    GROWTH-001 universe, 2003-01 onward:
                                    dividend-and-split-adjusted OHLC (o, h,
                                    l, c = closeadj; o/h/l scaled by
                                    closeadj/close), split-adjusted raw OHLC
                                    (o_raw.. c_raw, Sharadar's open..close),
                                    volume, daily marketcap (USD millions),
                                    SMAs, 52-week extremes, ATR, the H14
                                    pattern day, and point-in-time universe
                                    membership (member = a universe row
                                    exists for the latest month end on or
                                    before the date)
    data/processed/weekly.parquet   weekly bars (week = Monday to the last
                                    trading day) on adjusted closes, with
                                    the 30-week SMA and its 4-week lag, the
                                    prior-26-week high close, the 26-week
                                    average volume (current week included,
                                    TradingView's ta.sma convention), and
                                    the 26-week relative return against SPY
    data/processed/weekly_raw.parquet  the same on split-adjusted raw closes
                                    (for the section 4 TradingView check)
    data/processed/spy.parquet      SPY daily (adjusted and raw) with 50/200
                                    day SMAs; spy_weekly.parquet with the
                                    30-week SMA on both bases

Simulator (section 1, G1 to G10): an event-driven daily loop over the SPY
trading calendar. Signals are evaluated on the close of the system's
evaluation days and filled at the next open of that ticker (G3). Stops
and limits fill intraday at the stop or limit price, or at the open when
the bar gaps through it, whichever is worse for the trade (G3). Costs:
0.10% commission per side plus 0.10% slippage when the day's market cap
is at or above $2B, 0.25% otherwise or when unknown (G2). $100,000, no
leverage, no shorting, cash earns nothing (G4). Equal weight across the
slot count, sized on equity at the fill (G5); cash is held when no
candidate qualifies. Every closed trade (partials as their own rows) goes
to data/processed/trades_<system>.parquet with the features.parquet lag-0
row at entry (G9). Deterministic: no randomness, candidate ties broken by
ticker, duckdb single-threaded (G10).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import duckdb
import numpy as np
import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR

COMMISSION = 0.001
SLIP_LARGE, SLIP_SMALL, LARGE_CAP_MUSD = 0.001, 0.0025, 2000.0
CAPITAL = 100_000.0
BARS_START = "2003-01-01"
WINDOWS = {"build": ("2006-01-01", "2019-12-31"), "holdout": ("2020-01-01", "2025-06-30")}


def P(name: str) -> str:
    return f"read_parquet('{(RAW_DIR / name).as_posix()}')"


def pq(name: str) -> str:
    return f"read_parquet('{(PROCESSED_DIR / name).as_posix()}')"


# ------------------------------------------------------------------ data prep

def weekly_sql(src: str, price: str, spy_price: str) -> str:
    return f"""
        WITH wk AS (
            SELECT ticker, date_trunc('week', date)::DATE AS week_start, max(date) AS week_end,
                   arg_max({price}, date) AS wclose, max(h{'_raw' if price == 'c_raw' else ''}) AS whigh,
                   min(l{'_raw' if price == 'c_raw' else ''}) AS wlow, arg_min(o{'_raw' if price == 'c_raw' else ''}, date) AS wopen,
                   sum(v) AS wvol, count(*) AS n_days
            FROM {src} GROUP BY 1, 2
        ), spy AS (
            SELECT date_trunc('week', date)::DATE AS week_start, arg_max({spy_price}, date) AS spy_close
            FROM spy_daily GROUP BY 1
        ), w1 AS (
            SELECT wk.*, spy.spy_close, row_number() OVER w AS wn,
                   avg(wclose) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS sma30,
                   max(wclose) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 26 PRECEDING AND 1 PRECEDING) AS base_high,
                   avg(wvol) OVER (PARTITION BY ticker ORDER BY week_start ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) AS vol26,
                   lag(wclose) OVER w AS prev_close, lag(wclose, 26) OVER w AS close_26, lag(spy.spy_close, 26) OVER w AS spy_26
            FROM wk LEFT JOIN spy USING (week_start) WINDOW w AS (PARTITION BY ticker ORDER BY week_start)
        ), w2 AS (
            SELECT *, lag(sma30) OVER w AS prev_sma30, lag(sma30, 4) OVER w AS sma30_lag4,
                   CASE WHEN close_26 > 0 AND spy_26 > 0 THEN (wclose / close_26) / (spy_close / spy_26) - 1 END AS rs26
            FROM w1 WINDOW w AS (PARTITION BY ticker ORDER BY week_start)
        )
        SELECT *, lag(rs26) OVER (PARTITION BY ticker ORDER BY week_start) AS rs26_prev FROM w2
    """


def build_data(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("SET threads = 1")
    con.execute(f"CREATE TABLE utick AS SELECT DISTINCT ticker FROM {pq('universe.parquet')}")
    con.execute(f"""
        CREATE TABLE spy_daily AS
        SELECT date, closeadj AS c, close AS c_raw, open * closeadj / close AS o, open AS o_raw,
               avg(closeadj) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS sma50,
               avg(closeadj) OVER (ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200,
               row_number() OVER (ORDER BY date) AS rn
        FROM {P('funds.parquet')} WHERE ticker = 'SPY' AND close > 0 ORDER BY date
    """)
    con.execute(f"""
        CREATE TABLE bars AS
        WITH s AS (
            SELECT ticker, date, open * adj AS o, high * adj AS h, low * adj AS l, closeadj AS c, volume AS v,
                   open AS o_raw, high AS h_raw, low AS l_raw, close AS c_raw
            FROM (SELECT *, closeadj / close AS adj FROM {P('stocks.parquet')}
                  WHERE ticker IN (SELECT ticker FROM utick) AND date >= DATE '{BARS_START}' AND close > 0 AND closeadj > 0)
        ), d1 AS (
            SELECT *, row_number() OVER w AS rn, lag(c) OVER w AS prev_c,
                   avg(c) OVER (w ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS sma20,
                   avg(c) OVER (w ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS sma50,
                   avg(c) OVER (w ROWS BETWEEN 99 PRECEDING AND CURRENT ROW) AS sma100,
                   avg(c) OVER (w ROWS BETWEEN 149 PRECEDING AND CURRENT ROW) AS sma150,
                   avg(c) OVER (w ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) AS sma200,
                   avg(v) OVER (w ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS vol50,
                   avg(v) OVER (w ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS vol20,
                   max(c) OVER (w ROWS BETWEEN 251 PRECEDING AND 1 PRECEDING) AS chigh252_prev,
                   max(h) OVER (w ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS high252,
                   min(l) OVER (w ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS low252,
                   max(h) OVER (w ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS high20_prev,
                   count(*) OVER (w ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS n252
            FROM s WINDOW w AS (PARTITION BY ticker ORDER BY date)
        ), d2 AS (
            SELECT *, greatest(h - l, abs(h - prev_c), abs(l - prev_c)) AS tr, lag(sma200, 22) OVER w AS sma200_lag22
            FROM d1 WINDOW w AS (PARTITION BY ticker ORDER BY date)
        ), d3 AS (
            SELECT *, avg(tr) OVER (w ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS atr20
            FROM d2 WINDOW w AS (PARTITION BY ticker ORDER BY date)
        ), d4 AS (
            SELECT *, atr20 / nullif(c, 0) AS atr_ratio FROM d3
        ), d5 AS (
            SELECT *,
                   CASE WHEN rn >= 62 THEN
                        c > high20_prev
                        AND lag(atr_ratio, 1) OVER w < lag(atr_ratio, 21) OVER w
                        AND lag(atr_ratio, 21) OVER w < lag(atr_ratio, 41) OVER w
                        AND lag(vol20, 1) OVER w < lag(vol20, 21) OVER w
                        AND lag(vol20, 21) OVER w < lag(vol20, 41) OVER w
                   ELSE FALSE END AS h14_day
            FROM d4 WINDOW w AS (PARTITION BY ticker ORDER BY date)
        )
        SELECT d5.* EXCLUDE (prev_c, tr), m.marketcap,
               (u.month_end IS NOT NULL AND d5.date < u.month_end + INTERVAL 32 DAY) AS member
        FROM d5
        LEFT JOIN (SELECT ticker, date, marketcap FROM {P('daily.parquet')} WHERE ticker IN (SELECT ticker FROM utick)) m USING (ticker, date)
        ASOF LEFT JOIN (SELECT ticker, month_end FROM {pq('universe.parquet')}) u ON u.ticker = d5.ticker AND u.month_end <= d5.date
    """)
    con.execute(f"COPY (SELECT * FROM bars ORDER BY ticker, date) TO '{(PROCESSED_DIR / 'bars.parquet').as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.execute(f"CREATE TABLE weekly AS {weekly_sql('bars', 'c', 'c')}")
    con.execute(f"COPY (SELECT * FROM weekly ORDER BY ticker, week_end) TO '{(PROCESSED_DIR / 'weekly.parquet').as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.execute(f"CREATE TABLE weekly_raw AS {weekly_sql('bars', 'c_raw', 'c_raw')}")
    con.execute(f"COPY (SELECT * FROM weekly_raw ORDER BY ticker, week_end) TO '{(PROCESSED_DIR / 'weekly_raw.parquet').as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.execute("""
        CREATE TABLE spy_weekly AS
        WITH wk AS (SELECT date_trunc('week', date)::DATE AS week_start, max(date) AS week_end,
                           arg_max(c, date) AS wclose, arg_max(c_raw, date) AS wclose_raw FROM spy_daily GROUP BY 1)
        SELECT *, avg(wclose) OVER (ORDER BY week_start ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS sma30,
               avg(wclose_raw) OVER (ORDER BY week_start ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS sma30_raw,
               row_number() OVER (ORDER BY week_start) AS wn
        FROM wk
    """)
    con.execute(f"COPY (SELECT * FROM spy_daily ORDER BY date) TO '{(PROCESSED_DIR / 'spy.parquet').as_posix()}' (FORMAT PARQUET)")
    con.execute(f"COPY (SELECT * FROM spy_weekly ORDER BY week_end) TO '{(PROCESSED_DIR / 'spy_weekly.parquet').as_posix()}' (FORMAT PARQUET)")
    for t in ["bars", "weekly", "spy_daily", "spy_weekly"]:
        print(f"  {t}: {con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:,} rows", flush=True)


# ------------------------------------------------------------------ in-memory bars

# Columns the daily loop needs (signals are computed in SQL from the full table). Raw = split-adjusted only.
BAR_COLS = ["o", "h", "l", "c", "v", "sma20", "sma50", "vol50", "marketcap"]
RAW_COLS = ["o_raw", "h_raw", "l_raw", "c_raw"]


def npcol(a) -> np.ndarray:
    """duckdb fetchnumpy returns masked arrays for nullable columns; masked entries become NaN."""
    return np.ma.filled(a, np.nan).astype(float) if np.ma.isMaskedArray(a) else np.asarray(a, dtype=float)


class Bars:
    """Per-ticker numpy views over bars.parquet, loaded once (rows ordered by ticker, date)."""

    def __init__(self, con: duckdb.DuckDBPyConnection, start: str, tickers: list[str] | None = None, raw: bool = False):
        where = f"date >= DATE '{start}'" + (" AND ticker IN (" + ",".join(f"'{t}'" for t in tickers) + ")" if tickers else "")
        cols = BAR_COLS + (RAW_COLS if raw else [])
        res = con.execute(f"SELECT date, {', '.join(cols)} FROM {pq('bars.parquet')} WHERE {where} ORDER BY ticker, date").fetchnumpy()
        self.date = np.asarray(res["date"]).astype("datetime64[D]")
        self.cols = {c: npcol(res[c]) for c in cols}
        counts = con.execute(f"SELECT ticker, count(*) AS n FROM {pq('bars.parquet')} WHERE {where} GROUP BY ticker ORDER BY ticker").fetchall()
        self.slices, pos = {}, 0
        for t, n in counts:
            self.slices[t] = (pos, pos + int(n))
            pos += int(n)
        assert pos == len(self.date)

    def index(self, ticker: str, d: np.datetime64) -> int | None:
        s, e = self.slices.get(ticker, (0, 0))
        if e == s:
            return None
        i = s + int(np.searchsorted(self.date[s:e], d))
        return i if i < e and self.date[i] == d else None

    def next_index(self, ticker: str, d: np.datetime64) -> int | None:
        """First bar strictly after d."""
        s, e = self.slices.get(ticker, (0, 0))
        i = s + int(np.searchsorted(self.date[s:e], d, side="right"))
        return i if i < e else None



# ------------------------------------------------------------------ simulator

@dataclass
class Position:
    ticker: str
    shares: int
    entry_date: np.datetime64
    entry_price: float          # fill price including slippage
    entry_commission: float
    signal_date: np.datetime64
    rank: float
    bars_held: int = 0
    stop: float | None = None
    stop2: float | None = None
    target: float | None = None
    exit_pending: str | None = None
    state: dict = field(default_factory=dict)
    initial_shares: int = 0


class System:
    """Hooks a system implements. Dates are numpy datetime64[D]."""
    name = "base"
    slots = 10
    raw = False          # True = trade on split-adjusted raw prices (sanity check against TradingView)
    weekly_stops = False  # True = evaluate stops on weekly bars (TradingView weekly-chart emulation)

    def eval_days(self, calendar: np.ndarray) -> set: ...
    def regime_ok(self, d: np.datetime64) -> bool: return True
    def candidates(self, d: np.datetime64, held: set[str]) -> list[tuple[str, float]]: ...
    def on_entry(self, pos: Position, bars: Bars, i: int) -> None: ...
    def intraday(self, pos: Position, bars: Bars, i: int) -> list[tuple[str, float, float]]:
        """Return fills as (reason, price, fraction_of_position) for stops and limits hit inside the bar."""
        return []
    def on_close(self, pos: Position, bars: Bars, i: int, d: np.datetime64) -> str | None: return None


def slippage(marketcap_musd: float) -> float:
    return SLIP_LARGE if marketcap_musd is not None and not math.isnan(marketcap_musd) and marketcap_musd >= LARGE_CAP_MUSD else SLIP_SMALL


TRADE_COLS = ["ticker", "signal_date", "entry_date", "entry_price", "shares", "exit_date", "exit_price", "exit_reason", "pnl",
              "ret", "holding_days", "bars_held", "partial", "rank", "notional_in", "notional_out"]


class Engine:
    def __init__(self, bars: Bars, calendar: np.ndarray):
        self.bars, self.calendar = bars, calendar

    def px(self, sysm: System, i: int, col: str) -> float:
        return float(self.bars.cols[col + ("_raw" if sysm.raw else "")][i])

    def run(self, sysm: System, start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        b = self.bars
        cal = self.calendar[(self.calendar >= np.datetime64(start)) & (self.calendar <= np.datetime64(end))]
        evals = sysm.eval_days(cal)
        cash, positions, trades, curve = CAPITAL, [], [], []
        pending: list[tuple[str, float, np.datetime64]] = []
        PENDING_MAX_DAYS = 5   # an entry not filled within five trading days of its signal lapses
        last_close: dict[str, float] = {}

        def record(pos: Position, d, price, shares, reason, commission):
            cost = shares * pos.entry_price + pos.entry_commission * shares / pos.initial_shares
            proceeds = shares * price - commission
            trades.append({"ticker": pos.ticker, "signal_date": pos.signal_date, "entry_date": pos.entry_date,
                           "entry_price": pos.entry_price, "shares": shares, "exit_date": d, "exit_price": price,
                           "exit_reason": reason, "pnl": proceeds - cost, "ret": proceeds / cost - 1,
                           "holding_days": int((d - pos.entry_date).astype(int)), "bars_held": pos.bars_held,
                           "partial": shares != pos.initial_shares, "rank": pos.rank,
                           "notional_in": shares * pos.entry_price, "notional_out": shares * price})

        for d in cal:
            # 0. a ticker with no bar today and no bar after today has left the data: close at its last close
            for pos in list(positions):
                if b.index(pos.ticker, d) is None and b.next_index(pos.ticker, d) is None:
                    price = last_close.get(pos.ticker, pos.entry_price) * (1 - SLIP_SMALL)
                    comm = pos.shares * price * COMMISSION
                    cash += pos.shares * price - comm
                    record(pos, d, price, pos.shares, "delisted", comm)
                    positions.remove(pos)
            # 1. fills at the open: exits queued on the previous close, then entries
            for pos in list(positions):
                if pos.exit_pending:
                    i = b.index(pos.ticker, d)
                    if i is None:
                        continue
                    price = self.px(sysm, i, "o") * (1 - slippage(b.cols["marketcap"][i]))
                    comm = pos.shares * price * COMMISSION
                    cash += pos.shares * price - comm
                    record(pos, d, price, pos.shares, pos.exit_pending, comm)
                    positions.remove(pos)
            held = {p.ticker for p in positions}
            carried = []
            for ticker, rank, sdate in pending:
                if len(positions) >= sysm.slots or ticker in held:
                    continue
                i = b.index(ticker, d)
                if i is None:
                    if (d - sdate).astype(int) <= PENDING_MAX_DAYS * 2:
                        carried.append((ticker, rank, sdate))
                    continue
                equity = cash + sum(p.shares * last_close.get(p.ticker, p.entry_price) for p in positions)
                price = self.px(sysm, i, "o") * (1 + slippage(b.cols["marketcap"][i]))
                budget = min(equity / sysm.slots, cash)
                shares = int(math.floor(budget / (price * (1 + COMMISSION))))
                if shares < 1:
                    continue
                comm = shares * price * COMMISSION
                cash -= shares * price + comm
                pos = Position(ticker, shares, d, price, comm, sdate, rank, initial_shares=shares)
                sysm.on_entry(pos, b, i)
                positions.append(pos)
                held.add(ticker)
            pending = carried
            # 2. intraday stops and limits
            for pos in list(positions):
                i = b.index(pos.ticker, d)
                if i is None:
                    continue
                for reason, price, frac in sysm.intraday(pos, b, i):
                    shares = pos.shares if frac >= 1 else int(math.floor(pos.shares * frac))
                    if shares < 1:
                        continue
                    price = price * (1 - slippage(b.cols["marketcap"][i]))
                    comm = shares * price * COMMISSION
                    cash += shares * price - comm
                    record(pos, d, price, shares, reason, comm)
                    pos.shares -= shares
                    if pos.shares <= 0:
                        positions.remove(pos)
                        break
            # 3. close: exit signals, then entry signals on evaluation days
            for pos in positions:
                i = b.index(pos.ticker, d)
                if i is None:
                    continue
                pos.bars_held += 1
                last_close[pos.ticker] = self.px(sysm, i, "c")
                if pos.exit_pending is None:
                    pos.exit_pending = sysm.on_close(pos, b, i, d)
            if d in evals and sysm.regime_ok(d):
                free = sysm.slots - sum(1 for p in positions if p.exit_pending is None)
                if free > 0:
                    held = {p.ticker for p in positions}
                    cands = sorted(sysm.candidates(d, held), key=lambda x: (-x[1], x[0]))
                    pending = [(t, r, d) for t, r in cands[:free]]   # a new evaluation replaces any carried entries
            equity = cash + sum(p.shares * last_close.get(p.ticker, p.entry_price) for p in positions)
            curve.append({"date": d, "equity": equity, "cash": cash, "positions": len(positions)})
        # close whatever is still open at the last close of the run (flagged)
        d = cal[-1]
        for pos in positions:
            i = b.index(pos.ticker, d)
            price = (self.px(sysm, i, "c") if i is not None else last_close.get(pos.ticker, pos.entry_price)) \
                * (1 - slippage(b.cols["marketcap"][i] if i is not None else float("nan")))
            comm = pos.shares * price * COMMISSION
            record(pos, d, price, pos.shares, "end_of_test", comm)
        tr = pd.DataFrame(trades, columns=TRADE_COLS)
        if len(tr):
            tr = tr.sort_values(["exit_date", "entry_date", "ticker"]).reset_index(drop=True)
        return pd.DataFrame(curve), tr


# ------------------------------------------------------------------ metrics

def window_metrics(curve: pd.DataFrame, trades: pd.DataFrame, spy: pd.DataFrame, start: str, end: str) -> dict:
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    c = curve[(curve["date"] >= s) & (curve["date"] <= e)].copy()
    c["date"] = pd.to_datetime(c["date"])
    eq = c.set_index("date")["equity"]
    # start value = last equity before the window (or capital); the curve is continuous across windows (G7)
    before = curve[curve["date"] < s]
    e0 = float(before["equity"].iloc[-1]) if len(before) else CAPITAL
    years = (eq.index[-1] - (before["date"].iloc[-1] if len(before) else eq.index[0])).days / 365.25
    total = eq.iloc[-1] / e0 - 1
    cagr = (1 + total) ** (1 / years) - 1 if years > 0 else float("nan")
    path = pd.concat([pd.Series([e0]), eq]) if len(before) else eq
    dd = (path / path.cummax() - 1).min()
    r = eq.pct_change().dropna()
    if len(before):
        r = pd.concat([pd.Series([eq.iloc[0] / e0 - 1]), r])
    sharpe = r.mean() / r.std(ddof=0) * math.sqrt(252) if len(r) > 1 and r.std(ddof=0) > 0 else float("nan")
    roll = (eq / eq.shift(252) - 1).dropna()
    worst12 = float(roll.min()) if len(roll) else float("nan")
    t = trades[(trades["exit_date"] >= s) & (trades["exit_date"] <= e)] if len(trades) else trades
    n = len(t)
    wins, losses = t[t["pnl"] > 0], t[t["pnl"] <= 0]
    gp, gl = wins["pnl"].sum(), -losses["pnl"].sum()
    years_list = sorted(set(eq.index.year))
    per_year = {}
    for y in years_list:
        ey = eq[eq.index.year == y]
        prev = eq[eq.index.year < y]
        base = float(prev.iloc[-1]) if len(prev) else e0
        per_year[y] = float(ey.iloc[-1]) / base - 1
    # turnover: yearly (buys + sells) / 2 / mean equity, averaged over the window's years
    tos = []
    for y in years_list:
        ty = t[pd.to_datetime(t["exit_date"]).dt.year == y] if n else t
        by = trades[(pd.to_datetime(trades["entry_date"]).dt.year == y)] if len(trades) else trades
        vol = (by["notional_in"].sum() if len(by) else 0) + (ty["notional_out"].sum() if len(ty) else 0)
        tos.append(vol / 2 / float(eq[eq.index.year == y].mean()))
    sp = spy[(spy["date"] >= s) & (spy["date"] <= e)].set_index("date")["c"]
    sp0 = spy[spy["date"] < s]["c"].iloc[-1] if len(spy[spy["date"] < s]) else sp.iloc[0]
    sp_path = pd.concat([pd.Series([sp0]), sp])
    spy_total = sp.iloc[-1] / sp0 - 1
    spy_cagr = (1 + spy_total) ** (1 / years) - 1
    spy_dd = (sp_path / sp_path.cummax() - 1).min()
    spy_years = {y: float(sp[sp.index.year == y].iloc[-1]) / (float(sp[sp.index.year < y].iloc[-1]) if len(sp[sp.index.year < y]) else sp0) - 1
                 for y in years_list}
    return {"trades": n, "win_rate": len(wins) / n if n else float("nan"),
            "avg_winner": wins["ret"].mean() if len(wins) else float("nan"),
            "avg_loser": losses["ret"].mean() if len(losses) else float("nan"),
            "expectancy": t["ret"].mean() if n else float("nan"),
            "expectancy_dollar": t["pnl"].sum() / t["notional_in"].sum() if n and t["notional_in"].sum() > 0 else float("nan"),
            "profit_factor": gp / gl if gl > 0 else float("inf") if gp > 0 else float("nan"),
            "cagr": cagr, "total_return": total, "max_drawdown": float(dd), "worst_12m": worst12, "sharpe": sharpe,
            "turnover": float(np.mean(tos)) if tos else float("nan"),
            "avg_holding_days": t["holding_days"].mean() if n else float("nan"),
            "per_year": per_year, "spy_per_year": spy_years, "spy_cagr": spy_cagr, "spy_total": spy_total,
            "spy_max_drawdown": float(spy_dd), "equity_start": e0, "equity_end": float(eq.iloc[-1])}


def verdict(m_build: dict, m_hold: dict) -> str:
    def ok(m):
        return (m["expectancy_dollar"] > 0, m["cagr"] > m["spy_cagr"], m["max_drawdown"] >= 1.5 * m["spy_max_drawdown"])
    b, h = ok(m_build), ok(m_hold)
    if all(b) and all(h):
        return "PASS"
    if b[1] and h[1] and (sum(b) + sum(h) >= 5):
        return "MARGINAL"
    return "FAIL"


def attach_features(con: duckdb.DuckDBPyConnection, trades: pd.DataFrame) -> pd.DataFrame:
    """G9: the features.parquet lag-0 row at the latest month end on or before the entry date."""
    if not len(trades):
        return trades
    con.register("tr_df", trades)
    out = con.execute(f"""
        SELECT t.*, f.* EXCLUDE (ticker, month_end, lag)
        FROM tr_df t
        ASOF LEFT JOIN (SELECT * FROM {pq('features.parquet')} WHERE lag = 0) f
             ON f.ticker = t.ticker AND f.month_end <= t.entry_date
        ORDER BY t.exit_date, t.entry_date, t.ticker
    """).fetchdf()
    con.unregister("tr_df")
    return out
