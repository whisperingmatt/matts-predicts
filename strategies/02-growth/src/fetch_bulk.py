"""Setup — pull Sharadar bulk files (Full History) into data/raw/.

data/ does not persist between Claude Code cloud sessions (decisions.md,
2026-09-17 ruling). Run this at the start of any session that needs data,
before src/ingest.py:

    python -m src.fetch_bulk              # every table in config.BULK_TABLES
    python -m src.fetch_bulk stocks sp500 # a subset

For each table it asks api.sharadar.com for the bulk file status
(status=True), compares the Full History size with data/raw/<table>.csv.zip,
and downloads only when the local file is missing or a different size, so
re-running is cheap. The API answers years=full with a 302 to
static-sharadar.nyc3.digitaloceanspaces.com and requests follows it.
Downloads go to a .part file and are renamed on completion.

The key is read from the environment (SHARADAR_API_KEY, fallback
NASDAQ_DATA_LINK_API_KEY), never printed, and redacted from error text.

Exit code 0 only if every requested table is present at the expected size.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

from src.config import API_KEY_ENV, API_KEY_ENV_FALLBACK, BULK_TABLES, RAW_DIR, SHARADAR_API_BASE

CHUNK = 1 << 20  # 1 MiB


def get_key() -> str:
    key = os.environ.get(API_KEY_ENV) or os.environ.get(API_KEY_ENV_FALLBACK)
    if not key:
        raise SystemExit(f"FAIL: neither {API_KEY_ENV} nor {API_KEY_ENV_FALLBACK} is set.")
    return key


def redact(text: str, key: str) -> str:
    return text.replace(key, "<api_key>")


def full_history_status(table: str, key: str) -> dict:
    resp = requests.get(f"{SHARADAR_API_BASE}/{table}",
                        params={"api_key": key, "status": "True"}, timeout=60)
    resp.raise_for_status()
    files = resp.json().get("files", [])
    full = [f for f in files if f.get("history") == "full"]
    if not full:
        raise RuntimeError(f"no Full History file listed for {table}: {files}")
    return full[0]


def download(table: str, key: str, dest: Path) -> int:
    part = dest.with_name(dest.name + ".part")
    written = 0
    with requests.get(f"{SHARADAR_API_BASE}/{table}",
                      params={"api_key": key, "years": "full"},
                      stream=True, allow_redirects=True, timeout=(30, 600)) as resp:
        resp.raise_for_status()
        with open(part, "wb") as fh:
            for chunk in resp.iter_content(CHUNK):
                fh.write(chunk)
                written += len(chunk)
    part.replace(dest)
    return written


def main(argv: list[str]) -> int:
    tables = argv or BULK_TABLES
    unknown = [t for t in tables if t not in BULK_TABLES]
    if unknown:
        print(f"FAIL: unknown table(s) {unknown}; choose from {BULK_TABLES}")
        return 1
    key = get_key()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    all_ok = True
    total = 0
    for table in tables:
        dest = RAW_DIR / f"{table}.csv.zip"
        try:
            info = full_history_status(table, key)
            expected = int(info["size"])
            label = f"{info['name']} {info['sizeLabel']} modified {info['modified'][:10]}"
            if dest.exists() and dest.stat().st_size == expected:
                print(f"OK   {table}: present, {label}")
                total += expected
                continue
            print(f"GET  {table}: {label} ...", flush=True)
            got = download(table, key, dest)
            if got != expected:
                print(f"FAIL {table}: downloaded {got} bytes, status said {expected}")
                all_ok = False
                continue
            print(f"OK   {table}: downloaded {got} bytes")
            total += got
        except Exception as exc:  # noqa: BLE001 — report every failure mode verbatim
            print(f"FAIL {table}: {type(exc).__name__}: {redact(str(exc), key)}")
            all_ok = False
    print(f"RESULT: {'PASS' if all_ok else 'FAIL'} — {total / 1e6:.0f} MB present in {RAW_DIR}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
