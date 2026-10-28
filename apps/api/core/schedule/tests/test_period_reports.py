import uuid
from datetime import date

import pytest
from django.db.models import ProtectedError

from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportEquipment,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportMaterial,
    ReportStatus,
)
from schedule.models import (
    ActivityProgress,
    FigureValueStatus,
    PeriodReportFigure,
    PeriodReportFigureOverride,
    PeriodReportStatus,
    ProjectPeriodReport,
)
from schedule.services.measurement_service import ProgressValidationError
from schedule.services.period_report_service import apply_figure_override, approve_period_report, generate_period_report


def _url(project, suffix=''):
    return f'/api/v1/projects/{project.id}/progress-reports/{suffix}'


WEEKLY = {'kind': 'weekly', 'period_start': '2026-10-03', 'period_end': '2026-10-09'}
MONTHLY = {'kind': 'monthly', 'period_start': '2026-09-23', 'period_end': '2026-10-22'}


@pytest.mark.django_db
class TestPeriodReports:
    def test_generate_weekly_has_sections_and_not_recorded(self, project, auth_client):
        response = auth_client.post(_url(project), WEEKLY, format='json')
        assert response.status_code == 201
        figures = {f['section']: f for f in response.data['figures']}
        assert {
            'completed_activities',
            'critical_activities',
            'labor_machinery',
            'materials',
            'next_week_plan',
            'progress_summary',
            'barriers',
            'decisions_required',
        } <= set(figures)
        for section in ('critical_activities', 'barriers', 'decisions_required', 'labor_machinery', 'materials'):
            assert figures[section]['value_status'] == 'not_recorded'
            assert figures[section]['value'] is None
        assert figures['barriers']['source_path'] == f'/projects/{project.id}/barriers'
        assert response.data['status'] == 'generated'
        assert len(response.data['warnings']) > 0

    def test_generate_monthly_sections(self, project, auth_client):
        response = auth_client.post(_url(project), MONTHLY, format='json')
        assert response.status_code == 201
        sections = {f['section'] for f in response.data['figures']}
        assert sections == {
            'progress_summary',
            'baseline_variance',
            'cost',
            'commitments',
            'ipc',
            'risks',
            'hse_summary',
            'qc_summary',
            'next_month_forecast',
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

    def test_override_requires_reason_with_min_10_chars(self, project, auth_client):
        report = auth_client.post(_url(project), MONTHLY, format='json')
        figure_id = report.data['figures'][0]['id']
        # Empty reason
        resp1 = auth_client.post(
            _url(project, f'figures/{figure_id}/overrides/'), {'new_value': 12.5, 'reason': '  '}, format='json',
        )
        assert resp1.status_code == 400
        assert resp1.data['error']['code'] == 'override_reason_required'

        # Short reason (< 10 chars)
        resp2 = auth_client.post(
            _url(project, f'figures/{figure_id}/overrides/'), {'new_value': 12.5, 'reason': 'too short'}, format='json',
        )
        assert resp2.status_code == 400
        assert resp2.data['error']['code'] == 'override_reason_required'
        assert not PeriodReportFigureOverride.objects.exists()

    def test_override_creates_audit_row_and_preserves_calculated_value(self, project, auth_client, user):
        report = auth_client.post(_url(project), MONTHLY, format='json')
        cost = next(f for f in report.data['figures'] if f['section'] == 'cost')
        original_calc_value = cost['calculated_value']
        assert cost['is_overridden'] is False

        response = auth_client.post(
            _url(project, f'figures/{cost["id"]}/overrides/'),
            {'new_value': 12.5, 'reason': 'Corrected transcription from approved IPC'},
            format='json',
        )
        assert response.status_code == 201
        assert response.data['figure']['value'] == 12.5
        assert response.data['figure']['is_overridden'] is True
        assert response.data['figure']['calculated_value'] == original_calc_value
        assert response.data['figure']['value_status'] == 'recorded'
        assert response.data['figure']['override_count'] == 1

        override = PeriodReportFigureOverride.objects.get()
        assert override.old_value is None
        assert override.new_value == 12.5
        assert override.created_by_id == user.id

        figure = PeriodReportFigure.objects.get(pk=cost['id'])
        assert figure.value == 12.5
        assert figure.is_overridden is True
        assert figure.calculated_value == original_calc_value

    def test_service_override_reason_required(self, project, user):
        report = generate_period_report(project, 'weekly', date(2026, 10, 3), date(2026, 10, 9), user)
        figure = report.figures.first()
        with pytest.raises(ProgressValidationError) as exc:
            apply_figure_override(figure, 1, 'short', user)
        assert exc.value.code == 'override_reason_required'

    def test_cross_project_figure_not_found(self, project, auth_client, other_user):
        report = auth_client.post(_url(project), WEEKLY, format='json')
        figure_id = report.data['figures'][0]['id']
        other = f'/api/v1/projects/{uuid.uuid4()}/progress-reports/figures/{figure_id}/overrides/'
        response = auth_client.post(
            other,
            {'new_value': 1, 'reason': 'Valid reason with more than 10 characters'},
            format='json',
        )
        assert response.status_code in (403, 404)

    def test_weekly_rollup_from_approved_daily_reports(self, project, auth_client, user):
        # Create an approved daily report on 2026-10-06
        dr = DailyReport.objects.create(
            project=project,
            report_date=date(2026, 10, 6),
            status=ReportStatus.APPROVED,
            prepared_by=user,
            approved_by=user,
            created_by=user,
        )
        DailyReportLabor.objects.create(
            report=dr,
            labor_category='direct',
            job_title='Mason',
            work_hours=16.0,
            overtime_hours=4.0,
            total_count=2,
            contractor_name='Acme Builders',
        )
        DailyReportEquipment.objects.create(
            report=dr,
            equipment_name='CAT 320 Excavator',
            productive_hours=7.5,
            idle_hours=1.5,
            repair_hours=0.0,
        )
        DailyReportMaterial.objects.create(
            report=dr,
            material_description='Portland Cement Type II',
            quantity=120.0,
            unit='Bags',
            transaction_type='receipt',
        )
        DailyReportMaterial.objects.create(
            report=dr,
            material_description='Ready Mix Concrete C25',
            quantity=45.0,
            unit='m3',
            transaction_type='issue',
        )

        response = auth_client.post(_url(project), WEEKLY, format='json')
        assert response.status_code == 201
        figures = {f['section']: f for f in response.data['figures']}

        # Check labor & machinery
        lm = figures['labor_machinery']
        assert lm['value_status'] == 'recorded'
        assert lm['value']['total_regular_hours'] == 16.0
        assert lm['value']['total_overtime_hours'] == 4.0
        assert lm['value']['total_machinery_operating_hours'] == 7.5
        assert lm['value']['total_machinery_idle_hours'] == 1.5

        # Check materials
        mat = figures['materials']
        assert mat['value_status'] == 'recorded'
        mat_items = {m['material_name']: m for m in mat['value']['items']}
        assert mat_items['Portland Cement Type II']['delivered_quantity'] == 120.0
        assert mat_items['Ready Mix Concrete C25']['consumed_quantity'] == 45.0

    def test_unapproved_daily_reports_excluded_and_warnings_emitted(self, project, auth_client, user):
        # Create a draft (unapproved) daily report on 2026-10-07
        dr_draft = DailyReport.objects.create(
            project=project,
            report_date=date(2026, 10, 7),
            status=ReportStatus.DRAFT,
            prepared_by=user,
            created_by=user,
        )
        DailyReportLabor.objects.create(
            report=dr_draft,
            labor_category='direct',
            job_title='Carpenter',
            work_hours=50.0,
            overtime_hours=10.0,
            total_count=5,
        )

        response = auth_client.post(_url(project), WEEKLY, format='json')
        assert response.status_code == 201
        figures = {f['section']: f for f in response.data['figures']}

        # The 50 hours from draft report MUST NOT be included
        assert figures['labor_machinery']['value_status'] == 'not_recorded'

        # Header warnings must note unapproved day
        warnings = response.data['warnings']
        assert any('تأیید نشده است' in w for w in warnings)

    def test_figure_provenance_and_deletion_protection(self, project, auth_client, user):
        # Create approved daily report
        dr = DailyReport.objects.create(
            project=project,
            report_date=date(2026, 10, 8),
            status=ReportStatus.APPROVED,
            prepared_by=user,
            approved_by=user,
            created_by=user,
        )
        labor = DailyReportLabor.objects.create(
            report=dr,
            labor_category='direct',
            job_title='Welder',
            work_hours=8.0,
            total_count=1,
        )

        response = auth_client.post(_url(project), WEEKLY, format='json')
        assert response.status_code == 201
        lm_figure = next(f for f in response.data['figures'] if f['section'] == 'labor_machinery')

        # Query provenance sources
        sources_resp = auth_client.get(_url(project, f'figures/{lm_figure["id"]}/sources/'))
        assert sources_resp.status_code == 200
        assert len(sources_resp.data) >= 1
        item = sources_resp.data[0]
        assert item['source_type'] == 'daily_labor'
        assert item['source_id'] == str(labor.id)
        assert item['daily_report_id'] == str(dr.id)
        assert item['contributed_quantity']['regular_hours'] == 8.0

        # Attempt to delete the daily report - MUST raise ProtectedError
        with pytest.raises(ProtectedError):
            dr.delete()

    def test_monthly_report_comprehensive_chapters_and_approval(self, project, auth_client, user):
        # Create an approved daily report with an HSE incident
        dr = DailyReport.objects.create(
            project=project,
            report_date=date(2026, 10, 15),
            status=ReportStatus.APPROVED,
            prepared_by=user,
            approved_by=user,
            created_by=user,
        )
        DailyReportIncident.objects.create(
            report=dr,
            incident_type='safety',
            severity='minor',
            description='First-aid scratch on finger',
            corrective_action='Applied antiseptic bandage',
        )

        response = auth_client.post(_url(project), MONTHLY, format='json')
        assert response.status_code == 201
        report_id = response.data['id']
        figures = {f['section']: f for f in response.data['figures']}

        # Verify HSE summary
        hse = figures['hse_summary']
        assert hse['value_status'] == 'recorded'
        assert hse['value']['total_incidents'] == 1
        assert hse['value']['incidents'][0]['description'] == 'First-aid scratch on finger'

        # Approve report
        approve_resp = auth_client.post(_url(project, f'{report_id}/approve/'))
        assert approve_resp.status_code == 200
        assert approve_resp.data['status'] == 'approved'
        assert approve_resp.data['serial_number'].startswith('REP-')
        assert approve_resp.data['approved_by'] == str(user.id)
        assert approve_resp.data['approved_at'] is not None

        # Modifying figure of an approved report is locked
        fig_id = figures['progress_summary']['id']
        locked_resp = auth_client.post(
            _url(project, f'figures/{fig_id}/overrides/'),
            {'new_value': 99, 'reason': 'Attempt to edit approved locked report'},
            format='json',
        )
        assert locked_resp.status_code == 400
        assert locked_resp.data['error']['code'] == 'report_locked'

    def test_override_forbidden_for_user_without_edit_reports(self, project, auth_client, api_client, other_user, member):
        report = auth_client.post(_url(project), WEEKLY, format='json')
        fig_id = report.data['figures'][0]['id']

        api_client.force_authenticate(user=other_user)
        resp = api_client.post(
            _url(project, f'figures/{fig_id}/overrides/'),
            {'new_value': 123, 'reason': 'Trying to override without edit_reports'},
            format='json',
        )
        assert resp.status_code == 403

    def test_period_boundaries_are_enforced(self, project, auth_client):
        bad_week = auth_client.post(
            _url(project),
            {'kind': 'weekly', 'period_start': '2026-10-05', 'period_end': '2026-10-11'},
            format='json',
        )
        assert bad_week.status_code == 400
        assert bad_week.data['error']['code'] == 'invalid_period_boundary'

        bad_month = auth_client.post(
            _url(project),
            {'kind': 'monthly', 'period_start': '2026-10-01', 'period_end': '2026-10-31'},
            format='json',
        )
        assert bad_month.status_code == 400
        assert bad_month.data['error']['code'] == 'invalid_period_boundary'

    def test_override_rejects_negative_non_negative_metric(self, project, auth_client):
        report = auth_client.post(_url(project), MONTHLY, format='json')
        figure_id = next(f for f in report.data['figures'] if f['section'] == 'cost')['id']
        response = auth_client.post(
            _url(project, f'figures/{figure_id}/overrides/'),
            {'new_value': -1, 'reason': 'اصلاح مقدار ثبت شده در صورت جلسه'},
            format='json',
        )
        assert response.status_code == 400
        assert response.data['error']['code'] == 'invalid_non_negative_value'

    def test_override_rejects_stale_figure_version(self, project, auth_client):
        report = auth_client.post(_url(project), MONTHLY, format='json')
        figure = next(f for f in report.data['figures'] if f['section'] == 'cost')
        body = {'new_value': 1, 'reason': 'اصلاح مقدار ثبت شده در صورت جلسه', 'expected_version': figure['version']}
        first = auth_client.post(_url(project, f'figures/{figure["id"]}/overrides/'), body, format='json')
        assert first.status_code == 201
        second = auth_client.post(_url(project, f'figures/{figure["id"]}/overrides/'), body, format='json')
        assert second.status_code == 409
        assert second.data['error']['code'] == 'conflict'
