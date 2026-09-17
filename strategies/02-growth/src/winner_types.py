"""S9 — GROWTH-003 section 4: clustering winners into types. Ends chunk 4c.

Input:  data/processed/anatomy_fields.parquet (S8), deciles.parquet (lag 0
        percentile ranks), universe, labels, labels12, regime
Output: reports/winner_types.md (+ reports/winner_types_reading.md inserted
        verbatim when present)
        reports/s9_*.csv — every table unrounded, plus the per-winner
        cluster assignment (s9_winner_clusters.csv)

    python -m src.winner_types

Method (spec section 4, with Matt's S9 rulings in decisions.md "Chunk 4c"):
winners only, one row per winner at T-0; inputs are the section-2 numeric
fields at T-0 (never T-6 or T-12) plus the 23 GROWTH-002 percentile ranks
at lag 0. The 5.02 officer/director proxy (ev52_t12) is dropped, and
ev_total_t12 with it because it contains 5.02. scalemarketcap is not an
input (marketcap_musd is the point-in-time size). Dollar-scaled fields
(market cap, dollar volume, price) enter as log1p. A field whose winner
coverage is under 50% is left out for that label and listed. Remaining
nulls are filled with the winners' median for that field, then every
column is standardized to the winners' mean and standard deviation. The
same transform (same medians, same scaler) maps every population row for
the nearest-centroid assignment.

k-means for k in 2..6, n_init 10, seed 0, silhouette (full for launch_300;
a fixed 10,000-row sample, seed 0, for win_100), k chosen by silhouette,
every k reported. HDBSCAN (scikit-learn) with min_cluster_size = 1% of the
winners (at least 25) as a check: cluster count, noise share, adjusted Rand
index against the chosen k-means labels, and the overlap table. No cluster
is dropped or merged. Single-threaded BLAS and duckdb so outputs are
reproducible.

The T+k half of every timeline and every _f12 column are forward-looking.
"""
from __future__ import annotations

import sys

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from threadpoolctl import threadpool_limits

from src.anatomy import (BUCKET_ORDER, CODES, DECILE_FEATURES, LABELS, NUMERIC, STEPS, TL_MEASURES,
                         build_populations, cov, fmt, pq)
from src.config import REPORTS_DIR
from src.stats import md_table

SEED = 0
KS = list(range(2, 7))
N_INIT = 10
SILHOUETTE_SAMPLE = 10_000
MIN_COVERAGE = 0.50
EXCLUDED = {"ev52_t12": "5.02 officer/director proxy dropped (Matt's S9 brief)",
            "ev_total_t12": "contains the 5.02 count"}
LOG_FIELDS = ["avg_dollar_volume_20d", "price", "marketcap_musd"]
NUMERIC_INPUTS = [c for c in NUMERIC if c not in EXCLUDED]
RANK_INPUTS = [f"pr_{f}" for f in DECILE_FEATURES]
FINGERPRINT_MEAN = [*(f"ev{c}_t12" for c in CODES if c != "52"), "insider_net_buys_12m", "officer_buys_12m",
                    *(f"ev{c}_f12" for c in CODES), "ev_total_f12"]
FINGERPRINT_MEDIAN = ["shares_chg_4q", "shares_chg_8q", "shares_change_f12"]
CATEGORICAL_MIX = ["sector", "drawdown_bucket", "mst_bucket", "price_bucket", "profitable", "ipo_lt_3y"]


# ------------------------------------------------------------------ data

def load(con) -> None:
    con.execute(f"CREATE VIEW fields AS SELECT * FROM {pq('anatomy_fields.parquet')}")
    build_populations(con)
    ranks = ", ".join(f"d.{r}" for r in RANK_INPUTS)
    for label in LABELS:
        con.execute(f"""
            CREATE TABLE rows_{label} AS
            SELECT p.ticker, p.month_end, p.winner, f.* EXCLUDE (ticker, month_end, sector), coalesce(f.sector, 'Unknown') AS sector,
                   CASE WHEN f.sharesbas > 0 THEN f12.sharesbas / f.sharesbas - 1 END AS shares_change_f12, {ranks}
            FROM pop_{label} p
            LEFT JOIN fields f ON f.ticker = p.ticker AND f.month_end = p.month_end
            LEFT JOIN fields f12 ON f12.ticker = p.ticker AND f12.month_end = last_day(p.month_end + INTERVAL 12 MONTH)
            LEFT JOIN {pq('deciles.parquet')} d ON d.ticker = p.ticker AND d.month_end = p.month_end AND d.lag = 0
            ORDER BY p.month_end, p.ticker
        """)


