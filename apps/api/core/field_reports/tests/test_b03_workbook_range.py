from datetime import date, timedelta
from io import BytesIO

import openpyxl
import pytest
from rest_framework.test import APIClient

from common.jalali import gregorian_to_jalali
from field_reports.models import DailyReport, ReportStatus
from field_reports.services import approve_report
from field_reports.services.correction_service import cancel_correction, open_correction


pytestmark = pytest.mark.django_db
FIRST = date(2027, 5, 22)


def report_for(project, user, day=FIRST, **overrides):
    return DailyReport.all_objects.create(
        project=project, created_by=user, report_date=day, **{'status': ReportStatus.APPROVED, **overrides},
    )


def endpoint(project):
    return f'/api/v1/projects/{project.pk}/daily-reports/excel/'


def requested(client, project, start=FIRST, end=FIRST, **params):
    return client.get(endpoint(project), {'date_from': str(start), 'date_to': str(end), **params})


def sheet_names(response):
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return openpyxl.load_workbook(BytesIO(response.content)).sheetnames


def test_b03_range_uses_inclusive_default_limit_and_override(auth_client, project, user, settings):
    report_for(project, user)
    last = FIRST + timedelta(days=30)
    report_for(project, user, last)
    assert sheet_names(requested(auth_client, project, end=last)) == [
        '1406-03-01', gregorian_to_jalali(last).replace('/', '-'),
    ]
    too_long = requested(auth_client, project, end=last + timedelta(days=1))
    assert too_long.status_code == 400 and too_long.data['error']['code'] == 'export_date_range_too_large'
    settings.DAILY_REPORT_EXCEL_RANGE_MAX_DAYS = 32
    assert sheet_names(requested(auth_client, project, end=last + timedelta(days=1)))[0] == '1406-03-01'
    assert sheet_names(requested(auth_client, project, '1406/03/01', '1406/03/01')) == ['1406-03-01']


def test_b03_range_errors_and_authorization(auth_client, project, user, other_user):
    api_client = APIClient()
    api_client.force_authenticate(other_user)
    assert requested(api_client, project).status_code == 403
    for response in (
        auth_client.get(endpoint(project)),
        requested(auth_client, project, start='not a date'),
        requested(auth_client, project, start='1406/13/01'),
        requested(auth_client, project, start=FIRST + timedelta(days=1)),
    ):
        assert response.status_code == 400
        assert response.data['error']['code'] == 'invalid_export_date_range'
    empty = requested(auth_client, project)
    assert empty.status_code == 400 and empty.data['error']['code'] == 'no_reports_in_export_range'
    report_for(project, user, shift='day')
    report_for(project, user, shift='night')
    conflict = requested(auth_client, project)
    assert conflict.status_code == 409 and conflict.data['error']['code'] == 'ambiguous_legacy_report_date'


def test_b03_range_selection_across_corrections_is_read_only(auth_client, project, user, other_user):
    source = report_for(project, user, work_front='Prior approval')
    report_for(project, user, FIRST + timedelta(days=1), is_deleted=True)
    report_for(project, user, FIRST + timedelta(days=2), is_current=False)
    report_for(project, user, FIRST + timedelta(days=3), status=ReportStatus.DRAFT)
    later = FIRST + timedelta(days=4)
    report_for(project, user, later)

    correction = open_correction(source_report=source, user=user, reason='B03 range correction check')
    before = list(DailyReport.all_objects.order_by('pk').values())
    source_filename = f'{endpoint(project).removesuffix("excel/")}{source.pk}/excel/'
    assert auth_client.get(source_filename).status_code == 200
    assert sheet_names(requested(auth_client, project, end=later, is_current='false', status='draft')) == ['1406-03-05']
    assert list(DailyReport.all_objects.order_by('pk').values()) == before

    cancel_correction(correction=correction, user=user)
    assert sheet_names(requested(auth_client, project, end=later)) == ['1406-03-01', '1406-03-05']

    source.refresh_from_db()
    correction = open_correction(source_report=source, user=user, reason='B03 replacement approval check')
    approve_report(correction.result_report, other_user)
    assert sheet_names(requested(auth_client, project, end=later)) == ['1406-03-01', '1406-03-05']
