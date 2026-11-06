"""Unified project KPI / health dashboard views (blueprint K-02)."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from config.exceptions import CodedValidationError
from permissions.constants import PERMISSIONS
from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from permissions.redaction import redact_sensitive_payload
from projects.kpi_service import get_project_kpis
from projects.models import Project
from projects.services.kpi_drill_service import get_drill_rows


def _user_project_permissions(user, project_id) -> set[str]:
    return {c for c in PERMISSIONS if member_has_codename(user, project_id, c)}


class ProjectKpisView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(
        summary='Unified project KPIs',
        description='Aggregated physical, cost, cash, schedule, and alert KPIs (cached 5 min).',
        tags=['KPIs'],
    )
    def get(self, request, project_pk=None):
        get_object_or_404(Project, pk=project_pk)
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else timezone.localdate()
        force = request.query_params.get('force_refresh', '').lower() in ('1', 'true', 'yes')
        return Response(get_project_kpis(project_pk, as_of, force_refresh=force))


class ProjectKpiDrillView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_dashboard'

    @extend_schema(
        summary='KPI figure drill-through',
        description='List source rows for a dashboard figure_key (read-only).',
        tags=['KPIs'],
    )
    def get(self, request, project_pk=None):
        get_object_or_404(Project, pk=project_pk)
        figure_key = request.query_params.get('figure_key', '')
        as_of_raw = request.query_params.get('as_of')
        as_of = parse_jalali_or_gregorian(as_of_raw) if as_of_raw else timezone.localdate()
        approved_only = request.query_params.get('approved_only', 'true').lower() not in (
            '0',
            'false',
            'no',
        )
        perms = _user_project_permissions(request.user, project_pk)
        finance_keys = frozenset({'finance.budget', 'finance.actual_cost', 'evm.cpi'})
        cash_keys = frozenset({'cash.net_balance'})
        if figure_key in finance_keys and 'view_costs' not in perms:
            raise CodedValidationError(
                detail=_('Cost drill-through requires view_costs.'),
                code='drill_requires_view_costs',
            )
        if figure_key in cash_keys and 'view_cashflow' not in perms:
            raise CodedValidationError(
                detail=_('Cash drill-through requires view_cashflow.'),
                code='drill_requires_view_cashflow',
            )
        body = get_drill_rows(project_pk, figure_key, as_of, approved_only=approved_only)
        return Response(
            redact_sensitive_payload(
                body,
                perms,
                redact_wages=True,
                redact_stakeholder_contacts=True,
                redact_person_contacts=True,
            )
        )


class ProjectHealthView(ProjectKpisView):
    """Alias of /kpis/ per blueprint GET /projects/{id}/health."""

    @extend_schema(
        summary='Project health (KPI summary)',
        description='Alias of GET /kpis/ — dashboard KPI summary.',
        tags=['KPIs'],
    )
    def get(self, request, project_pk=None):
        return super().get(request, project_pk=project_pk)
