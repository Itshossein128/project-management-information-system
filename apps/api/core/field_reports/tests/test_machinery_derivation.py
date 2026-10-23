"""Machinery status-grid aggregation tests (feature 033, task T027)."""
from __future__ import annotations

from decimal import Decimal

import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReportDerivedSource, Equipment
from field_reports.services.daily_report_aggregation import (
    compute_aggregation_fingerprint,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import SUMMARY_DATE, make_sub_report
from sub_reports.models import DisciplineSubReportMachinery, SubReportStatus


def add_machinery(sub_report, **overrides):
    values = {
        'row_number': sub_report.machinery_rows.count() + 1,
        'equipment_type': 'excavator',
        'status_total': 1,
        'status_active': 1,
        'status_ready': 0,
        'status_inactive': 0,
        'status_under_repair': 0,
        'operating_hours': Decimal('8.00'),
        'stoppage_hours': Decimal('0.00'),
        'repair_hours': Decimal('0.00'),
        'stoppage_reason_code': '',
    }
    values.update(overrides)
    return DisciplineSubReportMachinery.objects.create(sub_report=sub_report, **values)


def make_machinery_report(project, user, *, version_number=1):
    unit = SpecialtyUnit.MACHINERY if version_number == 1 else SpecialtyUnit.BUILDINGS
    return make_sub_report(
        project,
        user,
        unit=unit,
        status=SubReportStatus.APPROVED,
        version_number=version_number,
    )


@pytest.mark.django_db
def test_five_statuses_are_derived_from_machinery_unit_report(project, user):
    report = make_machinery_report(project, user)
    source = add_machinery(
        report,
        status_total=5,
        status_active=2,
        status_ready=1,
        status_inactive=1,
        status_under_repair=1,
        operating_hours=Decimal('7.5'),
        stoppage_hours=Decimal('1.0'),
        repair_hours=Decimal('2.0'),
        stoppage_reason_code='breakdown',
    )

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    row = summary.machinery_rows.get(equipment_type='excavator')

    assert row.status_total == 5
    assert row.status_active == 2
    assert row.status_ready == 1
    assert row.status_inactive == 1
    assert row.status_under_repair == 1
    assert row.operating_hours == Decimal('7.5')
    assert row.stoppage_hours == Decimal('1.0')
    assert row.repair_hours == Decimal('2.0')
    assert row.stoppage_reason_code == 'breakdown'
    assert row.is_derived is True
    assert DailyReportDerivedSource.objects.filter(
        daily_report=summary,
        derived_kind='machinery',
        derived_row_id=str(row.id),
        source_row_id=str(source.id),
    ).exists()


@pytest.mark.django_db
def test_stable_equipment_identity_is_aggregated_exactly_once(project, user):
    equipment = Equipment.objects.create(
        project=project,
        equipment_code='EX-01',
        equipment_name='Excavator 01',
        equipment_type='excavator',
        created_by=user,
    )
    first = make_machinery_report(project, user, version_number=1)
    second = make_machinery_report(project, user, version_number=2)
    add_machinery(first, equipment_ref=equipment, status_total=1, status_active=1)
    add_machinery(second, equipment_ref=equipment, status_total=1, status_active=1)

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    rows = list(summary.machinery_rows.filter(equipment_ref=equipment))
    assert len(rows) == 1
    assert rows[0].status_total == 1
    assert DailyReportDerivedSource.objects.filter(
        daily_report=summary,
        derived_kind='machinery',
        derived_row_id=str(rows[0].id),
    ).count() == 2


@pytest.mark.django_db
def test_type_only_rows_are_not_identity_deduped(project, user):
    report = make_machinery_report(project, user)
    add_machinery(report, status_total=1, status_active=1)
    add_machinery(report, status_total=1, status_ready=1)

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    rows = list(summary.machinery_rows.filter(
        equipment_type='excavator', equipment_ref__isnull=True,
    ))
    assert len(rows) == 2


@pytest.mark.django_db
def test_item_and_type_rows_preserve_per_type_sum(project, user):
    equipment = Equipment.objects.create(
        project=project,
        equipment_code='EX-01',
        equipment_name='Excavator 01',
        equipment_type='excavator',
        created_by=user,
    )
    report = make_machinery_report(project, user)
    add_machinery(report, equipment_ref=equipment, status_total=1, status_active=1)
    add_machinery(report, status_total=2, status_active=2)

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    rows = summary.machinery_rows.filter(equipment_type='excavator')

    assert sum(row.status_total for row in rows) == 3
    assert sum(row.status_active for row in rows) == 3


@pytest.mark.django_db
def test_machinery_provenance_is_written_for_each_contributing_row(project, user):
    report = make_machinery_report(project, user)
    source = add_machinery(report)
    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    row = summary.machinery_rows.get()
    provenance = DailyReportDerivedSource.objects.get(
        daily_report=summary,
        derived_kind='machinery',
        derived_row_id=str(row.id),
        source_row_id=str(source.id),
    )

    assert provenance.source_report_id_snapshot == report.id
    assert provenance.source_report_version == report.version_number
    assert provenance.source_unit == SpecialtyUnit.MACHINERY
    assert provenance.source_row_kind == 'machinery'


@pytest.mark.django_db
def test_fingerprint_changes_when_machinery_payload_changes(project, user):
    report = make_machinery_report(project, user)
    first = compute_aggregation_fingerprint(None, [report])
    add_machinery(report, status_active=2, status_total=2)
    report.refresh_from_db()
    second = compute_aggregation_fingerprint(None, [report])

    assert first != second
