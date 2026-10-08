"""Schedule change request lifecycle: draft → submit → approve/reject."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from config.exceptions import ConflictError, CodedValidationError
from projects.models import Activity
from schedule.models import (
    BaselineSchedule,
    ScheduleChangeItem,
    ScheduleChangeRequest,
    ScheduleChangeRequestStatus,
)
from schedule.services.activity_validation import validate_activity_dates
from schedule.services.baseline_service import create_baseline_snapshot


def list_change_requests(project_id):
    return (
        ScheduleChangeRequest.objects.filter(project_id=project_id)
        .select_related('base_baseline', 'resulting_baseline', 'created_by', 'decided_by')
        .prefetch_related('items')
        .order_by('-created_at')
    )


@transaction.atomic
def create_change_request(*, project_id, user, reason='', milestone_impact='', cost_impact='', contract_impact='', items=None) -> ScheduleChangeRequest:
    base = BaselineSchedule.objects.filter(
        project_id=project_id,
        is_current=True,
        is_locked=True,
    ).first()
    if base is None:
        base = BaselineSchedule.objects.filter(
            project_id=project_id,
            is_locked=True,
        ).order_by('-locked_at').first()

    scr = ScheduleChangeRequest.objects.create(
        project_id=project_id,
        base_baseline=base,
        reason=reason or '',
        milestone_impact=milestone_impact or '',
        cost_impact=cost_impact or '',
        contract_impact=contract_impact or '',
        status=ScheduleChangeRequestStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    _replace_items(scr, items or [], project_id)
    return scr


@transaction.atomic
def update_change_request(scr: ScheduleChangeRequest, user, **fields) -> ScheduleChangeRequest:
    if scr.status != ScheduleChangeRequestStatus.DRAFT:
        raise ConflictError('Only draft change requests can be updated.', code='conflict')
    for key in ('reason', 'milestone_impact', 'cost_impact', 'contract_impact'):
        if key in fields and fields[key] is not None:
            setattr(scr, key, fields[key])
    scr.updated_by = user
    scr.save()
    if 'items' in fields and fields['items'] is not None:
        scr.items.all().delete()
        _replace_items(scr, fields['items'], scr.project_id)
    return scr


def _replace_items(scr: ScheduleChangeRequest, items: list, project_id) -> None:
    for item in items:
        activity_id = item.get('activity_id') or item.get('activity')
        if not activity_id:
            raise CodedValidationError(detail='activity_id is required on items.', code='validation_error')
        if not Activity.objects.filter(pk=activity_id, project_id=project_id, is_deleted=False).exists():
            raise CodedValidationError(detail='Activity not found in project.', code='validation_error')
        ScheduleChangeItem.objects.create(
            change_request=scr,
            activity_id=activity_id,
            proposed_planned_start=item.get('proposed_planned_start'),
            proposed_planned_finish=item.get('proposed_planned_finish'),
            proposed_duration_days=item.get('proposed_duration_days'),
            proposed_forecast_start=item.get('proposed_forecast_start'),
            proposed_forecast_finish=item.get('proposed_forecast_finish'),
            notes=item.get('notes') or '',
        )


@transaction.atomic
def submit_change_request(scr: ScheduleChangeRequest, user) -> ScheduleChangeRequest:
    if scr.status != ScheduleChangeRequestStatus.DRAFT:
        raise ConflictError('Only draft change requests can be submitted.', code='conflict')

    for field, label in (
        ('reason', 'reason'),
        ('milestone_impact', 'milestone_impact'),
        ('cost_impact', 'cost_impact'),
        ('contract_impact', 'contract_impact'),
    ):
        if not (getattr(scr, field) or '').strip():
            raise CodedValidationError(
                detail=f'{label} is required to submit.',
                code='validation_error',
            )

    if ScheduleChangeRequest.objects.filter(
        project_id=scr.project_id,
        status=ScheduleChangeRequestStatus.SUBMITTED,
        is_deleted=False,
    ).exclude(pk=scr.pk).exists():
        raise ConflictError(
            'Another schedule change request is already submitted.',
            code='schedule_change_in_flight',
        )

    scr.status = ScheduleChangeRequestStatus.SUBMITTED
    scr.submitted_at = timezone.now()
    scr.updated_by = user
    scr.save()
    return scr


@transaction.atomic
def approve_change_request(scr: ScheduleChangeRequest, user, decision_notes='') -> ScheduleChangeRequest:
    if scr.status != ScheduleChangeRequestStatus.SUBMITTED:
        raise ConflictError('Only submitted change requests can be approved.', code='conflict')

    for item in scr.items.select_related('activity'):
        activity = item.activity
        updates = {}
        if item.proposed_planned_start is not None:
            updates['planned_start'] = item.proposed_planned_start
        if item.proposed_planned_finish is not None:
            updates['planned_finish'] = item.proposed_planned_finish
        if item.proposed_duration_days is not None:
            updates['duration_days'] = item.proposed_duration_days
        if item.proposed_forecast_start is not None:
            updates['forecast_start'] = item.proposed_forecast_start
        if item.proposed_forecast_finish is not None:
            updates['forecast_finish'] = item.proposed_forecast_finish

        if not updates:
            continue

        merged = {
            'planned_start': updates.get('planned_start', activity.planned_start),
            'planned_finish': updates.get('planned_finish', activity.planned_finish),
            'forecast_start': updates.get('forecast_start', activity.forecast_start),
            'forecast_finish': updates.get('forecast_finish', activity.forecast_finish),
            'duration_days': updates.get('duration_days', activity.duration_days),
            'is_milestone': activity.is_milestone,
        }
        validate_activity_dates(
            project_id=scr.project_id,
            working_calendar_id=activity.working_calendar_id,
            activity=activity,
            **merged,
        )
        for key, value in updates.items():
            setattr(activity, key, value)
        activity.updated_by = user
        activity.save()

    version_name = f'SCR-{timezone.now().strftime("%Y%m%d-%H%M%S")}'
    baseline = create_baseline_snapshot(
        project_id=scr.project_id,
        version_name=version_name,
        user=user,
        make_current=False,
        source_change_request=scr,
        is_locked=True,
    )

    scr.status = ScheduleChangeRequestStatus.APPROVED
    scr.decided_by = user
    scr.decided_at = timezone.now()
    scr.decision_notes = decision_notes or ''
    scr.resulting_baseline = baseline
    scr.updated_by = user
    scr.save()
    return scr


@transaction.atomic
def reject_change_request(scr: ScheduleChangeRequest, user, decision_notes='') -> ScheduleChangeRequest:
    if scr.status != ScheduleChangeRequestStatus.SUBMITTED:
        raise ConflictError('Only submitted change requests can be rejected.', code='conflict')
    scr.status = ScheduleChangeRequestStatus.REJECTED
    scr.decided_by = user
    scr.decided_at = timezone.now()
    scr.decision_notes = decision_notes or ''
    scr.updated_by = user
    scr.save()
    return scr
