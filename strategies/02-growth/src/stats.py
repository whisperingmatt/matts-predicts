"""S4 — Statistics per spec section 7, build window only (D4).

Input:  data/processed/features.parquet, labels.parquet, regime.parquet,
        universe.parquet
Output: reports/build_window_results.md (tables + the reading in
        reports/build_window_reading.md, inserted verbatim when present)
        reports/s4_single_signal.csv, s4_combinations.csv,
        s4_expected_winners.csv, s4_sector_year.csv, s4_base_rates.csv

    python -m src.stats

Definitions (decisions.md 2026-09-17 "S4 statistics definitions"):
* A cell's rows are universe (ticker, month_end, lag) rows in the build
  window where the flag is non-null. base = launches / rows in that set.
  rate = launches / rows where the flag is TRUE. lift = rate / base.
  coverage = non-null rows / all rows. Reported beside every lift.
* 95% CI is Wilson on rate (n = flag-TRUE rows), divided by base, which is
  treated as fixed (it rests on far more rows than the flagged subset).
* D8: a cell needs >= MIN_EVENTS_PER_CELL launch events (launches among
  flag-TRUE rows, or launches in the bucket for base-rate cells). Below
  that the cell reads "insufficient" and carries no number.
* PASS (7): lift >= 2.0 with lower CI >= 1.5 at any lag, launch_300.
  CRASH-ONLY: passes overall but no (lag, drawdown bucket 0-10 or 10-20)
  cell passes.
* Combinations (7.4): within each lag, among flags with launch_300 lift
  >= 1.5 and >= 100 events at that lag, all 2- and 3-way ANDs. Ranked by
  lift then by catch = launches caught / all build-window launches.
* Expected winners (Matt, S4 brief): for the top ten combinations, per
  regime bucket, 10 x (bucket base rate) x (combination's overall lift).
  Assumes the lift is the same in every regime; the 7.3 tables show where
  it is not.
Nothing here recommends anything. Holdout rows are never read.
"""
from __future__ import annotations

import itertools
import math
import sys

import duckdb
import pandas as pd

from src.config import (BUILD_END, BUILD_START, LAGS, MAX_COMBINATION_SIZE, MIN_EVENTS_PER_CELL,
                        PROCESSED_DIR, REPORTS_DIR)
from src.features import FEATURE_STATUS

FLAGS = list(FEATURE_STATUS)
AVAILABLE = [f for f, s in FEATURE_STATUS.items() if s.startswith("available")]
UNAVAILABLE = [f for f in FLAGS if f not in AVAILABLE]
CONTROLS = [f for f in AVAILABLE if f.startswith("ctl_")]
THRESHOLDS = ["launch_300", "launch_200", "launch_500"]
BUCKET_TYPES = {"all": ["ALL"], "drawdown": ["0-10", "10-20", "20-30", ">30"], "mst": ["0-12", "13-24", ">24"]}
Z = 1.959964
PASS_LIFT, PASS_CI_LOW, COMBO_MIN_LIFT = 2.0, 1.5, 1.5
TOP_COMBOS, TOP_WINNERS = 20, 10


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return (center - half, center + half)


def pq(name: str) -> str:
    return f"read_parquet('{(PROCESSED_DIR / name).as_posix()}')"


# ------------------------------------------------------------------ data

INVERTED = {"inv_h15_near_high": "h15_near_high", "inv_h21_no_dilution": "h21_no_dilution",
            "inv_h8_fcf_divergence": "h8_fcf_divergence", "inv_ctl_divyield_gt_2": "ctl_divyield_gt_2"}


def load(con: duckdb.DuckDBPyConnection, start: str = BUILD_START, end: str = BUILD_END) -> None:
    """Table d: universe rows x lags inside [start, end] with flags, labels, regime, sector.

    The four inverted flags (NOT of the build window's backward signals; null
    stays null) are added for S5. They are not part of AVAILABLE, so the
    build-window tables never include them.
    """
    con.execute(f"""
        CREATE TABLE d AS
        SELECT f.ticker, f.month_end, f.lag, year(f.month_end) AS year,
               {", ".join("f." + c for c in FLAGS)},
               {", ".join(f"NOT f.{src} AS {inv}" for inv, src in INVERTED.items())},
               l.launch_300, l.launch_200, l.launch_500,
               r.drawdown_bucket, r.mst_bucket, coalesce(u.sector, 'Unknown') AS sector
        FROM {pq('features.parquet')} f
        JOIN {pq('labels.parquet')} l USING (ticker, month_end)
        JOIN {pq('regime.parquet')} r ON r.month_end = f.month_end
        JOIN {pq('universe.parquet')} u USING (ticker, month_end)
        WHERE f.month_end BETWEEN DATE '{start}' AND DATE '{end}'
    """)
    n, nl = con.execute("SELECT count(*), count(*) FILTER (WHERE lag = 0) FROM d").fetchone()
    print(f"rows {start}..{end}: {n:,} ({nl:,} per lag)")


