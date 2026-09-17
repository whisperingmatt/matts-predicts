"""S6 — GROWTH-002 decile retest, build window (spec sections 1 to 4, S6 half).

Input:  data/processed/features.parquet (with the six raw columns appended
        2026-09-18), labels12.parquet (E1), labels.parquet (launch_300
        reference), regime.parquet
Output: data/processed/deciles.parquet — decile rank per feature per
        (ticker, month_end, lag), every month (ranks are within month and
        lag, so holdout months rank without being read for results)
        reports/decile_build_results.md (+ reports/decile_build_reading.md
        inserted verbatim when present)
        reports/s6_decile_cells.csv, s6_extreme_cells.csv, s6_composite.csv

    python -m src.decile

Rules implemented (decisions.md 2026-09-17, "Chunk 4b"): decile =
min(10, floor(10 x percent_rank) + 1) within (month_end, lag) among
non-null rows, ties sharing the lowest rank; lift among non-null rows with
coverage beside it; Wilson CI over a fixed base; D8 at 100 events; declared
directions from spec section 3, fixed here before any result was seen;
build-window pass = extreme-cell lift >= 1.5, lower bound >= 1.2, and
Spearman |rho| >= 0.6 with the declared sign over D8-sufficient deciles;
composite per section 4. Holdout rows are never summarized here.
"""
from __future__ import annotations

import math
import sys

import duckdb
import pandas as pd

from src.config import BUILD_END, BUILD_START, LAGS, MIN_EVENTS_PER_CELL, PROCESSED_DIR, REPORTS_DIR
from src.stats import BUCKET_TYPES, f2, md_table, pct, wilson

# name -> (SQL over features f, declared direction). Order is the report order.
FEATURES: dict[str, tuple[str, str]] = {
    "ret_6m_skip1": ("f.rs6_return", "HIGH"),
    "ret_12m_skip1": ("f.rs12_return", "HIGH"),
    "eps_growth_q0": ("f.eps_growth_q0", "HIGH"),
    "rev_growth_accel": ("f.rev_growth_accel", "HIGH"),
    "op_margin_delta": ("f.op_margin_delta", "HIGH"),
    "peg": ("f.peg", "LOW"),
    "pe": ("f.pe", "LOW"),
    "pe_vs_5y_median": ("f.pe_vs_5y_median", "LOW"),
    "fcf_ps_slope": ("f.fcf_slope_num", "HIGH"),
    "pegy": ("CASE WHEN f.pe > 0 AND (f.eps_ttm_growth + f.divyield) > 0 "
             "THEN f.pe / ((f.eps_ttm_growth + f.divyield) * 100) END", "LOW"),
    "pct_from_52w_high": ("1 - f.high52_ratio", "LOW"),
    "dist_above_30w_sma": ("f.dist_above_30w_sma", "HIGH"),
    "atr_contraction": ("f.atr_contraction", "HIGH"),
    "inst_pct": ("f.inst_pct", "LOWMID"),
    "inst_pct_delta_qoq": ("f.inst_pct - f.inst_pct_prev", "HIGH"),
    "insider_buy_count_90d": ("f.insider_buyers_90d", "HIGH"),
    "net_debt_to_ebitda": ("f.net_debt_to_ebitda_ttm", "LOW"),
    "share_count_change_8q": ("f.share_count_change_8q", "LOW"),
    "shareholder_yield": ("f.divyield - f.share_count_change_8q / 2", "HIGH"),
    "marketcap": ("f.marketcap", "LOW"),
    "pb": ("f.pb", "LOW"),
    "dividend_yield": ("f.divyield", "LOW"),
}
LABELS = ["win_50", "win_100", "launch_300"]
PASS_LIFT, PASS_CI_LOW, PASS_RHO, RHO_MIN_DECILES = 1.5, 1.2, 0.6, 5
EXTREME = {"HIGH": [10], "LOW": [1], "LOWMID": [3, 4, 5, 6]}


def pq(name: str) -> str:
    return f"read_parquet('{(PROCESSED_DIR / name).as_posix()}')"


