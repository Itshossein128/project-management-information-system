"""Role-based dashboard pack assembly (FR-RPT US2/US4)."""

from __future__ import annotations

from datetime import date

from django.utils import timezone

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from projects.kpi_service import get_project_kpis
from projects.models import Project
from projects.services.figure_provenance import FIGURE_STATUS_INACTIVE, make_figure

PACK_PRIORITY = (
    'executive',
    'project_manager',
    'finance',
    'project_controls',
    'hr_site',
    'unit_manager',
)

ROLE_TO_PACK: dict[str, str] = {
    'executive_approver': 'executive',
    'project_manager': 'project_manager',
    'finance_manager': 'finance',
    'project_controls': 'project_controls',
    'planning_engineer': 'project_controls',
    'site_specialist': 'hr_site',
    'site_supervisor': 'hr_site',
    'hr_officer': 'hr_site',
    'viewer': 'project_manager',
    'supervisor_consultant': 'project_manager',
}

PACK_GROUPS: dict[str, list[tuple[str, str, list[str]]]] = {
    'executive': [
        ('portfolio', 'Portfolio status', ['evm.spi', 'evm.cpi', 'cash.net_balance']),
        ('risk_schedule', 'Schedule & liquidity', ['schedule.critical_activities', 'progress.plan_vs_actual']),
    ],
    'project_manager': [
        ('schedule', 'Plan vs actual', ['progress.plan_vs_actual', 'schedule.critical_activities']),
        ('finance', 'Budget & cost', ['finance.budget', 'finance.actual_cost', 'evm.cpi']),
        ('cash', 'Cash position', ['cash.net_balance']),
    ],
    'finance': [
        ('finance', 'Budget & cost', ['finance.budget', 'finance.actual_cost', 'evm.cpi']),
        ('cash', 'Cash & liquidity', ['cash.net_balance']),
    ],
    'project_controls': [
        ('evm', 'EVM', ['evm.spi', 'evm.cpi', 'progress.plan_vs_actual']),
        ('schedule', 'Critical path', ['schedule.critical_activities']),
    ],
    'hr_site': [
        ('hr_capacity', 'HR / site (stub)', []),
    ],
    'unit_manager': [
        ('unit_ops', 'Unit operations (stub)', []),
    ],
}


def member_role_names(user, project_id) -> set[str]:
    member = ProjectMember.objects.filter(
        project_id=project_id,
        user=user,
        status=MemberStatus.ACTIVE,
    ).first()
    if not member:
        return set()
    return set(
        ProjectMemberRole.objects.filter(member=member).values_list('role__role_name', flat=True)
    )


def resolve_pack_id(role_names: set[str], requested: str | None = None) -> str:
    if requested and requested in PACK_GROUPS:
        mapped = {ROLE_TO_PACK.get(r) for r in role_names}
        if requested in mapped or requested in ('hr_site', 'unit_manager'):
            return requested
    candidates = []
    for role in role_names:
        pack = ROLE_TO_PACK.get(role)
        if pack:
            candidates.append(pack)
    if not candidates:
        return 'project_manager'
    for pack in PACK_PRIORITY:
        if pack in candidates:
            return pack
    return candidates[0]


def _figure_from_map(fig_map: dict[str, dict], key: str) -> dict:
    return fig_map.get(key) or make_figure(figure_key=key, status=FIGURE_STATUS_INACTIVE)


def build_project_pack(project_id, user, *, as_of: date | None = None, pack: str | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    role_names = member_role_names(user, project_id)
    pack_id = resolve_pack_id(role_names, pack)
    kpis = get_project_kpis(project_id, as_of)
    fig_map = {f['figure_key']: f for f in kpis.get('figures') or []}

    groups = []
    for group_key, title, figure_keys in PACK_GROUPS.get(pack_id, []):
        if not figure_keys:
            groups.append(
                {
                    'group_key': group_key,
                    'title': title,
                    'figures': [
                        make_figure(
                            figure_key=f'{pack_id}.{group_key}',
                            status=FIGURE_STATUS_INACTIVE,
                        ),
                    ],
                }
            )
            continue
        groups.append(
            {
                'group_key': group_key,
                'title': title,
                'figures': [_figure_from_map(fig_map, k) for k in figure_keys],
            }
        )

    return {
        'pack_id': pack_id,
        'project_id': str(project_id),
        'as_of': as_of.strftime('%Y-%m-%d'),
        'groups': groups,
    }


def accessible_project_ids(user) -> list:
    return list(
        ProjectMember.objects.filter(
            user=user,
            status=MemberStatus.ACTIVE,
        ).values_list('project_id', flat=True)
    )


def build_portfolio_dashboard(user, *, as_of: date | None = None) -> dict:
    as_of = as_of or timezone.localdate()
    pack_id = 'executive'
    role_names: set[str] = set()
    for member in ProjectMember.objects.filter(user=user, status=MemberStatus.ACTIVE).prefetch_related(
        'member_roles__role'
    ):
        for pmr in member.member_roles.all():
            role_names.add(pmr.role.role_name)
    if 'executive_approver' in role_names or 'project_manager' in role_names:
        pack_id = 'executive'
    elif 'finance_manager' in role_names:
        pack_id = 'finance'

    project_ids = accessible_project_ids(user)
    projects = Project.objects.filter(id__in=project_ids).order_by('project_name')
    rows = []
    for project in projects:
        kpis = get_project_kpis(project.id, as_of)
        fig_map = {f['figure_key']: f for f in kpis.get('figures') or []}
        keys = []
        for _gk, _t, fks in PACK_GROUPS.get(pack_id, []):
            keys.extend(fks)
        rows.append(
            {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'figures': [_figure_from_map(fig_map, k) for k in keys] if keys else [],
            }
        )

    return {
        'pack_id': pack_id,
        'as_of': as_of.strftime('%Y-%m-%d'),
        'projects': rows,
    }
