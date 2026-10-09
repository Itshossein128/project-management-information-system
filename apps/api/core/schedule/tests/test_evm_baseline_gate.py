"""Baseline validity for EVM (FR-EVM-001)."""

import pytest
from django.utils import timezone

from schedule.services.evm_baseline import resolve_evm_baseline_validity
from schedule.services.evm_service import compute_evm
from schedule.tests.evm_fixtures import create_control_budget, lock_schedule_baseline


@pytest.mark.django_db
class TestEvmBaselineGate:
    def test_unlocked_schedule_warns(self, project, user):
        create_control_budget(project, user)
        result = resolve_evm_baseline_validity(project.id)
        assert 'baseline_not_locked' in result['warnings']
        assert result['validity'] != 'valid'
        assert result['schedule_baseline']['locked'] is False

    def test_locked_and_control_budget_valid(self, project, user):
        lock_schedule_baseline(project, user)
        create_control_budget(project, user)
        result = resolve_evm_baseline_validity(project.id)
        assert result['validity'] == 'valid'
        assert 'baseline_not_locked' not in result['warnings']
        assert result['budget_baseline']['approved'] is True

    def test_kpis_api_includes_baseline_warning(self, project, user, auth_client):
        create_control_budget(project, user)
        url = f'/api/v1/projects/{project.id}/progress/kpis/?force_refresh=1'
        response = auth_client.get(url)
        assert response.status_code == 200
        assert 'baseline_not_locked' in response.data['warnings']
        assert response.data['validity'] != 'valid'

    def test_compute_evm_partial_when_unlocked(self, project, user, activity):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        create_control_budget(project, user)
        evm = compute_evm(project.id, timezone.localdate())
        assert 'baseline_not_locked' in evm['warnings']
        assert evm['validity'] != 'valid'
