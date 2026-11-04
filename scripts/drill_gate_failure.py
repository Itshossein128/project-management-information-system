#!/usr/bin/env python3
"""Exercise the real gate CLI against a loopback GitHub API fixture; never deploy.

The harness exits 0 when the expected gate exit code and message are observed.
The child gate exits 1 for a blocked release and 0 for a healthy release.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
SHA = 'a' * 40
SCENARIOS = ('workflow-failure', 'api-failure', 'web-failure', 'missing-api', 'cancelled', 'success')


@contextmanager
def fixture_api(scenario):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            if self.path == f'/repos/rehearsal/fixture/actions/runs?head_sha={SHA}':
                conclusion = {'workflow-failure': 'failure', 'cancelled': 'cancelled'}.get(scenario, 'success')
                body = {'workflow_runs': [{'id': 1, 'name': 'CI', 'head_sha': SHA,
                         'status': 'completed', 'conclusion': conclusion}]}
            elif self.path == '/repos/rehearsal/fixture/actions/runs/1/jobs':
                body = {'jobs': [{'name': name, 'status': 'completed',
                         'conclusion': 'failure' if scenario == f'{name}-failure' else 'success'}
                         for name in ('web', 'api') if not (name == 'api' and scenario == 'missing-api')]}
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def run_drill(scenario):
    env = os.environ.copy()
    for key in ('GITHUB_TOKEN', 'GH_TOKEN'):
        env.pop(key, None)
    # Ensure the fixture stays local even on machines configured with a proxy.
    env['NO_PROXY'] = env['no_proxy'] = '127.0.0.1,localhost'
    with fixture_api(scenario) as (url, requests):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/verify_ci_gate.py'),
             '--repo', 'rehearsal/fixture', '--sha', SHA, '--api-url', url,
             '--timeout', '2', '--grace-period', '0', '--poll-interval', '1'],
            env=env, capture_output=True, text=True, timeout=10,
        )
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    expected = 0 if scenario == 'success' else 1
    marker = 'SUCCESS: [CI-GATE]' if expected == 0 else '[ERROR] [CI-GATE]'
    if result.returncode != expected or marker not in result.stdout:
        raise RuntimeError(f'{scenario}: expected gate exit={expected} and {marker!r}; got exit={result.returncode}')
    if expected == 1 and 'Deployment blocked!' not in result.stdout:
        raise RuntimeError(f'{scenario}: missing deployment-blocking message')
    # One runs request plus, at most, one jobs request proves no retry/poll on failure.
    expected_requests = 1 if scenario in ('workflow-failure', 'cancelled') else 2
    if len(requests) != expected_requests:
        raise RuntimeError(f'{scenario}: unexpected polling: {requests}')
    print(f'PASS drill={scenario} gate_exit={result.returncode} requests={len(requests)}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=SCENARIOS, default='api-failure')
    args = parser.parse_args()
    try:
        run_drill(args.scenario)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
