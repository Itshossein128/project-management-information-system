from rest_framework.exceptions import ValidationError
from risk.models import BarrierStatus

def validate_barrier_resolution(validated_data: dict, instance=None) -> None:
    """Ensure a resolved date is provided if the barrier log is resolved."""
    status = validated_data.get('status')
    if status == BarrierStatus.RESOLVED:
        resolved_date = validated_data.get('resolved_date')
        has_existing_date = instance and instance.resolved_date
        if not resolved_date and not has_existing_date:
            raise ValidationError(
                {'error': {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'}}
            )
