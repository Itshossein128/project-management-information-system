"""Activity relation create/delete with validation."""

from uuid import UUID

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from config.exceptions import ConflictError
from projects.models import Activity, ActivityRelation, RelationType
from schedule.services.cycle_detection import CYCLE_ERROR_MESSAGE, would_create_cycle


class RelationValidationError(ValidationError):
    pass


def _ensure_same_project(predecessor: Activity, successor: Activity) -> None:
    if predecessor.project_id != successor.project_id:
        raise ValidationError('پیش‌نیاز و جانشین باید متعلق به یک پروژه باشند.')


def create_activity_relation(
    *,
    project_id,
    predecessor_id: UUID,
    successor_id: UUID,
    relation_type: str = RelationType.FS,
    lag_days: int = 0,
    user,
) -> ActivityRelation:
    predecessor = Activity.objects.get(pk=predecessor_id, project_id=project_id)
    successor = Activity.objects.get(pk=successor_id, project_id=project_id)
    _ensure_same_project(predecessor, successor)

    if ActivityRelation.objects.filter(
        predecessor=predecessor,
        successor=successor,
    ).exists():
        raise ConflictError('این ارتباط قبلاً ثبت شده است.')

    if would_create_cycle(project_id, predecessor_id, successor_id):
        raise ValidationError(CYCLE_ERROR_MESSAGE)

    return ActivityRelation.objects.create(
        predecessor=predecessor,
        successor=successor,
        relation_type=relation_type,
        lag_days=lag_days,
        created_by=user,
        updated_by=user,
    )


@transaction.atomic
def create_relation_from_anchor(
    *,
    project_id,
    anchor_activity_id: UUID,
    role: str,
    other_activity_id: UUID,
    relation_type: str,
    lag_days: int,
    user,
) -> ActivityRelation:
    if role == 'predecessor':
        predecessor_id = anchor_activity_id
        successor_id = other_activity_id
    elif role == 'successor':
        predecessor_id = other_activity_id
        successor_id = anchor_activity_id
    else:
        raise ValidationError({'role': 'نقش باید predecessor یا successor باشد.'})

    return create_activity_relation(
        project_id=project_id,
        predecessor_id=predecessor_id,
        successor_id=successor_id,
        relation_type=relation_type,
        lag_days=lag_days,
        user=user,
    )


def soft_delete_relation(relation: ActivityRelation, user) -> None:
    relation.is_deleted = True
    relation.deleted_at = timezone.now()
    relation.updated_by = user
    relation.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
