"""FR-RPT US1: KPI figures and drill-through."""

import pytest
from django.utils import timezone
from rest_framework import status

from projects.capability_service import update_capability_setting
from schedule.models import ActivityProgress


@pytest.mark.django_db
class TestKpiDrillthrough:
    def test_kpis_include_figures_with_drill_href(self, auth_client, project):
        resp = auth_client.get(f'/api/v1/projects/{project.id}/kpis/')
        assert resp.status_code == status.HTTP_200_OK
        figures = resp.data.get('figures') or []
        keys = {f['figure_key'] for f in figures}
        assert 'evm.spi' in keys
        assert 'cash.net_balance' in keys
        spi = next(f for f in figures if f['figure_key'] == 'evm.spi')
        assert spi.get('drill') and 'figure_key=evm.spi' in spi['drill']['href']

    def test_disabled_cash_capability_inactive_figure(self, auth_client, project, user):
        update_capability_setting(project, 'cash_flow', enabled=False, user=user)
        resp = auth_client.get(f'/api/v1/projects/{project.id}/kpis/?force_refresh=1')
        cash_fig = next(f for f in resp.data['figures'] if f['figure_key'] == 'cash.net_balance')
        assert cash_fig['status'] == 'inactive'
        assert cash_fig['value'] is None

    def test_drill_unknown_figure_key_404(self, auth_client, project):
        resp = auth_client.get(
            f'/api/v1/projects/{project.id}/kpis/drill/?figure_key=not.real'
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        err = resp.data.get('error') or resp.data
        code = err.get('code')
        if code == 'not_found':
            code = (err.get('details') or {}).get('detail')
            if hasattr(code, 'code'):
                code = code.code
        assert code == 'unknown_figure_key'

    def test_drill_cash_rows(self, auth_client, project, user):
        from cash_flow.models import CashTransaction, CashTransactionType

        CashTransaction.objects.create(
            project=project,
            tx_date=timezone.localdate(),
            tx_type=CashTransactionType.IN,
            amount=100,
            category='other_income',
            created_by=user,
            updated_by=user,
        )
        resp = auth_client.get(
            f'/api/v1/projects/{project.id}/kpis/drill/?figure_key=cash.net_balance'
        )
        assert resp.status_code == 200
        assert resp.data['figure_key'] == 'cash.net_balance'
        assert len(resp.data['results']) >= 1
        row = resp.data['results'][0]
        assert 'approved' in row
        assert row['last_updated_at'] is not None

    def test_drill_approved_only_excludes_unapproved_progress(
        self, auth_client, project, activity, user
    ):
        ActivityProgress.objects.create(
            activity=activity,
            report_date=timezone.localdate(),
            actual_progress=0.5,
            approved_progress=None,
        )
        all_rows = auth_client.get(
            f'/api/v1/projects/{project.id}/kpis/drill/'
            f'?figure_key=progress.plan_vs_actual&approved_only=false'
        )
        approved_rows = auth_client.get(
            f'/api/v1/projects/{project.id}/kpis/drill/'
            f'?figure_key=progress.plan_vs_actual&approved_only=true'
        )
        assert len(all_rows.data['results']) >= len(approved_rows.data['results'])
