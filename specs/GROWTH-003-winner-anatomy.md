# SPEC GROWTH-003: Chunk 4c — Winner Anatomy (Descriptive, No Hypotheses)

Repo: matts-predicts
Path: strategies/02-growth/specs/GROWTH-003-winner-anatomy.md
Spec version: 1.0 — 2026-09-17
Status: LOCKED for build. Changes require a decisions.md entry.
Extends GROWTH-001 and GROWTH-002. Reuses universe, labels, features, regime.

## 0. Purpose (cold-start context)

GROWTH-001/002 tested pre-declared hypotheses and found the winner population looks unlike the textbook profile. This spec runs the reverse: take every winner, describe everything we can measure about it before and during the move, compare to the non-winner population, and let clustering find the winner types. No directions are declared. Nothing "passes" or "fails". The output is a description and a set of candidate types for a later hypothesis spec to test.

Winners: launch_300 (300% over 24m) and win_100 (100% over 12m), reported separately throughout. Population: all universe stock-months in the same window.

## 1. Locked decisions

F1. No declared directions, no pass criteria. Report distributions and ratios; the reading describes, it does not rank.
F2. Build and holdout windows are pooled for description (2006-01 to 2025-06 for win_100; to 2024-06 for launch_300). This is descriptive, not predictive, so the holdout gate does not apply. Record this in decisions.md.
F3. Every comparison is winner-vs-population, never winner-only. A pattern is a clue only if it is more common among winners than in the population at the same month.
F4. D8 applies to any cell reported as a ratio.
F5. Narrative qualities (moat, strategic pivot, management quality) are out of scope; 8-K item codes are the recorded proxy and the report says so.

## 2. New descriptive fields (compute on the existing grid, point-in-time)

From tickers: years_since_first_price (firstpricedate); sector; industry; exchange; scalemarketcap category.
From stocks: drawdown_from_3y_high at T-0; months_since_3y_low; realized_vol_12m; avg_dollar_volume_20d; price level bucket ($5–10, 10–20, 20–50, 50+).
From fundamentals (ARQ, point-in-time): profitable (netinc > 0) yes/no; revenue growth YoY; gross margin; opmargin; cash / marketcap; net debt / marketcap; capex / revenue; R&D / revenue; sharesbas change 4q and 8q; consecutive quarters of revenue growth; quarters since last loss.
From events (8-K item codes), counts in trailing 12m at T-0, and also in the 12m AFTER T-0 (to see what happened during the move):
  1.01 material agreement; 1.02 termination of agreement; 2.01 acquisition/disposition completed; 2.02 results of operations; 2.03 new financial obligation (debt); 3.02 unregistered equity sale; 5.02 officer/director change; 5.03 charter/bylaw change; 7.01 Reg FD; 8.01 other events. Flag: CEO change proxy = 5.02 in trailing 12m; financing proxy = any of 2.03 or 3.02 in trailing 12m; deal proxy = 2.01 in trailing 12m.
From insiders: net insider buys (count buys − count sells) trailing 12m; officer-only buys trailing 12m.
From holdings (2013+ only): inst_pct level and 4q delta.
From GROWTH-002: all decile ranks at T-0, T-6, T-12.
Regime: drawdown bucket and months-since-trough at T-0.

## 3. Session 8 — Anatomy tables

For each winner label, produce:
3.1 Profile table: for every field in section 2 and every decile rank, the winner median and the population median at T-0, T-6, T-12, plus the ratio of winner share to population share for each categorical bucket (sector, exchange, price bucket, profitable, CEO-change, financing, deal, IPO<3y). Coverage beside every cell.
3.2 Timeline table: for winners only, the median path of price, revenue growth, share count, insider net buys, and 8-K counts from T-24 to T+24 in 3-month steps, with the population median path overlaid (population aligned on calendar month). This shows what changed before the move and what happened during it.
3.3 During-move table: 8-K item counts and share count change in the 12m after T-0, winners vs population, to show whether winners raised money, did deals, or changed leadership while running.
3.4 Sector × regime table: winner share by sector within each drawdown bucket (D8 applies).
Write reports/anatomy_tables.md with a plain-prose description of the largest winner-vs-population gaps, in both directions. No recommendations.

## 4. Session 9 — Clustering into winner types

Input: winners only, one row per winner at T-0, using the section 2 numeric fields and GROWTH-002 percentile ranks, standardized. Method: k-means for k in 2..6 with silhouette reported; also HDBSCAN as a check. Pick k by silhouette, report all.
For each cluster: size; median of every field; the 8-K, insider, and share-count fingerprint; sector mix; regime mix; and the cluster's frequency in the population (assign every population row to its nearest cluster centroid and report what fraction of population rows fall in each cluster vs what fraction of winners do — that ratio is each type's rough lift).
Timeline (3.2) redrawn per cluster.
Write reports/winner_types.md with a plain-prose description of each type, a one-line name for it, and the two or three fields that most distinguish it. State plainly which types are mostly regime, which are mostly size/volatility, and which have a fundamental fingerprint. This ends chunk 4c.

## 5. Warnings before starting

- Point-in-time discipline holds for all "before T-0" fields. "After T-0" fields (3.3) are explicitly forward-looking and must be labelled as such everywhere; they describe the move, they cannot enter any later scoring model.
- 8-K item coverage varies by year; report coverage per code per year before using them.
- Do not drop or merge clusters to make a cleaner story. Report what the algorithm found.
- Deterministic ordering and fixed random seeds in all outputs.
