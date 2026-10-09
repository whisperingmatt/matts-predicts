# STRATEGY_SPEC.md — Gold Trend Component (Component #1 of multi-component FTP system) v3.0

**Purpose:** Pass Funded Trading Plus Experienced ($100k account, 10% target, 6% trailing max DD, 4% daily DD).
**Style:** End-of-day swing. D1 Donchian 55/20 breakout on XAU/USD. Positions run up to 90 days.
**Operator profile:** Solo, working day job, Sydney AEDT/AEST timezone.

---

## DESIGN PRINCIPLES (non-negotiable)

1. **Fixed reward-to-risk of at least 1:2 on every trade.** Hard rule. If 2R target is not reachable from entry given stop placement, skip the trade.
2. **Risk per trade = 0.4% of current account equity.** Never larger. Halved automatically if account DD reaches 4%.
3. **Trade only with the daily trend.** No counter-trend trades. No "catch the bottom" plays.
4. **All orders entered as pending limits at NY close.** No discretionary intraday entries. The operator's only daily job is to review the alert and let the limit orders run.
5. **All trades have stop AND target placed at entry.** No exceptions. No "I'll set it later."
6. **Circuit breakers are mechanical.** If hit, system stops opening trades. No override.

---

## INSTRUMENT UNIVERSE

5 instruments, scanned every session:

- GBP/USD
- EUR/USD
- AUD/USD
- USD/JPY
- XAU/USD (Gold)

Mix chosen for liquidity, low spread, and partial decorrelation (gold often moves opposite to dollar pairs).

---

## TIMEFRAMES

- **Daily (D1):** trend filter, regime detection
- **4-Hour (H4):** entry trigger
- **Indicators used:** EMA20, EMA50, ATR(14), RSI(14), ADX(14)

---

## ENTRY LOGIC

### Long entry (daily uptrend)

All five conditions must be true at NY close:

1. Daily close > Daily EMA20 > Daily EMA50
2. Daily ADX(14) > 20
3. Daily ATR(14) < 2× its own 20-day average (volatility not extreme)
4. Most recent H4 candle closes back above H4 EMA20, AND the previous H4 candle closed below H4 EMA20 (a "reclaim" of the EMA)
5. H4 RSI(14) on the reclaim candle is between 45 and 65 (not oversold-bouncing, not overbought-extending)

If all true, place a **buy limit** at the H4 EMA20 value of the next bar, GTC 24 hours.

### Short entry (daily downtrend)

Mirror of long:

1. Daily close < Daily EMA20 < Daily EMA50
2. Daily ADX(14) > 20
3. Daily ATR(14) < 2× its 20-day average
4. Most recent H4 candle closes back below H4 EMA20, previous H4 candle closed above
5. H4 RSI(14) between 35 and 55

Place a **sell limit** at H4 EMA20 of next bar, GTC 24h.

---

## STOP LOSS

- Stop distance = 1.5 × H4 ATR(14)
- For longs: stop = entry − (1.5 × ATR)
- For shorts: stop = entry + (1.5 × ATR)
- Stop is placed simultaneously with the limit order. If the broker rejects the bracket order, do not enter the trade.

---

## TAKE PROFIT

- Target distance = 2.0 × stop distance (fixed 1:2 R:R)
- For longs: target = entry + (2 × stop distance)
- For shorts: target = entry − (2 × stop distance)

This is the hard rule that flips the math from negative to positive expectancy.

---

## POSITION SIZING

```
risk_amount    = current_equity × 0.004      (0.4% of equity)
stop_distance  = 1.5 × ATR_H4                (in price units)
units          = risk_amount / stop_distance  (in instrument units)
```

For OANDA orders, convert `units` to integer instrument units (e.g. 1000 units of EUR/USD = 0.01 mini lot).

**Edge case — gold (XAU/USD):** stop_distance is in dollars per ounce. Pip value differs. Calculate units carefully.

**Minimum trade size:** if calculated units < broker minimum, skip the trade. Don't round up.

---

## CIRCUIT BREAKERS

These are hard rules. The system stops opening new trades when triggered.

