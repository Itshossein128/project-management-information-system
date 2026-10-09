"""Meeting action helpers for open-actions report."""

from datetime import date

from django.utils import timezone

from documents.models import MeetingAction, MeetingActionStatus


def list_open_meeting_actions(project_id, *, overdue: bool = False):
    qs = MeetingAction.objects.filter(
        project_id=project_id,
        is_deleted=False,
        status=MeetingActionStatus.OPEN,
    ).select_related('meeting', 'owner')
    if overdue:
        qs = qs.filter(due_date__lt=date.today())
    return qs


def mark_meeting_action_done(action: MeetingAction, user) -> MeetingAction:
    action.status = MeetingActionStatus.DONE
    action.completed_at = timezone.now()
    action.updated_by = user
    action.save(update_fields=['status', 'completed_at', 'updated_by', 'updated_at'])
    return action
