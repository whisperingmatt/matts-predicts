"""S7 — GROWTH-002 holdout (spec section 5, S7) on 2020-01 to 2025-06.

Runs the same decile engine (src/decile.py) on the build and holdout
windows, applies the full section 3 criterion (build AND holdout), scores
the composite with Matt's S7 recipe in both windows, and adds the
exploratory realized-volatility block outside the pass criteria.

    python -m src.decile_holdout

Output: reports/decile_holdout_results.md (+ reports/decile_holdout_reading.md
        inserted verbatim when present); reports/s7_extreme_cells.csv,
        s7_decile_cells.csv, s7_composite.csv, s7_realized_vol.csv,
        s7_expected_winners.csv

launch_300 is observable only through 2024-08 decision dates; its holdout
cells count only observable rows (decisions.md 2026-09-17, S7 rulings).
CONFIRMED on a label = a lag where the build extreme cell PASS-build
(lift >= 1.5, lower bound >= 1.2, rho with the declared sign) AND the
holdout extreme cell has lift >= 1.5 with lower bound >= 1.2 on >= 100
events. Expected win_50 per ten picks = 10 x holdout bucket base rate x
composite decile-10 holdout lift. No recommendations.
"""
from __future__ import annotations

import math
import sys

import duckdb
import pandas as pd

from src.config import BUILD_END, BUILD_START, LAGS, MIN_EVENTS_PER_CELL, PROCESSED_DIR, REPORTS_DIR
from src.decile import (EXPLORATORY, FEATURES, HOLDOUT_END_12M, HOLDOUT_START, LABELS, PASS_CI_LOW, PASS_LIFT,
                        build_deciles, cell_str, cells, composite, composite_members, decile_table, extreme_table,
                        verdicts)
from src.stats import BUCKET_TYPES, f2, md_table, pct

CORR_WITH = ["marketcap", "pct_from_52w_high", "share_count_change_8q"]


def holdout_pass(r) -> bool:
    return bool(r["sufficient"]) and r["lift"] >= PASS_LIFT and r["ci_low"] >= PASS_CI_LOW


