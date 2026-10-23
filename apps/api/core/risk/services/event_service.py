from typing import Dict, Any
from rest_framework.exceptions import APIException
from rest_framework import status
from config.exceptions import CodedValidationError
from risk.models import RiskEvent, RiskStatus, BarrierStatus, RiskActionStatus, EventType

class OpenActionsWarningException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'open_actions_warning'

    def __init__(self, open_actions_count: int):
        self.detail = {
            'code': 'open_actions_warning',
            'error': {
                'code': 'open_actions_warning',
                'message': 'اقدامات باز وجود دارد. برای بستن، تأیید کنید.',
                'open_actions_count': open_actions_count,
            }
        }

def validate_barrier_update(instance: Any, validated_data: Dict[str, Any]) -> None:
    new_status = validated_data.get('status')
    if new_status in (RiskStatus.CLOSED, BarrierStatus.RESOLVED):
        if not validated_data.get('resolved_date') and not instance.resolved_date:
            raise CodedValidationError(
                {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'},
                code='validation_error'
            )

def validate_risk_update(instance: RiskEvent, validated_data: Dict[str, Any], acknowledge_open_actions: bool = False) -> None:
    new_status = validated_data.get('status')
    if new_status == RiskStatus.CLOSED:
        open_count = instance.actions.filter(
            status=RiskActionStatus.OPEN,
            is_deleted=False,
        ).count()
        if open_count and not acknowledge_open_actions:
            raise OpenActionsWarningException(open_actions_count=open_count)
