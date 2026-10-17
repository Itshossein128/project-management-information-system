from django.utils.translation import gettext as _
from config.exceptions import CodedValidationError
from risk.models import RiskStatus, BarrierStatus, RiskActionStatus

def validate_barrier_status_update(instance, validated_data):
    new_status = validated_data.get('status')
    if new_status in (RiskStatus.CLOSED, BarrierStatus.RESOLVED):
        if not validated_data.get('resolved_date') and not instance.resolved_date:
            raise CodedValidationError(
                detail=_('برای وضعیت رفع شده، تاریخ رفع الزامی است.'),
                code='missing_resolved_date'
            )

def validate_risk_event_status_update(instance, validated_data, request_data):
    new_status = validated_data.get('status')
    if new_status == RiskStatus.CLOSED:
        open_count = instance.actions.filter(
            status=RiskActionStatus.OPEN,
            is_deleted=False,
        ).count()
        ack = bool(request_data.get('acknowledge_open_actions'))
        if open_count and not ack:
            raise CodedValidationError(
                detail={
                    'code': 'open_actions_warning',
                    'message': _('اقدامات باز وجود دارد. برای بستن، تأیید کنید.'),
                    'open_actions_count': open_count,
                },
                code='open_actions_warning',
            )