"""Business rules for user–business assignments (used by serializers)."""
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from business_meta.models import Business, BusinessJobPosition, UserBusinessAssignment

User = get_user_model()


@transaction.atomic
def create_assignment_for_user(
    *,
    business_id: int,
    user,
    job_position: BusinessJobPosition,
    **assignment_fields,
) -> UserBusinessAssignment:
    if job_position.business_id != business_id:
        raise ValidationError({'job_position': 'Job position does not belong to this business.'})
    if UserBusinessAssignment.objects.filter(business_id=business_id, user=user).exists():
        raise ValidationError({'user': 'This user is already assigned to this business.'})
    business = Business.objects.get(pk=business_id)
    return UserBusinessAssignment.objects.create(
        business=business,
        user=user,
        job_position=job_position,
        **assignment_fields,
    )
