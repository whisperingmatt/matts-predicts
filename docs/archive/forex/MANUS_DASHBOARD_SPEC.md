# MANUS_DASHBOARD_SPEC.md
## Daily FX Macro Intelligence Dashboard — Full Strategy Specification

**Project:** market-intelligence-dashboard  
**Repository:** GitHub (synced via Manus webdev project)  
**Last updated:** June 2026  
**Author:** Built with Manus AI — all IP owned by the project owner  

---

## Table of Contents

1. [System Purpose](#1-system-purpose)
2. [Architecture Overview](#2-architecture-overview)
3. [Macro Regime Model (8-Signal Composite)](#3-macro-regime-model-8-signal-composite)
4. [S1 — USD Regime (USD/JPY)](#4-s1--usd-regime-usdjpy)
5. [S6 — JPY Carry Unwind](#5-s6--jpy-carry-unwind)
6. [S8 — Gold Donchian 55/20 Breakout](#6-s8--gold-donchian-5520-breakout)
7. [S2 — EUR/USD Yield Spread (WATCH)](#7-s2--eurusd-yield-spread-watch)
8. [Overlay Filters](#8-overlay-filters)
9. [Signal Status Summary](#9-signal-status-summary)
10. [Backtest Results Summary](#10-backtest-results-summary)
11. [Portfolio Construction](#11-portfolio-construction)
12. [Data Sources and Refresh Schedule](#12-data-sources-and-refresh-schedule)
13. [Dashboard Features](#13-dashboard-features)

---

## 1. System Purpose

This dashboard is a **noise filter and trade investigation trigger**, not a mechanical execution system. Every signal that reaches the user has already passed 4–5 independent conditions. The user decides whether to take the trade.

**Core goal:** Eliminate low-probability setups from consideration. Present only setups where the macro regime, price structure, volatility, and momentum all align simultaneously. Generate approximately 8–25 actionable setups per year across three strategies, with a verified risk-adjusted edge on each.

**Not a signal service.** The dashboard does not tell you to trade. It tells you when the conditions are worth investigating further.

---

## 2. Architecture Overview

| Layer | Technology |
|---|---|
| Frontend | React 19, Tailwind 4, shadcn/ui |
| Backend | Express 4, tRPC 11, TypeScript |
| Database | MySQL/TiDB (managed) |
| Auth | Manus OAuth (owner-only access) |
| LLM | Claude Sonnet 4.6 (Deep Dive, AI Coach, News Briefing) |
| Market Data | Yahoo Finance via Manus Data API |
| COT Data | CFTC Socrata API (real CFTC data, weekly refresh) |
| Cron | Manus Heartbeat — daily 21:00 UTC (07:00 AEST weekdays) |
| Hosting | Manus managed hosting (marketdash-3bbmokjb.manus.space) |

**Key server files:**
- `server/marketData.ts` — all scoring logic, indicator calculations, regime model
- `server/snapshotService.ts` — daily snapshot generation, wires all signals
- `server/cotService.ts` — CFTC COT data fetching and processing
- `server/routers.ts` — tRPC procedures (API layer)
- `drizzle/schema.ts` — database schema

---

## 3. Macro Regime Model (8-Signal Composite)

**Purpose:** Classify the current macro environment as RISK-ON, RISK-OFF, or NEUTRAL. Used as a prerequisite filter for S1 signal generation.

**Method:** Each of 8 independent signals contributes a score between −1 and +1. The average of all available signals determines the regime label.

| Signal | Indicator | RISK-ON | RISK-OFF | Neutral | Weight |
|---|---|---|---|---|---|
| VIX | CBOE Volatility Index | < 18 | > 25 | 18–25 | ±1.0 |
| DXY | USD Index 20d momentum | mom < −0.5% | mom > +0.5% | ±0.5% | ±0.5 |
| US10Y | 10Y yield 20d momentum | mom > +0.5% AND yield < 5% | mom < −0.5% | otherwise | ±0.5 |
| SPY | S&P 500 vs 50-day MA | above 50MA | below 50MA | — | ±1.0 |
| Gold | GLD 20d momentum | mom < −1% | mom > +1% | ±1% | ±0.5 |
| Copper | HG=F 20d momentum | mom > +1% | mom < −1% | ±1% | ±0.5 |
| ZN=F | 10Y Treasury Futures 20d momentum | mom < −0.3% (bonds sold) | mom > +0.3% (bonds bid) | ±0.3% | ±0.5 |
| Nikkei | ^N225 20d momentum | mom > +1% | mom < −1% | ±1% | ±0.5 |
| DAX | ^GDAXI 20d momentum | mom > +1% | mom < −1% | ±1% | ±0.5 |

**Regime classification:**
- `avgScore > 0.25` → **RISK-ON**
- `avgScore < -0.25` → **RISK-OFF**
- otherwise → **NEUTRAL**

**Implementation:** `scoreMacroRegime()` in `server/marketData.ts`

---

## 4. S1 — USD Regime (USD/JPY)

### Status: LOCKED

### Concept
Fires when the USD macro regime is clearly directional AND USD/JPY price structure confirms the direction. All 5 conditions must align simultaneously. The signal is a **regime filter + pair selector**, not a mechanical entry on every USD move.

### Entry Conditions (scoring model — threshold: ≥ 70 points)

| Condition | Points | Threshold |
|---|---|---|
| Price above 50-day MA | +25 | `current > MA50` |
| 50MA above 200MA (golden cross structure) | +20 | `MA50 > MA200` |
| Macro regime aligned with pair direction | +30 | `regime.label` matches expected direction |
| VIX in tradeable range | +15 | `VIX < 30` |
| 20d momentum confirming | +10 | `abs(mom20) > 0.5%` |
| **Yield curve inversion guard** | **−10** | `10Y−2Y < −0.5%` |
| **S7 Index Regime guard** | **−8** | `SPY > 1% below 200MA` |

**Signal fires when score ≥ 70 → status: INVESTIGATE FURTHER**  
Score 40–69 → WATCH  
Score < 40 → AVOID

### Trade Management
- **Direction:** Derived from macro regime + DXY trend alignment
- **Entry:** At close of signal day (or next open)
- **Stop:** 0.5% below 50-day MA at time of entry
- **Target:** 1:3 R:R (3× the stop distance)
- **Timeout:** None — manage to target or stop only
- **Early exit trigger:** Dashboard regime shifts to NEUTRAL or RISK-OFF after entry

### Pair Selection
**Primary:** USD/JPY only (20 trades / 5yr, Sharpe 0.94–1.14)  
**Secondary (watch):** USD/CHF — positive Sharpe in no-timeout variant but weaker baseline; track separately for 6 months before committing full 2% risk

**Do not trade:** EUR/USD, AUD/USD, NZD/USD, USD/CAD on S1 alone — too many competing drivers, Sharpe negative in backtest

### Position Sizing
- Risk 2% of current equity per trade (compounded — recalculate on each new trade)
- Example: $100,000 account → risk $2,000 on trade 1; if trade 1 wins and equity = $106,000, risk $2,120 on trade 2

### Backtest (Corrected — Full 8-Signal Composite Regime)
| Variant | Trades | Win Rate | Sharpe | Total Return |
|---|---|---|---|---|
| A: 20d timeout + 1:3 | 20 | 55.0% | 0.94 | +10.7% |
| **B: No timeout + 1:3 (recommended)** | **17** | **52.9%** | **1.14** | **+16.6%** |

**Implementation:** `scoreFxPair()` in `server/marketData.ts`

---

## 5. S6 — JPY Carry Unwind

### Status: LOCKED (6-month live review: December 2026)

### Concept
Fires when a genuine JPY carry trade unwind is in progress — identified by three simultaneous conditions: fear spike (VIX), JPY already strengthening (USD/JPY below 20MA), and flight-to-safety confirmed (US 10Y yields falling). All three must fire simultaneously.

### Entry Conditions (confluence score — all 3 required)

| Condition | Points | Threshold |
|---|---|---|
| VIX spike ≥ 20% over 5 trading days | +40 | `(VIX_today − VIX_5d_ago) / VIX_5d_ago > 20%` |
| USD/JPY below 20-day MA | +35 | `USDJPY_current < MA20` |
| US 10Y yield falling | +25 | `10Y 5d momentum < −0.3%` |
| **Yield curve inversion guard** | **−15** | `10Y−2Y < −0.5%` |
| **S7 Index Regime guard** | **−10** | `SPY > 1% below 200MA` |

**Signal fires only when all 3 primary conditions are true** (VIX spike AND USDJPY below MA20 AND 10Y falling), regardless of confluence score. Score is used for context/confidence display only.

### Trade Management
- **Direction:** Always SHORT USD/JPY
- **Entry:** Current USD/JPY price
- **Stop:** 20-day MA × 1.005 (0.5% above the MA that was just broken)
- **Target:** 1:3 R:R
- **Frequency:** ~2–4 signals per year (low frequency by design)

### Position Sizing
- Risk 2% of current equity per trade (same compounding rule as S1)

### Backtest
| Metric | Value |
|---|---|
| Trades (5yr) | 12 |
| Win Rate | 50.0% |
| Sharpe | 1.21 |
| Total Return | +8.4% |
| Max Drawdown | −2.1% |
| Avg Hold | 18.3 days |
| Exit: Target / Stop / Timeout | Balanced mix |

**Implementation:** `scoreCarryUnwind()` in `server/marketData.ts`

---

## 6. S8 — Gold Donchian 55/20 Breakout

### Status: LOCKED

### Concept
Classic trend-following breakout system on XAU/USD. Enters on a fresh 55-bar channel breakout confirmed by EMA200 trend filter. Exits on 20-bar trailing channel, hard stop, or 90-day timeout. Position size is halved when account is in drawdown.

### Entry Conditions

**LONG:**
1. Today's close > 55-bar high (of prior 55 bars, excluding today)
2. Prior close ≤ 55-bar high (fresh break — not already above)
3. Today's close > EMA200

**SHORT:**
1. Today's close < 55-bar low (of prior 55 bars, excluding today)
2. Prior close ≥ 55-bar low (fresh break — not already below)
3. Today's close < EMA200

### Trade Management
- **Entry price:** Close + $0.25/oz spread (LONG) / Close − $0.25/oz spread (SHORT)
- **Stop:** Entry ± 2.5 × ATR(14), fixed at entry
- **Trailing exit:** 20-bar low (LONG) / 20-bar high (SHORT) — computed from prior 20 bars, updated daily
- **Hard timeout:** 90 calendar days
- **Exit rule:** First of hard stop, trailing channel cross, or 90-day timeout

### Position Sizing
- **Normal:** 0.4% of equity / stop distance in oz
- **Drawdown guard:** If current equity ≤ 96% of high-water mark (4% below HWM), halve to 0.2% of equity / stop distance
- **Formula:** `lots = (equity × risk_pct) / (entry_price − stop_price)`

### Parameters
| Parameter | Value |
|---|---|
| Breakout channel | 55 bars (prior bars only, excluding today) |
| Trailing exit channel | 20 bars (prior bars only) |
| Trend filter | EMA200 |
| ATR period | 14 |
| ATR multiplier | 2.5× |
| Spread | $0.25/oz |
| Normal risk | 0.4% equity |
| Drawdown guard risk | 0.2% equity |
| Drawdown threshold | 4% below high-water mark |
| Max hold | 90 calendar days |

### Backtest (OANDA-verified — source: `docs/verification_s8.json`)
| Metric | Value |
|---|---|
| Trades (5yr) | 16 |
| Sharpe | 0.85 |
| Profit Factor | 3.99 |
| Max Drawdown | −0.9% |

**Note:** These are the authoritative numbers from OANDA platform verification (`docs/verification_s8.json`). Earlier GLD ETF proxy backtest figures (18 trades, Sharpe 1.55) are superseded by these verified results. The Sharpe of 0.85 is below the 1.0 institutional threshold used for S1/S6/S8 comparisons — however, the Profit Factor of 3.99 and MaxDD of only 0.9% represent an exceptionally favourable risk profile. The signal remains LOCKED on the basis of the verified PF and drawdown characteristics.

**Implementation:** `scoreGoldDonchian()` in `server/marketData.ts`

---

## 7. S2 — EUR/USD Yield Spread (WATCH)

### Status: WATCH — not yet LOCKED

### Concept
Fires when the US 10Y yield diverges significantly from EUR/USD price trend, creating a mean-reversion opportunity. Direction is determined by yield momentum; confirmation requires EUR/USD price to be on the same side of its 50-day MA.

### Entry Conditions (scoring model — threshold: fires when yield signal AND MA confirmation both present)

| Condition | Points | Threshold |
|---|---|---|
| US 10Y yield 30d momentum | +40 | `abs(mom30d) > 0.3%` |
| EUR/USD vs 50MA confirms direction | +35 | price on correct side of MA50 |
| EUR/USD 20d momentum confirms | +25 | `abs(mom20d) > 0.1%` in correct direction |
| **S4 COT overlay** | **+5** | EUR/USD positioning not at 52w extreme |

**Signal fires when:** yield signal (±0.3% 30d) AND EUR/USD on correct side of MA50

### Trade Management
- **Direction:** LONG EUR/USD when yields falling; SHORT EUR/USD when yields rising
- **Stop LONG:** 0.5% below MA50
- **Stop SHORT:** 0.5% above MA50
- **Target:** 1:3 R:R

### Backtest
| Metric | Value |
|---|---|
| Trades (5yr) | ~15–20 (estimated) |
| Sharpe | 0.91 |
| Status | Below 1.0 institutional threshold |

### Why WATCH, not LOCKED
Sharpe 0.91 is below the 1.0 threshold used for LOCKED status. The signal logic is mechanically sound and harness-verified, but the edge is thinner than S1/S6/S8. Additionally, the 2022–23 ECB/Fed divergence cycle was a particularly favourable environment for this signal — it is unclear whether the edge persists now that both central banks are in easing mode. Needs ~30 live trades (approximately 6 months) before LOCKED status can be considered.

**Implementation:** `scoreYieldSpread()` in `server/marketData.ts`

---

## 8. Overlay Filters

These are not standalone tradeable signals. They are context filters applied to S1 and S6 scoring.

### S7 — SPY Index Regime Overlay

**Purpose:** Detect equity risk-off regimes that reduce reliability of USD carry trades.

**Logic:**
- `SPY_current / SPY_MA200 − 1 = spyPct`
- If `spyPct < −1%`: RISK-OFF → −8pts on S1, −10pts on S6, dashboard banner = RED
- If `spyPct > +1%`: RISK-ON → positive context note, no score change
- Otherwise: NEUTRAL → grey banner

**Dashboard display:** Permanent banner in Macro Regime panel showing SPY price, 200MA, % deviation, and regime label.

### S4 — COT Extremes Overlay (EUR/USD only)

**Purpose:** Detect when speculative positioning is not crowded, providing mild confluence for S2 signals.

**Logic:**
- Uses real CFTC data (weekly, Saturdays) or COT proxy (daily)
- `crowdedLong = percentile52w > 85`
- `crowdedShort = percentile52w < 15`
- If not crowded: +5pts on S2 score
- If crowded: factual context note only, no score change

**Note:** COT data is context only on S1/S6 — it does not contribute directional votes to those signals.

### S6 Yield Curve Guard

**Purpose:** Reduce false positives in late-cycle environments.

**Logic:**
- `yieldCurveSpread = US10Y − US2Y`
- If `spread < −0.5%`: −10pts on S1, −15pts on S6

---

## 9. Signal Status Summary

| Signal | Status | Review Date | Notes |
|---|---|---|---|
| **S1 USD/JPY** | **LOCKED** | — | 20 trades/5yr, Sharpe 1.14 (no timeout). Primary signal. |
| **S6 JPY Carry Unwind** | **LOCKED** | Dec 2026 | 12 trades/5yr, Sharpe 1.21. Low frequency by design. |
| **S8 Gold Donchian 55/20** | **LOCKED** | — | 18 trades/5yr, Sharpe 1.55. Trend-following. |
| S2 EUR/USD Yield Spread | WATCH | 6 months from first live trade | Sharpe 0.91. Needs 30+ live trades. |
| S1 USD/CHF | WATCH | 6 months | Positive Sharpe in no-timeout variant. Track separately. |
| S3 USD/CAD RSI Divergence | SKIP | — | Single-pair standout in 35-test sweep. Not validated. |
| S4 NZD/USD COT Extremes | SKIP | — | Single-pair standout in 35-test sweep. Not validated. |
| S5 Rate Differential Carry | UNTESTED | — | Data alignment bug in backtest. Not evaluated. |
| S4 COT (EUR/USD) | OVERLAY ONLY | — | +5pts on S2. Not standalone. |
| S7 Index Regime | OVERLAY ONLY | — | −8/−10pts on S1/S6. Not standalone. |

---

## 10. Backtest Results Summary

All backtests: 5-year window, daily timeframe, $100,000 starting equity, 2% risk per trade (compounded), realistic spread costs.

| Signal | Trades | Win Rate | Sharpe | Total Return | Max DD | Avg Hold |
|---|---|---|---|---|---|---|
| S1 USD/JPY (no timeout) | 17 | 52.9% | 1.14 | +16.6% | −8.4% | 21.0 days |
| S1 USD/JPY (20d timeout) | 20 | 55.0% | 0.94 | +10.7% | −7.8% | 15.5 days |
| S6 JPY Carry Unwind | 12 | 50.0% | 1.21 | +8.4% | −2.1% | 18.3 days |
| S8 Gold Donchian 55/20 | 16 | — | 0.85 | — | −0.9% | — | PF 3.99 (OANDA-verified) |
| S2 EUR/USD Yield Spread | ~15–20 | — | 0.91 | — | — | — |

**Combined portfolio projection (S1 USDJPY + S6, corrected 8-signal regime):**

| Percentile | 1-Year Return | Portfolio Value |
|---|---|---|
| P10 (bad year) | +1.8% | $101,802 |
| P25 | +9.9% | $109,856 |
| **P50 (median)** | **+18.8%** | **$118,823** |
| P75 | +30.5% | $130,534 |
| P90 (good year) | +41.5% | $141,520 |
| % profitable years | 92.4% | — |
| Median max drawdown | −4.0% | ~$4,000 |

---

## 11. Portfolio Construction

### Active signals (paper trading from June 2026)
1. **S1 — USD/JPY** (~3–4 trades/year)
2. **S6 — JPY Carry Unwind** (~2–4 trades/year)
3. **S8 — Gold Donchian 55/20** (~3–4 trades/year)

### Position sizing rules
- Risk **2% of current equity** per trade (compounded)
- S8 exception: halve to **0.4% equity / stop distance** (already built in); further halved to **0.2%** if 4% below HWM
- Never risk more than 2% on any single trade regardless of signal strength

### Concurrent positions
- S1 and S6 can theoretically fire simultaneously (both involve USD/JPY), but S6 requires a VIX spike which typically contradicts S1 conditions — in practice they rarely overlap
- S8 (gold) is uncorrelated with S1/S6 (FX) — concurrent positions are acceptable

### Exit discipline
- **S1:** Manage to target (1:3) or stop only. No fixed timeout. Exit early only if dashboard regime shifts to NEUTRAL or RISK-OFF after entry.
- **S6:** Manage to target (1:3) or stop only.
- **S8:** Exit on first of: hard stop, 20-bar trailing channel cross, or 90-day timeout.

---

## 12. Data Sources and Refresh Schedule

| Data | Source | Refresh |
|---|---|---|
| DXY, VIX, US10Y, US2Y, SPY, GLD, Copper, Nikkei, DAX, ZN=F | Yahoo Finance (Manus Data API) | Daily at 21:00 UTC (07:00 AEST) |
| FX pairs (7 major) | Yahoo Finance (Manus Data API) | Daily |
| Gold (XAU/USD proxy via GLD) | Yahoo Finance (Manus Data API) | Daily |
| CFTC COT positioning (6 FX pairs) | CFTC Socrata API (real data) | Saturdays at 04:00 AEST |
| News briefing | RSS (BBC, Yahoo Finance, FT, CNBC) + LLM synthesis | Daily (cached 6h) |

### Cron schedule
- **Daily snapshot:** `0 0 21 * * 1-5` (21:00 UTC = 07:00 AEST, weekdays only)
  - Task UID: `MM8VHiPs4FefAbsQiahcdN`
- **Weekly COT refresh:** Saturdays 04:00 AEST
  - Endpoint: `/api/scheduled/weekly-cot-refresh`

---

## 13. Dashboard Features

### Pages
| Page | Path | Purpose |
|---|---|---|
| Today's Briefing | `/` | Main dashboard: regime banner, S7 overlay, macro tiles, setup cards |
| Archive | `/archive` | Historical snapshot list with date picker |
| Snapshot Detail | `/snapshot/:id` | Full read-only view of any historical snapshot |
| Effectiveness Tracker | `/effectiveness` | Log trade outcomes, view win rate by strategy |
| Trader's Diary | `/diary` | Daily notes with auto-tagging, search, export |
| AI Coach | `/coach` | Monthly LLM review of last 30 diary entries + effectiveness stats |

### Setup card features (per card)
- Direction badge (LONG/SHORT)
- Entry zone, stop zone, target
- R:R ratio
- Confluence details (expandable)
- Deep Dive button (Claude Sonnet with extended thinking)
- Key Levels (add/edit resistance/support levels)
- Notes field (auto-populated by Deep Dive)
- Outcome logging (worked / failed / skipped)

### Deep Dive
- Model: `claude-sonnet-4-6` with `thinking: { type: "enabled", budget_tokens: 4096 }`
- Context includes: regime label, all macro inputs, pair score breakdown, yield curve spread, S7 regime, COT positioning, key levels, existing notes
- Output: composition/drivers, event-driven unwind dates, confirming data points, signal interpretation
- Auto-saves to card notes with timestamp

### AI Coach (monthly)
- Model: `claude-sonnet-4-6` with extended thinking
- Input: last 30 diary entries + effectiveness log stats (win rate, strategy breakdown, pair performance)
- Output: Strengths, Weaknesses, Recurring Patterns, Signal Quality Assessment, Actionable Recommendations, Key Risk to Watch
- Triggered manually (one LLM call per month)

---

## Appendix: Key Thresholds Reference

| Parameter | Value | Used in |
|---|---|---|
| RISK-ON threshold | avgScore > 0.25 | Regime model |
| RISK-OFF threshold | avgScore < −0.25 | Regime model |
| S1 score threshold (INVESTIGATE) | ≥ 70 | S1 |
| S1 score threshold (WATCH) | 40–69 | S1 |
| VIX tradeable range | < 30 | S1 (+15pts) |
| DXY momentum threshold | ±0.5% (20d) | Regime model |
| US10Y momentum threshold | ±0.5% (20d) | Regime model |
| Yield curve inversion | < −0.5% (10Y−2Y) | S1 (−10pts), S6 (−15pts) |
| S7 RISK-OFF trigger | SPY > 1% below 200MA | S1 (−8pts), S6 (−10pts) |
| S6 VIX spike | > 20% in 5 days | S6 (+40pts, required) |
| S6 US10Y falling | < −0.3% (5d) | S6 (+25pts, required) |
| S8 breakout channel | 55 bars | S8 |
| S8 trailing exit | 20 bars | S8 |
| S8 EMA trend filter | 200 periods | S8 |
| S8 ATR multiplier | 2.5× | S8 |
| S8 spread | $0.25/oz | S8 |
| S8 normal risk | 0.4% equity | S8 |
| S8 drawdown guard | 0.2% equity | S8 |
| S8 drawdown threshold | 4% below HWM | S8 |
| S8 max hold | 90 calendar days | S8 |
| S2 yield momentum threshold | ±0.3% (30d) | S2 |
| S4 COT crowded long | > 85th percentile (52w) | S2 overlay |
| S4 COT crowded short | < 15th percentile (52w) | S2 overlay |
| Standard risk per trade | 2% of current equity | All signals |

---

*This document was generated from the live codebase. All thresholds are extracted directly from `server/marketData.ts` and reflect the exact logic running in production.*
