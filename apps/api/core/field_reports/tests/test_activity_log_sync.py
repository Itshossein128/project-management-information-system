import pytest
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReport, DailyReportActivity, ReportStatus
from field_reports.services import approve_report
from field_reports.services.activity_log import serialize_activity_log_row, activity_log_queryset
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus


@pytest.fixture
def activity_log_url(project):
    return f'/api/v1/projects/{project.id}/activity-log/'


@pytest.fixture
def filter_options_url(project):
    return f'/api/v1/projects/{project.id}/activity-log/filter-options/'


@pytest.mark.django_db
def test_serialize_activity_log_row_includes_discipline_and_parcel(project, user):
    today = timezone.localdate()
    report = DailyReport.objects.create(
        project=project,
        report_date=today,
        status=ReportStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    act = DailyReportActivity.objects.create(
        report=report,
        activity_description='Installation of conduit',
        shift='shift_1',
        source_discipline='ELECTRICAL',
        parcel='قطعه ۵',
        subcontractor_name='برق‌کاران برتر',
        quantity=120.5,
        unit='m',
        quantity_measured=True,
    )
    data = serialize_activity_log_row(act)
    assert data['source_discipline'] == 'ELECTRICAL'
    assert data['parcel'] == 'قطعه ۵'
    assert data['subcontractor'] == 'برق‌کاران برتر'
    assert data['quantity'] == 120.5


@pytest.mark.django_db
def test_activity_log_queryset_filters_by_discipline_and_parcel(project, user):
    today = timezone.localdate()
    report = DailyReport.objects.create(
        project=project,
        report_date=today,
        status=ReportStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    act1 = DailyReportActivity.objects.create(
        report=report,
        activity_description='Electrical pipe',
        shift='shift_1',
        source_discipline='ELECTRICAL',
        parcel='قطعه ۱',
    )
    act2 = DailyReportActivity.objects.create(
        report=report,
        activity_description='Civil excavation',
        shift='shift_1',
        source_discipline='CIVIL',
        parcel='قطعه ۲',
    )

    # Filter by discipline
    qs_elec = activity_log_queryset(project.id, {'source_discipline': 'ELECTRICAL'})
    assert act1 in list(qs_elec)
    assert act2 not in list(qs_elec)

    # Filter by parcel
    qs_p2 = activity_log_queryset(project.id, {'parcel': 'قطعه ۲'})
    assert act2 in list(qs_p2)
    assert act1 not in list(qs_p2)


@pytest.mark.django_db
def test_activity_log_filter_options_returns_disciplines_and_parcels(auth_client, filter_options_url, project, user):
    today = timezone.localdate()
    report = DailyReport.objects.create(
        project=project,
        report_date=today,
        status=ReportStatus.APPROVED,
        created_by=user,
        updated_by=user,
    )
    DailyReportActivity.objects.create(
        report=report,
        activity_description='Painting',
        shift='shift_1',
        source_discipline='CIVIL',
        parcel='قطعه A',
    )

    response = auth_client.get(filter_options_url)
    assert response.status_code == status.HTTP_200_OK
    assert 'disciplines' in response.data
    assert 'CIVIL' in response.data['disciplines']
    assert 'parcels' in response.data
    assert 'قطعه A' in response.data['parcels']


@pytest.mark.django_db
def test_activity_log_cache_invalidation_on_approve(auth_client, activity_log_url, project, user):
    today = timezone.localdate()
    report = DailyReport.objects.create(
        project=project,
        report_date=today,
        status=ReportStatus.SUBMITTED,
        created_by=user,
        updated_by=user,
    )
    DailyReportActivity.objects.create(
        report=report,
        activity_description='Foundation pour',
        shift='shift_1',
        source_discipline='CIVIL',
        parcel='قطعه B',
    )

    # 1. Warm cache before approval - approved_only defaults to true, so 0 activities returned
    res1 = auth_client.get(activity_log_url)
    assert res1.status_code == status.HTTP_200_OK
    assert res1.data['count'] == 0

    # 2. Approve the report
    approve_report(report, user)

    # 3. Read activity log again - MUST immediately reflect the approved activity without stale cache
    res2 = auth_client.get(activity_log_url)
    assert res2.status_code == status.HTTP_200_OK
    assert res2.data['count'] == 1
    assert res2.data['results'][0]['activity_description'] == 'Foundation pour'
    assert res2.data['results'][0]['source_discipline'] == 'CIVIL'
    assert res2.data['results'][0]['parcel'] == 'قطعه B'
