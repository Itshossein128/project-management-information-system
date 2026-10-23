"""Document-anchored material reconciliation service (feature 033, task T037).

Compares each material row on a project daily report against the specific
project-scoped warehouse document record referenced by
``warehouse_document_reference`` (R5 / FR-023 / FR-024). Never uses total
inventory balance as the reconciliation basis; global balance is retained
only under the explicitly labeled ``cross_check`` advisory key.
"""
from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from field_reports.models import (
    DailyReport,
    MaterialTransactionType,
    ReconciliationStatus,
)
from resources.services.balance_service import compute_material_balance
from sub_reports.services.section_validation import resolve_warehouse_document


def reconcile_material_row(project_id, row) -> tuple[str, object | None]:
    """Resolve the referenced warehouse document and compute reconciliation status."""
    doc_ref = (getattr(row, 'warehouse_document_reference', '') or '').strip()
    if not doc_ref:
        return ReconciliationStatus.INSUFFICIENT_DATA, None

    resolved_doc = resolve_warehouse_document(
        project_id, doc_ref, getattr(row, 'material_ref_id', None)
    )
    if resolved_doc is None or getattr(resolved_doc, 'quantity', None) is None:
        return ReconciliationStatus.INSUFFICIENT_DATA, None

    recorded_qty = Decimal(str(row.quantity))
    document_qty = Decimal(str(resolved_doc.quantity))
    status = (
        ReconciliationStatus.MATCH
        if recorded_qty == document_qty
        else ReconciliationStatus.MISMATCH
    )
    return status, resolved_doc


def reconcile_report_materials(report: DailyReport) -> dict:
    """Reconcile all active material rows on ``report`` against specific warehouse documents."""
    items = []
    now = timezone.now()
    rows = (
        report.material_entries.filter(is_deleted=False)
        .select_related('material_ref')
        .order_by('id')
    )

    for row in rows:
        status, resolved_doc = reconcile_material_row(report.project_id, row)
        doc_id_str = str(resolved_doc.id) if resolved_doc is not None else ''

        update_fields = [
            'reconciliation_status',
            'reconciliation_document_id',
            'reconciliation_checked_at',
        ]
        row.reconciliation_status = status
        row.reconciliation_document_id = doc_id_str
        row.reconciliation_checked_at = now
        if row.transaction_type == MaterialTransactionType.RECEIPT and (
            row.warehouse_document_reference or ''
        ).strip():
            # Keep receipt_resolved aligned when a document is resolved
            if resolved_doc is not None and not row.receipt_resolved:
                row.receipt_resolved = True
                update_fields.append('receipt_resolved')
        row.save(update_fields=update_fields)

        available_str = None
        if row.material_ref_id and row.material_ref is not None:
            try:
                balance_info = compute_material_balance(row.material_ref)
                available = Decimal(str(balance_info['current_balance']))
                available_str = f"{available:.4f}"
            except Exception:
                available_str = None

        recorded_str = f"{Decimal(str(row.quantity)):.4f}"
        doc_qty_str = (
            f"{Decimal(str(resolved_doc.quantity)):.4f}"
            if (resolved_doc is not None and resolved_doc.quantity is not None)
            else None
        )
        tx_kind = (
            'consumption'
            if row.transaction_type == MaterialTransactionType.ISSUE
            else row.transaction_type
        )
        doc_ref = (row.warehouse_document_reference or '').strip() or None

        items.append({
            'material_entry_id': str(row.id),
            'material_id': str(row.material_ref_id) if row.material_ref_id else None,
            'material_ref': str(row.material_ref_id) if row.material_ref_id else None,
            'material_description': row.material_description,
            'transaction_type': tx_kind,
            'warehouse_document_reference': doc_ref,
            'recorded_qty': recorded_str,
            'consumed_qty': recorded_str,
            'document_qty': doc_qty_str,
            'unit': row.unit,
            'status': status,
            'evidence': {
                'resolved_document_id': str(resolved_doc.id) if resolved_doc is not None else None,
                'basis': 'specific_document',
            },
            'cross_check': {
                'global_balance': available_str,
                'advisory_only': True,
            },
        })

    return {
        'items': items,
        'cross_check': {
            'basis': 'global_balance_advisory_only',
        },
    }
