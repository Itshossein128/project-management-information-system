"""Activity CRUD helpers, filters, and weight summary."""

from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from config.exceptions import ConflictError
from projects.models import Activity, ActivityStatus, WBS
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule


def get_wbs_descendant_ids(project_id, wbs_id: UUID) -> list[UUID]:
    """Return wbs_id and all descendant node ids for the project."""
    try:
        node = WBS.objects.get(pk=wbs_id, project_id=project_id)
    except WBS.DoesNotExist:
        return []
    ids = [node.id]
    for descendant in node.get_descendants():
        ids.append(descendant.id)
    return ids


def filter_activities_queryset(qs: QuerySet, project_id, params) -> QuerySet:
    wbs_id = params.get('wbs_id')
    if wbs_id:
        wbs_ids = get_wbs_descendant_ids(project_id, wbs_id)
        if wbs_ids:
            qs = qs.filter(wbs_id__in=wbs_ids)
        else:
            qs = qs.none()

    status = params.get('status')
    if status:
        qs = qs.filter(status=status)

    responsible_id = params.get('responsible_id')
    if responsible_id:
        qs = qs.filter(responsible_id=responsible_id)

    is_overdue = params.get('is_overdue')
    if is_overdue and str(is_overdue).lower() in ('true', '1', 'yes'):
        today = timezone.localdate()
        qs = qs.filter(
            planned_finish__lt=today,
        ).exclude(status=ActivityStatus.COMPLETED)

    search = (params.get('search') or '').strip()
    if search:
        qs = qs.filter(
            Q(activity_name__icontains=search) | Q(activity_code__icontains=search),
        )

    ordering = params.get('ordering', 'activity_code')
    allowed = {
        'activity_code', '-activity_code',
        'activity_name', '-activity_name',
        'planned_start', '-planned_start',
        'planned_finish', '-planned_finish',
        'status', '-status',
    }
    if ordering in allowed:
        qs = qs.order_by(ordering)
    else:
        qs = qs.order_by('activity_code')

    return qs


def base_activity_queryset(project_id):
    return (
        Activity.objects.filter(project_id=project_id)
        .select_related('wbs', 'responsible', 'unit', 'project')
        .annotate(
            predecessor_count=Count(
                'predecessor_relations',
                filter=Q(predecessor_relations__is_deleted=False),
            ),
            successor_count=Count(
                'successor_relations',
                filter=Q(successor_relations__is_deleted=False),
            ),
        )
    )


def compute_weight_summary(project_id) -> dict:
    activities = Activity.objects.filter(project_id=project_id)
    total = Decimal('0')
    for act in activities:
        if act.weight is not None:
            total += act.weight

    remaining = Decimal('1') - total
    is_balanced = abs(total - Decimal('1')) <= Decimal('0.01')
    warning = None
    if not is_balanced:
        total_pct = int(round(float(total) * 100))
        remaining_pct = int(round(abs(float(remaining)) * 100))
        if total < Decimal('1'):
            warning = (
                f'مجموع وزن فعالیت‌ها {total_pct}٪ است. '
                f'برای تکمیل {remaining_pct}٪ باقی‌مانده اقدام کنید.'
            )
        else:
            warning = f'مجموع وزن فعالیت‌ها {total_pct}٪ است و از ۱۰۰٪ بیشتر است.'

    return {
        'total_weight': float(total),
        'remaining': float(remaining),
        'is_balanced': is_balanced,
        'warning': warning,
    }


def assert_can_delete_activity(activity: Activity) -> None:
    if ActivityProgress.objects.filter(activity=activity).exists():
        raise ConflictError('این فعالیت دارای رکورد پیشرفت است و قابل حذف نیست')


@transaction.atomic
def create_activity(*, project_id, user, **fields) -> Activity:
    return Activity.objects.create(
        project_id=project_id,
        created_by=user,
        updated_by=user,
        **fields,
    )


@transaction.atomic
def update_activity(activity: Activity, user, **fields) -> Activity:
    for key, value in fields.items():
        setattr(activity, key, value)
    activity.updated_by = user
    activity.save()
    return activity


def get_activity_network(project_id) -> dict:
    activities = list(
        Activity.objects.filter(project_id=project_id).order_by('activity_code'),
    )
    current_baseline = BaselineSchedule.objects.filter(
        project_id=project_id,
        is_current=True,
    ).first()

    critical_ids: set = set()
    if current_baseline:
        critical_ids = set(
            BaselineActivity.objects.filter(
                baseline=current_baseline,
                is_critical=True,
            ).values_list('activity_id', flat=True),
        )

    nodes = [
        {
            'id': str(act.id),
            'code': act.activity_code,
            'name': act.activity_name,
            'status': act.status,
            'planned_start': act.planned_start.isoformat() if act.planned_start else None,
            'planned_finish': act.planned_finish.isoformat() if act.planned_finish else None,
            'is_critical': act.id in critical_ids,
        }
        for act in activities
    ]

    from projects.models import ActivityRelation

    edges = [
        {
            'from': str(rel.predecessor_id),
            'to': str(rel.successor_id),
            'relation_type': rel.relation_type,
            'lag_days': rel.lag_days,
        }
        for rel in ActivityRelation.objects.filter(
            predecessor__project_id=project_id,
        ).select_related('predecessor', 'successor')
    ]

    return {'nodes': nodes, 'edges': edges}
