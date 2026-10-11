from rest_framework.exceptions import ValidationError
from risk.models import RiskStatus, BarrierStatus, RiskActionStatus

def validate_barrier_update(instance, validated_data):
    new_status = validated_data.get('status')
    if new_status in (RiskStatus.CLOSED, BarrierStatus.RESOLVED):
        if not validated_data.get('resolved_date') and not instance.resolved_date:
            raise ValidationError(
                {'error': {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'}}
            )

def validate_risk_event_update(instance, validated_data, request_data):
    new_status = validated_data.get('status')
    if new_status == RiskStatus.CLOSED:
        open_count = instance.actions.filter(
            status=RiskActionStatus.OPEN,
            is_deleted=False,
        ).count()
        ack = bool(request_data.get('acknowledge_open_actions'))
        if open_count and not ack:
            raise ValidationError(
                {
                    'code': 'open_actions_warning',
                    'error': {
                        'code': 'open_actions_warning',
                        'message': 'اقدامات باز وجود دارد. برای بستن، تأیید کنید.',
                        'open_actions_count': open_count,
                    },
                }
            )
