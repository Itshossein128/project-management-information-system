"""Live manager notification for fast-track purchase requisitions."""

from __future__ import annotations

import logging

from procurement.models import RequisitionHeader, RequisitionType

logger = logging.getLogger(__name__)

ALERT_TYPE = 'procurement_fast_track'


def fast_track_trigger_ref(requisition: RequisitionHeader) -> str:
    return f'fast_track:{requisition.id}'


def fast_track_link(requisition: RequisitionHeader) -> str:
    return f'/projects/{requisition.project_id}/procurement/req/{requisition.id}'


def fast_track_message(requisition: RequisitionHeader) -> str:
    extra = f' — {requisition.urgency}' if requisition.urgency else ''
    return (
        f'درخواست خرید فورس‌ماژور {requisition.requisition_number} ثبت شد{extra}. '
        'نیاز به توجه فوری مدیر پروژه دارد.'
    )


def notify_fast_track_requisition(requisition: RequisitionHeader):
    """Fire the seeded fast-track alert. Cooldown prevents duplicate in-app/email spam."""
    if getattr(requisition, 'is_deleted', False):
        return None
    if requisition.requisition_type != RequisitionType.FAST_TRACK:
        return None

    try:
        from alerts.services.alert_engine import fire_alert_for_type

        return fire_alert_for_type(
            requisition.project_id,
            ALERT_TYPE,
            fast_track_trigger_ref(requisition),
            fast_track_message(requisition),
            link=fast_track_link(requisition),
        )
    except Exception:  # noqa: BLE001
        logger.exception(
            'Fast-track notify failed for requisition %s',
            getattr(requisition, 'id', None),
        )
        return None
