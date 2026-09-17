# SPEC GROWTH-002: Chunk 4b — Decile-Ranked Retest at the 12-Month Horizon

Repo: matts-predicts
Path: strategies/02-growth/specs/GROWTH-002-decile-retest.md
Spec version: 1.0 — 2026-09-18
Status: LOCKED for build. Changes require a decisions.md entry.
Supersedes nothing. Extends GROWTH-001. All GROWTH-001 decisions D1–D9 remain in force except where stated below.

## 0. Why this spec exists (cold-start context)

GROWTH-001 tested binary threshold flags against a 300%-in-24-months label. Two flaws surfaced in S4/S5:

1. The label is too rare (0.66% build, 1.25% holdout) and dominated by market regime. The strategy trades a rotating 10-slot book on a 12-month horizon, so the label should match that horizon.
2. Binary flags true for most rows have a lift ceiling near 1.0 (lift ≤ 1 / share_true), so several features could not pass regardless of their real information content.

This spec fixes both: every feature is ranked into cross-sectional deciles each month, and tested against 12-month labels. Existing features.parquet, labels, universe, and regime tags are reused. Do not rebuild them.

## 1. Locked decisions (new)

E1. New labels on the existing universe grid, from month-end close (closeadj): fwd_12m_return ≥ 50% (win_50), ≥ 100% (win_100). Keep launch_300 (24m) as a reference column only. Delist before t+12 uses last adjusted close as terminal, as in D1.
E2. Every continuous feature is converted to a decile rank (1–10) computed cross-sectionally within each month_end and lag, among non-null rows only. Decile 10 = highest raw value. Binary flags from GROWTH-001 are retained as-is for comparison but are not the primary test.
E3. Two new features: pegy = pe / ((eps_growth_4q + dividend_yield) × 100); shareholder_yield = dividend_yield + buyback_yield, where buyback_yield = (shares_8q_ago − shares_now) / shares_8q_ago, annualized over 2 years. Both nulls per the GROWTH-001 rules.
E4. Build 2006-01 to 2019-12; holdout 2020-01 to 2025-06 (12-month labels are observable to mid-2025). Holdout not opened until build results are committed (same gate as D4, enforced by session split in section 5).
E5. D8 (≥100 events per cell) applies. Event count for win_50 will be far larger than for launch_300, so most cells should be readable.
E6. Direction is declared per feature BEFORE results, in section 3. A feature passes only in its declared direction. No post-hoc flipping.

## 2. Features to rank (raw values from features.parquet unless noted)

Momentum: ret_6m_skip1, ret_12m_skip1 (H9 raw values, not the top-decile flag)
Earnings: eps_growth_q0 (H1 raw), rev_growth_accel (H4 raw), op_margin_delta
Valuation: peg (H5), pe, pe_vs_5y_median ratio (H6), fcf_ps_slope (H8), pegy (new)
Structure: pct_from_52w_high (H15 raw), dist_above_30w_sma (H13 raw), atr_contraction (H14 raw)
Ownership: inst_pct (H10), inst_pct_delta_qoq, insider_buy_count_90d (H11)
Balance: net_debt_to_ebitda (H20), share_count_change_8q (H21), shareholder_yield (new)
Size: marketcap (H7)
Controls: pb, dividend_yield

Regime tags from GROWTH-001 section 6 unchanged.

## 3. Declared direction and pass criteria (set before results)

Direction (which decile is hypothesized to launch more):
- HIGH decile better: ret_6m_skip1, ret_12m_skip1, eps_growth_q0, rev_growth_accel, op_margin_delta, fcf_ps_slope, inst_pct_delta_qoq, insider_buy_count_90d, shareholder_yield, atr_contraction (more contraction), dist_above_30w_sma
- LOW decile better: peg, pe, pe_vs_5y_median, pegy, marketcap, net_debt_to_ebitda, share_count_change_8q (fewer new shares), pb, dividend_yield, pct_from_52w_high
- inst_pct: declared LOW-to-MID (deciles 3–6) per H10's "rising from a low base"

A feature PASSES on a label if, in its declared extreme decile (10 for HIGH, 1 for LOW):
- lift ≥ 1.5 with Wilson 95% lower bound ≥ 1.2 in the build window, AND
- the same in the holdout, AND
- the decile lift curve is broadly monotonic in the declared direction (Spearman rank correlation between decile number and lift, sign as declared, |rho| ≥ 0.6) in the build window.

A feature is REGIME-DEPENDENT if it passes overall but the extreme-decile lift is < 1.2 in every regime bucket with drawdown < 20%.

Study VALID if win_50 base rate is between 3% and 25% in the build window. Outside that, stop and report.

## 4. Composite (build window only, then holdout)

After single-feature results, build one composite: the mean decile rank of all features that pass on win_50 in the build window (LOW-direction features use 11 − decile so higher is always better). Rank the composite into deciles per month. Report lift of composite decile 10, and deciles 8–10 pooled, on win_50, win_100, and launch_300, raw and by regime. Also report what fraction of universe rows land in composite decile 10 (this is the candidate pool size).

If fewer than 3 features pass, report that and build the composite from the top 3 by build-window extreme-decile lift, clearly labelled as unconfirmed.

## 5. Sessions (one task each)

S6: labels (E1), new features (E3), decile ranks (E2), build-window single-feature tables and composite (section 4). Write reports/decile_build_results.md. Wrap, PR. Do not open holdout.
S7: holdout single-feature and composite. Write reports/decile_holdout_results.md with a plain-prose reading covering: which features confirmed, the composite's holdout lift, candidate pool size, and expected win_50 count per 10 picks by regime (10 × conditional base rate × lift). Wrap, PR. This ends chunk 4b.

## 6. Warnings before starting

- Deciles are computed within month AND lag. Never rank across months (that leaks the future through the ranking population).
- Rank among non-null rows only; nulls stay null. Report coverage beside every decile lift.
- Do not tune thresholds, directions, or the composite recipe after seeing results. If something looks wrong, report it; the fix goes through decisions.md.
- Deterministic ordering in all outputs (carry the S5 fix).