def design(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], pd.DataFrame]:
    """Standardized matrix for winners and population; the transform is fitted on winners only."""
    w = rows[rows["winner"]]
    inputs = NUMERIC_INPUTS + RANK_INPUTS
    covs = w[inputs].notna().mean()
    kept = [c for c in inputs if covs[c] >= MIN_COVERAGE]
    X = rows[kept].astype(float).copy()
    for c in LOG_FIELDS:
        if c in kept:
            X[c] = np.log1p(X[c].clip(lower=0))
    med = X[rows["winner"]].median()
    X = X.fillna(med)
    mu, sd = X[rows["winner"]].mean(), X[rows["winner"]].std(ddof=0)
    kept = [c for c in kept if sd[c] > 0]
    Z = (X[kept] - mu[kept]) / sd[kept]
    spec = pd.DataFrame({"field": inputs, "winner_coverage": [covs[c] for c in inputs],
                         "used": [c in kept for c in inputs],
                         "imputed_share": [1 - covs[c] if c in kept else float("nan") for c in inputs],
                         "log1p": [c in LOG_FIELDS for c in inputs]})
    return Z[rows["winner"].values], Z[~rows["winner"].values], kept, spec


# ------------------------------------------------------------------ clustering

def kmeans_sweep(Zw: pd.DataFrame) -> tuple[pd.DataFrame, dict[int, KMeans]]:
    out, models = [], {}
    n = len(Zw)
    for k in KS:
        km = KMeans(n_clusters=k, n_init=N_INIT, random_state=SEED).fit(Zw.values)
        sil = silhouette_score(Zw.values, km.labels_, sample_size=min(n, SILHOUETTE_SAMPLE), random_state=SEED)
        sizes = np.bincount(km.labels_, minlength=k)
        out.append({"k": k, "silhouette": sil, "inertia": km.inertia_, "smallest_cluster": int(sizes.min()),
                    "largest_cluster": int(sizes.max()), "sizes": "/".join(str(s) for s in sizes)})
        models[k] = km
    return pd.DataFrame(out), models


def relabel(km: KMeans, Zw: pd.DataFrame) -> np.ndarray:
    """Cluster ids in descending size order (1 = largest) so the report order is deterministic."""
    sizes = np.bincount(km.labels_, minlength=km.n_clusters)
    order = np.argsort(-sizes, kind="stable")
    mapping = {int(old): i + 1 for i, old in enumerate(order)}
    return np.array([mapping[int(l)] for l in km.labels_]), mapping


HDBSCAN_MIN_SAMPLES = [None, 25, 10, 5]  # None = scikit-learn default (= min_cluster_size); the rest are the sensitivity check


