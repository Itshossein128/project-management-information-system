from rest_framework.exceptions import ValidationError

from risk.models import BarrierStatus


def validate_barrier_resolution(status: str | None, resolved_date, existing_resolved_date) -> None:
    """Ensure a resolved date is provided if the barrier log's status is changed to resolved."""
    if status == BarrierStatus.RESOLVED:
        if not resolved_date and not existing_resolved_date:
            raise ValidationError({'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'})
