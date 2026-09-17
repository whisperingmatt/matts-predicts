"""S3 — Regime tags per spec section 6.

Output: data/processed/regime.parquet, one row per month_end from 1998-01
        to HOLDOUT_END, with:
  spy_closeadj, spy_ath, drawdown (<= 0), drawdown_bucket ('0-10', '10-20',
  '20-30', '>30'), trough_date, months_since_trough, mst_bucket ('0-12',
  '13-24', '>24'), vix_close.

    python -m src.regime

SPY month-end closeadj comes from the funds table (SFP), the S&P 500 proxy
the spec names. Drawdown is from the prior all-time high of month-end
closes. A drawdown episode runs from one all-time high to the next; its
trough is the lowest month-end close inside it. months_since_trough at a
month is months since the trough of the current episode when in drawdown,
or of the episode just closed when at a new high.

VIX close is the CBOE daily history CSV (free, section 6), fetched to
data/raw/VIX_History.csv when missing; the month's value is the last close
on or before the month end.
"""
from __future__ import annotations

import sys

import duckdb
import pandas as pd
import requests

from src.config import HOLDOUT_END, PROCESSED_DIR, RAW_DIR

VIX_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
REGIME_START = "1998-01-31"


def fetch_vix() -> pd.DataFrame:
    path = RAW_DIR / "VIX_History.csv"
    if not path.exists():
        resp = requests.get(VIX_URL, timeout=60)
        resp.raise_for_status()
        path.write_bytes(resp.content)
        print(f"downloaded {VIX_URL} -> {path} ({len(resp.content):,} bytes)")
    vix = pd.read_csv(path)
    vix.columns = [c.strip().lower() for c in vix.columns]
    vix["date"] = pd.to_datetime(vix["date"], format="%m/%d/%Y")
    return vix[["date", "close"]].rename(columns={"close": "vix_close"}).sort_values("date")


def drawdown_bucket(dd: float) -> str:
    d = -dd
    if d <= 0.10:
        return "0-10"
    if d <= 0.20:
        return "10-20"
    if d <= 0.30:
        return "20-30"
    return ">30"


def mst_bucket(m: int) -> str:
    if m <= 12:
        return "0-12"
    if m <= 24:
        return "13-24"
    return ">24"


def main() -> int:
    con = duckdb.connect()
    spy = con.execute(f"""
        SELECT last_day(date) AS month_end, arg_max(closeadj, date) AS spy_closeadj
        FROM read_parquet('{(RAW_DIR / 'funds.parquet').as_posix()}')
        WHERE ticker = 'SPY' AND date <= DATE '{HOLDOUT_END}'
        GROUP BY 1 ORDER BY 1
    """).fetchdf()
    spy["month_end"] = pd.to_datetime(spy["month_end"])

    rows = []
    ath = -1.0
    episode_min = None       # (close, date) lowest close since the last ATH
    last_closed_trough = None
    for me, close in zip(spy["month_end"], spy["spy_closeadj"]):
        if close >= ath:
            # new all-time high closes the episode; its trough becomes the reference
            if episode_min is not None:
                last_closed_trough = episode_min[1]
            ath = close
            episode_min = None
            trough_date = last_closed_trough
        else:
            if episode_min is None or close < episode_min[0]:
                episode_min = (close, me)
            trough_date = episode_min[1]
        dd = close / ath - 1
        mst = None if trough_date is None else (me.year - trough_date.year) * 12 + (me.month - trough_date.month)
        rows.append((me, close, ath, dd, drawdown_bucket(dd), trough_date, mst,
                     None if mst is None else mst_bucket(mst)))
    reg = pd.DataFrame(rows, columns=["month_end", "spy_closeadj", "spy_ath", "drawdown", "drawdown_bucket",
                                      "trough_date", "months_since_trough", "mst_bucket"])

    vix = fetch_vix()
    vix_me = vix.groupby(vix["date"] + pd.offsets.MonthEnd(0))["vix_close"].last().rename_axis("month_end").reset_index()
    reg = reg.merge(vix_me, on="month_end", how="left")
    reg = reg[reg["month_end"] >= pd.Timestamp(REGIME_START)].reset_index(drop=True)
    reg["month_end"] = reg["month_end"].dt.date
    reg["trough_date"] = pd.to_datetime(reg["trough_date"]).dt.date

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "regime.parquet"
    con.register("reg", reg)
    con.execute(f"COPY (SELECT * FROM reg) TO '{out.as_posix()}' (FORMAT PARQUET)")

    print(f"regime.parquet: {len(reg):,} month ends {reg['month_end'].min()}..{reg['month_end'].max()} -> {out}")
    print("drawdown buckets:", reg["drawdown_bucket"].value_counts().sort_index().to_dict())
    print("months-since-trough buckets:", reg["mst_bucket"].value_counts(dropna=False).sort_index().to_dict())
    print(f"deepest drawdown: {reg['drawdown'].min():.1%} at {reg.loc[reg['drawdown'].idxmin(), 'month_end']}")
    print(f"VIX: {reg['vix_close'].notna().sum():,} of {len(reg):,} months populated; max {reg['vix_close'].max():.1f} "
          f"at {reg.loc[reg['vix_close'].idxmax(), 'month_end']}")
    missing_vix = int(reg["vix_close"].isna().sum())
    print("RESULT:", "PASS — every month tagged" if missing_vix == 0 else f"FAIL — {missing_vix} months without VIX")
    return 0 if missing_vix == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
