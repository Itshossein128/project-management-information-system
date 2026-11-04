"""Fail-closed regression tests independent of the live environment."""
from io import BytesIO
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock
import urllib.error

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_smoke_test as runner


def response(body, status=200):
    result = MagicMock()
    result.__enter__.return_value = SimpleNamespace(status=status, read=lambda: json.dumps(body).encode())
    return result


def test_http_200_is_parsed_and_token_is_attached(monkeypatch):
    urlopen = MagicMock(return_value=response({'status': 'ok'}))
    monkeypatch.setattr(runner.urllib.request, 'urlopen', urlopen)
    assert runner.Smoke('http://localhost:8001').request('/api/health/', token='fixture') == {'status': 'ok'}
    req = urlopen.call_args.args[0]
    assert req.get_header('Authorization') == 'Bearer fixture'


@pytest.mark.parametrize('status', [401, 403, 404, 429, 500, 503])
def test_http_errors_cannot_turn_into_success_or_leak_response(monkeypatch, status):
    error = urllib.error.HTTPError('http://localhost/path', status, 'failed', {}, BytesIO(b'sensitive'))
    monkeypatch.setattr(runner.urllib.request, 'urlopen', MagicMock(side_effect=error))
    with pytest.raises(RuntimeError, match=f'got {status}') as exc:
        runner.Smoke('http://localhost').request('/path')
    assert 'sensitive' not in str(exc.value)


def test_expected_scope_denial_is_checked(monkeypatch):
    monkeypatch.setattr(runner.urllib.request, 'urlopen', MagicMock(return_value=response({}, 200)))
    with pytest.raises(RuntimeError, match='expected HTTP 403, got 200'):
        runner.Smoke('http://localhost').request('/path', expected=403)


@pytest.mark.parametrize('body', [
    {'summary': {'created': 0, 'merged': 0, 'skipped': 0, 'conflicts': 0, 'errors': 1}},
    {'summary': {'created': 0, 'merged': 0, 'skipped': 0, 'conflicts': 1, 'errors': 0}},
])
def test_sync_http_200_with_item_errors_is_failure(monkeypatch, body):
    smoke = runner.Smoke('http://localhost')
    smoke.tokens['site_supervisor'] = 'fixture'
    monkeypatch.setattr(smoke, 'request', lambda *args, **kwargs: body)
    with pytest.raises(RuntimeError, match='sync-batch returned errors'):
        smoke.sync(SimpleNamespace(pk='project'))


@pytest.mark.parametrize('body', [{}, {'results': []}, {'results': 'invalid'}])
def test_empty_or_invalid_progress_fails(monkeypatch, body):
    smoke = runner.Smoke('http://localhost')
    smoke.tokens['project_controls'] = 'fixture'
    monkeypatch.setattr(smoke, 'request', lambda *args, **kwargs: body)
    with pytest.raises(RuntimeError, match='missing S-curve'):
        smoke.progress(SimpleNamespace(pk='project'))


def test_incomplete_cost_summary_fails(monkeypatch):
    smoke = runner.Smoke('http://localhost')
    smoke.tokens['finance_manager'] = 'fixture'
    monkeypatch.setattr(smoke, 'request', lambda *args, **kwargs: {})
    with pytest.raises(RuntimeError, match='cost totals'):
        smoke.costs(SimpleNamespace(pk='project'))


def test_nonempty_but_incorrect_progress_fails(monkeypatch):
    smoke = runner.Smoke('http://localhost')
    smoke.tokens['project_controls'] = 'fixture'
    monkeypatch.setattr(smoke, 'request', lambda *args, **kwargs: {'results': [{
        'planned_progress': 0, 'actual_progress': 0, 'variance': 0,
    }]})
    with pytest.raises(RuntimeError, match='differs from seeded'):
        smoke.progress(SimpleNamespace(pk='project'))


def test_known_cost_aggregation_passes(monkeypatch):
    smoke = runner.Smoke('http://localhost')
    smoke.tokens['finance_manager'] = 'fixture'
    monkeypatch.setattr(smoke, 'request', lambda *args, **kwargs: {
        'total_budget': 1000, 'total_actual': 250, 'total_committed': 0,
        'budget_consumption_pct': 25, 'currency': 'IRR',
    })
    smoke.costs(SimpleNamespace(pk='project'))


def test_failed_check_is_counted_and_no_100_percent_claim(capsys):
    smoke = runner.Smoke('http://localhost')
    smoke.check('healthy', lambda: None)
    smoke.check('broken', lambda: runner.require(False, 'expected failure'))
    assert smoke.summary() == 1
    output = capsys.readouterr().out
    assert 'SMOKE 1/2 passed; 1 failed' in output
    assert '100% pass' not in output


def test_empty_run_cannot_pass():
    assert runner.Smoke('http://localhost').summary() == 1
