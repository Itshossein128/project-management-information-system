"""Acceptance reports cannot promote skipped/eager/empty evidence to success."""
import json
from unittest.mock import Mock

import pytest
from django.core.management.base import CommandError
from schedule.management.commands.verify_import_runtime import Command, _MATRIX_GROUPS


def _command(monkeypatch, eager=False, observed=True):
    cmd=Command()
    monkeypatch.setattr(cmd,'_preflight',lambda prefix:{'status':'ready','eager':eager,'not_run':[]})
    monkeypatch.setattr(cmd,'_matrix',lambda *args:{group:'pass' for group in _MATRIX_GROUPS})
    if observed:
        cmd._scenario_evidence={group:{'status':'pass','observed':{'fixture':'example'}} for group in _MATRIX_GROUPS}
    return cmd


def test_eager_report_cannot_claim_real_worker_acceptance(monkeypatch,tmp_path):
    cmd=_command(monkeypatch,eager=True)
    target=tmp_path/'report.json'
    with pytest.raises(CommandError):
        cmd.handle(run_matrix=True,project_prefix='A7P5-',reference='',output=str(target))
    assert json.loads(target.read_text())['status']=='invalid_evidence'


def test_all_pass_labels_without_observations_are_incomplete(monkeypatch,tmp_path):
    cmd=_command(monkeypatch,observed=False)
    target=tmp_path/'report.json'
    with pytest.raises(CommandError):
        cmd.handle(run_matrix=True,project_prefix='A7P5-',reference='',output=str(target))
    assert json.loads(target.read_text())['status']=='incomplete'


def test_blocked_preflight_never_mutates_the_acceptance_database(monkeypatch):
    cmd=Command();attempt=Mock(side_effect=AssertionError('must not create fixtures'))
    monkeypatch.setattr(cmd,'_attempt_isolated_matrix',attempt)
    report=cmd._matrix({'status':'blocked','database':'a7p5_import','eager':False},'A7P5-','')
    assert all(report[group]=='not-run' for group in _MATRIX_GROUPS)
    attempt.assert_not_called()
