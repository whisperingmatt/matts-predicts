"""S5 — Holdout per spec section 8 on 2020-01 to 2024-06 (Matt's S5 brief).

Input:  the same parquet files as src/stats.py
Output: reports/holdout_results.md (tables + reports/holdout_reading.md
        inserted verbatim when present); reports/s5_single_signal.csv,
        s5_combinations.csv, s5_base_rates.csv, s5_sector.csv

    python -m src.holdout

Section 8 reruns 7.1 to 7.5 on the holdout for the passing signals and the
top combinations. Matt's brief (decisions.md 2026-09-17 "S5 holdout
rulings") fixes the list: the three build-window PASS flags (sponsorship
carried with its calm-only caveat), the two-horizon strength combination
at every lag, the fifth D8-clearing build combination (PEG < 0.5 AND
PE < 15 at lag 3, section 8's "top-20"), and the four backward build-window
signals as inverted flags. launch_200 is reported beside launch_300
throughout. The sector table is pooled across years. Regime buckets as in
S4. CONFIRM = holdout lift >= 1.5 with lower CI >= 1.0 (section 8), on
cells that meet D8.

The window ends 2024-06 because a 24-month return is not observable after
2024-08 decision dates with prices to 2026-09-16; D4's 2026-06 end cannot
be labeled yet (decisions.md).

Build-window numbers for the same flags are recomputed here with the same
code for side-by-side comparison; the inverted flags had no build-window
row in S4. Nothing here recommends anything.
"""
from __future__ import annotations

import math
import sys

import pandas as pd

from src.config import BUILD_END, BUILD_START, LAGS, MIN_EVENTS_PER_CELL, REPORTS_DIR
from src.stats import (BUCKET_TYPES, INVERTED, base_rates, evaluate_combos, f2, load, md_table, pct,
                       sector_year, single_signal)
import duckdb

H_START, H_END = "2020-01-31", "2024-06-30"
CONFIRM_LIFT, CONFIRM_CI_LOW = 1.5, 1.0
TESTED = {
    "h9_rs6_top_decile": "PASS in build (lags 3, 6, 12)",
    "h9_rs12_top_decile": "PASS in build (lags 3, 6, 12)",
    "h10_sponsorship": "PASS in build, calm-only: 2014-2019 data, no bear-market cell",
    "inv_h15_near_high": "inverted: NOT near 52-week high (build lift 0.40-0.55)",
    "inv_h21_no_dilution": "inverted: shares up more than 2% over 8 quarters (build lift 0.55-0.61)",
    "inv_h8_fcf_divergence": "inverted: NOT fcf_divergence (build lift 0.51-0.61)",
    "inv_ctl_divyield_gt_2": "inverted: dividend yield <= 2% or none (build lift 0.34-0.47)",
}
COMBOS = [(lag, ("h9_rs6_top_decile", "h9_rs12_top_decile")) for lag in LAGS] + \
         [(3, ("h5_peg_lt_05", "ctl_pe_lt_15"))]
THR = ["launch_300", "launch_200"]


def confirm(row) -> bool:
    return bool(row["sufficient"]) and row["lift"] >= CONFIRM_LIFT and row["ci_low"] >= CONFIRM_CI_LOW


def cell(r) -> str:
    if r is None:
        return "n/a"
    return (f"{r['lift']:.2f} [{r['ci_low']:.2f}, {r['ci_high']:.2f}] ({int(r['events'])})"
            if r["sufficient"] else f"insufficient ({int(r['events'])})")


