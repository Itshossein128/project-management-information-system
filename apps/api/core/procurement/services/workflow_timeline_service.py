"""Workflow timeline and approval visibility for procurement requisitions."""
from __future__ import annotations

from procurement.models import ApprovalAction, ApprovalLog, RequisitionScope, RequisitionStatus
from procurement.services.approval_engine import STEP_REQUIRED_ROLES, get_required_role

ROADMAP_STEP_CODES: list[str] = [
    RequisitionStatus.DRAFT,
    RequisitionStatus.TECHNICAL_REVIEW,
    RequisitionStatus.WORKSHOP_APPROVAL,
    RequisitionStatus.CONTROL_CHECK,
    RequisitionStatus.PM_APPROVAL,
    RequisitionStatus.PROCUREMENT_QUEUE,
    RequisitionStatus.HQ_CONTROL_APPROVAL,
    RequisitionStatus.FINAL_APPROVAL,
]

PROCUREMENT_ROLE_LABELS: dict[str, str] = {
    'block_engineer': 'مهندس بلوک',
    'technical_office': 'دفتر فنی',
    'workshop_supervisor': 'سرپرست کارگاه',
    'project_controller': 'کنترل پروژه',
    'project_manager': 'مدیر پروژه',
    'procurement_officer': 'کارپرداز',
    'hq_project_controller': 'کنترل پروژه دفتر مرکزی',
    'ceo_or_pm_budget': 'مدیرعامل / بودجه PM',
}


def _status_label(code: str) -> str:
    if not code:
        return ''
    try:
        return RequisitionStatus(code).label
    except ValueError:
        return code


def _role_label(role_code: str | None) -> str | None:
    if not role_code:
        return None
    return PROCUREMENT_ROLE_LABELS.get(role_code, role_code)


def _effective_steps(requisition) -> list[str]:
    """Roadmap step codes that count toward progress (excludes skipped workshop step)."""
    if requisition.scope == RequisitionScope.WORKSHOP:
        return [s for s in ROADMAP_STEP_CODES if s != RequisitionStatus.WORKSHOP_APPROVAL]
    return list(ROADMAP_STEP_CODES)


def _get_logs(requisition) -> list:
    if hasattr(requisition, '_prefetched_objects_cache') and 'approval_logs' in requisition._prefetched_objects_cache:
        logs = list(requisition.approval_logs.all())
        if len(logs) > 1 and logs[0].performed_at > logs[-1].performed_at:
            logs.reverse()
        return logs
    return list(
        ApprovalLog.objects.filter(requisition=requisition)
        .select_related('performed_by')
        .order_by('performed_at')
    )


def _get_latest_log(requisition):
    prefetched = getattr(requisition, '_prefetched_objects_cache', None)
    if prefetched and 'approval_logs' in prefetched:
        logs = list(requisition.approval_logs.all())
        if logs:
            if len(logs) > 1 and logs[0].performed_at < logs[-1].performed_at:
                return logs[-1]
            return logs[0]
    return (
        ApprovalLog.objects.filter(requisition=requisition)
        .select_related('performed_by')
        .order_by('-performed_at')
        .first()
    )


def _performer_name(user) -> str | None:
    return str(user) if user else None


def get_role_label(role_code: str | None) -> str | None:
    return _role_label(role_code)


def get_roadmap_steps(requisition) -> list[dict]:
    skip_workshop = requisition.scope == RequisitionScope.WORKSHOP
    steps = []
    for code in ROADMAP_STEP_CODES:
        is_skipped = code == RequisitionStatus.WORKSHOP_APPROVAL and skip_workshop
        role = STEP_REQUIRED_ROLES.get(code)
        if code == RequisitionStatus.DRAFT:
            from procurement.services.approval_engine import DRAFT_ROLE_BY_SCOPE
            role = DRAFT_ROLE_BY_SCOPE.get(requisition.scope, 'block_engineer')
        steps.append({
            'code': code,
            'label': _status_label(code),
            'required_role': role,
            'required_role_label': _role_label(role),
            'skipped': is_skipped,
        })
    return steps


def _step_index(code: str) -> int:
    try:
        return ROADMAP_STEP_CODES.index(code)
    except ValueError:
        return -1


def _completed_step_codes(requisition, logs: list) -> dict[str, dict]:
    """Map step code -> completion info from approve logs."""
    completed: dict[str, dict] = {}
    for log in logs:
        if log.action == ApprovalAction.APPROVE and log.step_from:
            completed[log.step_from] = {
                'completed_at': log.performed_at.isoformat(),
                'completed_by_name': _performer_name(log.performed_by),
            }
    return completed


def _partial_events(logs: list) -> list[dict]:
    events = []
    for log in logs:
        if log.action != ApprovalAction.PARTIAL_APPROVE:
            continue
        events.append({
            'at': log.performed_at.isoformat(),
            'by_name': _performer_name(log.performed_by),
            'action': log.action,
            'action_display': log.get_action_display(),
            'details': log.details or [],
        })
    return events


