project: matts-predicts
session-type: build
session: 2026-09-17 AEST — S9 (GROWTH-003 section 4): clustering winners into types; end of chunk 4c
status: COMPLETE — k-means 2 to 6 with silhouette, HDBSCAN check, per-cluster fingerprints, population frequency and rough lift, per-cluster timelines, reports/winner_types.md with the reading; chunk 4c ends.
claude-interface: Code
source: Claude Code on the web, 2026-09-17
session-duration: ~1.5 hours

---

## What Was Built or Changed

src/winner_types.py is new. It takes the S8 fields at T-0 (anatomy_fields.parquet) plus the 23 GROWTH-002 percentile ranks at lag 0 for every winner, applies Matt's three S9 rulings (T-0 only; the 5.02 proxy dropped, and ev_total_t12 with it; scalemarketcap excluded in favor of the point-in-time market cap), logs the three dollar fields, leaves out fields under 50% winner coverage, fills nulls with the winners' median, standardizes on the winners, and runs k-means for k 2 to 6 (n_init 10, seed 0) with silhouette. HDBSCAN runs at min_cluster_size 1% of winners at the default min_samples and three looser settings as the check, with an adjusted Rand index against the k-means labels. For the chosen k it writes cluster sizes, the median of every field, the 8-K, insider and share-count fingerprint (forward-looking rows labeled), sector and regime mix, the population frequency by nearest centroid and the rough lift, and the S8 timeline redrawn per cluster. reports/winner_types.md embeds reports/winner_types_reading.md; ten s9_*.csv files carry every table unrounded plus the per-winner assignment.

scikit-learn 1.9.1 (with scipy, joblib, threadpoolctl) was added to requirements.txt. BLAS and duckdb run single-threaded; two consecutive runs produce identical checksums for all eleven outputs.

## Files Touched [MANDATORY]

- strategies/02-growth/src/winner_types.py (new)
- strategies/02-growth/reports/winner_types.md, winner_types_reading.md (new)
- strategies/02-growth/reports/s9_kmeans_sweep.csv, s9_hdbscan.csv, s9_clusters.csv, s9_cluster_mean_z.csv, s9_cluster_medians.csv, s9_cluster_fingerprint.csv, s9_cluster_mix.csv, s9_cluster_timeline.csv, s9_inputs.csv, s9_winner_clusters.csv (new)
- strategies/02-growth/requirements.txt (scikit-learn 1.9.1, scipy 1.17.1, joblib 1.6.0, threadpoolctl 3.7.0)
- decisions.md ("S9 rulings" under Chunk 4c)
- BACKLOG.md (S9 DONE; chunk 4c ends; startup sequence includes winner_types)
- docs/wrapits/WRAPIT_2026-09-17-2310_s9-winner-types-chunk-4c-end.md (this file)

## Environment Variables [MANDATORY]

None used or changed (no data was fetched; the S8 parquet files were still on disk in this container).

## Services and Integrations Touched [MANDATORY]

PyPI (scikit-learn install). GitHub for the PR. No Sharadar calls.

## Endpoints Added or Changed [MANDATORY]

None.

## Database Changes [MANDATORY]

None.

## Gate Tests Run [MANDATORY — what ran, what it returned, or "None"]

- `python -m src.winner_types` → launch_300: 4,301 winners, 529,158 rows, 51 inputs; k=2 silhouette 0.0829; HDBSCAN clusters by setting 0/0/2/2. win_100: 20,367 winners, 558,318 rows, 53 inputs; k=2 silhouette 0.0854; HDBSCAN 0/0/0/0. RESULT: PASS. Runtime 2m53s single-threaded.
- Reproducibility: md5 of the ten s9_*.csv files and winner_types.md identical across two consecutive runs (11 of 11 OK).
- Timeline self-check: cluster medians at T+24 for launch_300 are +407% (c1) and +390% (c2), both at or above the +300% label; win_100 at T+12 are +142% and +131%, both above +100%.
- `python -m pytest -q tests` → 4 passed.

## How to Verify This Is Working Right Now

1. Fresh container: run the S8 startup sequence (fetch_bulk, ingest, universe, labels, regime, features, labels12, decile, anatomy), then `python -m src.winner_types`.
2. Confirm the last line reads RESULT: PASS and reports/winner_types.md has 532 lines with the k-means sweep showing k=2 silhouette 0.0829 (launch_300) and 0.0854 (win_100).

