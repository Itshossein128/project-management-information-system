#!/usr/bin/env python
"""
Lightweight concurrent load smoke for Sprint 13 hot paths.

Usage (from apps/api/core, with API running and a JWT):

  ACCESS_TOKEN=... PROJECT_ID=... python ../../scripts/load_smoke_kpis.py

Hits /kpis/, /alerts/active/, /gantt/ with N concurrent workers.
"""

from __future__ import annotations

import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.environ.get('API_BASE', 'http://127.0.0.1:8000/api/v1')
TOKEN = os.environ.get('ACCESS_TOKEN', '')
PROJECT_ID = os.environ.get('PROJECT_ID', '')
WORKERS = int(os.environ.get('LOAD_WORKERS', '8'))
ROUNDS = int(os.environ.get('LOAD_ROUNDS', '3'))

PATHS = [
    'kpis/',
    'alerts/active/',
    'gantt/',
]


def fetch(path: str) -> tuple[str, int, float]:
    url = f'{BASE}/projects/{PROJECT_ID}/{path}'
    req = urllib.request.Request(
        url,
        headers={'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/json'},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
    elapsed = (time.perf_counter() - start) * 1000
    return path, status, elapsed


def main() -> int:
    if not TOKEN or not PROJECT_ID:
        print('Set ACCESS_TOKEN and PROJECT_ID env vars', file=sys.stderr)
        return 2

    jobs = []
    for _ in range(ROUNDS):
        for path in PATHS:
            jobs.append(path)

    results: dict[str, list[float]] = {p: [] for p in PATHS}
    failures = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fetch, p) for p in jobs]
        for fut in as_completed(futures):
            path, status, ms = fut.result()
            results[path].append(ms)
            if status >= 400:
                failures += 1
                print(f'FAIL {path} status={status} {ms:.0f}ms')

    print(f'workers={WORKERS} rounds={ROUNDS} failures={failures}')
    for path, samples in results.items():
        if not samples:
            continue
        print(
            f'{path:20s} n={len(samples)} '
            f'p50={statistics.median(samples):.0f}ms '
            f'mean={statistics.mean(samples):.0f}ms '
            f'max={max(samples):.0f}ms'
        )
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