def main() -> int:
    # Build window, same code, for comparison columns.
    cb_con = duckdb.connect()
    load(cb_con, BUILD_START, BUILD_END)
    ss_b = single_signal(cb_con, list(TESTED))
    ss_b["window"] = "build"
    cb_b = evaluate_combos(cb_con, COMBOS)
    cb_b["window"] = "build"

    # Holdout.
    con = duckdb.connect()
    load(con, H_START, H_END)
    n_lag0, k300, k200 = con.execute(
        "SELECT count(*), count(*) FILTER (WHERE launch_300), count(*) FILTER (WHERE launch_200) FROM d WHERE lag = 0").fetchone()
    yearly, buckets = base_rates(con)
    ss_h = single_signal(con, list(TESTED))
    ss_h["window"] = "holdout"
    ss_h["confirm"] = ss_h.apply(confirm, axis=1)
    cb_h = evaluate_combos(con, COMBOS)
    cb_h["window"] = "holdout"
    cb_h["confirm"] = cb_h.apply(confirm, axis=1)
    sy = sector_year(con)
    sec = sy.groupby("sector", as_index=False)[["rows_", "k300"]].sum()
    sec200 = con.execute("SELECT sector, count(*) FILTER (WHERE launch_200) AS k200 FROM d WHERE lag = 0 GROUP BY 1").fetchdf()
    sec = sec.merge(sec200, on="sector").sort_values("sector")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat([ss_b, ss_h]).to_csv(REPORTS_DIR / "s5_single_signal.csv", index=False)
    pd.concat([cb_b.drop(columns=["flags"]), cb_h.drop(columns=["flags"])]).to_csv(REPORTS_DIR / "s5_combinations.csv", index=False)
    pd.concat([yearly.assign(bucket_type="year", bucket=yearly["year"]).drop(columns=["year"]), buckets]).to_csv(
        REPORTS_DIR / "s5_base_rates.csv", index=False)
    sec.to_csv(REPORTS_DIR / "s5_sector.csv", index=False)

    # ---------------------------------------------------------------- report
    L = ["# Holdout results — Section 2 Growth, spec section 8", "",
         f"Window {H_START[:7]} to {H_END[:7]}. {n_lag0:,} universe stock-months per lag, four lags. {k300:,} launch_300",
         f"({100 * k300 / n_lag0:.2f}%) and {k200:,} launch_200 ({100 * k200 / n_lag0:.2f}%). Every number comes from src/holdout.py",
         "over the same parquet files as S4. D4 names 2026-06 as the holdout end; 24-month returns are not",
         "observable after 2024-08 decision dates with prices to 2026-09-16, so the window ends 2024-06.",
         "",
         "Tested (Matt's S5 brief and section 8): the three build-window PASS flags, the two-horizon strength",
         "combination at every lag, the fifth D8-clearing build combination, and the four backward build",
         "signals inverted. Definitions as in S4: lift among non-null rows, coverage beside it, Wilson CI on",
         f"the flagged rate over a fixed base, D8 at {MIN_EVENTS_PER_CELL} launch events. CONFIRM = lift >= {CONFIRM_LIFT} with",
         f"lower CI >= {CONFIRM_CI_LOW} on a D8-sufficient cell. Build-window columns are recomputed here with the same",
         "code. No recommendations.", ""]
    reading = REPORTS_DIR / "holdout_reading.md"
    if reading.exists():
        L += ["## Reading", "", reading.read_text().strip(), ""]

    L += ["## 7.1 Base rates by year (holdout)", ""]
    rows = []
    for _, r in yearly.iterrows():
        rows.append([r["year"], f"{int(r['rows_']):,}", int(r["k300"]),
                     pct(r["k300"] / r["rows_"]) if r["k300"] >= MIN_EVENTS_PER_CELL else "insufficient",
                     int(r["k200"]), pct(r["k200"] / r["rows_"]) if r["k200"] >= MIN_EVENTS_PER_CELL else "insufficient"])
    L += md_table(["year", "rows", "launch_300", "rate_300", "launch_200", "rate_200"], rows)

    L += ["## Base rate inside each regime bucket (holdout)", ""]
    rows = []
    for _, r in buckets.iterrows():
        rows.append([r["bucket_type"], r["bucket"], f"{int(r['rows_']):,}", int(r["k300"]),
                     pct(r["k300"] / r["rows_"]) if r["k300"] >= MIN_EVENTS_PER_CELL else "insufficient",
                     int(r["k200"]), pct(r["k200"] / r["rows_"]) if r["k200"] >= MIN_EVENTS_PER_CELL else "insufficient"])
    L += md_table(["bucket type", "bucket", "rows", "launch_300", "rate_300", "launch_200", "rate_200"], rows, 2)
    L += ["Buckets absent from the holdout: drawdown >30, months-since-trough >24.", ""]

    L += ["## Launch rate by sector, pooled across the holdout", ""]
    rows = []
    for _, r in sec.iterrows():
        rows.append([r["sector"], f"{int(r['rows_']):,}", int(r["k300"]),
                     pct(r["k300"] / r["rows_"]) if r["k300"] >= MIN_EVENTS_PER_CELL else "insufficient",
                     int(r["k200"]), pct(r["k200"] / r["rows_"]) if r["k200"] >= MIN_EVENTS_PER_CELL else "insufficient"])
    L += md_table(["sector", "rows", "launch_300", "rate_300", "launch_200", "rate_200"], rows)

    for thr in THR:
        L += [f"## 7.2 Single-signal lift, {thr}: build window beside holdout", "",
              "Build cell = lift [CI] (events) recomputed on 2006-01 to 2019-12. Holdout columns follow.", ""]
        rows = []
        for flag, note in TESTED.items():
            for lag in LAGS:
                b = ss_b[(ss_b["flag"] == flag) & (ss_b["lag"] == lag) & (ss_b["threshold"] == thr) & (ss_b["bucket_type"] == "all")].iloc[0]
                h = ss_h[(ss_h["flag"] == flag) & (ss_h["lag"] == lag) & (ss_h["threshold"] == thr) & (ss_h["bucket_type"] == "all")].iloc[0]
                ok = bool(h["sufficient"])
                rows.append([flag, lag, cell(b), pct(h["coverage"], 1), pct(h["true_share"], 1), f"{int(h['n_true']):,}",
                             int(h["events"]), pct(h["rate"]) if ok else "insufficient", f2(h["lift"], ok), f2(h["ci_low"], ok),
                             f2(h["ci_high"], ok), "CONFIRM" if confirm(h) else ("insufficient" if not ok else "not confirmed")])
        L += md_table(["flag", "lag", "build", "coverage", "true share", "rows_true", "events", "rate", "lift", "CI low", "CI high", "holdout"], rows)

    L += ["### Verdicts (section 8 CONFIRM rule)", ""]
    rows = []
    for flag, note in TESTED.items():
        h3 = ss_h[(ss_h["flag"] == flag) & (ss_h["threshold"] == "launch_300") & (ss_h["bucket_type"] == "all")]
        h2 = ss_h[(ss_h["flag"] == flag) & (ss_h["threshold"] == "launch_200") & (ss_h["bucket_type"] == "all")]
        c3 = ",".join(str(int(x)) for x in h3[h3["confirm"]]["lag"]) or "-"
        c2 = ",".join(str(int(x)) for x in h2[h2["confirm"]]["lag"]) or "-"
        best = h3.loc[h3["lift"].where(h3["sufficient"]).idxmax()] if h3["sufficient"].any() else None
        rows.append([flag, note, "CONFIRMS" if c3 != "-" else ("insufficient" if best is None else "NOT CONFIRMED"), c3, c2,
                     "-" if best is None else f"{best['lift']:.2f} [{best['ci_low']:.2f}, {best['ci_high']:.2f}] at lag {int(best['lag'])}"])
    L += md_table(["flag", "why tested", "launch_300", "confirming lags 300", "confirming lags 200", "best holdout cell (300)"], rows, 3)

    for bt, label in (("drawdown", "SPY drawdown bucket"), ("mst", "months-since-trough bucket")):
        bks = [b for b in BUCKET_TYPES[bt] if (buckets[(buckets["bucket_type"] == bt) & (buckets["bucket"] == b)]["rows_"].sum() > 0)]
        for thr in THR:
            L += [f"## 7.3 Holdout lift within each {label}, {thr}", ""]
            sub = ss_h[(ss_h["threshold"] == thr) & (ss_h["bucket_type"] == bt)]
            rows = []
            for flag in TESTED:
                for lag in LAGS:
                    cells = []
                    for b in bks:
                        r = sub[(sub["flag"] == flag) & (sub["lag"] == lag) & (sub["bucket"] == b)]
                        cells.append(cell(None if r.empty else r.iloc[0]) + (" CONFIRM" if (not r.empty and confirm(r.iloc[0])) else ""))
                    rows.append([flag, lag] + cells)
            L += md_table(["flag", "lag"] + bks, rows, 2)

    L += ["## 7.4 Combinations: build window beside holdout", "",
          "The two-horizon strength pair at every lag, and PEG < 0.5 AND PE < 15 at lag 3 (the fifth build",
          "combination that met D8). catch = launches caught / all holdout launches at that lag.", ""]
    rows = []
    for (lag, flags) in COMBOS:
        name = " AND ".join(flags)
        b = cb_b[(cb_b["lag"] == lag) & (cb_b["combo"] == name)].iloc[0]
        h = cb_h[(cb_h["lag"] == lag) & (cb_h["combo"] == name)].iloc[0]
        ok, ok2 = bool(h["sufficient"]), bool(h["sufficient_200"])
        rows.append([name, lag, cell(b), f"{int(h['n_true']):,}", int(h["events"]), pct(h["rate"]) if ok else "insufficient",
                     f2(h["lift"], ok), f2(h["ci_low"], ok), f2(h["ci_high"], ok), pct(h["catch"], 1),
                     "CONFIRM" if confirm(h) else ("insufficient" if not ok else "not confirmed"),
                     int(h["events_200"]), f2(h["lift_200"], ok2), f2(h["ci_low_200"], ok2),
                     "CONFIRM" if (ok2 and h["lift_200"] >= CONFIRM_LIFT and h["ci_low_200"] >= CONFIRM_CI_LOW) else ("insufficient" if not ok2 else "not confirmed")])
    L += md_table(["combination", "lag", "build (300)", "rows_true", "events_300", "rate_300", "lift_300", "CI low", "CI high", "catch_300",
                   "holdout 300", "events_200", "lift_200", "CI low 200", "holdout 200"], rows)

    out = REPORTS_DIR / "holdout_results.md"
    out.write_text("\n".join(L))
    print(f"holdout: {n_lag0:,} rows per lag, {k300:,} launch_300, {k200:,} launch_200")
    v = ss_h[(ss_h["threshold"] == "launch_300") & (ss_h["bucket_type"] == "all")]
    print(v.pivot(index="flag", columns="lag", values="lift").round(2).to_string())
    print("confirming (300):", sorted(set(v[v["confirm"]]["flag"])))
    print(cb_h[["lag", "combo", "events", "lift", "ci_low", "confirm", "events_200", "lift_200", "ci_low_200"]].round(2).to_string(index=False))
    print(f"-> {out}")
    print("RESULT: PASS — holdout report written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