def hdbscan_check(Zw: pd.DataFrame, km_labels: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    """HDBSCAN at min_cluster_size = 1% of winners (at least 25), at the default min_samples and three looser
    settings. The crosstab returned is for the first setting that finds any cluster (the default when it does)."""
    n = len(Zw)
    mcs = max(25, round(0.01 * n))
    out, ct = [], None
    for ms in HDBSCAN_MIN_SAMPLES:
        lab = HDBSCAN(min_cluster_size=mcs, min_samples=ms, copy=True).fit(Zw.values).labels_
        noise = float((lab == -1).mean())
        n_clusters = int(len(set(lab)) - (1 if -1 in lab else 0))
        ari = adjusted_rand_score(km_labels, lab)
        ari_nonnoise = adjusted_rand_score(km_labels[lab != -1], lab[lab != -1]) if (lab != -1).sum() else float("nan")
        out.append({"min_cluster_size": mcs, "min_samples": mcs if ms is None else ms, "clusters": n_clusters,
                    "noise_share": noise, "ari_all": ari, "ari_excluding_noise": ari_nonnoise,
                    "sizes": "/".join(str(int((lab == c).sum())) for c in sorted(set(lab)) if c != -1)})
        if ct is None and n_clusters > 0:
            ct = pd.crosstab(pd.Series(km_labels, name="kmeans"), pd.Series(lab, name="hdbscan"))
    if ct is None:
        ct = pd.crosstab(pd.Series(km_labels, name="kmeans"), pd.Series(np.full(n, -1), name="hdbscan"))
    return pd.DataFrame(out), ct


# ------------------------------------------------------------------ description

def cluster_summary(rows, Zw, Zp, km, mapping, kept) -> tuple[pd.DataFrame, pd.DataFrame]:
    w = rows[rows["winner"]].copy()
    p = rows[~rows["winner"]].copy()
    w["cluster"] = relabel(km, Zw)[0]
    p["cluster"] = np.array([mapping[int(l)] for l in km.predict(Zp.values)])
    nw, npop = len(w), len(rows)
    out, dist = [], []
    zmeans = pd.DataFrame(Zw.values, columns=kept).groupby(w["cluster"].values).mean()
    for c in sorted(w["cluster"].unique()):
        cw = int((w["cluster"] == c).sum())
        cp = int((p["cluster"] == c).sum()) + cw  # population includes winners (F3)
        wshare, pshare = cw / nw, cp / npop
        top = zmeans.loc[c].abs().sort_values(ascending=False).head(3)
        out.append({"cluster": c, "winners": cw, "winner_share": wshare, "population_rows": cp,
                    "population_share": pshare, "lift": wshare / pshare, "winner_rate": cw / cp,
                    "top_fields": "; ".join(f"{f} ({zmeans.loc[c, f]:+.2f} sd)" for f in top.index)})
        for f in kept:
            dist.append({"cluster": c, "field": f, "mean_z": zmeans.loc[c, f]})
    return pd.DataFrame(out), pd.DataFrame(dist), w, p


def cluster_medians(w: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    fields = NUMERIC_INPUTS + ["ev52_t12", "ev_total_t12"] + RANK_INPUTS
    out = []
    for f in fields:
        rec = {"field": f, "all_winners": w[f].median(), "population": rows[f].median()}
        for c in sorted(w["cluster"].unique()):
            rec[f"c{c}"] = w.loc[w["cluster"] == c, f].median()
        out.append(rec)
    return pd.DataFrame(out)


def fingerprint(w: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for f in FINGERPRINT_MEAN + FINGERPRINT_MEDIAN:
        stat = "mean" if f in FINGERPRINT_MEAN else "median"
        agg = (lambda s: s.mean()) if stat == "mean" else (lambda s: s.median())
        rec = {"field": f, "stat": stat, "all_winners": agg(w[f]), "population": agg(rows[f])}
        for c in sorted(w["cluster"].unique()):
            rec[f"c{c}"] = agg(w.loc[w["cluster"] == c, f])
        out.append(rec)
    return pd.DataFrame(out)


def mixes(w: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    out = []
    for cat in CATEGORICAL_MIX:
        vals = sorted(rows[cat].dropna().astype(str).unique())
        for v in vals:
            rec = {"category": cat, "bucket": v,
                   "all_winners": (w[cat].astype(str) == v).mean(),
                   "population": (rows[cat].astype(str) == v).mean()}
            for c in sorted(w["cluster"].unique()):
                sub = w[w["cluster"] == c]
                rec[f"c{c}"] = (sub[cat].astype(str) == v).mean()
            out.append(rec)
    return pd.DataFrame(out)


def cluster_timeline(con, label: str, w: pd.DataFrame) -> pd.DataFrame:
    con.execute("CREATE OR REPLACE TABLE steps AS SELECT unnest([" + ", ".join(str(k) for k in STEPS) + "])::INTEGER AS k")
    con.register("assign_df", w[["ticker", "month_end", "cluster"]])
    con.execute("CREATE OR REPLACE TABLE assign AS SELECT * FROM assign_df")
    con.execute(f"""
        CREATE OR REPLACE TABLE tl AS
        SELECT p.ticker, p.month_end, p.winner, a.cluster, s.k,
               f.closeadj / f0.closeadj - 1 AS price_return, f.rev_growth_yoy,
               CASE WHEN f0.sharesbas > 0 THEN f.sharesbas / f0.sharesbas - 1 END AS shares_change,
               f.insider_net_buys_12m, f.ev_total_t12
        FROM pop_{label} p CROSS JOIN steps s
        JOIN fields f0 ON f0.ticker = p.ticker AND f0.month_end = p.month_end
        LEFT JOIN fields f ON f.ticker = p.ticker AND f.month_end = last_day(p.month_end + to_months(s.k))
        LEFT JOIN assign a ON a.ticker = p.ticker AND a.month_end = p.month_end
    """)
    out = []
    for m in TL_MEASURES:
        df = con.execute(f"""
            WITH pm AS (SELECT month_end, k, median({m}) AS pmed FROM tl GROUP BY 1, 2)
            SELECT t.cluster, t.k, median(t.{m}) AS winner_median, count(t.{m}) AS winner_n, count(*) AS winners,
                   median(pm.pmed) AS population_median
            FROM tl t JOIN pm USING (month_end, k) WHERE t.winner GROUP BY 1, 2 ORDER BY 1, 2
        """).fetchdf()
        df.insert(0, "measure", m)
        out.append(df)
    t = pd.concat(out, ignore_index=True)
    t.insert(0, "label", label)
    return t


# ------------------------------------------------------------------ report

def kind_of(f: str) -> str:
    if f.startswith("pr_"):
        return "x"
    return NUMERIC.get(f, ("x", ""))[0]


def write_report(res: dict) -> None:
    L = ["# Winner types — Section 2 Growth, GROWTH-003 session 9 (end of chunk 4c)", "",
         "Descriptive clustering of the winners described in reports/anatomy_tables.md. Inputs are the section-2",
         "numeric fields at T-0 plus the 23 GROWTH-002 percentile ranks at lag 0, winners only, standardized on the",
         "winners (decisions.md \"Chunk 4c\", S9 rulings: T-0 only; the 5.02 proxy dropped, and ev_total_t12 with it;",
         "scalemarketcap excluded in favor of the point-in-time market cap; dollar fields as log1p; fields under 50%",
         "winner coverage left out per label; nulls filled with the winners' median). k-means for k 2 to 6 with",
         "silhouette, k chosen by silhouette; HDBSCAN as a check. No cluster was dropped or merged. Population",
         "frequency assigns every population row (winners included, F3) to its nearest k-means centroid in the same",
         "standardized space; lift = the cluster's share of winners / its share of population rows. Every number",
         "comes from src/winner_types.py; unrounded tables in reports/s9_*.csv, the per-winner assignment in",
         "reports/s9_winner_clusters.csv. Seeds fixed (0); single-threaded so the outputs reproduce.", "",
         "Everything measured after T-0 (the T+k half of a timeline, every _f12 column) is FORWARD-LOOKING and",
         "describes the move; it was not a clustering input and cannot enter a later scoring model.", ""]
    for label, r in res.items():
        L += [f"## {label}", "",
              f"{r['n_winners']:,} winners in {r['n_pop']:,} population rows; {len(r['kept'])} inputs used "
              f"({r['spec']['used'].sum()} of {len(r['spec'])} candidates)."]
        left = r["spec"][~r["spec"]["used"]]
        if len(left):
            L.append("Left out for coverage under 50%: " + ", ".join(f"{f} ({100 * c:.0f}%)" for f, c in zip(left["field"], left["winner_coverage"])) + ".")
        imp = r["spec"][r["spec"]["used"] & (r["spec"]["imputed_share"] > 0.05)]
        if len(imp):
            L.append("Inputs with more than 5% of winners imputed: " + ", ".join(f"{f} ({100 * s:.0f}%)" for f, s in zip(imp["field"], imp["imputed_share"])) + ".")
        L.append("")
        L += ["### k-means sweep", ""]
        L += md_table(["k", "silhouette", "inertia", "cluster sizes (largest first)"],
                      [[int(x["k"]), f"{x['silhouette']:.4f}", f"{x['inertia']:,.0f}",
                        "/".join(str(s) for s in sorted((int(v) for v in x["sizes"].split("/")), reverse=True))]
                       for _, x in r["sweep"].iterrows()])
        L += [f"Chosen k = {r['k']} (highest silhouette). Clusters are numbered by size, 1 = largest.", ""]
        h = r["hdbscan"]
        L += ["### HDBSCAN check", "",
              f"min_cluster_size {int(h['min_cluster_size'].iloc[0])} (1% of winners). The first row is scikit-learn's default",
              "min_samples; the others are the sensitivity check. ARI = adjusted Rand index against the chosen k-means labels.", ""]
        L += md_table(["min_samples", "clusters", "sizes", "noise share", "ARI all", "ARI excluding noise"],
                      [[int(x["min_samples"]), int(x["clusters"]), x["sizes"] or "none", f"{100 * x['noise_share']:.1f}%",
                        f"{x['ari_all']:.3f}", "n/a" if pd.isna(x["ari_excluding_noise"]) else f"{x['ari_excluding_noise']:.3f}"]
                       for _, x in h.iterrows()])
        L += ["Overlap with the k-means clusters (first setting that found any cluster, else all noise):", ""]
        ct = r["crosstab"]
        L += md_table(["k-means \\ HDBSCAN"] + [("noise" if c == -1 else f"h{c}") for c in ct.columns],
                      [[f"c{i}"] + [f"{int(v):,}" for v in ct.loc[i]] for i in ct.index])
        L += ["### Clusters", ""]
        L += md_table(["cluster", "winners", "winner share", "population rows", "population share", "lift", "winner rate", "most distinguishing fields (mean z within cluster)"],
                      [[f"c{int(x['cluster'])}", f"{int(x['winners']):,}", f"{100 * x['winner_share']:.1f}%", f"{int(x['population_rows']):,}",
                        f"{100 * x['population_share']:.1f}%", f"{x['lift']:.2f}", f"{100 * x['winner_rate']:.2f}%", x["top_fields"]]
                       for _, x in r["summary"].iterrows()])
        base = r["n_winners"] / r["n_pop"]
        L += [f"Base winner rate over the population: {100 * base:.2f}%. Winner rate in a cluster = winners in it / population rows assigned to it (winners included).", ""]
        cl = [f"c{c}" for c in sorted(r["w"]["cluster"].unique())]
        L += ["### Median of every field by cluster (raw values, nulls excluded; ranks are GROWTH-002 percentile ranks at lag 0)", ""]
        rows_ = []
        for _, x in r["medians"].iterrows():
            kd = kind_of(x["field"])
            rows_.append([x["field"]] + [fmt(x[c], kd) for c in cl] + [fmt(x["all_winners"], kd), fmt(x["population"], kd)])
        L += md_table(["field"] + cl + ["all winners", "population"], rows_)
        L += ["### 8-K, insider and share-count fingerprint (mean for counts, median for share changes; _f12 rows are forward-looking)", ""]
        rows_ = []
        for _, x in r["fingerprint"].iterrows():
            kd = "pct" if x["stat"] == "median" else "cnt"
            rows_.append([x["field"], x["stat"]] + [fmt(x[c], kd) if kd == "pct" else f"{x[c]:.2f}" for c in cl]
                         + [fmt(x["all_winners"], kd) if kd == "pct" else f"{x['all_winners']:.2f}",
                            fmt(x["population"], kd) if kd == "pct" else f"{x['population']:.2f}"])
        L += md_table(["field", "stat"] + cl + ["all winners", "population"], rows_)
        L += ["### Sector and regime mix (share of the cluster's winners in each bucket)", ""]
        for cat in CATEGORICAL_MIX:
            t = r["mix"][r["mix"]["category"] == cat]
            L += [f"{cat}", ""]
            L += md_table(["bucket"] + cl + ["all winners", "population"],
                          [[x["bucket"]] + [f"{100 * x[c]:.1f}%" for c in cl] + [f"{100 * x['all_winners']:.1f}%", f"{100 * x['population']:.1f}%"]
                           for _, x in t.iterrows()])
        L += ["### Timeline by cluster (winner median at T+k; population overlay = median over the cluster's winners of the population median at the same calendar month)", ""]
        for c in sorted(r["w"]["cluster"].unique()):
            L += [f"c{c}", ""]
            rows_ = []
            for k in STEPS:
                row = [f"{k:+d}"]
                for m in TL_MEASURES:
                    x = r["timeline"][(r["timeline"]["cluster"] == c) & (r["timeline"]["measure"] == m) & (r["timeline"]["k"] == k)]
                    if x.empty:
                        row += ["n/a", "n/a"]
                        continue
                    x = x.iloc[0]
                    kd = "pct" if m in ("price_return", "rev_growth_yoy", "shares_change") else "cnt"
                    row += [f"{fmt(x['winner_median'], kd)} ({cov(x['winner_n'] / x['winners'])})", fmt(x["population_median"], kd)]
                rows_.append(row)
            L += md_table(["k"] + [f"{m} {s}" for m in TL_MEASURES for s in ("W", "P")], rows_)
    reading = REPORTS_DIR / "winner_types_reading.md"
    if reading.exists():
        L += ["", reading.read_text().rstrip(), ""]
    (REPORTS_DIR / "winner_types.md").write_text("\n".join(L))


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET threads = 1")
    print("load", flush=True)
    load(con)
    res, csv = {}, {k: [] for k in ["sweep", "hdbscan", "summary", "dist", "medians", "fingerprint", "mix", "timeline", "spec", "assign"]}
    with threadpool_limits(limits=1):
        for label in LABELS:
            rows = con.execute(f"SELECT * FROM rows_{label}").fetchdf()
            Zw, Zp, kept, spec = design(rows)
            print(f"{label}: {len(Zw):,} winners, {len(rows):,} rows, {len(kept)} inputs", flush=True)
            sweep, models = kmeans_sweep(Zw)
            k = int(sweep.sort_values(["silhouette", "k"], ascending=[False, True]).iloc[0]["k"])
            km = models[k]
            labels_km, mapping = relabel(km, Zw)
            hd, ct = hdbscan_check(Zw, labels_km)
            summary, dist, w, p = cluster_summary(rows, Zw, Zp, km, mapping, kept)
            med, fp, mix = cluster_medians(w, rows), fingerprint(w, rows), mixes(w, rows)
            tl = cluster_timeline(con, label, w)
            print(f"  k={k} silhouette={sweep.set_index('k').loc[k, 'silhouette']:.4f}; hdbscan clusters by setting: "
                  + "/".join(str(int(c)) for c in hd["clusters"]), flush=True)
            res[label] = {"n_winners": len(Zw), "n_pop": len(rows), "kept": kept, "spec": spec, "sweep": sweep, "k": k,
                          "hdbscan": hd, "crosstab": ct, "summary": summary, "medians": med, "fingerprint": fp,
                          "mix": mix, "timeline": tl, "w": w}
            for name, df in [("sweep", sweep), ("hdbscan", hd), ("summary", summary), ("dist", dist),
                             ("medians", med), ("fingerprint", fp), ("mix", mix), ("timeline", tl), ("spec", spec),
                             ("assign", w[["ticker", "month_end", "cluster"]])]:
                d = df.copy()
                d.insert(0, "label", label) if "label" not in d.columns else None
                csv[name].append(d)
    names = {"sweep": "s9_kmeans_sweep", "hdbscan": "s9_hdbscan", "summary": "s9_clusters", "dist": "s9_cluster_mean_z",
             "medians": "s9_cluster_medians", "fingerprint": "s9_cluster_fingerprint", "mix": "s9_cluster_mix",
             "timeline": "s9_cluster_timeline", "spec": "s9_inputs", "assign": "s9_winner_clusters"}
    for key, frames in csv.items():
        pd.concat(frames, ignore_index=True).to_csv(REPORTS_DIR / f"{names[key]}.csv", index=False)
    write_report(res)
    print(f"RESULT: PASS — {REPORTS_DIR / 'winner_types.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
