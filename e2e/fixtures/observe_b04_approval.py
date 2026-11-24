"""Bracket approval commit visibility using read-only PostgreSQL queries."""
import json
import os
from sys import argv
from time import monotonic, sleep

import psycopg


with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True, connect_timeout=3) as db:
    deadline = monotonic() + 15
    lower_bound = None
    while monotonic() < deadline:
        status, started, observed = db.execute(
            """
            SELECT status,
                   EXTRACT(EPOCH FROM statement_timestamp()) * 1000,
                   EXTRACT(EPOCH FROM clock_timestamp()) * 1000
            FROM daily_reports
            WHERE id = %s AND project_id = %s
            """,
            (argv[1], argv[2]),
        ).fetchone()
        if status == 'approved':
            assert lower_bound is not None, 'Timing fixture was already approved'
            print(json.dumps({
                'commit_lower_ms': lower_bound,
                'commit_upper_ms': float(observed),
            }), flush=True)
            break
        if lower_bound is None:
            print('ready', flush=True)
        lower_bound = float(started)
        sleep(0.005)
    else:
        raise RuntimeError('Approval did not become visible in PostgreSQL')