def spearman(x: list[float], y: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    if len(x) < 2:
        return float("nan")
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


# ------------------------------------------------------------------ data

def build_deciles(con: duckdb.DuckDBPyConnection) -> None:
    raw = ", ".join(f"{expr} AS {name}" for name, (expr, _) in FEATURES.items())
    con.execute(f"""
        CREATE TABLE d0 AS
        SELECT f.ticker, f.month_end, f.lag, {raw},
               l12.win_50, l12.win_100, l24.launch_300,
               r.drawdown_bucket, r.mst_bucket,
               f.month_end BETWEEN DATE '{BUILD_START}' AND DATE '{BUILD_END}' AS in_build
        FROM {pq('features.parquet')} f
        JOIN {pq('labels12.parquet')} l12 USING (ticker, month_end)
        JOIN {pq('labels.parquet')} l24 USING (ticker, month_end)
        JOIN {pq('regime.parquet')} r ON r.month_end = f.month_end
    """)
    ranks = ", ".join(
        f"CASE WHEN {name} IS NOT NULL THEN least(10, floor(10 * percent_rank() OVER "
        f"(PARTITION BY month_end, lag, {name} IS NULL ORDER BY {name})) + 1)::INTEGER END AS dec_{name}"
        for name in FEATURES)
    con.execute(f"""
        CREATE TABLE d AS
        SELECT ticker, month_end, lag, win_50, win_100, launch_300, drawdown_bucket, mst_bucket, in_build,
               {ranks}
        FROM d0
    """)
    out = PROCESSED_DIR / "deciles.parquet"
    con.execute(f"COPY (SELECT * FROM d ORDER BY month_end, ticker, lag) TO '{out.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    n = con.execute("SELECT count(*) FROM d").fetchone()[0]
    print(f"deciles.parquet: {n:,} rows, {len(FEATURES)} features -> {out}")


# ------------------------------------------------------------- statistics

def cells(con) -> pd.DataFrame:
    """One row per (feature, lag, bucket_type, bucket, decile) with counts for every label, build window."""
    frames = []
    for name in FEATURES:
        rows = con.execute(f"""
            WITH g AS (
                SELECT lag, 'all' AS bucket_type, 'ALL' AS bucket, dec_{name} AS dec, win_50, win_100, launch_300 FROM d WHERE in_build
                UNION ALL
                SELECT lag, 'drawdown', drawdown_bucket, dec_{name}, win_50, win_100, launch_300 FROM d WHERE in_build
                UNION ALL
                SELECT lag, 'mst', mst_bucket, dec_{name}, win_50, win_100, launch_300 FROM d WHERE in_build
            )
            SELECT lag, bucket_type, bucket, dec, count(*) AS n,
                   count(*) FILTER (WHERE win_50) AS k_win_50,
                   count(*) FILTER (WHERE win_100) AS k_win_100,
                   count(*) FILTER (WHERE launch_300) AS k_launch_300
            FROM g GROUP BY 1, 2, 3, 4
        """).fetchdf()
        rows["feature"] = name
        frames.append(rows)
    c = pd.concat(frames, ignore_index=True)
    c["_o"] = c["feature"].map({f: i for i, f in enumerate(FEATURES)})
    c["dec"] = c["dec"].astype("Int64")
    return c.sort_values(["_o", "lag", "bucket_type", "bucket", "dec"], na_position="last").drop(columns="_o").reset_index(drop=True)


def decile_table(c: pd.DataFrame) -> pd.DataFrame:
    """Per (feature, lag, bucket, label): base among non-null rows, coverage, and per-decile lift."""
    out = []
    for (feature, lag, bt, b), grp in c.groupby(["feature", "lag", "bucket_type", "bucket"], sort=False):
        rows_all = grp["n"].sum()
        nn = grp[grp["dec"].notna()]
        n_nn = nn["n"].sum()
        for label in LABELS:
            k_nn = nn[f"k_{label}"].sum()
            base = k_nn / n_nn if n_nn else float("nan")
            for _, r in nn.iterrows():
                k, n = int(r[f"k_{label}"]), int(r["n"])
                rate = k / n if n else float("nan")
                lo, hi = wilson(k, n)
                out.append({"feature": feature, "direction": FEATURES[feature][1], "lag": lag, "bucket_type": bt,
                            "bucket": b, "label": label, "decile": int(r["dec"]), "rows": n, "row_share": n / n_nn,
                            "events": k, "rate": rate, "base": base, "coverage": n_nn / rows_all,
                            "lift": rate / base if base else float("nan"),
                            "ci_low": lo / base if base else float("nan"), "ci_high": hi / base if base else float("nan"),
                            "sufficient": k >= MIN_EVENTS_PER_CELL})
    return pd.DataFrame(out)


def extreme_table(c: pd.DataFrame, dt: pd.DataFrame) -> pd.DataFrame:
    """The declared extreme cell per (feature, lag, bucket, label), with rho and the build-window verdict."""
    out = []
    for (feature, lag, bt, b), grp in c.groupby(["feature", "lag", "bucket_type", "bucket"], sort=False):
        direction = FEATURES[feature][1]
        nn = grp[grp["dec"].notna()]
        n_nn = nn["n"].sum()
        rows_all = grp["n"].sum()
        ext = nn[nn["dec"].isin(EXTREME[direction])]
        for label in LABELS:
            k_nn = nn[f"k_{label}"].sum()
            base = k_nn / n_nn if n_nn else float("nan")
            k, n = int(ext[f"k_{label}"].sum()), int(ext["n"].sum())
            rate = k / n if n else float("nan")
            lo, hi = wilson(k, n)
            lift = rate / base if base else float("nan")
            ci_low = lo / base if base else float("nan")
            curve = dt[(dt["feature"] == feature) & (dt["lag"] == lag) & (dt["bucket_type"] == bt) & (dt["bucket"] == b)
                       & (dt["label"] == label) & dt["sufficient"]]
            rho = spearman(curve["decile"].tolist(), curve["lift"].tolist()) if len(curve) >= RHO_MIN_DECILES else float("nan")
            rho_ok = {"HIGH": rho >= PASS_RHO, "LOW": rho <= -PASS_RHO, "LOWMID": True}[direction] if not math.isnan(rho) or direction == "LOWMID" else False
            sufficient = k >= MIN_EVENTS_PER_CELL
            passes = bool(sufficient and lift >= PASS_LIFT and ci_low >= PASS_CI_LOW and rho_ok)
            out.append({"feature": feature, "direction": direction, "lag": lag, "bucket_type": bt, "bucket": b, "label": label,
                        "extreme_deciles": "+".join(str(x) for x in EXTREME[direction]), "coverage": n_nn / rows_all,
                        "rows": n, "row_share": n / n_nn if n_nn else float("nan"), "events": k, "rate": rate, "base": base,
                        "lift": lift, "ci_low": ci_low, "ci_high": hi / base if base else float("nan"),
                        "rho": rho, "rho_deciles": len(curve), "sufficient": sufficient, "pass_build": passes})
    return pd.DataFrame(out)


def verdicts(ex: pd.DataFrame) -> pd.DataFrame:
    out = []
    for feature in FEATURES:
        for label in LABELS:
            s = ex[(ex["feature"] == feature) & (ex["label"] == label) & (ex["bucket_type"] == "all")]
            passing = s[s["pass_build"]]
            best = s.loc[s["lift"].where(s["sufficient"]).idxmax()] if s["sufficient"].any() else None
            regime_dep = None
            if len(passing):
                lag = int(passing.iloc[0]["lag"])
                calm = ex[(ex["feature"] == feature) & (ex["label"] == label) & (ex["lag"] == lag)
                          & (ex["bucket_type"] == "drawdown") & (ex["bucket"].isin(["0-10", "10-20"]))]
                regime_dep = bool(len(calm) and (calm["lift"] < 1.2).all())
            out.append({"feature": feature, "direction": FEATURES[feature][1], "label": label,
                        "verdict_build": "PASS-build" if len(passing) else ("insufficient" if best is None else "FAIL"),
                        "pass_lags": ",".join(str(int(x)) for x in sorted(passing["lag"])),
                        "best_lag": None if best is None else int(best["lag"]),
                        "best_lift": None if best is None else best["lift"],
                        "best_ci_low": None if best is None else best["ci_low"],
                        "best_rho": None if best is None else best["rho"],
                        "best_events": None if best is None else int(best["events"]),
                        "regime_dependent": regime_dep})
    return pd.DataFrame(out)


# --------------------------------------------------------------- composite

def composite(con, vd: pd.DataFrame, ex: pd.DataFrame) -> tuple[list[str], bool, pd.DataFrame]:
    members = vd[(vd["label"] == "win_50") & (vd["verdict_build"] == "PASS-build")]["feature"].tolist()
    unconfirmed = False
    if len(members) < 3:
        unconfirmed = True
        best = (ex[(ex["label"] == "win_50") & (ex["bucket_type"] == "all") & ex["sufficient"]]
                .groupby("feature")["lift"].max().sort_values(ascending=False))
        members = [f for f in FEATURES if f in best.index[:3]]
    oriented = ", ".join(
        f"CASE WHEN FEATURES_DIR = 'x' THEN 0 END" for _ in [])  # placeholder to keep f-string simple
    terms = []
    for m in members:
        terms.append(f"dec_{m}" if FEATURES[m][1] in ("HIGH", "LOWMID") else f"(11 - dec_{m})")
    nn = " AND ".join(f"dec_{m} IS NOT NULL" for m in members)
    con.execute(f"""
        CREATE TABLE comp AS
        WITH c AS (
            SELECT ticker, month_end, lag, win_50, win_100, launch_300, drawdown_bucket, mst_bucket, in_build,
                   CASE WHEN {nn} THEN ({" + ".join(terms)}) / {len(terms)}.0 END AS score
            FROM d
        )
        SELECT *, CASE WHEN score IS NOT NULL THEN least(10, floor(10 * percent_rank() OVER
                       (PARTITION BY month_end, lag, score IS NULL ORDER BY score)) + 1)::INTEGER END AS dec_comp
        FROM c
    """)
    rows = con.execute("""
        WITH g AS (
            SELECT lag, 'all' AS bucket_type, 'ALL' AS bucket, dec_comp, win_50, win_100, launch_300 FROM comp WHERE in_build
            UNION ALL SELECT lag, 'drawdown', drawdown_bucket, dec_comp, win_50, win_100, launch_300 FROM comp WHERE in_build
            UNION ALL SELECT lag, 'mst', mst_bucket, dec_comp, win_50, win_100, launch_300 FROM comp WHERE in_build
        )
        SELECT lag, bucket_type, bucket, dec_comp AS dec, count(*) AS n,
               count(*) FILTER (WHERE win_50) AS k_win_50, count(*) FILTER (WHERE win_100) AS k_win_100,
               count(*) FILTER (WHERE launch_300) AS k_launch_300
        FROM g GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4
    """).fetchdf()
    rows["dec"] = rows["dec"].astype("Int64")
    out = []
    for (lag, bt, b), grp in rows.groupby(["lag", "bucket_type", "bucket"], sort=False):
        rows_all = grp["n"].sum()
        nn_ = grp[grp["dec"].notna()]
        n_nn = nn_["n"].sum()
        for label in LABELS:
            base = nn_[f"k_{label}"].sum() / n_nn if n_nn else float("nan")
            for cell_name, decs in (("decile 10", [10]), ("deciles 8-10", [8, 9, 10])):
                sel = nn_[nn_["dec"].isin(decs)]
                k, n = int(sel[f"k_{label}"].sum()), int(sel["n"].sum())
                rate = k / n if n else float("nan")
                lo, hi = wilson(k, n)
                out.append({"lag": lag, "bucket_type": bt, "bucket": b, "label": label, "cell": cell_name,
                            "rows": n, "row_share": n / n_nn if n_nn else float("nan"), "pool_share_of_all": n / rows_all,
                            "events": k, "rate": rate, "base": base, "coverage": n_nn / rows_all,
                            "lift": rate / base if base else float("nan"),
                            "ci_low": lo / base if base else float("nan"), "ci_high": hi / base if base else float("nan"),
                            "sufficient": k >= MIN_EVENTS_PER_CELL})
    return members, unconfirmed, pd.DataFrame(out)


# ---------------------------------------------------------------- report

def cell_str(r) -> str:
    return (f"{r['lift']:.2f} [{r['ci_low']:.2f}, {r['ci_high']:.2f}] ({int(r['events'])})" if r["sufficient"]
            else f"insufficient ({int(r['events'])})")


def write_report(dt, ex, vd, members, unconfirmed, comp, base_by_year, n_lag0) -> None:
    L = ["# Decile retest — build-window results (GROWTH-002, S6)", "",
         f"Window 2006-01 to 2019-12. {n_lag0:,} universe stock-months per lag, four lags. Labels: win_50 and win_100",
         "(12-month forward return >= 50% / >= 100%, E1) with launch_300 (24-month, D1) as reference. Every",
         "number comes from src/decile.py over data/processed/{features,labels12,labels,regime}.parquet. The",
         "holdout was not summarized.", "",
         "Definitions. Decile = rank within (month_end, lag) among non-null rows, ties sharing the lowest rank,",
         "decile 10 = highest raw value; decile sizes are unequal where a feature has mass points, so each cell",
         "prints its row share. base = events / non-null rows at that lag; lift = cell rate / base; coverage =",
         f"non-null rows / all rows. Wilson 95% CI over a fixed base. D8: {MIN_EVENTS_PER_CELL} events per cell. Directions were",
         "declared in spec section 3 before any result. Build-window pass (half of the section 3 criterion) =",
         f"extreme-cell lift >= {PASS_LIFT} with lower bound >= {PASS_CI_LOW}, and Spearman |rho| >= {PASS_RHO} with the declared",
         "sign over the D8-sufficient deciles (at least 5). The holdout half is S7. No recommendations.", ""]
    reading = REPORTS_DIR / "decile_build_reading.md"
    if reading.exists():
        L += ["## Reading", "", reading.read_text().strip(), ""]

    L += ["## Base rates by year (12-month labels), build window", ""]
    rows = [[y, f"{int(n):,}", int(a), pct(a / n), int(b), pct(b / n), int(c), pct(c / n)] for y, n, a, b, c in base_by_year]
    L += md_table(["year", "rows", "win_50", "rate_50", "win_100", "rate_100", "launch_300", "rate_300"], rows)

    for label in LABELS:
        L += [f"## Extreme-decile cells, {label}, by lag", "",
              "Extreme = decile 10 for HIGH, decile 1 for LOW, deciles 3-6 pooled for LOW-to-MID (inst_pct).", ""]
        rows = []
        for feature in FEATURES:
            for lag in LAGS:
                r = ex[(ex["feature"] == feature) & (ex["lag"] == lag) & (ex["bucket_type"] == "all") & (ex["label"] == label)].iloc[0]
                ok = bool(r["sufficient"])
                rows.append([feature, r["direction"], lag, pct(r["coverage"], 1), pct(r["row_share"], 1), f"{int(r['rows']):,}",
                             int(r["events"]), pct(r["rate"]) if ok else "insufficient", f2(r["lift"], ok), f2(r["ci_low"], ok),
                             f2(r["ci_high"], ok), "n/a" if math.isnan(r["rho"]) else f"{r['rho']:.2f}",
                             "PASS-build" if r["pass_build"] else ("insufficient" if not ok else "")])
        L += md_table(["feature", "dir", "lag", "coverage", "cell share", "rows", "events", "rate", "lift", "CI low", "CI high", "rho", "cell"], rows, 3)

    L += ["## Verdicts (build-window half of section 3), all labels", ""]
    rows = []
    for _, r in vd.iterrows():
        has = r["best_lag"] is not None and not pd.isna(r["best_lag"])
        rows.append([r["feature"], r["direction"], r["label"], r["verdict_build"], r["pass_lags"] or "-",
                     int(r["best_lag"]) if has else "-", f2(r["best_lift"]) if has else "-", f2(r["best_ci_low"]) if has else "-",
                     ("n/a" if pd.isna(r["best_rho"]) else f"{r['best_rho']:.2f}") if has else "-",
                     int(r["best_events"]) if has else "-",
                     "-" if r["regime_dependent"] is None else ("yes" if r["regime_dependent"] else "no")])
    L += md_table(["feature", "dir", "label", "verdict", "passing lags", "best lag", "lift", "CI low", "rho", "events", "regime-dependent"], rows, 4)

    L += ["## Decile lift curves, win_50, lag 0", "", "Cell = lift (events); insufficient cells show the event count only.", ""]
    rows = []
    for feature in FEATURES:
        s = dt[(dt["feature"] == feature) & (dt["lag"] == 0) & (dt["bucket_type"] == "all") & (dt["label"] == "win_50")]
        cells_ = []
        for dnum in range(1, 11):
            r = s[s["decile"] == dnum]
            cells_.append("-" if r.empty else (f"{r.iloc[0]['lift']:.2f} ({int(r.iloc[0]['events'])})" if r.iloc[0]["sufficient"]
                                                else f"insuff. ({int(r.iloc[0]['events'])})"))
        rows.append([feature, FEATURES[feature][1]] + cells_)
    L += md_table(["feature", "dir"] + [f"D{i}" for i in range(1, 11)], rows, 2)

    L += ["## Extreme-cell lift by SPY drawdown bucket, win_50 (regime-dependence check)", ""]
    rows = []
    for feature in FEATURES:
        for lag in LAGS:
            cells_ = []
            for b in BUCKET_TYPES["drawdown"]:
                r = ex[(ex["feature"] == feature) & (ex["lag"] == lag) & (ex["bucket_type"] == "drawdown") & (ex["bucket"] == b) & (ex["label"] == "win_50")]
                cells_.append("n/a" if r.empty else cell_str(r.iloc[0]))
            rows.append([feature, lag] + cells_)
    L += md_table(["feature", "lag"] + BUCKET_TYPES["drawdown"], rows, 2)

    L += ["## Composite (section 4)", "",
          ("Members = features that PASS-build on win_50: " if not unconfirmed else
           "Fewer than 3 features PASS-build on win_50; composite built from the top 3 by extreme-decile lift, UNCONFIRMED: ")
          + ", ".join(members) + ".",
          "Composite = mean oriented decile (11 - decile for LOW features) over rows where every member is non-null,",
          "ranked into deciles per (month_end, lag). pool share = rows in the cell / all universe rows at that lag.", ""]
    rows = []
    for lag in LAGS:
        for label in LABELS:
            for cell_name in ("decile 10", "deciles 8-10"):
                r = comp[(comp["lag"] == lag) & (comp["bucket_type"] == "all") & (comp["label"] == label) & (comp["cell"] == cell_name)].iloc[0]
                ok = bool(r["sufficient"])
                rows.append([lag, label, cell_name, pct(r["coverage"], 1), pct(r["pool_share_of_all"], 1), f"{int(r['rows']):,}", int(r["events"]),
                             pct(r["rate"]) if ok else "insufficient", f2(r["lift"], ok), f2(r["ci_low"], ok), f2(r["ci_high"], ok)])
    L += md_table(["lag", "label", "cell", "coverage", "pool share", "rows", "events", "rate", "lift", "CI low", "CI high"], rows, 3)
    for bt, label_name in (("drawdown", "SPY drawdown bucket"), ("mst", "months-since-trough bucket")):
        L += [f"### Composite by {label_name}, lag 0", ""]
        rows = []
        for label in LABELS:
            for cell_name in ("decile 10", "deciles 8-10"):
                cells_ = []
                for b in BUCKET_TYPES[bt]:
                    r = comp[(comp["lag"] == 0) & (comp["bucket_type"] == bt) & (comp["bucket"] == b) & (comp["label"] == label) & (comp["cell"] == cell_name)]
                    cells_.append("n/a" if r.empty else cell_str(r.iloc[0]))
                rows.append([label, cell_name] + cells_)
        L += md_table(["label", "cell"] + BUCKET_TYPES[bt], rows, 2)

    out = REPORTS_DIR / "decile_build_results.md"
    out.write_text("\n".join(L))
    print(f"-> {out}")


def main() -> int:
    tmp = PROCESSED_DIR / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute("SET memory_limit = '10GB'")
    build_deciles(con)
    n_lag0, k50 = con.execute("SELECT count(*), count(*) FILTER (WHERE win_50) FROM d WHERE in_build AND lag = 0").fetchone()
    base50 = k50 / n_lag0
    print(f"build window: {n_lag0:,} rows per lag, win_50 base {base50:.2%}")
    if not 0.03 <= base50 <= 0.25:
        print("STOP: win_50 base rate outside [3%, 25%] (GROWTH-002 section 3)")
        return 1
    base_by_year = con.execute("""
        SELECT year(month_end), count(*), count(*) FILTER (WHERE win_50), count(*) FILTER (WHERE win_100),
               count(*) FILTER (WHERE launch_300) FROM d WHERE in_build AND lag = 0 GROUP BY 1 ORDER BY 1""").fetchall()
    c = cells(con)
    dt = decile_table(c)
    ex = extreme_table(c, dt)
    vd = verdicts(ex)
    members, unconfirmed, comp = composite(con, vd, ex)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    dt.to_csv(REPORTS_DIR / "s6_decile_cells.csv", index=False)
    ex.to_csv(REPORTS_DIR / "s6_extreme_cells.csv", index=False)
    comp.assign(members="|".join(members), unconfirmed=unconfirmed).to_csv(REPORTS_DIR / "s6_composite.csv", index=False)
    write_report(dt, ex, vd, members, unconfirmed, comp, base_by_year, n_lag0)
    print(vd[vd["label"] == "win_50"][["feature", "direction", "verdict_build", "pass_lags", "best_lag", "best_lift", "best_ci_low", "best_rho", "best_events", "regime_dependent"]].round(2).to_string(index=False))
    print(f"composite members ({'UNCONFIRMED top-3' if unconfirmed else 'PASS-build set'}): {members}")
    print(comp[(comp["bucket_type"] == "all") & (comp["lag"] == 0)][["label", "cell", "pool_share_of_all", "events", "lift", "ci_low", "ci_high"]].round(3).to_string(index=False))
    print("RESULT: PASS — build-window decile report written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
