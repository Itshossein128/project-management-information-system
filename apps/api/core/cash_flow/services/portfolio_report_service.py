"""Portfolio cash / need / allocation report (FR-CASH-009)."""

from __future__ import annotations

from decimal import Decimal

from cash_flow.models import AllocationDecisionLine, ProjectPriorityScore
from cash_flow.services.net_need_service import suggested_net_need
from cash_flow.services.portfolio_access import projects_visible_for_cashflow
from cash_flow.services.projection_service import _month_end, _parse_month, build_projected_series


def build_portfolio_report(user, from_month, to_month, cycle_id=None) -> dict:
    start = _parse_month(from_month)
    end = _parse_month(to_month)
    projects = list(projects_visible_for_cashflow(user))

    project_rows = []
    tot_in = Decimal('0')
    tot_out = Decimal('0')
    tot_net = Decimal('0')

    for project in projects:
        series = build_projected_series(project.id, start, end)
        inflow = sum(Decimal(str(m['projected_inflow'])) for m in series['months'])
        outflow = sum(Decimal(str(m['projected_outflow'])) for m in series['months'])
        net = inflow - outflow
        need = suggested_net_need(project.id, start, _month_end(end))
        score = ProjectPriorityScore.objects.filter(project_id=project.id).first()
        inflow_status = 'unregistered'
        if series['months']:
            # registered if any month registered
            inflow_status = (
                'registered'
                if any(m.get('inflow_status') == 'registered' for m in series['months'])
                else 'unregistered'
            )
        project_rows.append(
            {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'projected_inflow': float(inflow),
                'projected_outflow': float(outflow),
                'net_need': float(net),
                'suggested_net_need': float(need['suggested_net_need']),
                'composite': float(score.composite) if score else None,
                'inflow_status': inflow_status,
            }
        )
        tot_in += inflow
        tot_out += outflow
        tot_net += net

    alloc_qs = AllocationDecisionLine.objects.filter(
        is_deleted=False,
        decision__is_deleted=False,
        project_id__in=[p.id for p in projects],
    ).select_related('decision')
    if cycle_id:
        alloc_qs = alloc_qs.filter(decision__cycle_id=cycle_id)

    allocations = []
    tot_alloc = Decimal('0')
    for ln in alloc_qs:
        allocations.append(
            {
                'cycle_id': str(ln.decision.cycle_id),
                'decision_id': str(ln.decision_id),
                'project_id': str(ln.project_id),
                'amount': float(ln.amount),
                'owner_id': str(ln.decision.owner_id),
                'rationale': ln.decision.rationale,
            }
        )
        tot_alloc += Decimal(ln.amount)

    return {
        'projects': project_rows,
        'allocations': allocations,
        'totals': {
            'projected_inflow': float(tot_in),
            'projected_outflow': float(tot_out),
            'net_need': float(tot_net),
            'allocated': float(tot_alloc),
        },
    }