# ------------------------------------------------------------- base rates

def base_rates(con) -> tuple[pd.DataFrame, pd.DataFrame]:
    yearly = con.execute("""
        SELECT year::VARCHAR AS year, count(*) AS rows_,
               count(*) FILTER (WHERE launch_300) AS k300, count(*) FILTER (WHERE launch_200) AS k200,
               count(*) FILTER (WHERE launch_500) AS k500
        FROM d WHERE lag = 0 GROUP BY 1
        UNION ALL
        SELECT 'overall', count(*), count(*) FILTER (WHERE launch_300), count(*) FILTER (WHERE launch_200),
               count(*) FILTER (WHERE launch_500) FROM d WHERE lag = 0
        ORDER BY 1
    """).fetchdf()
    buckets = con.execute("""
        SELECT 'drawdown' AS bucket_type, drawdown_bucket AS bucket, count(*) AS rows_,
               count(*) FILTER (WHERE launch_300) AS k300, count(*) FILTER (WHERE launch_200) AS k200,
               count(*) FILTER (WHERE launch_500) AS k500
        FROM d WHERE lag = 0 GROUP BY 2
        UNION ALL
        SELECT 'mst', mst_bucket, count(*), count(*) FILTER (WHERE launch_300), count(*) FILTER (WHERE launch_200),
               count(*) FILTER (WHERE launch_500) FROM d WHERE lag = 0 GROUP BY 2
    """).fetchdf()
    order = {b: i for i, b in enumerate(BUCKET_TYPES["drawdown"] + BUCKET_TYPES["mst"])}
    buckets = buckets.sort_values(["bucket_type", "bucket"], key=lambda s: s.map(order) if s.name == "bucket" else s)
    return yearly, buckets


# ---------------------------------------------------------- single signal

def single_signal(con, flags: list[str] | None = None) -> pd.DataFrame:
    frames = []
    for flag in (flags or AVAILABLE):
        rows = con.execute(f"""
            WITH g AS (
                SELECT lag, 'all' AS bucket_type, 'ALL' AS bucket, {flag} AS flag, launch_300, launch_200, launch_500 FROM d
                UNION ALL
                SELECT lag, 'drawdown', drawdown_bucket, {flag}, launch_300, launch_200, launch_500 FROM d
                UNION ALL
                SELECT lag, 'mst', mst_bucket, {flag}, launch_300, launch_200, launch_500 FROM d
            )
            SELECT lag, bucket_type, bucket, count(*) AS rows_all, count(flag) AS n_nn,
                   count(*) FILTER (WHERE flag) AS n_true,
                   count(*) FILTER (WHERE flag IS NOT NULL AND launch_300) AS k300_nn,
                   count(*) FILTER (WHERE flag AND launch_300) AS k300_true,
                   count(*) FILTER (WHERE flag IS NOT NULL AND launch_200) AS k200_nn,
                   count(*) FILTER (WHERE flag AND launch_200) AS k200_true,
                   count(*) FILTER (WHERE flag IS NOT NULL AND launch_500) AS k500_nn,
                   count(*) FILTER (WHERE flag AND launch_500) AS k500_true
            FROM g GROUP BY 1, 2, 3
        """).fetchdf()
        rows["flag"] = flag
        frames.append(rows)
    wide = pd.concat(frames, ignore_index=True)
    # duckdb GROUP BY order is not stable; sort in FLAGS order so combination names keep the spec's order
    wide["_o"] = wide["flag"].map({f: i for i, f in enumerate(FLAGS + list(INVERTED))})
    wide = wide.sort_values(["_o", "lag", "bucket_type", "bucket"]).drop(columns="_o").reset_index(drop=True)
    out = []
    for thr in THRESHOLDS:
        t = thr.split("_")[1]
        sub = wide[["flag", "lag", "bucket_type", "bucket", "rows_all", "n_nn", "n_true",
                    f"k{t}_nn", f"k{t}_true"]].copy()
        sub.columns = ["flag", "lag", "bucket_type", "bucket", "rows_all", "n_nn", "n_true", "k_nn", "k_true"]
        sub["threshold"] = thr
        out.append(sub)
    ss = pd.concat(out, ignore_index=True)
    ss["coverage"] = ss["n_nn"] / ss["rows_all"]
    ss["true_share"] = ss["n_true"] / ss["n_nn"].where(ss["n_nn"] > 0)
    ss["base"] = ss["k_nn"] / ss["n_nn"].where(ss["n_nn"] > 0)
    ss["rate"] = ss["k_true"] / ss["n_true"].where(ss["n_true"] > 0)
    ss["lift"] = ss["rate"] / ss["base"].where(ss["base"] > 0)
    ci = ss.apply(lambda r: wilson(int(r["k_true"]), int(r["n_true"])), axis=1, result_type="expand")
    ss["ci_low"] = ci[0] / ss["base"].where(ss["base"] > 0)
    ss["ci_high"] = ci[1] / ss["base"].where(ss["base"] > 0)
    ss["events"] = ss["k_true"]
    ss["sufficient"] = ss["events"] >= MIN_EVENTS_PER_CELL
    ss["passes"] = ss["sufficient"] & (ss["lift"] >= PASS_LIFT) & (ss["ci_low"] >= PASS_CI_LOW)
    return ss


