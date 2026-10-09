"""Liquidity scores, proposal generation, decisions, overlap, simulations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from cash_flow.models import (
    AllocationDecision,
    AllocationDecisionLine,
    AllocationProposal,
    AllocationProposalLine,
    AllocationSimulation,
    LiquidityAllocationCycle,
    LiquidityCycleStatus,
    ProjectPriorityScore,
)
from cash_flow.services.net_need_service import suggested_net_need
from cash_flow.services.portfolio_access import projects_visible_for_cashflow
from config.exceptions import CodedValidationError


def score_to_dict(score: ProjectPriorityScore) -> dict:
    return {
        'urgency': float(score.urgency),
        'return_score': float(score.return_score),
        'recovery_speed': float(score.recovery_speed),
        'risk': float(score.risk),
        'composite': float(score.composite),
        'notes': score.notes or '',
    }


def upsert_priority_score(project_id, data: dict, user) -> ProjectPriorityScore:
    fields = ('urgency', 'return_score', 'recovery_speed', 'risk')
    for f in fields:
        if f not in data:
            raise CodedValidationError(detail=f'{f} is required', code='score_component_required')
        val = Decimal(str(data[f]))
        if val < 0 or val > 100:
            raise CodedValidationError(detail=f'{f} must be between 0 and 100', code='score_out_of_range')
        data[f] = val

    score = ProjectPriorityScore.objects.filter(project_id=project_id).first()
    payload = {
        'urgency': data['urgency'],
        'return_score': data['return_score'],
        'recovery_speed': data['recovery_speed'],
        'risk': data['risk'],
        'notes': data.get('notes') or '',
        'updated_by': user,
    }
    if score is None:
        score = ProjectPriorityScore.objects.create(
            project_id=project_id,
            created_by=user,
            **payload,
        )
    else:
        for k, v in payload.items():
            setattr(score, k, v)
        score.save()
    return score


def get_priority_score(project_id) -> ProjectPriorityScore | None:
    return ProjectPriorityScore.objects.filter(project_id=project_id).first()


def create_cycle(user, data: dict) -> LiquidityAllocationCycle:
    return LiquidityAllocationCycle.objects.create(
        name=data['name'],
        period_start=data['period_start'],
        period_end=data['period_end'],
        available_liquidity=Decimal(str(data.get('available_liquidity') or 0)),
        currency=data.get('currency') or 'IRR',
        status=LiquidityCycleStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )


@transaction.atomic
def generate_proposal(cycle: LiquidityAllocationCycle, user) -> dict:
    pool = Decimal(cycle.available_liquidity or 0)
    if pool <= 0:
        proposal = AllocationProposal.objects.create(
            cycle=cycle,
            algorithm_note='equal_weight_greedy',
            created_by=user,
            updated_by=user,
        )
        cycle.status = LiquidityCycleStatus.PROPOSED
        cycle.updated_by = user
        cycle.save(update_fields=['status', 'updated_by', 'updated_at'])
        return {
            'id': str(proposal.id),
            'lines': [],
            'message': 'no_available_liquidity',
            'warnings': {'incomplete_score_projects': []},
        }

    visible = list(projects_visible_for_cashflow(user))
    incomplete = []
    ranked = []
    for project in visible:
        score = ProjectPriorityScore.objects.filter(project_id=project.id).first()
        if score is None:
            incomplete.append(str(project.id))
            continue
        need = suggested_net_need(project.id, cycle.period_start, cycle.period_end)
        need_amt = Decimal(str(need['suggested_net_need']))
        ranked.append((project, score, need_amt))

    ranked.sort(key=lambda t: t[1].composite, reverse=True)

    # Soft-delete prior draft proposals for cycle (keep history simple: replace lines via new proposal)
    AllocationProposal.objects.filter(cycle=cycle, is_deleted=False).update(
        is_deleted=True, deleted_at=timezone.now()
    )

    proposal = AllocationProposal.objects.create(
        cycle=cycle,
        algorithm_note='equal_weight_greedy',
        created_by=user,
        updated_by=user,
    )

    remaining = pool
    lines_out = []
    rank = 1
    for project, score, need_amt in ranked:
        if need_amt <= 0 or remaining <= 0:
            continue
        allot = min(need_amt, remaining)
        AllocationProposalLine.objects.create(
            proposal=proposal,
            project=project,
            suggested_amount=allot,
            rank=rank,
            composite_snapshot=score.composite,
            need_snapshot=need_amt,
            created_by=user,
            updated_by=user,
        )
        lines_out.append(
            {
                'project_id': str(project.id),
                'suggested_amount': float(allot),
                'rank': rank,
                'composite_snapshot': float(score.composite),
                'need_snapshot': float(need_amt),
            }
        )
        remaining -= allot
        rank += 1

    cycle.status = LiquidityCycleStatus.PROPOSED
    cycle.updated_by = user
    cycle.save(update_fields=['status', 'updated_by', 'updated_at'])

    return {
        'id': str(proposal.id),
        'lines': lines_out,
        'message': None,
        'warnings': {'incomplete_score_projects': incomplete},
    }


def _periods_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start <= b_end and b_start <= a_end


def find_overlapping_lines(user, lines: list[dict], exclude_decision_id=None) -> list[dict]:
    overlaps = []
    existing = AllocationDecisionLine.objects.filter(
        is_deleted=False,
        decision__is_deleted=False,
        project_id__in=[ln['project_id'] for ln in lines],
    ).select_related('decision')
    if exclude_decision_id:
        existing = existing.exclude(decision_id=exclude_decision_id)

    visible_ids = set(projects_visible_for_cashflow(user).values_list('id', flat=True))
    for ln in lines:
        pid = ln['project_id']
        if pid not in visible_ids and str(pid) not in {str(x) for x in visible_ids}:
            # still check by string id
            pass
        p_start = ln['period_start'] if isinstance(ln['period_start'], date) else date.fromisoformat(str(ln['period_start'])[:10])
        p_end = ln['period_end'] if isinstance(ln['period_end'], date) else date.fromisoformat(str(ln['period_end'])[:10])
        for ex in existing:
            if str(ex.project_id) != str(pid):
                continue
            if _periods_overlap(p_start, p_end, ex.period_start, ex.period_end):
                overlaps.append(
                    {
                        'project_id': str(pid),
                        'existing_decision_id': str(ex.decision_id),
                        'period_start': ex.period_start.isoformat(),
                        'period_end': ex.period_end.isoformat(),
                    }
                )
    return overlaps


@transaction.atomic
def create_decision(cycle: LiquidityAllocationCycle, user, data: dict) -> AllocationDecision:
    owner_id = data.get('owner_id')
    rationale = (data.get('rationale') or '').strip()
    if not owner_id:
        raise CodedValidationError(detail='owner_id is required', code='owner_required')
    if not rationale:
        raise CodedValidationError(detail='rationale is required', code='rationale_required')

    lines = data.get('lines') or []
    acknowledge = bool(data.get('acknowledge_overlap'))
    overlaps = find_overlapping_lines(user, lines) if lines else []
    if overlaps and not acknowledge:
        raise CodedValidationError(
            detail={'code': 'overlapping_allocation', 'overlaps': overlaps},
            code='overlapping_allocation',
        )

    proposal = None
    proposal_id = data.get('proposal_id')
    if proposal_id:
        proposal = AllocationProposal.objects.filter(id=proposal_id, cycle=cycle).first()
    else:
        proposal = (
            AllocationProposal.objects.filter(cycle=cycle, is_deleted=False)
            .order_by('-generated_at')
            .first()
        )

    decision = AllocationDecision.objects.create(
        cycle=cycle,
        owner_id=owner_id,
        rationale=rationale,
        proposal=proposal,
        acknowledge_overlap=acknowledge,
        created_by=user,
        updated_by=user,
    )
    for ln in lines:
        AllocationDecisionLine.objects.create(
            decision=decision,
            project_id=ln['project_id'],
            amount=Decimal(str(ln['amount'])),
            period_start=ln['period_start']
            if isinstance(ln['period_start'], date)
            else date.fromisoformat(str(ln['period_start'])[:10]),
            period_end=ln['period_end']
            if isinstance(ln['period_end'], date)
            else date.fromisoformat(str(ln['period_end'])[:10]),
            schedule_impact=ln.get('schedule_impact') or '',
            cost_impact=ln.get('cost_impact') or '',
            created_by=user,
            updated_by=user,
        )

    cycle.status = LiquidityCycleStatus.DECIDED
    cycle.updated_by = user
    cycle.save(update_fields=['status', 'updated_by', 'updated_at'])
    return decision


def decision_to_dict(decision: AllocationDecision) -> dict:
    return {
        'id': str(decision.id),
        'cycle_id': str(decision.cycle_id),
        'owner_id': str(decision.owner_id),
        'rationale': decision.rationale,
        'decided_at': decision.decided_at.isoformat() if decision.decided_at else None,
        'acknowledge_overlap': decision.acknowledge_overlap,
        'proposal_id': str(decision.proposal_id) if decision.proposal_id else None,
        'lines': [
            {
                'project_id': str(ln.project_id),
                'amount': float(ln.amount),
                'period_start': ln.period_start.isoformat(),
                'period_end': ln.period_end.isoformat(),
                'schedule_impact': ln.schedule_impact,
                'cost_impact': ln.cost_impact,
            }
            for ln in decision.lines.filter(is_deleted=False)
        ],
    }


def save_simulation(cycle: LiquidityAllocationCycle, user, name: str, lines: list) -> AllocationSimulation:
    return AllocationSimulation.objects.create(
        cycle=cycle,
        name=name,
        payload={'lines': lines},
        created_by=user,
        updated_by=user,
    )


def compare_simulation(sim: AllocationSimulation) -> dict:
    proposal = (
        AllocationProposal.objects.filter(cycle_id=sim.cycle_id, is_deleted=False)
        .order_by('-generated_at')
        .first()
    )
    proposal_by_project = {}
    if proposal:
        for ln in proposal.lines.filter(is_deleted=False):
            proposal_by_project[str(ln.project_id)] = Decimal(ln.suggested_amount)

    sim_lines = (sim.payload or {}).get('lines') or []
    diffs = []
    seen = set()
    for ln in sim_lines:
        pid = str(ln['project_id'])
        seen.add(pid)
        sim_amt = Decimal(str(ln.get('amount') or 0))
        prop_amt = proposal_by_project.get(pid, Decimal('0'))
        diffs.append(
            {
                'project_id': pid,
                'simulation_amount': float(sim_amt),
                'proposal_amount': float(prop_amt),
                'diff': float(sim_amt - prop_amt),
            }
        )
    for pid, prop_amt in proposal_by_project.items():
        if pid in seen:
            continue
        diffs.append(
            {
                'project_id': pid,
                'simulation_amount': 0.0,
                'proposal_amount': float(prop_amt),
                'diff': float(-prop_amt),
            }
        )
    return {
        'simulation_id': str(sim.id),
        'proposal_id': str(proposal.id) if proposal else None,
        'diffs': diffs,
    }
