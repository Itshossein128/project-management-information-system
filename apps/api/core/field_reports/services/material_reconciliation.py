"""Advisory material consumption vs inventory balance hints."""
from __future__ import annotations

from decimal import Decimal

from field_reports.models import DailyReport, MaterialTransactionType
from resources.services.balance_service import compute_material_balance


def reconcile_report_materials(report: DailyReport) -> dict:
    items = []
    rows = report.material_entries.filter(
        is_deleted=False,
        transaction_type=MaterialTransactionType.ISSUE,
    )
    for row in rows:
        if not row.material_ref_id:
            items.append({
                'material_entry_id': str(row.id),
                'material_id': None,
                'material_description': row.material_description,
                'consumed_qty': str(row.quantity),
                'unit': row.unit,
                'available_balance': None,
                'status': 'insufficient_data',
            })
            continue
        try:
            balance_info = compute_material_balance(row.material_ref)
            available = Decimal(str(balance_info['current_balance']))
        except Exception:
            items.append({
                'material_entry_id': str(row.id),
                'material_id': str(row.material_ref_id),
                'material_description': row.material_description,
                'consumed_qty': str(row.quantity),
                'unit': row.unit,
                'available_balance': None,
                'status': 'insufficient_data',
            })
            continue

        consumed = Decimal(row.quantity)
        status = 'match' if consumed <= available else 'mismatch'
        items.append({
            'material_entry_id': str(row.id),
            'material_id': str(row.material_ref_id),
            'material_description': row.material_description,
            'consumed_qty': str(consumed),
            'unit': row.unit,
            'available_balance': str(available),
            'status': status,
        })
    return {'items': items}