def verdicts(ss: pd.DataFrame) -> pd.DataFrame:
    s = ss[(ss["threshold"] == "launch_300")]
    rows = []
    for flag in AVAILABLE:
        overall = s[(s["flag"] == flag) & (s["bucket_type"] == "all")]
        passing = overall[overall["passes"]]
        best = overall.loc[overall["lift"].where(overall["sufficient"]).idxmax()] if overall["sufficient"].any() else None
        calm = s[(s["flag"] == flag) & (s["bucket_type"] == "drawdown") & (s["bucket"].isin(["0-10", "10-20"]))]
        verdict = "PASS" if len(passing) else ("insufficient" if best is None else "FAIL")
        if verdict == "PASS" and not calm["passes"].any():
            verdict = "CRASH-ONLY"
        rows.append({
            "flag": flag, "verdict": verdict,
            "pass_lags": ",".join(str(int(x)) for x in sorted(passing["lag"].tolist())),
            "best_lag": None if best is None else int(best["lag"]),
            "best_lift": None if best is None else best["lift"],
            "best_ci_low": None if best is None else best["ci_low"],
            "best_events": None if best is None else int(best["events"]),
            "best_coverage": None if best is None else best["coverage"],
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------ combinations

def evaluate_combos(con, combos: list[tuple[int, tuple[str, ...]]]) -> pd.DataFrame:
    """One row per (lag, combination): AND of the flags, lift against the base among rows where all are non-null.

    Also carries the launch_200 lift and CI (k200_nn / n_nn as its base) so a
    combination can be read on both thresholds.
    """
    total = {int(r[0]): int(r[1]) for r in con.execute(
        "SELECT lag, count(*) FILTER (WHERE launch_300) FROM d GROUP BY 1").fetchall()}
    total200 = {int(r[0]): int(r[1]) for r in con.execute(
        "SELECT lag, count(*) FILTER (WHERE launch_200) FROM d GROUP BY 1").fetchall()}
    rows_all = {int(r[0]): int(r[1]) for r in con.execute("SELECT lag, count(*) FROM d GROUP BY 1").fetchall()}
    out = []
    for lag, combo in combos:
        nn = " AND ".join(f"{c} IS NOT NULL" for c in combo)
        tr = " AND ".join(combo)
        r = con.execute(f"""
            SELECT count(*) FILTER (WHERE {nn}), count(*) FILTER (WHERE {tr}),
                   count(*) FILTER (WHERE {nn} AND launch_300), count(*) FILTER (WHERE {tr} AND launch_300),
                   count(*) FILTER (WHERE {nn} AND launch_200), count(*) FILTER (WHERE {tr} AND launch_200),
                   count(*) FILTER (WHERE {tr} AND launch_500)
            FROM d WHERE lag = {lag}
        """).fetchone()
        n_nn, n_true, k_nn, k_true, k200_nn, k200, k500 = r
        base = k_nn / n_nn if n_nn else float("nan")
        rate = k_true / n_true if n_true else float("nan")
        lo, hi = wilson(k_true, n_true)
        base200 = k200_nn / n_nn if n_nn else float("nan")
        rate200 = k200 / n_true if n_true else float("nan")
        lo2, hi2 = wilson(k200, n_true)
        out.append({
            "lag": lag, "size": len(combo), "combo": " AND ".join(combo), "flags": combo,
            "n_nn": n_nn, "n_true": n_true, "events": k_true, "base": base, "rate": rate,
            "lift": rate / base if base else float("nan"),
            "ci_low": lo / base if base else float("nan"), "ci_high": hi / base if base else float("nan"),
            "catch": k_true / total[lag] if total.get(lag) else float("nan"), "nn_share": n_nn / rows_all[lag],
            "rate_200": rate200, "events_200": k200,
            "lift_200": rate200 / base200 if base200 else float("nan"),
            "ci_low_200": lo2 / base200 if base200 else float("nan"),
            "ci_high_200": hi2 / base200 if base200 else float("nan"),
            "catch_200": k200 / total200[lag] if total200.get(lag) else float("nan"),
            "rate_500": k500 / n_true if n_true else float("nan"),
            "events_500": k500,
            "sufficient": k_true >= MIN_EVENTS_PER_CELL,
            "sufficient_200": k200 >= MIN_EVENTS_PER_CELL,
        })
    if not out:
        return pd.DataFrame(columns=["lag", "size", "combo", "lift", "sufficient"])
    return pd.DataFrame(out)


def combinations(con, ss: pd.DataFrame) -> pd.DataFrame:
    s = ss[(ss["threshold"] == "launch_300") & (ss["bucket_type"] == "all")]
    combos = []
    for lag in LAGS:
        q = s[(s["lag"] == lag) & s["sufficient"] & (s["lift"] >= COMBO_MIN_LIFT)]["flag"].tolist()
        for size in range(2, MAX_COMBINATION_SIZE + 1):
            combos += [(lag, c) for c in itertools.combinations(q, size)]
    cb = evaluate_combos(con, combos)
    if cb.empty:
        return cb
    cb["qualifying_flags_at_lag"] = cb["lag"].map(
        {lag: ", ".join(s[(s["lag"] == lag) & s["sufficient"] & (s["lift"] >= COMBO_MIN_LIFT)]["flag"]) for lag in LAGS})
    return cb.sort_values(["sufficient", "lift", "catch"], ascending=[False, False, False]).reset_index(drop=True)


def expected_winners(cb: pd.DataFrame, buckets: pd.DataFrame) -> pd.DataFrame:
    top = cb[cb["sufficient"]].head(TOP_WINNERS)
    rows = []
    for _, c in top.iterrows():
        row = {"lag": c["lag"], "combo": c["combo"], "lift": c["lift"], "events": c["events"]}
        for _, b in buckets.iterrows():
            key = f"{b['bucket_type']} {b['bucket']}"
            if b["k300"] >= MIN_EVENTS_PER_CELL:
                row[key] = 10 * (b["k300"] / b["rows_"]) * c["lift"]
            else:
                row[key] = None
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------ sector x year

def sector_year(con) -> pd.DataFrame:
    return con.execute("""
        SELECT sector, year, count(*) AS rows_, count(*) FILTER (WHERE launch_300) AS k300
        FROM d WHERE lag = 0 GROUP BY 1, 2 ORDER BY 1, 2
    """).fetchdf()


# ---------------------------------------------------------------- report

def f2(x, ok=True, nd=2):
    if not ok or x is None or (isinstance(x, float) and math.isnan(x)):
        return "insufficient" if not ok else "n/a"
    return f"{x:.{nd}f}"


def pct(x, nd=2):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.{nd}f}%"


def md_table(header: list[str], rows: list[list[str]], align_right_from: int = 1) -> list[str]:
    lines = ["| " + " | ".join(header) + " |",
             "| " + " | ".join("---" if i < align_right_from else "---:" for i in range(len(header))) + " |"]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return lines + [""]


def write_report(yearly, buckets, ss, vd, cb, ew, sy, n_rows_lag0):
    L = []
    L += ["# Build-window results — Section 2 Growth, spec section 7",
          "",
          f"Window 2006-01 to 2019-12 (D4). {n_rows_lag0:,} universe stock-months per lag, four lags (T-0, T-3, T-6, T-12).",
          "Every number comes from src/stats.py over data/processed/{features,labels,regime,universe}.parquet.",
          "The holdout was not read.",
          "",
          "Definitions. A cell's rows are the universe rows where the flag is non-null. base = launches / rows in",
          "that set; rate = launches / flag-TRUE rows; lift = rate / base. coverage = non-null rows / all rows and",
          "sits beside every lift. CI is the 95% Wilson interval on rate, divided by base. D8: a cell needs at least",
          f"{MIN_EVENTS_PER_CELL} launch events among flag-TRUE rows (or in the bucket, for base rates); below that it reads",
          "\"insufficient\". PASS = lift >= 2.0 with lower CI >= 1.5 at any lag. CRASH-ONLY = passes overall but in no",
          "drawdown bucket below 20%. No recommendations are made in this report.",
          ""]
    reading = REPORTS_DIR / "build_window_reading.md"
    if reading.exists():
        L += ["## Reading", "", reading.read_text().strip(), ""]

    # 7.1
    L += ["## 7.1 Base rates by year", ""]
    rows = []
    for _, r in yearly.iterrows():
        ok3, ok2, ok5 = (r["k300"] >= MIN_EVENTS_PER_CELL, r["k200"] >= MIN_EVENTS_PER_CELL, r["k500"] >= MIN_EVENTS_PER_CELL)
        rows.append([r["year"], f"{int(r['rows_']):,}", int(r["k300"]), pct(r["k300"] / r["rows_"]) if ok3 else "insufficient",
                     int(r["k200"]), pct(r["k200"] / r["rows_"]) if ok2 else "insufficient",
                     int(r["k500"]), pct(r["k500"] / r["rows_"]) if ok5 else "insufficient"])
    L += md_table(["year", "rows", "launch_300", "rate_300", "launch_200", "rate_200", "launch_500", "rate_500"], rows)

    # base rate by regime bucket
    L += ["## Base rate inside each regime bucket (section 6 buckets, decision month)", ""]
    rows = []
    for _, r in buckets.iterrows():
        ok3, ok2, ok5 = (r["k300"] >= MIN_EVENTS_PER_CELL, r["k200"] >= MIN_EVENTS_PER_CELL, r["k500"] >= MIN_EVENTS_PER_CELL)
        rows.append([r["bucket_type"], r["bucket"], f"{int(r['rows_']):,}", int(r["k300"]),
                     pct(r["k300"] / r["rows_"]) if ok3 else "insufficient", int(r["k200"]),
                     pct(r["k200"] / r["rows_"]) if ok2 else "insufficient", int(r["k500"]),
                     pct(r["k500"] / r["rows_"]) if ok5 else "insufficient"])
    L += md_table(["bucket type", "bucket", "rows", "launch_300", "rate_300", "launch_200", "rate_200", "launch_500", "rate_500"], rows, 2)

    # sector x year
    L += ["## Launch rate (launch_300) by sector and entry year", "",
          "Cell = launches / universe rows for that sector and year; D8 applied per cell. The last column and",
          "row are the same cells summed, so a sector or a year can pass D8 where its cells do not.", ""]
    years = sorted(sy["year"].unique())
    sectors = sorted(sy["sector"].unique())
    piv_r = sy.pivot(index="sector", columns="year", values="rows_").fillna(0)
    piv_k = sy.pivot(index="sector", columns="year", values="k300").fillna(0)
    rows = []
    for s in sectors:
        cells = []
        for y in years:
            k, n = piv_k.loc[s, y], piv_r.loc[s, y]
            cells.append(pct(k / n, 1) if k >= MIN_EVENTS_PER_CELL and n > 0 else ("insufficient" if n > 0 else "n/a"))
        k, n = piv_k.loc[s].sum(), piv_r.loc[s].sum()
        cells.append(f"{pct(k / n, 2)} ({int(k)}/{int(n):,})" if k >= MIN_EVENTS_PER_CELL else f"insufficient ({int(k)}/{int(n):,})")
        rows.append([s] + cells)
    cells = []
    for y in years:
        k, n = piv_k[y].sum(), piv_r[y].sum()
        cells.append(pct(k / n, 2) if k >= MIN_EVENTS_PER_CELL else "insufficient")
    rows.append(["all sectors"] + cells + [pct(piv_k.values.sum() / piv_r.values.sum(), 2)])
    L += md_table(["sector"] + [str(y) for y in years] + ["all years (launches/rows)"], rows)

    # 7.2 single signal launch_300
    s3 = ss[(ss["threshold"] == "launch_300") & (ss["bucket_type"] == "all")]
    L += ["## 7.2 Single-signal lift, launch_300, by lag", "",
          "rows_true = flag-TRUE rows; events = launches among them; rate = events / rows_true.", ""]
    rows = []
    for flag in AVAILABLE:
        for lag in LAGS:
            r = s3[(s3["flag"] == flag) & (s3["lag"] == lag)].iloc[0]
            ok = bool(r["sufficient"])
            rows.append([flag, lag, pct(r["coverage"], 1), pct(r["true_share"], 1), f"{int(r['n_true']):,}", int(r["events"]),
                         pct(r["rate"]) if ok else "insufficient", f2(r["lift"], ok), f2(r["ci_low"], ok), f2(r["ci_high"], ok),
                         "PASS" if r["passes"] else ("insufficient" if not ok else "")])
    L += md_table(["flag", "lag", "coverage", "true share", "rows_true", "events", "rate", "lift", "CI low", "CI high", "cell"], rows)

    L += ["### Verdicts (launch_300, section 7 pass/fail criteria)", ""]
    rows = []
    for _, r in vd.iterrows():
        has = not pd.isna(r["best_lag"])
        rows.append([r["flag"], FEATURE_STATUS[r["flag"]].split(" (")[0], r["verdict"], r["pass_lags"] or "-",
                     int(r["best_lag"]) if has else "-", f2(r["best_lift"]) if has else "-",
                     f2(r["best_ci_low"]) if has else "-", int(r["best_events"]) if has else "-",
                     pct(r["best_coverage"], 1) if has else "-"])
    L += md_table(["flag", "status", "verdict", "passing lags", "best lag", "lift", "CI low", "events", "coverage"], rows, 3)
    L += ["Unavailable or deferred, no lift computed: " + ", ".join(f"{f} ({FEATURE_STATUS[f]})" for f in UNAVAILABLE), ""]

    # 7.3 regime
    for bt, label in (("drawdown", "SPY drawdown bucket"), ("mst", "months-since-trough bucket")):
        bks = BUCKET_TYPES[bt]
        L += [f"## 7.3 Single-signal lift within each {label}, launch_300", "",
              "Cell = lift (events) or insufficient. Lift is against the base rate of the same bucket among non-null rows.", ""]
        sub = ss[(ss["threshold"] == "launch_300") & (ss["bucket_type"] == bt)]
        rows = []
        for flag in AVAILABLE:
            for lag in LAGS:
                cells = []
                for b in bks:
                    r = sub[(sub["flag"] == flag) & (sub["lag"] == lag) & (sub["bucket"] == b)]
                    if r.empty:
                        cells.append("n/a")
                        continue
                    r = r.iloc[0]
                    cells.append(f"{r['lift']:.2f} [{r['ci_low']:.2f}, {r['ci_high']:.2f}] ({int(r['events'])})"
                                 + (" PASS" if r["passes"] else "") if r["sufficient"] else f"insufficient ({int(r['events'])})")
                rows.append([flag, lag] + cells)
        L += md_table(["flag", "lag"] + bks, rows, 2)

    # 7.4 combinations
    L += ["## 7.4 Combinations (2- and 3-signal ANDs), launch_300", "",
          f"Candidates per lag: flags with lift >= {COMBO_MIN_LIFT} and >= {MIN_EVENTS_PER_CELL} events at that lag.",
          "catch = launches the combination catches / all launches at that lag. non-null share = rows where every",
          "flag in the combination is non-null / all rows. Ranked by lift, then catch. Top 20 shown; all in",
          "reports/s4_combinations.csv.", ""]
    for lag in LAGS:
        q = cb[cb["lag"] == lag]["qualifying_flags_at_lag"].iloc[0] if (cb["lag"] == lag).any() else "none"
        L.append(f"- lag {lag}: {q or 'none'}")
    L.append("")
    rows = []
    for _, r in cb.head(TOP_COMBOS).iterrows():
        ok = bool(r["sufficient"])
        rows.append([r["combo"], int(r["lag"]), f"{int(r['n_true']):,}", int(r["events"]), pct(r["rate"]) if ok else "insufficient",
                     f2(r["lift"], ok), f2(r["ci_low"], ok), f2(r["ci_high"], ok), pct(r["catch"], 1), pct(r["nn_share"], 1),
                     pct(r["rate_200"]) if ok else "insufficient",
                     pct(r["rate_500"]) if r["events_500"] >= MIN_EVENTS_PER_CELL else "insufficient"])
    L += md_table(["combination", "lag", "rows_true", "events", "rate_300", "lift", "CI low", "CI high", "catch", "non-null share",
                   "rate_200", "rate_500"], rows)
    n_suff = int(cb["sufficient"].sum()) if len(cb) else 0
    L += [f"{len(cb)} combinations evaluated, {n_suff} with >= {MIN_EVENTS_PER_CELL} events.", ""]

    # expected winners
    L += ["## Expected launches per ten picks, top ten combinations, by regime bucket", "",
          "Cell = 10 x (bucket base rate for launch_300) x (combination's overall lift). This assumes the",
          "combination's lift is the same in every regime; section 7.3 shows where single signals are not.",
          "Buckets with fewer than 100 launches read insufficient.", ""]
    if len(ew):
        bcols = [c for c in ew.columns if c not in ("lag", "combo", "lift", "events")]
        rows = []
        for _, r in ew.iterrows():
            rows.append([r["combo"], int(r["lag"]), f2(r["lift"])] + [f2(r[c]) if r[c] is not None and not pd.isna(r[c]) else "insufficient" for c in bcols])
        L += md_table(["combination", "lag", "lift"] + bcols, rows, 2)
    else:
        L += ["No combination met D8.", ""]

    # 7.5 controls
    L += ["## 7.5 Control signals", "",
          "The three controls (pe < 15, pb < 1.5, dividend yield > 2%) are in every table above under ctl_*,",
          "computed identically. Their verdict rows are in the verdict table.", ""]

    # launch_200 / launch_500 single-signal
    for thr in ("launch_200", "launch_500"):
        L += [f"## Single-signal lift, {thr}, by lag", ""]
        st = ss[(ss["threshold"] == thr) & (ss["bucket_type"] == "all")]
        rows = []
        for flag in AVAILABLE:
            cells = []
            for lag in LAGS:
                r = st[(st["flag"] == flag) & (st["lag"] == lag)].iloc[0]
                cells.append(f"{r['lift']:.2f} [{r['ci_low']:.2f}, {r['ci_high']:.2f}] ({int(r['events'])})" if r["sufficient"]
                             else f"insufficient ({int(r['events'])})")
            rows.append([flag] + cells)
        L += md_table(["flag"] + [f"lag {lag}" for lag in LAGS], rows)

    out = REPORTS_DIR / "build_window_results.md"
    out.write_text("\n".join(L))
    return out


def main() -> int:
    con = duckdb.connect()
    load(con)
    n_lag0 = con.execute("SELECT count(*) FROM d WHERE lag = 0").fetchone()[0]
    yearly, buckets = base_rates(con)
    ss = single_signal(con)
    vd = verdicts(ss)
    cb = combinations(con, ss)
    ew = expected_winners(cb, buckets)
    sy = sector_year(con)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ss.drop(columns=[]).to_csv(REPORTS_DIR / "s4_single_signal.csv", index=False)
    cb.drop(columns=["flags"]).to_csv(REPORTS_DIR / "s4_combinations.csv", index=False)
    ew.to_csv(REPORTS_DIR / "s4_expected_winners.csv", index=False)
    sy.to_csv(REPORTS_DIR / "s4_sector_year.csv", index=False)
    pd.concat([yearly.assign(bucket_type="year", bucket=yearly["year"]).drop(columns=["year"]), buckets]).to_csv(
        REPORTS_DIR / "s4_base_rates.csv", index=False)
    out = write_report(yearly, buckets, ss, vd, cb, ew, sy, n_lag0)
    print(vd.to_string(index=False))
    print(f"\ncombinations evaluated: {len(cb)}, meeting D8: {int(cb['sufficient'].sum()) if len(cb) else 0}")
    if len(cb):
        print(cb[cb["sufficient"]].head(10)[["lag", "combo", "events", "lift", "ci_low", "catch"]].to_string(index=False))
    print(f"-> {out}")
    print("RESULT: PASS — report written" if out.exists() else "RESULT: FAIL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
