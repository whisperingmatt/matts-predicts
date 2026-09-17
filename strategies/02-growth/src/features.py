"""S3 — Features per spec section 5 at lags 0, 3, 6, 12 months.
Point-in-time on SF1 datekey (D2). Nulls where data insufficient, never filled.
H12 short_fuel is UNAVAILABLE (no Sharadar short-interest field; decisions.md 2026-09-17).
Output: data/processed/features.parquet, one row per (ticker, month_end, lag).

Not yet built. Write tests/test_point_in_time.py before computing any feature
(spec section 10).
"""


def main() -> None:
    raise NotImplementedError("S3 — see BACKLOG.md")


if __name__ == "__main__":
    main()
