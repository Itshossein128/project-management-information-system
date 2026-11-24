from datetime import date, datetime, timezone
from subprocess import run
import re

import pytest
from rest_framework.test import APIClient

from common.reporting_units import CANONICAL_SPECIALTY_UNITS
from sub_reports.models import (
    DisciplineSubReport, DisciplineSubReportActivity, SubReportStatus, UnitReportEventType, UnitReportStatusEvent,
)


pytestmark = pytest.mark.django_db


def path(project, unit, report):
    return f'/api/v1/projects/{project.pk}/units/{unit}/daily-reports/{report.pk}/pdf/'


def pdf_text(content, target):
    target.write_bytes(content)
    return run(['pdftotext', '-raw', target, '-'], check=True, capture_output=True, text=True).stdout


def watermark(text):
    return re.search(r'D\s*R\s*A\s*F\s*T', text)


@pytest.mark.parametrize('unit', CANONICAL_SPECIALTY_UNITS)
def test_b03_discipline_pdf_renders_exact_unit_and_scope(auth_client, project, user, other_user, unit, tmp_path):
    report = DisciplineSubReport.objects.create(
        project=project, unit=unit, report_date=date(2027, 5, 22), created_by=user,
    )
    DisciplineSubReportActivity.objects.create(sub_report=report, row_number=1, activity_description='Unit activity')
    url = path(project, unit, report)
    api_client = APIClient()
    assert api_client.get(url).status_code == 401
    api_client.force_authenticate(other_user)
    assert api_client.get(url).status_code == 403
    wrong_unit = next(other for other in CANONICAL_SPECIALTY_UNITS if other != unit)
    assert auth_client.get(path(project, wrong_unit, report)).status_code == 404
    response = auth_client.get(url, HTTP_ACCEPT_LANGUAGE='en')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert response['Content-Disposition'] == f'attachment; filename="unit-daily-report-{unit}-1406-03-01.pdf"'
    text = pdf_text(response.content, tmp_path / 'unit.pdf')
    assert 'Unit activity' in text and watermark(text)
    report.soft_delete(user=user)
    assert auth_client.get(url).status_code == 404


def test_b03_unit_pdf_watermarks_each_page_and_records_approval_evidence(auth_client, project, user, tmp_path):
    history = DisciplineSubReport.objects.create(
        project=project, unit='buildings', report_date=date(2027, 5, 22), created_by=user,
        is_current=False, status=SubReportStatus.APPROVED,
    )
    draft = DisciplineSubReport.objects.create(
        project=project, unit='buildings', report_date=history.report_date, created_by=user,
        supersedes=history, lineage_id=history.lineage_id, version_number=2,
    )
    UnitReportStatusEvent.objects.create(
        report_version=history, actor=user, actor_name='Recorded approver', actor_position='Site manager',
        event_type=UnitReportEventType.APPROVED, to_status=SubReportStatus.APPROVED,
        occurred_at=datetime(2027, 5, 22, 22, 30, tzinfo=timezone.utc),
    )
    DisciplineSubReportActivity.objects.create(sub_report=history, row_number=1, activity_description='Historic value')
    DisciplineSubReportActivity.objects.bulk_create([
        DisciplineSubReportActivity(sub_report=draft, row_number=i + 1, activity_description=f'Draft row {i} ' * 6)
        for i in range(65)
    ])
    approved = auth_client.get(path(project, history.unit, history), HTTP_ACCEPT_LANGUAGE='en')
    assert approved.status_code == 200
    text = pdf_text(approved.content, tmp_path / 'approved.pdf')
    assert 'Site manager' in text and 'Recorded approver' in text
    assert '1406/03/02 02:00' in text
    assert 'Historic value' in text and watermark(text) is None
    current = auth_client.get(path(project, draft.unit, draft), HTTP_ACCEPT_LANGUAGE='en')
    assert current.status_code == 200
    pages = pdf_text(current.content, tmp_path / 'draft.pdf').strip('\f').split('\f')
    assert len(pages) > 1 and all(watermark(page) for page in pages)
