"""Alert engine tests."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from alerts.models import AlertLog, AlertRule
from alerts.services.alert_engine import check_and_fire_for_project, fire_alert, fire_alert_for_type
from notifications.models import Notification


@pytest.fixture
def finance_manager_role(db):
    from master_data.models import Role

    return Role.objects.get(role_name='finance_manager')


@pytest.fixture
def alert_rule(db, project):
    return AlertRule.objects.create(
        project=None,
        alert_type='budget_overrun',
        name='تجاوز بودجه',
        threshold=Decimal('90'),
        notify_roles='project_manager',
        cooldown_hours=24,
        is_active=True,
    )


def test_fire_alert_creates_log(db, project, alert_rule, user):
    log = fire_alert(
        alert_rule.id,
        'wbs:test',
        'Test message',
        project.id,
    )
    assert log is not None
    assert AlertLog.objects.filter(project=project).count() == 1


def test_fire_alert_respects_cooldown(db, project, alert_rule):
    fire_alert(alert_rule.id, 'wbs:test', 'First', project.id)
    second = fire_alert(alert_rule.id, 'wbs:test', 'Second', project.id)
    assert second is None
    assert AlertLog.objects.filter(trigger_reference='wbs:test').count() == 1


def test_check_and_fire_for_project_runs(db, project):
    AlertRule.objects.create(
        project=None,
        alert_type='baseline_not_set',
        name='خط مبنا',
        threshold=0,
        notify_roles='project_manager',
        is_active=True,
    )
    check_and_fire_for_project(project.id)
    assert AlertLog.objects.filter(project=project).exists()


def test_fire_alert_for_type_uses_seeded_rule(db, project, user, finance_manager_role):
    from master_data.models import ProjectMember, ProjectMemberRole

    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)

    log = fire_alert_for_type(
        project.id,
        'ipc_payment_overdue',
        'ipc:test-1',
        'صدور موقت شماره ۱ تأخیر دارد',
    )
    assert log is not None
    assert AlertLog.objects.filter(project=project, trigger_reference='ipc:test-1').exists()
    assert Notification.objects.filter(project=project).exists()


def test_fire_alert_for_type_returns_none_without_rule(db, project):
    AlertRule.objects.filter(alert_type='ipc_payment_overdue').delete()
    log = fire_alert_for_type(project.id, 'ipc_payment_overdue', 'ipc:x', 'msg')
    assert log is None
