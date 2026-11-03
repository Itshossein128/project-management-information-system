#!/usr/bin/env python3
"""Verify client reference fixtures under real-data/ are present (R.0.03).

Does not import MPP/XLSX into the database — that belongs to A.7 / A.1.
This script only asserts the delivery-plan fixtures exist and are non-empty
so the isolated test environment can load them later.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Keep in sync with permissions.test_accounts.REFERENCE_FIXTURES (and R.0.01).
REFERENCE_FIXTURES = (
    ('plan.mpp', ROOT / 'real-data' / 'plan.mpp'),
    (
        'shiraz_daily_report',
        ROOT / 'real-data' / 'گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز.xlsx',
    ),
)


def main() -> int:
    failed = 0
    for label, path in REFERENCE_FIXTURES:
        if path.is_file() and path.stat().st_size > 0:
            print(f'OK  {label}: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)')
        else:
            print(f'FAIL {label}: missing or empty → {path}', file=sys.stderr)
            failed += 1
    if failed:
        print(f'{failed} fixture(s) missing.', file=sys.stderr)
        return 1
    print('All reference fixtures present.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