## What Breaks and How to Fix It

If the import of HDBSCAN from sklearn.cluster fails, the venv has scikit-learn under 1.3; reinstall from requirements.txt. If anatomy_fields.parquet is missing, run src/anatomy.py first. If checksums differ between runs, threading was re-enabled; the module pins BLAS and duckdb to one thread.

## Environment Facts Learned [MANDATORY — constraints/quirks found, or "None"; anything permanent also goes to CLAUDE.md]

- HDBSCAN (scikit-learn) on ~50 standardized dimensions labels everything noise at its default min_samples for both winner sets; looser settings find only small fragments. Recorded in the report, not in CLAUDE.md (a finding, not an environment fact).
- k-means with n_init 10 and threadpoolctl limited to one thread reproduces exactly across runs. Added to CLAUDE.md alongside the duckdb note.

## Ephemeral Outputs Not Yet Saved

None.

## Plain English Summary for Matt [MANDATORY]

The winners do not fall into types. The silhouette, which measures how separated clusters are, peaks at k = 2 at 0.08 for both labels, where anything under about 0.25 means no real structure, and HDBSCAN, which looks for dense groups, finds none at all. What k-means gives at k = 2 is a cut across one axis: how far the stock has fallen, its momentum, its volatility and its size. One end, about half of the winners, is the crash rebound: 74% below its three-year high, three months off the low, unprofitable, carrying net debt, with insiders buying, small and cheap, over-represented in Energy and in deep market drawdowns. The other end is the pullback in an uptrend: near its highs by comparison, top momentum ranks, revenue growing in the mid teens, R&D spend, no net debt, Technology and Healthcare, calm markets. The crash-rebound end has a rough lift of 2.7 for launch_300 and 2.0 for win_100, but the S8 loss_50 table already showed those same fields raise the loss rate more than the win rate, so that lift runs both ways. Neither end has an 8-K fingerprint. Chunk 4c ends here; the next step is chat, with the S8 and S9 reports as input.

## Decisions Made [MANDATORY — Decision | Reason | Alternatives rejected, or "None"; survivors must also land in decisions.md]

- T-0 fields only | Matt's brief | T-6 and T-12 values as extra columns.
- 5.02 proxy dropped, ev_total_t12 with it | Matt's brief; the total contains 5.02 | keeping the total.
- scalemarketcap excluded, marketcap_musd kept | Matt's brief; not point in time | including it.
- log1p on the three dollar fields | heavy tails would own a k-means cluster | raw z-scores; rank transforms.
- 50% winner-coverage floor per label, then winners' median imputation | inputs with 80% nulls would be mostly imputed constants | dropping rows with any null (would discard most winners).
- Silhouette on a fixed 10,000 sample for win_100 | full pairwise on 20,367 rows is 400 million distances | full computation.
- HDBSCAN sensitivity rows (min_samples 25, 10, 5) beside the default | the default returned all noise, which by itself says little | default only.
- Clusters numbered by size | deterministic report order | scikit-learn's arbitrary ids.
- scikit-learn 1.9.1 pinned | needed for k-means, silhouette, HDBSCAN | the hdbscan package (extra dependency).
All recorded in decisions.md "S9 rulings".

## Open Items for Next Session [MANDATORY — DONE: <item> closes existing items; confirm BACKLOG.md was updated this session]

- DONE: S9 per GROWTH-003 section 4. Chunk 4c ends.
- No build session is scheduled; chat decides the next spec using reports/anatomy_tables.md and reports/winner_types.md.
- Carried: rename the environment variable to SHARADAR_API_KEY (non-blocking).
- BACKLOG.md updated this session.

## Open Questions for Matt

- The clustering result is "one axis, two ends". If chat wants types anyway, the only lever left inside the spec is the input set; a smaller, hand-picked input set would be a new spec, not a rerun.
- The crash-rebound end's lift runs in both directions (S8 section 3.5). Any later hypothesis spec built on it needs the loss side stated up front.

## SESSION REVIEW [MANDATORY — 1-5 rating + what went wrong]

4. The first HDBSCAN run reported only the default setting, which was all noise and uninformative; the sensitivity rows were added on the second run. Nothing else went wrong; the k-means result was reproducible on the first checksum test.

## MATT-NOTE [Optional session rating]

