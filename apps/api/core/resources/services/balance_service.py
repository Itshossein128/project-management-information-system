"""Material balance calculations."""

from __future__ import annotations

from django.db.models import Q, Sum

from resources.models import InventoryTransaction, Material, MaterialRequest, TransactionType


def material_balance_list(project_id, *, discipline=None, location=None, block_type=None, low_stock=False):
    qs = Material.objects.filter(project_id=project_id)
    if discipline:
        qs = qs.filter(discipline=discipline)
    if location:
        qs = qs.filter(location__icontains=location)
    if block_type:
        qs = qs.filter(block_type__icontains=block_type)

    results = []
    for material in qs:
        row = compute_material_balance(material)
        if low_stock and not row['is_low_stock']:
            continue
        results.append(row)
    return results


def compute_material_balance(material: Material) -> dict:
    txs = InventoryTransaction.objects.filter(material=material, is_deleted=False)
    received = (
        txs.filter(tx_type=TransactionType.IN).aggregate(total=Sum('quantity'))['total'] or 0
    )
    issued = (
        txs.filter(tx_type__in=[TransactionType.OUT, TransactionType.WASTE]).aggregate(
            total=Sum('quantity')
        )['total']
        or 0
    )
    adjusted = (
        txs.filter(tx_type=TransactionType.ADJUST).aggregate(total=Sum('quantity'))['total'] or 0
    )
    # Match running_balance: IN +, OUT/WASTE -, ADJUST +/- (signed quantity)
    balance = float(received) + float(adjusted) - float(issued)
    min_level = float(material.min_stock_level) if material.min_stock_level else None
    is_low = min_level is not None and balance <= min_level
    total_requested = (
        MaterialRequest.objects.filter(material=material, is_deleted=False).aggregate(
            total=Sum('requested_qty')
        )['total']
        or 0
    )
    last_tx = txs.order_by('-tx_date').first()
    return {
        'material_id': str(material.id),
        'material_code': material.material_code,
        'material_name': material.material_name,
        'unit': material.unit.symbol if material.unit_id else '',
        'discipline': material.discipline,
        'location': material.location,
        'block_type': material.block_type,
        'estimated_total_qty': float(material.estimated_total_qty)
        if material.estimated_total_qty
        else None,
        'total_requested': float(total_requested),
        'total_received': float(received),
        'total_issued': float(issued),
        'total_adjusted': float(adjusted),
        'current_balance': balance,
        'min_stock_level': min_level,
        'is_low_stock': is_low,
        'last_transaction_date': last_tx.tx_date.isoformat() if last_tx else None,
    }


def running_balance(material_id, *, project_id=None):
    qs = InventoryTransaction.objects.filter(material_id=material_id, is_deleted=False)
    if project_id is not None:
        qs = qs.filter(project_id=project_id)
    txs = qs.order_by('tx_date', 'created_at')
    running = 0.0
    rows = []
    for tx in txs:
        qty = float(tx.quantity)
        if tx.tx_type == TransactionType.IN:
            running += qty
        elif tx.tx_type in (TransactionType.OUT, TransactionType.WASTE):
            running -= qty
        else:
            running += qty
        rows.append(
            {
                'date': tx.tx_date.isoformat(),
                'transaction_type': tx.tx_type,
                'qty': qty,
                'running_balance': running,
            }
        )
    return rows