def main() -> int:
    tmp = PROCESSED_DIR / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    con.execute("SET memory_limit = '10GB'")
    build_deciles(con)

    # Build window (same code as S6, recipe per S7).
    c_b = cells(con, BUILD_START, BUILD_END, list(FEATURES) + list(EXPLORATORY))
    dt_b = decile_table(c_b)
    ex_b = extreme_table(c_b, dt_b)
    vd_b = verdicts(ex_b)
    members, unconfirmed = composite_members(vd_b, ex_b)
    comp_b = composite(con, members, BUILD_START, BUILD_END)

    # Holdout.
    c_h = cells(con, HOLDOUT_START, HOLDOUT_END_12M, list(FEATURES) + list(EXPLORATORY))
    dt_h = decile_table(c_h)
    ex_h = extreme_table(c_h, dt_h)
    ex_h["pass_holdout"] = ex_h.apply(holdout_pass, axis=1)
    comp_h = composite(con, members, HOLDOUT_START, HOLDOUT_END_12M)
    for df, w in ((ex_b, "build"), (ex_h, "holdout"), (dt_b, "build"), (dt_h, "holdout"), (comp_b, "build"), (comp_h, "holdout")):
        df["window"] = w

    # Full section 3 verdict: a lag passing both windows on the label.
    verdict_rows = []
    for feature in FEATURES:
        for label in LABELS:
            b = ex_b[(ex_b["feature"] == feature) & (ex_b["label"] == label) & (ex_b["bucket_type"] == "all")]
            h = ex_h[(ex_h["feature"] == feature) & (ex_h["label"] == label) & (ex_h["bucket_type"] == "all")]
            both = sorted(set(b[b["pass_build"]]["lag"]) & set(h[h["pass_holdout"]]["lag"]))
            hbest = h.loc[h["lift"].where(h["sufficient"]).idxmax()] if h["sufficient"].any() else None
            calm = ex_h[(ex_h["feature"] == feature) & (ex_h["label"] == label) & (ex_h["bucket_type"] == "drawdown")
                        & (ex_h["bucket"].isin(["0-10", "10-20"])) & ex_h["sufficient"]]
            verdict_rows.append({
                "feature": feature, "direction": FEATURES[feature][1], "label": label,
                "build_pass_lags": ",".join(str(int(x)) for x in sorted(b[b["pass_build"]]["lag"])) or "-",
                "holdout_pass_lags": ",".join(str(int(x)) for x in sorted(h[h["pass_holdout"]]["lag"])) or "-",
                "verdict": "CONFIRMED" if both else ("NOT CONFIRMED" if b["pass_build"].any() else "no build pass"),
                "confirmed_lags": ",".join(str(int(x)) for x in both) or "-",
                "holdout_best": "-" if hbest is None else f"{hbest['lift']:.2f} [{hbest['ci_low']:.2f}, {hbest['ci_high']:.2f}] lag {int(hbest['lag'])} ({int(hbest['events'])})",
                "holdout_calm_min_lift": float("nan") if calm.empty else calm["lift"].min(),
            })
    vd = pd.DataFrame(verdict_rows)

    # Holdout base rates.
    n_h, k50_h, k100_h, n300_h, k300_h = con.execute(f"""
        SELECT count(*), count(*) FILTER (WHERE win_50), count(*) FILTER (WHERE win_100), count(launch_300),
               count(*) FILTER (WHERE launch_300)
        FROM d WHERE month_end BETWEEN DATE '{HOLDOUT_START}' AND DATE '{HOLDOUT_END_12M}' AND lag = 0""").fetchone()
    by_year = con.execute(f"""
        SELECT year(month_end), count(*), count(*) FILTER (WHERE win_50), count(*) FILTER (WHERE win_100),
               count(launch_300), count(*) FILTER (WHERE launch_300)
        FROM d WHERE month_end BETWEEN DATE '{HOLDOUT_START}' AND DATE '{HOLDOUT_END_12M}' AND lag = 0 GROUP BY 1 ORDER BY 1""").fetchall()
    buckets = con.execute(f"""
        SELECT 'drawdown' AS bt, drawdown_bucket AS b, count(*) AS n, count(*) FILTER (WHERE win_50) AS k50,
               count(*) FILTER (WHERE win_100) AS k100 FROM d
        WHERE month_end BETWEEN DATE '{HOLDOUT_START}' AND DATE '{HOLDOUT_END_12M}' AND lag = 0 GROUP BY 2
        UNION ALL
        SELECT 'mst', mst_bucket, count(*), count(*) FILTER (WHERE win_50), count(*) FILTER (WHERE win_100) FROM d
        WHERE month_end BETWEEN DATE '{HOLDOUT_START}' AND DATE '{HOLDOUT_END_12M}' AND lag = 0 GROUP BY 2""").fetchdf()
    order = {b: i for i, b in enumerate(BUCKET_TYPES["drawdown"] + BUCKET_TYPES["mst"])}
    buckets = buckets.sort_values(["bt", "b"], key=lambda s: s.map(order) if s.name == "b" else s).reset_index(drop=True)

    # Expected win_50 per ten picks: 10 x bucket base x composite decile-10 holdout lift (overall, lag 0).
    ew = []
    for cell_name in ("decile 10", "deciles 8-10"):
        cr = comp_h[(comp_h["lag"] == 0) & (comp_h["bucket_type"] == "all") & (comp_h["label"] == "win_50") & (comp_h["cell"] == cell_name)].iloc[0]
        row = {"cell": cell_name, "holdout_lift": cr["lift"], "events": int(cr["events"]), "sufficient": bool(cr["sufficient"])}
        for _, b in buckets.iterrows():
            row[f"{b['bt']} {b['b']}"] = 10 * (b["k50"] / b["n"]) * cr["lift"] if b["k50"] >= MIN_EVENTS_PER_CELL and cr["sufficient"] else None
        ew.append(row)
    ew = pd.DataFrame(ew)

    # Exploratory realized volatility: decile lifts (both windows) and Spearman on decile ranks, lag 0.
    corr = []
    for w, (s0, e0) in (("build", (BUILD_START, BUILD_END)), ("holdout", (HOLDOUT_START, HOLDOUT_END_12M))):
        for other in CORR_WITH:
            r = con.execute(f"""
                SELECT corr(dec_realized_vol_12m, dec_{other}), count(*) FROM d
                WHERE lag = 0 AND month_end BETWEEN DATE '{s0}' AND DATE '{e0}'
                  AND dec_realized_vol_12m IS NOT NULL AND dec_{other} IS NOT NULL""").fetchone()
            corr.append({"window": w, "feature": other, "spearman_on_deciles": r[0], "rows": r[1]})
    corr = pd.DataFrame(corr)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat([ex_b, ex_h]).to_csv(REPORTS_DIR / "s7_extreme_cells.csv", index=False)
    pd.concat([dt_b, dt_h]).to_csv(REPORTS_DIR / "s7_decile_cells.csv", index=False)
    pd.concat([comp_b, comp_h]).assign(members="|".join(members), unconfirmed=unconfirmed).to_csv(REPORTS_DIR / "s7_composite.csv", index=False)
    pd.concat([dt_b[dt_b["feature"] == "realized_vol_12m"], dt_h[dt_h["feature"] == "realized_vol_12m"]]).to_csv(REPORTS_DIR / "s7_realized_vol.csv", index=False)
    corr.to_csv(REPORTS_DIR / "s7_realized_vol_corr.csv", index=False)
    ew.to_csv(REPORTS_DIR / "s7_expected_winners.csv", index=False)

    # ---------------------------------------------------------------- report
    L = ["# Decile retest — holdout results (GROWTH-002, S7). End of chunk 4b.", "",
         f"Holdout {HOLDOUT_START[:7]} to {HOLDOUT_END_12M[:7]} (E4). {n_h:,} universe stock-months per lag, four lags. win_50 {k50_h:,}",
         f"({100 * k50_h / n_h:.2f}%), win_100 {k100_h:,} ({100 * k100_h / n_h:.2f}%). launch_300 is observable only through 2024-08",
         f"decision dates: {n300_h:,} rows carry it in the holdout, {k300_h:,} launches. Every number comes from",
         "src/decile_holdout.py over the same parquet files as S6; the build window is recomputed with the same code.",
         "", "Definitions as in reports/decile_build_results.md. Composite recipe (S7): mean of raw percentile ranks,",
         "LOW features as 1 - rank, over rows where every member is non-null, then deciles per (month_end, lag). Full",
         f"section 3 pass = build PASS-build and holdout lift >= {PASS_LIFT} with lower bound >= {PASS_CI_LOW} at the same lag.",
         "The realized-volatility block is exploratory and outside the pass criteria. No recommendations.", ""]
    reading = REPORTS_DIR / "decile_holdout_reading.md"
    if reading.exists():
        L += ["## Reading", "", reading.read_text().strip(), ""]

    L += ["## Base rates by year (holdout)", ""]
    rows = [[y, f"{int(n):,}", int(a), pct(a / n), int(b), pct(b / n), f"{int(n3):,}", "-" if n3 == 0 else int(c),
             "-" if n3 == 0 else (pct(c / n3) if c >= MIN_EVENTS_PER_CELL else "insufficient")] for y, n, a, b, n3, c in by_year]
    L += md_table(["year", "rows", "win_50", "rate_50", "win_100", "rate_100", "rows with launch_300", "launch_300", "rate_300"], rows)
    L += ["## Base rate inside each regime bucket (holdout)", ""]
    rows = [[b["bt"], b["b"], f"{int(b['n']):,}", int(b["k50"]), pct(b["k50"] / b["n"]) if b["k50"] >= MIN_EVENTS_PER_CELL else "insufficient",
             int(b["k100"]), pct(b["k100"] / b["n"]) if b["k100"] >= MIN_EVENTS_PER_CELL else "insufficient"] for _, b in buckets.iterrows()]
    L += md_table(["bucket type", "bucket", "rows", "win_50", "rate_50", "win_100", "rate_100"], rows, 2)
    L += ["Buckets absent from the holdout: drawdown >30, months-since-trough >24.", ""]

    for label in LABELS:
        L += [f"## Extreme-decile cells, {label}: build beside holdout", "",
              "Build and holdout cells = lift [CI] (events). rho = Spearman over D8 deciles in that window.", ""]
        rows = []
        for feature in FEATURES:
            for lag in LAGS:
                b = ex_b[(ex_b["feature"] == feature) & (ex_b["lag"] == lag) & (ex_b["bucket_type"] == "all") & (ex_b["label"] == label)].iloc[0]
                h = ex_h[(ex_h["feature"] == feature) & (ex_h["lag"] == lag) & (ex_h["bucket_type"] == "all") & (ex_h["label"] == label)].iloc[0]
                rows.append([feature, b["direction"], lag, cell_str(b), "n/a" if math.isnan(b["rho"]) else f"{b['rho']:.2f}",
                             "PASS-build" if b["pass_build"] else "", pct(h["coverage"], 1), pct(h["row_share"], 1), cell_str(h),
                             "n/a" if math.isnan(h["rho"]) else f"{h['rho']:.2f}", "pass" if h["pass_holdout"] else ""])
        L += md_table(["feature", "dir", "lag", "build", "rho", "build verdict", "hold. coverage", "hold. cell share", "holdout", "rho", "holdout"], rows, 3)

    L += ["## Verdicts (full section 3 criterion, build AND holdout)", ""]
    rows = [[r["feature"], r["direction"], r["label"], r["verdict"], r["build_pass_lags"], r["holdout_pass_lags"], r["confirmed_lags"],
             r["holdout_best"], "n/a" if pd.isna(r["holdout_calm_min_lift"]) else f"{r['holdout_calm_min_lift']:.2f}"] for _, r in vd.iterrows()]
    L += md_table(["feature", "dir", "label", "verdict", "build pass lags", "holdout pass lags", "confirmed lags", "holdout best cell",
                   "min holdout lift, calm buckets"], rows, 4)

    L += ["## Holdout decile lift curves, win_50, lag 0", ""]
    rows = []
    for feature in FEATURES:
        s = dt_h[(dt_h["feature"] == feature) & (dt_h["lag"] == 0) & (dt_h["bucket_type"] == "all") & (dt_h["label"] == "win_50")]
        cs = []
        for dnum in range(1, 11):
            r = s[s["decile"] == dnum]
            cs.append("-" if r.empty else (f"{r.iloc[0]['lift']:.2f} ({int(r.iloc[0]['events'])})" if r.iloc[0]["sufficient"] else f"insuff. ({int(r.iloc[0]['events'])})"))
        rows.append([feature, FEATURES[feature][1]] + cs)
    L += md_table(["feature", "dir"] + [f"D{i}" for i in range(1, 11)], rows, 2)

    L += ["## Holdout extreme-cell lift by SPY drawdown bucket, win_50", ""]
    bks = [b for b in BUCKET_TYPES["drawdown"] if (buckets[(buckets["bt"] == "drawdown") & (buckets["b"] == b)]["n"].sum() > 0)]
    rows = []
    for feature in FEATURES:
        for lag in LAGS:
            cs = []
            for b in bks:
                r = ex_h[(ex_h["feature"] == feature) & (ex_h["lag"] == lag) & (ex_h["bucket_type"] == "drawdown") & (ex_h["bucket"] == b) & (ex_h["label"] == "win_50")]
                cs.append("n/a" if r.empty else cell_str(r.iloc[0]))
            rows.append([feature, lag] + cs)
    L += md_table(["feature", "lag"] + bks, rows, 2)

    L += ["## Composite (section 4), build beside holdout", "",
          ("Members (PASS-build on win_50): " if not unconfirmed else "Fewer than 3 features PASS-build on win_50; composite = top 3 by extreme-decile lift, UNCONFIRMED: ")
          + ", ".join(members) + ".", "Recipe: mean of oriented raw percentile ranks; pool share = cell rows / all universe rows at that lag.", ""]
    rows = []
    for lag in LAGS:
        for label in LABELS:
            for cell_name in ("decile 10", "deciles 8-10"):
                b = comp_b[(comp_b["lag"] == lag) & (comp_b["bucket_type"] == "all") & (comp_b["label"] == label) & (comp_b["cell"] == cell_name)].iloc[0]
                h = comp_h[(comp_h["lag"] == lag) & (comp_h["bucket_type"] == "all") & (comp_h["label"] == label) & (comp_h["cell"] == cell_name)].iloc[0]
                rows.append([lag, label, cell_name, pct(b["pool_share_of_all"], 1), cell_str(b), pct(h["coverage"], 1), pct(h["pool_share_of_all"], 1),
                             f"{int(h['rows']):,}", cell_str(h), "pass" if holdout_pass(h) else ""])
        L += []
    L += md_table(["lag", "label", "cell", "build pool", "build", "hold. coverage", "hold. pool", "hold. rows", "holdout", "holdout ≥1.5/1.2"], rows, 3)
    for bt, label_name in (("drawdown", "SPY drawdown bucket"), ("mst", "months-since-trough bucket")):
        bks2 = [b for b in BUCKET_TYPES[bt] if (buckets[(buckets["bt"] == bt) & (buckets["b"] == b)]["n"].sum() > 0)]
        L += [f"### Holdout composite by {label_name}, lag 0", ""]
        rows = []
        for label in LABELS:
            for cell_name in ("decile 10", "deciles 8-10"):
                cs = []
                for b in bks2:
                    r = comp_h[(comp_h["lag"] == 0) & (comp_h["bucket_type"] == bt) & (comp_h["bucket"] == b) & (comp_h["label"] == label) & (comp_h["cell"] == cell_name)]
                    cs.append("n/a" if r.empty else cell_str(r.iloc[0]))
                rows.append([label, cell_name] + cs)
        L += md_table(["label", "cell"] + bks2, rows, 2)

    L += ["## Expected win_50 per ten picks, by regime bucket (holdout)", "",
          "Cell = 10 x holdout bucket base rate (win_50) x the composite cell's overall holdout lift at lag 0.",
          "Buckets with fewer than 100 wins, or a composite cell under D8, read insufficient.", ""]
    bcols = [c for c in ew.columns if c not in ("cell", "holdout_lift", "events", "sufficient")]
    rows = [[r["cell"], f2(r["holdout_lift"], bool(r["sufficient"])), int(r["events"])] +
            [f2(r[c]) if r[c] is not None and not pd.isna(r[c]) else "insufficient" for c in bcols] for _, r in ew.iterrows()]
    L += md_table(["composite cell", "holdout lift", "events"] + bcols, rows, 1)

    L += ["## Exploratory: 12-month realized volatility deciles (outside the pass criteria)", "",
          "Annualized standard deviation of daily log returns over the 252 trading days ending on the decision trade",
          "date, ranked like every other feature. No direction was declared and no verdict is given. Cell = lift (events).", ""]
    for label in LABELS:
        rows = []
        for w, dtw in (("build", dt_b), ("holdout", dt_h)):
            for lag in LAGS:
                s = dtw[(dtw["feature"] == "realized_vol_12m") & (dtw["lag"] == lag) & (dtw["bucket_type"] == "all") & (dtw["label"] == label)]
                cs = []
                for dnum in range(1, 11):
                    r = s[s["decile"] == dnum]
                    cs.append("-" if r.empty else (f"{r.iloc[0]['lift']:.2f} ({int(r.iloc[0]['events'])})" if r.iloc[0]["sufficient"] else f"insuff. ({int(r.iloc[0]['events'])})"))
                cov = s["coverage"].iloc[0] if len(s) else float("nan")
                rows.append([w, lag, pct(cov, 1)] + cs)
        L += [f"### realized_vol_12m decile lifts, {label}", ""]
        L += md_table(["window", "lag", "coverage"] + [f"D{i}" for i in range(1, 11)], rows, 3)
    L += ["### Spearman correlation of the realized-volatility decile with other feature deciles, lag 0", "",
          "Computed as the correlation of the two decile ranks over rows where both are non-null.", ""]
    rows = [[r["window"], r["feature"], f"{r['spearman_on_deciles']:.3f}", f"{int(r['rows']):,}"] for _, r in corr.iterrows()]
    L += md_table(["window", "feature decile", "Spearman", "rows"], rows, 2)

    out = REPORTS_DIR / "decile_holdout_results.md"
    out.write_text("\n".join(L))
    print(f"holdout: {n_h:,} rows per lag; win_50 {100 * k50_h / n_h:.2f}%, win_100 {100 * k100_h / n_h:.2f}%; launch_300 observable rows {n300_h:,}")
    print(vd[["feature", "label", "verdict", "build_pass_lags", "holdout_pass_lags", "confirmed_lags", "holdout_best"]].to_string(index=False))
    print(f"composite members ({'UNCONFIRMED top-3' if unconfirmed else 'PASS-build set'}): {members}")
    print(comp_h[(comp_h["bucket_type"] == "all") & (comp_h["lag"] == 0)][["label", "cell", "pool_share_of_all", "events", "lift", "ci_low", "ci_high"]].round(3).to_string(index=False))
    print(corr.round(3).to_string(index=False))
    print(f"-> {out}")
    print("RESULT: PASS — holdout decile report written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
