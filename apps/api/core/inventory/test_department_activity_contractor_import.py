"""TDD: department activity import resolves پیمانکار to stakeholders (027 US1)."""

import io

import pytest
from openpyxl import Workbook

from inventory.department_activity_io import import_activities_from_xlsx
from inventory.models import Department, DepartmentActivityRecord
from projects.models import Stakeholder
from projects.tests.contractor_select_helpers import make_active_contractor


def _xlsx(rows):
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.django_db
def test_import_resolves_exact_contractor_name(project, user):
    make_active_contractor(project, user, 'Con B')
    rows = [
        ('date', 'location', 'activity_description', 'contractor', 'description'),
        ('2024-04-01', 'Gate', 'Patrol', 'Con B', 'ok'),
    ]
    created, errors = import_activities_from_xlsx(
        project, Department.SECURITY, _xlsx(rows)
    )
    assert errors == []
    assert created == 1
    row = DepartmentActivityRecord.objects.get(project=project, date='2024-04-01')
    assert row.contractor == 'Con B'
    assert row.contractor_ref_id is not None


@pytest.mark.django_db
def test_import_unknown_contractor_fails_without_create(project, user):
    before = DepartmentActivityRecord.objects.filter(project=project).count()
    stake_before = Stakeholder.objects.filter(project=project).count()
    rows = [
        ('date', 'location', 'activity_description', 'contractor', 'description'),
        ('2024-04-02', 'Gate', 'Patrol', 'Unknown Co', 'ok'),
    ]
    created, errors = import_activities_from_xlsx(
        project, Department.SECURITY, _xlsx(rows)
    )
    assert created == 0
    assert len(errors) == 1
    assert 'contractor' in errors[0]['errors']
    assert DepartmentActivityRecord.objects.filter(project=project).count() == before
    assert Stakeholder.objects.filter(project=project).count() == stake_before
