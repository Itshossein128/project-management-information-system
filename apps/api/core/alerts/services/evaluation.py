"""Alert evaluation helpers — delegates to alert_engine."""

from alerts.services.alert_engine import fire_alert_for_type


def ensure_project_rules(project_id):
    """Legacy helper — default rules are seeded system-wide."""
    return None


def fire_subcontractor_at_risk(sub, reasons: list[str]):
    fire_alert_for_type(
        sub.project_id,
        'subcontractor_at_risk',
        f'sub_risk:{sub.id}',
        f'پیمانکار {sub.company_name} در وضعیت ریسک قرار گرفت: {"؛ ".join(reasons)}',
        link=f'/projects/{sub.project_id}/subcontractors/{sub.id}',
    )


def fire_cash_gap(project_id, month: str, amount: float):
    fire_alert_for_type(
        project_id,
        'cash_gap_detected',
        f'cash_gap:{month}',
        f'کمبود نقدینگی در {month}: مبلغ {amount:,.0f} ریال',
    )
