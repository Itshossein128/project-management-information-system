from config.exceptions import ValidationError
from risk.models import BarrierStatus

def validate_barrier_resolution(serializer_data, instance=None):
    """
    Ensure a resolved date is provided if the barrier log's status is changed to resolved.
    """
    status = serializer_data.get('status')
    resolved_date = serializer_data.get('resolved_date')

    if status == BarrierStatus.RESOLVED:
        has_resolved_date = resolved_date or (instance and instance.resolved_date)
        if not has_resolved_date:
            raise ValidationError({'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'})
