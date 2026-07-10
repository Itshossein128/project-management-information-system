import pytest
from django.utils import timezone

from field_reports.models import ActivityRowShift, DailyReport, DailyReportActivity, ReportStatus
from field_reports.tasks import recalculate_activity_progress
from projects.models import Activity
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule
from schedule.services.evm_service import compute_evm
from schedule.services.progress_service import (
    get_planned_progress_on_date,
    get_project_progress_on_date,
    get_s_curve_data,
    invalidate_s_curve_cache,
    s_curve_cache_key,
)
from schedule.tasks import compute_baseline_progress


@pytest.mark.django_db
class TestProgressService:
    def test_weighted_project_progress(self, project, user, activity, wbs):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        ActivityProgress.objects.create(
            activity=activity,
            report_date='2024-10-01',
            actual_progress=0.5,
        )
        assert get_project_progress_on_date(project.id, timezone.datetime(2024, 10, 5).date()) == pytest.approx(0.5)

    def test_baseline_interpolation_task(self, project, user, activity):
        baseline = BaselineSchedule.objects.create(
            project=project,
            version_name='BL1',
            is_current=True,
        )
        BaselineActivity.objects.create(
            baseline=baseline,
            activity=activity,
            planned_start='2024-10-01',
            planned_finish='2024-10-03',
        )
        result = compute_baseline_progress(str(baseline.id))
        assert result['rows'] == 3
        assert ActivityProgress.objects.filter(activity=activity, planned_progress__isnull=False).count() == 3

    def test_s_curve_daily_warning(self, project, activity):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        date_from = timezone.datetime(2024, 1, 1).date()
        date_to = timezone.datetime(2025, 6, 1).date()
        data, warning = get_s_curve_data(project.id, date_from, date_to, 'daily', force_refresh=True)
        assert warning is not None
        assert len(data) > 365

    def test_s_curve_force_refresh(self, project, activity, monkeypatch):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        date_from = timezone.datetime(2024, 10, 1).date()
        date_to = timezone.datetime(2024, 10, 3).date()
        calls = {'n': 0}
        original = get_project_progress_on_date

        def counted(*args, **kwargs):
            calls['n'] += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(
            'schedule.services.progress_service.get_project_progress_on_date',
            counted,
        )
        get_s_curve_data(project.id, date_from, date_to, 'daily', force_refresh=True)
        first_calls = calls['n']
        get_s_curve_data(project.id, date_from, date_to, 'daily', force_refresh=False)
        assert calls['n'] == first_calls
        get_s_curve_data(project.id, date_from, date_to, 'daily', force_refresh=True)
        assert calls['n'] > first_calls

    def test_evm_zeros_without_cost_data(self, project, activity):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        evm = compute_evm(project.id, timezone.localdate())
        assert evm['bac'] == 0
        assert evm['ac'] == 0
        assert evm['cpi'] is None

    def test_manual_progress_source(self, project, user, activity, auth_client):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        url = f'/api/v1/projects/{project.id}/progress/manual/'
        response = auth_client.post(
            url,
            {
                'activity_id': str(activity.id),
                'report_date': '1403/07/10',
                'actual_progress': 40,
                'notes': 'manual entry',
            },
            format='json',
        )
        assert response.status_code == 201
        progress = ActivityProgress.objects.get(activity=activity)
        assert progress.source == ActivityProgress.ProgressSource.MANUAL
        assert float(progress.actual_progress) == pytest.approx(0.4)

    def test_progress_snapshot_endpoint(self, project, activity, auth_client):
        activity.weight = 1.0
        activity.save(update_fields=['weight'])
        ActivityProgress.objects.create(
            activity=activity,
            report_date='2024-10-01',
            planned_progress=0.6,
            actual_progress=0.4,
        )
        url = f'/api/v1/projects/{project.id}/progress/'
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data['actual_progress_pct'] == 40.0
        assert response.data['planned_progress_pct'] == 60.0

    def test_recalc_invalidates_cache(self, project, user, activity, monkeypatch):
        activity.weight = 1.0
        activity.total_quantity = 100
        activity.save(update_fields=['weight', 'total_quantity'])
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-10-01',
            status=ReportStatus.APPROVED,
            approved_by=user,
            created_by=user,
            updated_by=user,
        )
        DailyReportActivity.objects.create(
            report=report,
            activity_ref=activity,
            activity_description='work',
            shift=ActivityRowShift.SHIFT_1,
            quantity=25,
            quantity_measured=True,
        )
        deleted = []
        monkeypatch.setattr(
            'schedule.services.progress_service.invalidate_s_curve_cache',
            lambda pid: deleted.append(pid),
        )
        recalculate_activity_progress(str(report.id))
        assert deleted == [project.id]