1. **Daily loss circuit breaker:** if today's realised P&L is ≤ −2% of equity, no new entries for the rest of the day. (FTP daily DD is 4%; we halt at half that to keep buffer.)
2. **Account drawdown circuit breaker:** if account equity drops to 4% below the high water mark, risk-per-trade is automatically cut from 0.4% to 0.2% until equity recovers to within 2% of HWM.
3. **Max open positions:** 5 at any time across all instruments.
4. **Max new trades per day:** 3.
5. **Correlation cap:** no more than 2 simultaneous trades on the same USD direction (e.g. long EUR/USD + long GBP/USD + long AUD/USD = blocked at 2).

---

## EXCLUDED CONDITIONS

No new entry orders when any of these are true:

1. Within 30 minutes (before or after) of a high-impact news event for the relevant currency (use Forex Factory or equivalent calendar).
2. Friday after 12:00 EST (avoid weekend gap exposure).
3. First 24h after FOMC, NFP, or central bank rate decisions.
4. Spread on the instrument is > 3× its average.

---

## EXIT LOGIC

Primary exits (mechanical):
- Stop loss hits → trade closes at stop
- Take profit hits → trade closes at target

Time exit (failsafe):
- If position open longer than 90 calendar days, close at market on day 91. Final parameter — validated by iteration C forward-walk test (OOS PF 7.69).

No discretionary exits in v1.0. No "moving to break-even." No trailing stops. We trust the math. v2.0 can layer in trade management once we have 6 months of v1 data.

---

## FTP CONSISTENCY RULE COMPLIANCE

FTP requires no single day to produce more than 35% of total profit on a passing run. The system tracks this:

- After each closed day, log the day's P&L
- Calculate each day's % of cumulative profit
- If any single day would exceed 30%, system warns operator (don't fail at 35%, warn at 30%)
- Operator manually decides whether to skip new entries the next day

This is a manual oversight in v1. Can be automated later.

---

## OUTPUTS

The strategy module must produce, every NY close:

1. **Daily alert JSON** written to `docs/daily_alert.json`:
```json
{
  "timestamp_utc": "2026-05-21T21:00:00Z",
  "account_equity": 97968.30,
  "drawdown_status": "OK",
  "trades_today": [
    {
      "instrument": "GBP_USD",
      "direction": "BUY",
      "entry_limit": 1.34520,
      "stop_loss": 1.33450,
      "take_profit": 1.36660,
      "units": 365,
      "risk_usd": 391.87,
      "reward_usd": 783.74,
      "expires_utc": "2026-05-22T21:00:00Z",
      "reason": "D1 uptrend + ADX 23.4 + H4 EMA20 reclaim, RSI 54.2"
    }
  ],
  "filtered_setups": [
    {"instrument": "EUR_USD", "skipped": "D1 ADX = 17.2 (below 20)"}
  ]
}
```

2. **Equity log** appended to `docs/equity_history.json` daily.
3. **Trade log** appended to `docs/trade_history.json` on every close.

---

## BACKTEST REQUIREMENTS

Before any live trading:

- Backtest period: **3 years** (the most recent 3 full years available from OANDA candles)
- All 5 instruments simultaneously
- Realistic spread: 1.5 pips on majors, 25 pips on gold (or actual OANDA average spread by instrument)
- Realistic slippage: 0.5 pips per side
- Position sizing tracked against equity curve (compounding allowed)
- Starting balance: $100,000

**Required outputs from backtest:**
1. Total trades, wins, losses
2. Win rate overall and per instrument
3. Average win, average loss, expectancy per trade
4. Profit factor
5. Maximum drawdown (% and $)
6. Sharpe-like ratio
7. Monthly P&L table
8. Equity curve chart (PNG saved to docs/)
9. Drawdown curve chart (PNG saved to docs/)
10. Trade distribution histogram
11. Consistency rule check: any month/day exceeding 35% of total profit?

**Pass/fail criteria for live deployment:**
- Profit factor ≥ 1.3
- Max drawdown ≤ 5% (since FTP allows 6%)
- At least 80 trades over the 3 years (statistical significance)
- No single day producing > 35% of total profit (FTP compliance)
- Positive expectancy after all costs

If backtest fails any of these, do NOT go live. Iterate the strategy.

---

## VERSION HISTORY

- **v1.0** — initial spec, 2026-05-20
- **v3.0** — renamed to Gold Trend Component (Component #1); locked 90-day time cap as final parameter following iteration C forward-walk validation (OOS PF 7.69, 2026-05-22)

---

## Component #2 — Pending

Higher-frequency mean reversion system. Research target for next session. Not built.
