"""Sprint 9 alert engine: sync conflict checker."""

import pytest

from alerts.models import AlertLog, AlertRule
from alerts.services.alert_engine import _check_sync_conflict_unresolved
from field_reports.models import SyncConflictLog


@pytest.mark.django_db
def test_sync_conflict_checker_fires(project):
    rule = AlertRule.objects.create(
        project=project,
        alert_type='sync_conflict_unresolved',
        name='Sync conflicts',
        is_active=True,
        cooldown_hours=1,
        notify_roles='project_manager',
    )
    SyncConflictLog.objects.create(
        project=project,
        local_id='offline-1',
        conflict_reason='تعارض تست',
    )
    _check_sync_conflict_unresolved(rule, project.id)
    assert AlertLog.objects.filter(rule=rule, project=project).exists()
