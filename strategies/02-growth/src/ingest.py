"""S2 — convert Sharadar bulk files to parquet. Spec sections 3, 10.

Input:  data/raw/<table>.csv.zip  (Full History, from src/fetch_bulk.py)
Output: data/raw/<table>.parquet  plus data/raw/ingest_manifest.json

    python -m src.ingest               # every table in config.BULK_TABLES
    python -m src.ingest stocks        # a subset
    python -m src.ingest --raw-dir X   # another directory (tests)

Each zip holds one CSV. It is extracted next to the zip, streamed by duckdb
into a zstd parquet file with types sniffed over the whole file (so a late
non-numeric value cannot mistype a column), and the CSV is deleted. Nothing
is held in memory (spec section 10). Column names are the direct-API names
(decisions.md 2026-09-17 mapping); nothing is renamed or filtered here.

The manifest records rows, columns, and min/max of the table's date column
for every converted table, so a wrap can cite them without re-scanning.
"""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from src.config import BULK_TABLES, RAW_DIR

# The column that bounds each table's history, for the manifest only.
DATE_COLUMN = {
    "tickers": "lastpricedate", "fundamentals": "date", "stocks": "date",
    "daily": "date", "insiders": "date", "holdings": "date", "sp500": "date",
    "funds": "date",
}


def extract_csv(zip_path: Path, csv_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.namelist() if m.lower().endswith(".csv")]
        if len(members) != 1:
            raise RuntimeError(f"{zip_path.name}: expected one CSV member, found {members}")
        with zf.open(members[0]) as src, open(csv_path, "wb") as dst:
            while chunk := src.read(1 << 24):
                dst.write(chunk)


def convert(table: str, raw_dir: Path, con: duckdb.DuckDBPyConnection) -> dict:
    zip_path = raw_dir / f"{table}.csv.zip"
    csv_path = raw_dir / f"{table}.csv"
    parquet_path = raw_dir / f"{table}.parquet"
    if not zip_path.exists():
        raise FileNotFoundError(f"{zip_path} missing — run python -m src.fetch_bulk {table}")
    extract_csv(zip_path, csv_path)
    try:
        con.execute(f"""
            COPY (SELECT * FROM read_csv('{csv_path.as_posix()}', header=true,
                                         sample_size=-1, dateformat='%Y-%m-%d'))
            TO '{parquet_path.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """)
    finally:
        csv_path.unlink(missing_ok=True)
    date_col = DATE_COLUMN[table]
    rows, dmin, dmax = con.execute(f"""
        SELECT count(*), min({date_col}), max({date_col})
        FROM read_parquet('{parquet_path.as_posix()}')
    """).fetchone()
    cols = [r[0] for r in con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{parquet_path.as_posix()}')").fetchall()]
    return {
        "table": table, "rows": rows, "columns": cols, "date_column": date_col,
        "date_min": str(dmin), "date_max": str(dmax),
        "zip_bytes": zip_path.stat().st_size, "parquet_bytes": parquet_path.stat().st_size,
        "converted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main(argv: list[str]) -> int:
    raw_dir = RAW_DIR
    if "--raw-dir" in argv:
        i = argv.index("--raw-dir")
        raw_dir = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    tables = argv or BULK_TABLES
    unknown = [t for t in tables if t not in BULK_TABLES]
    if unknown:
        print(f"FAIL: unknown table(s) {unknown}; choose from {BULK_TABLES}")
        return 1
    manifest_path = raw_dir / "ingest_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    con = duckdb.connect()
    con.execute("SET preserve_insertion_order = false")  # lower memory on big CSVs
    all_ok = True
    for table in tables:
        try:
            info = convert(table, raw_dir, con)
        except Exception as exc:  # noqa: BLE001 — report every failure mode verbatim
            print(f"FAIL {table}: {type(exc).__name__}: {exc}")
            all_ok = False
            continue
        manifest[table] = info
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"OK   {table}: {info['rows']:,} rows, {len(info['columns'])} columns, "
              f"{info['date_column']} {info['date_min']}..{info['date_max']}, "
              f"parquet {info['parquet_bytes'] / 1e6:.0f} MB")
    print(f"RESULT: {'PASS' if all_ok else 'FAIL'} — manifest at {manifest_path}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
