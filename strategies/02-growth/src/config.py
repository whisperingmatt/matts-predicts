"""Constants fixed by the locked spec. Do not change without a decisions.md entry."""
from pathlib import Path

STRATEGY_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = STRATEGY_DIR / "data" / "raw"
PROCESSED_DIR = STRATEGY_DIR / "data" / "processed"
REPORTS_DIR = STRATEGY_DIR / "reports"

# Sharadar direct API (api.sharadar.com), not Nasdaq Data Link. See decisions.md
# 2026-09-17 "D6 superseded". The fallback variable name is the one S1 chose
# before the subscription type was known; both are read, neither is ever printed.
SHARADAR_API_BASE = "https://api.sharadar.com/v1.0/data"
API_KEY_ENV = "SHARADAR_API_KEY"
API_KEY_ENV_FALLBACK = "NASDAQ_DATA_LINK_API_KEY"

# D6 (superseded) — direct-API table names. NDL aliases: fundamentals=SF1,
# stocks=SEP, daily=DAILY, tickers=TICKERS, insiders=SF2, holdings=SF3,
# sp500=SP500. Verified against sharadar.com/docs 2026-09-17.
TABLES = ["tickers", "fundamentals", "stocks", "daily", "insiders", "holdings", "sp500"]

# Bulk files pulled by src/fetch_bulk.py (Full History). funds is added for
# S3 regime tags (SPY) and H16 (sector SPDRs); it is not an S1 check table.
BULK_TABLES = [*TABLES, "funds"]

# D4 — windows
BUILD_START, BUILD_END = "2006-01-31", "2019-12-31"
HOLDOUT_START, HOLDOUT_END = "2020-01-31", "2026-06-30"

# D3 — universe floors
MIN_PRICE = 5.0
MIN_AVG_DOLLAR_VOLUME_20D = 1_000_000

# D1 — launch thresholds (forward 24-month return)
LAUNCH_THRESHOLDS = {"launch_200": 2.0, "launch_300": 3.0, "launch_500": 5.0}

# D8, D9
MIN_EVENTS_PER_CELL = 100
MAX_COMBINATION_SIZE = 3

# Section 5 — lags in months
LAGS = [0, 3, 6, 12]
