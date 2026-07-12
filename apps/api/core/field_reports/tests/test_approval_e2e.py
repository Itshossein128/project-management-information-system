"""Approve daily report → progress update integration."""

import pytest
from rest_framework import status

from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    ReportStatus,
)
from schedule.models import ActivityProgress


@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True


@pytest.fixture
def dr_base(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
class TestApprovalProgressE2E:
    def test_approve_updates_activity_progress(self, auth_client, dr_base, project, user, activity):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-11-01',
            status=ReportStatus.DRAFT,
            prepared_by=user,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='کار',
            shift=ActivityRowShift.SHIFT_1,
            quantity=30,
            quantity_measured=True,
        )

        auth_client.post(f'{dr_base}{report.id}/submit/')
        auth_client.post(f'{dr_base}{report.id}/review/')
        response = auth_client.post(f'{dr_base}{report.id}/approve/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'approved'

        progress = ActivityProgress.objects.filter(
            activity=activity,
            report_date='2024-11-01',
        ).first()
        assert progress is not None
        assert float(progress.cumulative_quantity) == 30.0
