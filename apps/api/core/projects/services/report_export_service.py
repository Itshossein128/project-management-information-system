"""Standard report catalog, run, and immutable export versions (FR-RPT US3)."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from django.utils import timezone
from django.utils.dateparse import parse_date

from projects.kpi_service import get_project_kpis
from projects.models import ReportExportVersion

REPORT_CATALOG = [
    {
        'report_type': 'weekly_progress',
        'title': 'Weekly summary',
        'supported_filters': ['date_from', 'date_to', 'wbs', 'status'],
        'approved_only_default': True,
    },
    {
        'report_type': 'monthly_project',
        'title': 'Monthly project summary',
        'supported_filters': ['date_from', 'date_to', 'wbs', 'status'],
        'approved_only_default': True,
    },
    {
        'report_type': 'portfolio_summary',
        'title': 'Portfolio summary',
        'supported_filters': ['date_from', 'date_to'],
        'approved_only_default': True,
    },
    {
        'report_type': 'risk_issue',
        'title': 'Risk & issue register',
        'supported_filters': ['date_from', 'date_to', 'owner', 'status'],
        'approved_only_default': True,
    },
    {
        'report_type': 'budget_variance',
        'title': 'Budget variance',
        'supported_filters': ['date_from', 'date_to', 'cbs', 'wbs'],
        'approved_only_default': True,
    },
]

CATALOG_TYPES = frozenset(r['report_type'] for r in REPORT_CATALOG)


def catalog_entries(*, portfolio: bool = False) -> list[dict]:
    if portfolio:
        return [r for r in REPORT_CATALOG if r['report_type'] in ('portfolio_summary',)]
    return list(REPORT_CATALOG)


def _parse_filters(query_params: dict) -> dict:
    filters: dict[str, Any] = {}
    for key in (
        'date_from', 'date_to', 'unit', 'contract', 'wbs', 'cbs', 'owner', 'status', 'project',
    ):
        raw = query_params.get(key)
        if raw is not None and raw != '':
            filters[key] = raw
    approved_raw = query_params.get('approved_only', 'true')
    filters['approved_only'] = str(approved_raw).lower() not in ('0', 'false', 'no')
    return filters


def _as_of_from_filters(filters: dict) -> date:
    raw = filters.get('date_to') or filters.get('date_from')
    if raw:
        parsed = parse_date(str(raw))
        if parsed:
            return parsed
    return timezone.localdate()


def _run_weekly_progress(project_id, filters: dict) -> dict:
    as_of = _as_of_from_filters(filters)
    kpis = get_project_kpis(project_id, as_of)
    rows = []
    for fig in kpis.get('figures') or []:
        if filters.get('approved_only') and fig.get('label_unapproved'):
            continue
        rows.append(fig)
    return {
        'report_type': 'weekly_progress',
        'project_id': str(project_id),
        'as_of': as_of.isoformat(),
        'filters': filters,
        'figures': rows,
        'summary': kpis.get('physical_progress'),
    }


def _run_monthly_project(project_id, filters: dict) -> dict:
    body = _run_weekly_progress(project_id, filters)
    body['report_type'] = 'monthly_project'
    return body


def _run_portfolio_summary(project_ids: list, filters: dict) -> dict:
    as_of = _as_of_from_filters(filters)
    projects = []
    for pid in project_ids:
        kpis = get_project_kpis(pid, as_of)
        projects.append({'project_id': str(pid), 'panel': kpis.get('panel'), 'as_of': kpis.get('as_of')})
    return {
        'report_type': 'portfolio_summary',
        'filters': filters,
        'as_of': as_of.isoformat(),
        'projects': projects,
    }


def _run_risk_issue(project_id, filters: dict) -> dict:
    from risk.models import RiskEvent

    qs = RiskEvent.objects.filter(project_id=project_id, is_deleted=False)
    if filters.get('status'):
        qs = qs.filter(status=filters['status'])
    if filters.get('owner'):
        qs = qs.filter(owner_id=filters['owner'])
    rows = []
    for ev in qs.order_by('-updated_at')[:500]:
        approved = ev.status not in ('draft', 'open_draft')
        if filters.get('approved_only') and not approved:
            continue
        row = {
            'id': str(ev.id),
            'title': (ev.description or '')[:120],
            'status': ev.status,
            'approved': approved,
            'last_updated_at': ev.updated_at.isoformat() if ev.updated_at else None,
        }
        if not approved:
            row['label_unapproved'] = True
        rows.append(row)
    return {'report_type': 'risk_issue', 'filters': filters, 'results': rows}


def _run_budget_variance(project_id, filters: dict) -> dict:
    as_of = _as_of_from_filters(filters)
    kpis = get_project_kpis(project_id, as_of)
    cost = kpis.get('cost') or {}
    bac = float(cost.get('budget') or 0)
    ac = float(cost.get('actual_cost') or 0)
    return {
        'report_type': 'budget_variance',
        'filters': filters,
        'budget': bac,
        'actual_cost': ac,
        'variance': bac - ac,
        'cpi': cost.get('cpi'),
    }


def run_report(
    report_type: str,
    *,
    project_id=None,
    portfolio_project_ids: list | None = None,
    query_params: dict | None = None,
    user_permissions: set[str] | None = None,
) -> dict:
    if report_type not in CATALOG_TYPES:
        from rest_framework.exceptions import NotFound

        raise NotFound(detail={'code': 'unknown_report_type'})
    filters = _parse_filters(query_params or {})
    perms = user_permissions or set()

    if report_type == 'portfolio_summary':
        ids = portfolio_project_ids or []
        return _run_portfolio_summary(ids, filters)
    if project_id is None:
        from rest_framework.exceptions import ValidationError

        raise ValidationError({'project': 'Project is required for this report type.'})

    if report_type == 'weekly_progress':
        return _run_weekly_progress(project_id, filters)
    if report_type == 'monthly_project':
        return _run_monthly_project(project_id, filters)
    if report_type == 'risk_issue':
        return _run_risk_issue(project_id, filters)
    if report_type == 'budget_variance':
        return _run_budget_variance(project_id, filters)
    return {'report_type': report_type, 'filters': filters, 'results': []}


def _redact_wage_fields(payload: dict, permissions: set[str]) -> dict:
    if 'view_wage' in permissions:
        return payload
    # Shallow redaction marker for wage-bearing exports
    if isinstance(payload, dict):
        out = dict(payload)
        if 'wage' in out:
            out['wage'] = None
            out['wage_redacted'] = True
        return out
    return payload


def create_export(
    *,
    report_type: str,
    user,
    project=None,
    portfolio_project_ids: list | None = None,
    filters: dict | None = None,
    fmt: str = 'json',
    user_permissions: set[str] | None = None,
) -> ReportExportVersion:
    filters = dict(filters or {})
    approved_only = filters.get('approved_only', True)
    if isinstance(approved_only, str):
        approved_only = approved_only.lower() not in ('0', 'false', 'no')

    body = run_report(
        report_type,
        project_id=project.id if project else None,
        portfolio_project_ids=portfolio_project_ids,
        query_params=filters,
        user_permissions=user_permissions,
    )
    body = _redact_wage_fields(body, user_permissions or set())
    extracted_at = timezone.now()
    envelope = {
        'extracted_at': extracted_at.isoformat(),
        'extracted_by': str(user.id),
        'report_type': report_type,
        'filters': filters,
        'approved_only': approved_only,
        'data': body,
    }
    raw = json.dumps(envelope, sort_keys=True, default=str)
    sha = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    version = ReportExportVersion.objects.create(
        report_type=report_type,
        project=project,
        filters=filters,
        extracted_at=extracted_at,
        extracted_by=user,
        approved_only=bool(approved_only),
        payload_sha256=sha,
        payload_json=envelope if fmt == 'json' else None,
    )
    return version


def export_metadata(version: ReportExportVersion) -> dict:
    return {
        'id': str(version.id),
        'report_type': version.report_type,
        'project_id': str(version.project_id) if version.project_id else None,
        'filters': version.filters,
        'extracted_at': version.extracted_at.isoformat(),
        'extracted_by': str(version.extracted_by_id),
        'approved_only': version.approved_only,
        'payload_sha256': version.payload_sha256 or None,
        'download_url': (
            f'/api/v1/projects/{version.project_id}/reports/exports/{version.id}/download/'
            if version.project_id
            else f'/api/v1/portfolio/reports/exports/{version.id}/download/'
        ),
    }


def export_download_payload(version: ReportExportVersion) -> dict:
    if version.payload_json:
        return version.payload_json
    return export_metadata(version)
