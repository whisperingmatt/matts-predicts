# HANDOFF.md — Daily Bridge

> Live two-way handoff between web Claude (planning) and Claude Code (building).

---

## DATE
2026-06-14 (Saturday)

## STATUS — Where We Are Today

v5.0 deployment system built and tested. Gold spec reconciled. NAS100 excluded (confirmed 0 trades). Full signal chain running end-to-end. Telegram integration wired — waiting for credentials from user.

---

## RESULTS — v3.0 vs v5.0 Reconciliation (2026-06-14)

**File shipped:** `docs/reconcile_v3_v5.json`, `backtest/reconcile_v3_v5.py`

**Window:** 2021-06-13 to 2026-06-11 (5-year, OANDA XAU/USD D1)

```
                        v3.0            v5.0
Trades             :    16              17
Win Rate           :    56.2%           70.6%
Profit Factor      :    3.607           4.401       (+22%)  OK
Max Drawdown       :    0.98%           0.45%       (-54%)  OK
Total P&L          :    $6,314          $3,887
Avg Win / Loss     :    $971 / $-346    $419 / $-229
Sharpe M1          :    4.79            4.62
Exits              :    STOP:6 TRAIL:6 TIME:4   STOP:2 TARGET:5 TIME:10
ATR-filtered trades:    n/a             2
```

**VERDICT: PROCEED.** v5.0 improves PF (+22%) and slashes DD (-54%). Total P&L lower because wins are capped at 2R (no more trailing runs to $5k+), but risk-adjusted profile is better. Both pass the 10% degradation gate.

**Interpretation of v5.0 trade characteristics:**
- 10 TIME exits (vs 4 v3.0): fixed target rarely hit in 90 days — gold trends slowly
- 5 TARGET exits: when target IS hit, big clean wins
- 2 STOP exits (vs 6 v3.0): stop floor (swing-low based) is wider, letting trades breathe
- Win rate jump (56% → 70%): wider stop = fewer false stop-outs

**Key trade-off:** v5.0 gives up the possibility of large trend-following wins ($5k+ from 2025 bull run) in exchange for a more controlled, consistent profile.

---

## RESULTS — NAS100 Reconciliation (2026-06-14)

**CONFIRMED: 0 trades on NAS100_USD with canonical repo code.**

Root cause: position sizing floors to 0 units.
- NAS100 at ~20,000 points, ATR14 ~300-400 points
- Stop distance = 2.5 × 350 = 875 points
- Risk = $100k × 0.4% = $400
- Units = $400 / 875 = 0.46 → floor(0.46) = 0

Web Claude's "16 trades, PF 2.80" used different sizing assumptions (likely a fixed lot size or different pip_value for index contracts). The canonical repo code gives 0 trades. NAS100 EXCLUDED from v5.0.

**v5.0 instruments: XAU_USD + USD_JPY only.**

---

## COMPONENTS SHIPPED (2026-06-14)

| File | Status | Notes |
|------|--------|-------|
| `backtest/reconcile_v3_v5.py` | ✅ Written + run | Side-by-side v3.0/v5.0 comparison |
| `strategy/portfolio_v5.py` | ✅ Written + tested | Signal engine for XAU_USD + USD_JPY |
| `scripts/daily_alert.py` | ✅ Written + tested | Full chain: fetch → signal → Telegram → log |
| `scripts/update_equity.py` | ✅ Written + tested | CLI equity updater, writes config/equity.json |
| `scripts/telegram_test.py` | ✅ Written | Test bot credentials before going live |
| `docs/telegram_setup.md` | ✅ Written | Full setup instructions |
| `config/equity.json` | ✅ Created | Initialized at $97,971 |
| `Procfile` | ✅ Created | Railway worker: python -m scripts.daily_alert --server |

---

## BLOCKERS — What's Needed to Complete Deployment

### 1. Telegram credentials (REQUIRED before first live alert)

1. Open Telegram → @BotFather → `/newbot`
2. Copy token → add to `.env` as `TELEGRAM_BOT_TOKEN`
3. Start a chat with your bot → send any message
4. Get chat ID: `curl https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Add to `.env` as `TELEGRAM_CHAT_ID`
6. Test: `python -m scripts.telegram_test`

### 2. Railway deploy (after Telegram is confirmed working)

1. Confirm Telegram test passes locally
2. Add env vars to Railway dashboard:
   - `OANDA_API_KEY`, `OANDA_ENV=practice`
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
3. Deploy from main branch (Procfile picks up `scripts.daily_alert --server`)
4. Check Railway logs at next 21:05 UTC for first live alert

### 3. Update equity before first real run

```
python -m scripts.update_equity 97971
```
(Already initialized at $97,971 — update as needed.)

---

## NEXT STEPS (when ready)

1. Get Telegram credentials → run `scripts/telegram_test.py`
2. Run `scripts/daily_alert.py` with live credentials to see full message in Telegram
3. Deploy to Railway
4. Monitor first few alerts manually (no trades yet)

---

## NOTES TO FUTURE WEB CLAUDE

- v5.0 spec: stop floor = max(2.5×ATR, swing-low distance), fixed 1:2 target, ATR filter 2×ATR20MA, 90d cap
- v3.0 was trailing channel + no target + no ATR filter
- NAS100 sizing problem: OANDA NAS100 is in USD points, sizing is risk/stop_pts → floors to 0 at 0.4% risk
  - To include NAS100 later: need to adjust risk % (e.g. 2%) or set a minimum lot size floor
- USD_JPY included in v5.0 but NOT yet backtested with Donchian 55/20 — should validate before live
- config/equity.json = source of truth for position sizing; update with `scripts/update_equity.py`
- signals.json in docs/ keeps rolling 90-day history of all signal checks (including no-signal days)
- strategy/portfolio_v5.py is the standalone signal engine; daily_alert.py is the scheduler wrapper

---

## PREVIOUS RESULTS (carried from 2026-06-13)

### S1: USD/JPY USD-Regime (LONG only) — VERIFIED

```
Period:         2021-01-04 to 2026-06-12  (5 years)
Trades:         24             [canonical: 24]  MATCH
Win Rate:       70.8%          [canonical: 70.8%]  MATCH
Sharpe:         4.40           [canonical: 4.40]  MATCH
Total P&L:      $14,954
Profit Factor:  4.79
Max Drawdown:   1.5%
```

Manus M3 Sharpe method confirmed: `mean/std * sqrt(252 / avg_hold_days)` → 1.61 (vs Manus 1.64).

### S2: EUR/USD Yield Spread Divergence (SHORT only) — VERIFIED

```
Trades:         23
Win Rate:       43.5%
Sharpe (M3):    0.86           [Manus: 0.91]  close
Profit Factor:  1.56
Max Drawdown:   4.1%
```

Assumptions A1-A4 still pending web Claude confirmation.

### S8: Gold Donchian 55/20 — VERIFIED (5-year OANDA)

```
Trades:         16   Win Rate: 56.2%   PF: 3.989   Max DD: 0.9%
```
