from rest_framework.exceptions import ValidationError

from risk.models import RiskStatus, RiskActionStatus, BarrierStatus


def validate_barrier_closure(barrier_event, validated_data: dict) -> None:
    new_status = validated_data.get('status')

    if new_status in (RiskStatus.CLOSED, getattr(BarrierStatus, 'RESOLVED', 'resolved')):
        if not validated_data.get('resolved_date') and not barrier_event.resolved_date:
            raise ValidationError(
                {'error': {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'}}
            )


def validate_risk_closure(risk_event, validated_data: dict, request_data: dict) -> None:
    new_status = validated_data.get('status')

    if new_status == RiskStatus.CLOSED:
        open_count = risk_event.actions.filter(
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
