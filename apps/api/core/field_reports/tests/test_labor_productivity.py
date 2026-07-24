"""Tests for labor productivity service."""

import pytest
from rest_framework import status

from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    DailyReportLabor,
    LaborCategory,
    ReportStatus,
)
from field_reports.services.labor_productivity import labor_productivity_report
from projects.models import Activity


@pytest.fixture
def other_activity(db, project, wbs, user):
    return Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='A-002',
        activity_name='Other activity',
        total_quantity=100,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestLaborProductivity:
    def test_activity_productivity(self, project, user, activity):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-01',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='کار',
            shift=ActivityRowShift.SHIFT_1,
            quantity=50,
            quantity_measured=True,
        )
        DailyReportLabor.objects.create(
            report=report,
            labor_category=LaborCategory.DIRECT,
            job_title='کارگر',
            shift_1_count=5,
            work_hours=40,
        )

        data = labor_productivity_report(project.id)
        assert data['total_labor_hours'] == 40.0
        assert data['total_executed_qty'] == 50.0
        assert data['project_productivity_index'] == 1.25
        assert len(data['rows']) == 1
        assert data['rows'][0]['labor_hours'] == 40.0
        assert data['rows'][0]['productivity_index'] == 1.25
        assert data['rows'][0]['actual_man_days'] == 5.0

    def test_hours_allocated_by_qty_share_across_activities(
        self, project, user, activity, other_activity
    ):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-05',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='A',
            shift=ActivityRowShift.SHIFT_1,
            quantity=30,
            quantity_measured=True,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=other_activity,
            activity_description='B',
            shift=ActivityRowShift.SHIFT_1,
            quantity=10,
            quantity_measured=True,
        )
        DailyReportLabor.objects.create(
            report=report,
            labor_category=LaborCategory.DIRECT,
            job_title='کارگر',
            shift_1_count=4,
            work_hours=40,
        )

        data = labor_productivity_report(project.id)
        by_id = {r['activity_id']: r for r in data['rows']}
        assert by_id[str(activity.id)]['labor_hours'] == 30.0
        assert by_id[str(other_activity.id)]['labor_hours'] == 10.0
        assert by_id[str(activity.id)]['productivity_index'] == 1.0
        assert by_id[str(other_activity.id)]['productivity_index'] == 1.0
        assert by_id[str(activity.id)]['actual_man_days'] == 3.0
        assert by_id[str(other_activity.id)]['actual_man_days'] == 1.0

    def test_job_title_grouping(self, project, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-02',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportLabor.objects.create(
            report=report,
            labor_category=LaborCategory.INDIRECT,
            job_title='مهندس',
            shift_1_count=2,
            work_hours=16,
        )

        data = labor_productivity_report(project.id, group_by='job_title')
        assert data['group_by'] == 'job_title'
        assert data['rows'][0]['job_title'] == 'مهندس'
        assert data['rows'][0]['labor_hours'] == 16.0
        assert data['rows'][0]['hours_per_headcount'] == 8.0

    def test_api_endpoint(self, auth_client, project, user, activity):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-03',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='کار',
            shift=ActivityRowShift.SHIFT_1,
            quantity=10,
            quantity_measured=True,
        )
        DailyReportLabor.objects.create(
            report=report,
            labor_category=LaborCategory.DIRECT,
            job_title='کارگر',
            total_count=4,
        )

        url = f'/api/v1/projects/{project.id}/labor-productivity/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'total_labor_hours' in resp.data
