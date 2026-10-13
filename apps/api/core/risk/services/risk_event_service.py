from rest_framework.exceptions import ValidationError
from risk.models import RiskActionStatus, RiskStatus

def validate_risk_event_closure(instance, validated_data, acknowledge_open_actions=False):
    new_status = validated_data.get('status')
    if new_status == RiskStatus.CLOSED:
        open_count = instance.actions.filter(
            status=RiskActionStatus.OPEN,
            is_deleted=False,
        ).count()
        if open_count and not acknowledge_open_actions:
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
