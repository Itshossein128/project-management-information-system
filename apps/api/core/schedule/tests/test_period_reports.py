import uuid
from datetime import date

import pytest

from schedule.models import (
    ActivityProgress,
    FigureValueStatus,
    PeriodReportFigure,
    PeriodReportFigureOverride,
    PeriodReportStatus,
    ProjectPeriodReport,
)
from schedule.services.measurement_service import ProgressValidationError
from schedule.services.period_report_service import apply_figure_override, generate_period_report


def _url(project, suffix=''):
    return f'/api/v1/projects/{project.id}/progress-reports/{suffix}'


WEEKLY = {'kind': 'weekly', 'period_start': '2026-10-05', 'period_end': '2026-10-11'}
MONTHLY = {'kind': 'monthly', 'period_start': '2026-10-01', 'period_end': '2026-10-31'}


@pytest.mark.django_db
class TestPeriodReports:
    def test_generate_weekly_has_sections_and_not_recorded(self, project, auth_client):
        response = auth_client.post(_url(project), WEEKLY, format='json')
        assert response.status_code == 201
        figures = {f['section']: f for f in response.data['figures']}
        assert {'critical_activities', 'next_week_plan', 'barriers', 'decisions_required'} <= set(figures)
        for section in ('critical_activities', 'barriers', 'decisions_required'):
            assert figures[section]['value_status'] == 'not_recorded'
            assert figures[section]['value'] is None
        assert figures['barriers']['source_path'] == f'/projects/{project.id}/barriers'
        assert response.data['status'] == 'generated'

    def test_generate_monthly_sections(self, project, auth_client):
        response = auth_client.post(_url(project), MONTHLY, format='json')
        assert response.status_code == 201
        sections = {f['section'] for f in response.data['figures']}
        assert sections == {
            'progress_summary', 'baseline_variance', 'cost', 'commitments',
            'ipc', 'risks', 'next_month_forecast',
        }
        assert all(f['value_status'] == 'not_recorded' for f in response.data['figures'])

    def test_recorded_figures_have_provenance(self, project, activity, approved_measurement, auth_client, user):
        activity.weight = 1.0
        activity.planned_start = '2026-10-12'
        activity.planned_finish = '2026-10-14'
        activity.save(update_fields=['weight', 'planned_start', 'planned_finish'])
        ActivityProgress.objects.create(
            activity=activity, report_date='2026-10-08', planned_progress=0.5,
            actual_progress=0.4, approved_progress=0.4,
        )
        response = auth_client.post(_url(project), WEEKLY, format='json')
        figures = {f['section']: f for f in response.data['figures']}
        summary = figures['progress_summary']
        assert summary['value_status'] == 'recorded'
        assert summary['value']['actual_progress_pct'] == 40.0
        assert summary['source_approved'] is True
        assert summary['source_path'] == f'/projects/{project.id}/progress'
        plan = figures['next_week_plan']
        assert plan['value_status'] == 'recorded'
        assert [a['activity_code'] for a in plan['value']['activities']] == ['A1']

    def test_regenerate_supersedes_prior(self, project, auth_client):
        first = auth_client.post(_url(project), WEEKLY, format='json')
        second = auth_client.post(_url(project), WEEKLY, format='json')
        assert first.data['id'] != second.data['id']
        old = ProjectPeriodReport.objects.get(pk=first.data['id'])
        assert old.status == PeriodReportStatus.SUPERSEDED
        assert str(old.superseded_by_id) == second.data['id']
        listing = auth_client.get(_url(project) + '?kind=weekly')
        assert [r['id'] for r in listing.data] == [second.data['id']]
        detail = auth_client.get(_url(project, f'{first.data["id"]}/'))
        assert detail.status_code == 200
        assert detail.data['status'] == 'superseded'

    def test_invalid_period(self, project, auth_client):
        response = auth_client.post(
            _url(project), {'kind': 'weekly', 'period_start': '2026-10-11', 'period_end': '2026-10-05'},
            format='json',
        )
        assert response.status_code == 400
        assert response.data['error']['code'] == 'invalid_period'

    def test_figure_immutable_via_patch(self, project, auth_client):
        report = auth_client.post(_url(project), WEEKLY, format='json')
        figure = report.data['figures'][0]
        response = auth_client.patch(
            _url(project, f'figures/{figure["id"]}/'), {'value': 5}, format='json',
        )
        assert response.status_code == 400
        assert response.data['error']['code'] == 'figure_immutable'
        assert PeriodReportFigure.objects.get(pk=figure['id']).value == figure['value']

    def test_override_requires_reason(self, project, auth_client):
        report = auth_client.post(_url(project), MONTHLY, format='json')
        figure_id = report.data['figures'][0]['id']
        response = auth_client.post(
            _url(project, f'figures/{figure_id}/overrides/'), {'new_value': 12.5, 'reason': '  '}, format='json',
        )
        assert response.status_code == 400
        assert response.data['error']['code'] == 'override_reason_required'
        assert not PeriodReportFigureOverride.objects.exists()

    def test_override_creates_audit_row_and_updates_value(self, project, auth_client, user):
        report = auth_client.post(_url(project), MONTHLY, format='json')
        cost = next(f for f in report.data['figures'] if f['section'] == 'cost')
        response = auth_client.post(
            _url(project, f'figures/{cost["id"]}/overrides/'),
            {'new_value': 12.5, 'reason': 'Corrected transcription from approved IPC'},
            format='json',
        )
        assert response.status_code == 201
        assert response.data['figure']['value'] == 12.5
        assert response.data['figure']['value_status'] == 'recorded'
        assert response.data['figure']['override_count'] == 1
        override = PeriodReportFigureOverride.objects.get()
        assert override.old_value is None
        assert override.new_value == 12.5
        assert override.created_by_id == user.id
        figure = PeriodReportFigure.objects.get(pk=cost['id'])
        assert figure.value == 12.5
        assert figure.value_status == FigureValueStatus.RECORDED

    def test_service_override_reason_required(self, project, user):
        report = generate_period_report(project, 'weekly', date(2026, 10, 5), date(2026, 10, 11), user)
        figure = report.figures.first()
        with pytest.raises(ProgressValidationError) as exc:
            apply_figure_override(figure, 1, '', user)
        assert exc.value.code == 'override_reason_required'

    def test_cross_project_figure_not_found(self, project, auth_client, other_user):
        report = auth_client.post(_url(project), WEEKLY, format='json')
        figure_id = report.data['figures'][0]['id']
        other = f'/api/v1/projects/{uuid.uuid4()}/progress-reports/figures/{figure_id}/overrides/'
        response = auth_client.post(other, {'new_value': 1, 'reason': 'x'}, format='json')
        assert response.status_code in (403, 404)
