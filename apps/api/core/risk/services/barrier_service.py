from rest_framework.exceptions import ValidationError
from risk.models import BarrierStatus

def validate_barrier_resolution(validated_data, instance):
    """Ensure a resolved date is provided if the barrier log's status is changed to resolved."""
    if validated_data.get('status') == BarrierStatus.RESOLVED:
        if not validated_data.get('resolved_date') and not instance.resolved_date:
            raise ValidationError(
                {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'},
            )
