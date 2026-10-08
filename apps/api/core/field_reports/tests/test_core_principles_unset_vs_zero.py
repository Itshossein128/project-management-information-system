"""US4: unset vs zero for daily report activity quantity."""
from decimal import Decimal

import pytest

from common.unset import coerce_optional_decimal
from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    ReportShift,
    ReportStatus,
)
from field_reports.serializers import DailyReportActivitySerializer


@pytest.mark.django_db
def test_quantity_null_vs_zero(project, user):
    report = DailyReport.objects.create(
        project=project,
        report_date='2024-05-01',
        shift=ReportShift.DAY,
        status=ReportStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    unset_row = DailyReportActivity.objects.create(
        report=report,
        activity_description='unset qty',
        shift=ActivityRowShift.SHIFT_1,
        quantity=None,
        quantity_measured=False,
    )
    zero_row = DailyReportActivity.objects.create(
        report=report,
        activity_description='zero qty',
        shift=ActivityRowShift.SHIFT_1,
        quantity=Decimal('0'),
        quantity_measured=True,
    )
    assert unset_row.quantity is None
    assert zero_row.quantity == Decimal('0')
    assert coerce_optional_decimal(None) is None
    assert coerce_optional_decimal(0) == Decimal('0')

    ser_unset = DailyReportActivitySerializer(unset_row).data
    ser_zero = DailyReportActivitySerializer(zero_row).data
    assert ser_unset['quantity'] is None
    assert Decimal(ser_zero['quantity']) == Decimal('0')


@pytest.mark.django_db
def test_approval_status_distinct(project, user):
    draft = DailyReport.objects.create(
        project=project,
        report_date='2024-05-02',
        shift=ReportShift.DAY,
        status=ReportStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    approved = DailyReport.objects.create(
        project=project,
        report_date='2024-05-03',
        shift=ReportShift.DAY,
        status=ReportStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    assert draft.status != approved.status
    assert draft.status == ReportStatus.DRAFT
    assert approved.status == ReportStatus.APPROVED
