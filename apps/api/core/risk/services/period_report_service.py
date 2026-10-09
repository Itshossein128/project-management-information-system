"""Project + period quality/safety report aggregation."""

from __future__ import annotations

from datetime import date

from django.db.models import Q

from risk.models import (
    CorrectiveAction,
    HseEvent,
    HseEventKind,
    Inspection,
    Nonconformity,
    SafetyTraining,
    WorkPermit,
)


def _summary_row(*, id, event_date, description, status='', wbs=None, extra=None) -> dict:
    row = {
        'id': str(id),
        'date': event_date.isoformat() if event_date else None,
        'description': description or '',
        'status': status or '',
        'wbs': str(wbs) if wbs else None,
    }
    if extra:
        row.update(extra)
    return row


def build_quality_safety_period_report(
    project_id,
    date_from: date,
    date_to: date,
) -> dict:
    inspections = Inspection.objects.filter(
        project_id=project_id,
        inspection_date__gte=date_from,
        inspection_date__lte=date_to,
    )
    nonconformities = Nonconformity.objects.filter(
        project_id=project_id,
        raised_date__gte=date_from,
        raised_date__lte=date_to,
    )
    corrective_actions = CorrectiveAction.objects.filter(project_id=project_id).filter(
        Q(due_date__gte=date_from, due_date__lte=date_to)
        | Q(
            nonconformity__raised_date__gte=date_from,
            nonconformity__raised_date__lte=date_to,
        )
    ).distinct()

    incidents = HseEvent.objects.filter(
        project_id=project_id,
        kind=HseEventKind.INCIDENT,
        event_date__gte=date_from,
        event_date__lte=date_to,
    )
    near_misses = HseEvent.objects.filter(
        project_id=project_id,
        kind=HseEventKind.NEAR_MISS,
        event_date__gte=date_from,
        event_date__lte=date_to,
    )
    work_permits = WorkPermit.objects.filter(
        project_id=project_id,
        permit_date__gte=date_from,
        permit_date__lte=date_to,
    )
    trainings = SafetyTraining.objects.filter(
        project_id=project_id,
        training_date__gte=date_from,
        training_date__lte=date_to,
    )

    insp_rows = [
        _summary_row(
            id=i.id,
            event_date=i.inspection_date,
            description=i.description,
            status=i.result or '',
            wbs=i.wbs_id,
        )
        for i in inspections
    ]
    ncr_rows = [
        _summary_row(
            id=n.id,
            event_date=n.raised_date,
            description=n.description,
            status=n.status,
            wbs=n.wbs_id,
        )
        for n in nonconformities
    ]
    ca_rows = [
        _summary_row(
            id=c.id,
            event_date=c.due_date,
            description=c.description,
            status=c.status,
        )
        for c in corrective_actions
    ]
    incident_rows = [
        _summary_row(
            id=e.id,
            event_date=e.event_date,
            description=e.description,
            status=e.status,
            wbs=e.wbs_id,
            extra={'kind': e.kind},
        )
        for e in incidents
    ]
    near_rows = [
        _summary_row(
            id=e.id,
            event_date=e.event_date,
            description=e.description,
            status=e.status,
            wbs=e.wbs_id,
            extra={'kind': e.kind},
        )
        for e in near_misses
    ]
    permit_rows = [
        _summary_row(
            id=p.id,
            event_date=p.permit_date,
            description=p.description or p.permit_type,
            status=p.status,
        )
        for p in work_permits
    ]
    train_rows = [
        _summary_row(
            id=t.id,
            event_date=t.training_date,
            description=t.topic,
            status='',
        )
        for t in trainings
    ]

    return {
        'project_id': str(project_id),
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'inspections': insp_rows,
        'nonconformities': ncr_rows,
        'corrective_actions': ca_rows,
        'incidents': incident_rows,
        'near_misses': near_rows,
        'work_permits': permit_rows,
        'trainings': train_rows,
        'counts': {
            'inspections': len(insp_rows),
            'nonconformities': len(ncr_rows),
            'corrective_actions': len(ca_rows),
            'incidents': len(incident_rows),
            'near_misses': len(near_rows),
            'work_permits': len(permit_rows),
            'trainings': len(train_rows),
        },
    }
