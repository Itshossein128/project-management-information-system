import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from field_reports.models import DailyReport, ReportShift, ReportStatus
from projects.models import Project

User = get_user_model()

@pytest.fixture
def project(db):
    user = User.objects.create_user(username='pm', password='pwd')
    return Project.objects.create(
        project_code='PRJ-001',
        project_name='Test Project',
        employer='Test Employer',
        start_date='2024-01-01'
    )

@pytest.mark.django_db
class TestDailyReportModel:
    def test_create_daily_report(self, project):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-01-01',
            shift=ReportShift.DAY,
            weather='Sunny'
        )
        assert report.id is not None
        assert report.status == ReportStatus.DRAFT
        assert report.synced_from_offline is False

    def test_unique_together_constraint(self, project):
        DailyReport.objects.create(
            project=project,
            report_date='2024-01-01',
            shift=ReportShift.DAY
        )
        with pytest.raises(IntegrityError):
            DailyReport.objects.create(
                project=project,
                report_date='2024-01-01',
                shift=ReportShift.DAY
            )