def build_workflow_timeline(requisition) -> list[dict]:
    logs = _get_logs(requisition)
    roadmap = get_roadmap_steps(requisition)
    completed_map = _completed_step_codes(requisition, logs)
    partial_events = _partial_events(logs)

    current_status = requisition.status
    is_terminal_approved = current_status == RequisitionStatus.APPROVED
    is_rejected = current_status == RequisitionStatus.REJECTED

    rejection_step = None
    if is_rejected:
        for log in reversed(logs):
            if log.action == ApprovalAction.REJECT:
                rejection_step = log.step_from
                break

    current_idx = _step_index(current_status) if current_status in ROADMAP_STEP_CODES else -1

    timeline = []
    for step_def in roadmap:
        code = step_def['code']
        entry: dict = {
            'code': code,
            'label': step_def['label'],
            'required_role': step_def['required_role'],
            'required_role_label': step_def['required_role_label'],
            'skipped': step_def['skipped'],
            'state': 'pending',
            'completed_at': None,
            'completed_by_name': None,
            'sub_events': [],
        }

        if step_def['skipped']:
            entry['state'] = 'skipped'
        elif is_terminal_approved:
            entry['state'] = 'completed'
            info = completed_map.get(code)
            if info:
                entry['completed_at'] = info['completed_at']
                entry['completed_by_name'] = info['completed_by_name']
        elif is_rejected and code == rejection_step:
            entry['state'] = 'rejected'
            for log in reversed(logs):
                if log.action == ApprovalAction.REJECT and log.step_from == code:
                    entry['completed_at'] = log.performed_at.isoformat()
                    entry['completed_by_name'] = _performer_name(log.performed_by)
                    break
        elif code == current_status and current_status in ROADMAP_STEP_CODES:
            entry['state'] = 'current'
        elif _step_index(code) < current_idx and current_idx >= 0:
            entry['state'] = 'completed'
            info = completed_map.get(code)
            if info:
                entry['completed_at'] = info['completed_at']
                entry['completed_by_name'] = info['completed_by_name']
        elif code in completed_map:
            entry['state'] = 'completed'
            info = completed_map[code]
            entry['completed_at'] = info['completed_at']
            entry['completed_by_name'] = info['completed_by_name']

        if code == RequisitionStatus.FINAL_APPROVAL and partial_events:
            entry['sub_events'] = partial_events

        timeline.append(entry)

    return timeline


def compute_workflow_progress(requisition) -> str:
    effective = _effective_steps(requisition)
    total = len(effective)
    if requisition.status == RequisitionStatus.APPROVED:
        return f'{total}/{total}'

    completed_count = 0
    current_idx = _step_index(requisition.status)
    for code in effective:
        idx = _step_index(code)
        if current_idx >= 0 and idx < current_idx:
            completed_count += 1

    return f'{completed_count}/{total}'


def get_current_step_label(requisition) -> str | None:
    if requisition.status in (RequisitionStatus.APPROVED, RequisitionStatus.REJECTED):
        return _status_label(requisition.status)
    if requisition.status in ROADMAP_STEP_CODES:
        return _status_label(requisition.status)
    return None


def get_next_approver(requisition) -> dict | None:
    if requisition.status in (RequisitionStatus.APPROVED, RequisitionStatus.REJECTED):
        return None
    role = get_required_role(requisition)
    if not role:
        return None
    return {
        'role': role,
        'role_label': _role_label(role),
    }


def get_last_action_summary(requisition) -> dict | None:
    log = _get_latest_log(requisition)
    if log is None:
        return None
    step_label = _status_label(log.step_to or log.step_from)
    if log.action == ApprovalAction.CREATE:
        step_label = _status_label(RequisitionStatus.DRAFT)
    elif log.action == ApprovalAction.PARTIAL_APPROVE:
        step_label = _status_label(RequisitionStatus.FINAL_APPROVAL)
    return {
        'at': log.performed_at.isoformat(),
        'by_name': _performer_name(log.performed_by),
        'action': log.action,
        'action_display': log.get_action_display(),
        'step_label': step_label,
    }


def build_approval_summary(requisition) -> dict:
    return {
        'last_action': get_last_action_summary(requisition),
        'workflow_progress': compute_workflow_progress(requisition),
        'workflow_step_label': get_current_step_label(requisition),
    }


def log_requisition_created(header, user) -> ApprovalLog:
    return ApprovalLog.objects.create(
        requisition=header,
        step_from='',
        step_to=RequisitionStatus.DRAFT,
        action=ApprovalAction.CREATE,
        performed_by=user,
        comments='',
    )


def log_partial_approve(requisition, user, updated_items: list) -> ApprovalLog:
    details = []
    for item in updated_items:
        details.append({
            'item_id': str(item.id),
            'line_number': item.line_number,
            'material_code': item.material.material_code,
            'requested_qty': str(item.requested_qty),
            'approved_qty': str(item.approved_qty) if item.approved_qty is not None else None,
            'status': item.status,
        })
    return ApprovalLog.objects.create(
        requisition=requisition,
        step_from=RequisitionStatus.FINAL_APPROVAL,
        step_to=RequisitionStatus.FINAL_APPROVAL,
        action=ApprovalAction.PARTIAL_APPROVE,
        performed_by=user,
        comments='',
        details=details,
    )
