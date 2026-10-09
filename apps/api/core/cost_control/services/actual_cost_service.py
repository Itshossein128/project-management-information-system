"""Actual cost approve/void lifecycle."""

from __future__ import annotations

from rest_framework.exceptions import ValidationError

from cost_control.models import ActualCost, ActualCostStatus
from projects.models import CapabilityMode, ProjectCapabilitySetting


REQUIRE_COST_DOCUMENT_KEY = 'require_cost_document'


def _invalidate_evm_caches(project_id) -> None:
    """Clear progress/EVM caches so AC mutations are visible on next KPI read."""
    try:
        from schedule.services.progress_service import invalidate_progress_caches

        invalidate_progress_caches(project_id)
    except Exception:  # noqa: BLE001 - cache is best-effort
        pass


def project_requires_cost_document(project) -> bool:
    row = ProjectCapabilitySetting.objects.filter(
        project=project,
        capability_key=REQUIRE_COST_DOCUMENT_KEY,
        enabled=True,
    ).first()
    if not row:
        return False
    return row.mode != CapabilityMode.DISABLED


def approve_actual_cost(actual: ActualCost, user) -> ActualCost:
    from permissions.sod import assert_not_self_final_approve

    assert_not_self_final_approve(actual.created_by_id, user)
    if actual.status == ActualCostStatus.VOID:
        raise ValidationError(
            {
                'code': 'invalid_status_transition',
                'message': 'Cannot approve a void actual cost.',
            }
        )
    if actual.status == ActualCostStatus.APPROVED:
        return actual
    if not actual.wbs_id and not actual.cbs_id:
        raise ValidationError(
            {
                'code': 'wbs_or_cbs_required',
                'message': 'Approve requires wbs or cbs.',
            }
        )
    if project_requires_cost_document(actual.project):
        doc = (actual.invoice_number or '').strip() or (actual.document_ref or '').strip()
        if not doc:
            raise ValidationError(
                {
                    'code': 'cost_document_required',
                    'message': 'Supporting document is required by project policy.',
                }
            )
    actual.status = ActualCostStatus.APPROVED
    actual.approved_by = user
    actual.save(update_fields=['status', 'approved_by', 'updated_at'])
    _invalidate_evm_caches(actual.project_id)
    return actual


def void_actual_cost(actual: ActualCost, user=None) -> ActualCost:
    if actual.status != ActualCostStatus.APPROVED:
        raise ValidationError(
            {
                'code': 'invalid_status_transition',
                'message': 'Only approved actual costs can be voided.',
            }
        )
    actual.status = ActualCostStatus.VOID
    update_fields = ['status', 'updated_at']
    if user is not None:
        actual.updated_by = user
        update_fields.append('updated_by')
    actual.save(update_fields=update_fields)
    _invalidate_evm_caches(actual.project_id)
    return actual
