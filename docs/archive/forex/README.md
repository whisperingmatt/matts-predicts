# Forex work (parked)

Status: parked as of 9 Oct 2026. Nothing here is active, deployed or maintained. These six files were copied from two repos before those repos were deleted. Both repos were last touched 14 Jun 2026.

## Where each file came from

From `whisperingmatt/market-intelligence-dashboard` (built with Manus AI, commit 9463227):

- `MANUS_DASHBOARD_SPEC.md`: full strategy spec for the macro dashboard (8-signal regime model, S1 USD/JPY, S6 JPY carry unwind, S8 gold Donchian, S2 EUR/USD yield spread, backtest tables).
- `cotService.ts`: CFTC Commitments of Traders fetcher (Socrata API, Legacy and TFF datasets). Reusable if positioning data is ever wanted.

From `whisperingmatt/gbpusd-trading-system` (Python, OANDA and Telegram, commit c72659e). Despite its name it ended up as a Gold and USD/JPY system:

- `STRATEGY_SPEC.md`: the v5.0 locked spec.
- `HANDOFF.md`: daily bridge notes, 14 Jun 2026. Holds the S1, S2 and S8 verification results, the v3.0 vs v5.0 Gold reconciliation and the NAS100 exclusion.
- `HANDOFF_RESULTS.md`: an older handoff from 20 May 2026, from the earlier multi-pair GBP/USD era (v1.0 baseline, 52 trades). It describes a different system from `HANDOFF.md`. Kept for history only.
- `reconcile_v3_v5.json`: the Gold Donchian v3.0 vs v5.0 reconciliation data (5 years, OANDA XAU/USD).

## The two systems disagreed on S1 and S2

The same strategies were backtested in both systems and the numbers did not match. The disagreement was not resolved before the work was parked.

- S1 (USD/JPY): the dashboard spec gives 17 trades, 52.9% win rate, Sharpe 1.14, +16.6% (no timeout) or 20 trades, 55% win rate, Sharpe 0.94 (20-day timeout). `HANDOFF.md` reports 24 trades, 70.8% win rate and Sharpe 4.40 (daily-spread method), and says "MATCH" to a canonical 24 trades. It gives a trade-based Sharpe of 1.61 against 1.64 from the dashboard. The `CLAUDE.md` in that repo (not copied here) instead says 19 trades, 63.2% win rate, Sharpe 1.64. So the gbpusd repo is not consistent with itself either.
- S2 (EUR/USD): the dashboard spec gives about 15 to 20 trades and Sharpe 0.91. `HANDOFF.md` reports 23 trades, 43.5% win rate and Sharpe 0.86, marked "close". Four assumptions (A1 to A4: how "diverges" is defined, the moving-average conditions, no DXY filter, no Bund yield) were never confirmed.
- Different Sharpe methods (daily-spread vs per-trade) inflate or deflate results, so compare like with like.
- S8 (Gold Donchian) is the only strategy verified against OANDA data in both places. The profit factor of 3.99 (16 trades) is consistent.

Treat every figure above as unverified. Before any of it informs a real decision, rerun it from the specs against independent data.
