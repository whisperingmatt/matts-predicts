"""Constants fixed by the locked spec. Do not change without a decisions.md entry."""
from pathlib import Path

STRATEGY_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = STRATEGY_DIR / "data" / "raw"
PROCESSED_DIR = STRATEGY_DIR / "data" / "processed"
REPORTS_DIR = STRATEGY_DIR / "reports"

API_KEY_ENV = "NASDAQ_DATA_LINK_API_KEY"

# D6 — Sharadar tables on Nasdaq Data Link. Verified 2026-09-17 (see decisions.md).
TABLES = ["SF1", "SEP", "DAILY", "TICKERS", "SF2", "SF3", "SP500"]

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
