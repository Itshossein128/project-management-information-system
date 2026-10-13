from rest_framework.exceptions import ValidationError
from risk.models import BarrierStatus, RiskStatus

def validate_barrier_resolution(instance, validated_data):
    new_status = validated_data.get('status')
    if new_status in (RiskStatus.CLOSED, BarrierStatus.RESOLVED):
        if not validated_data.get('resolved_date') and not instance.resolved_date:
            raise ValidationError(
                {'error': {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'}}
            )
