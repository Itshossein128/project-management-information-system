"""Material consumption vs planned analytics."""

from __future__ import annotations

from django.db.models import Sum

from projects.models import Activity
from resources.models import InventoryTransaction, Material, TransactionType


def _issued_qty(qs):
    """
    Calculates the total quantity of materials issued to the field from a given queryset
    of inventory transactions (excludes waste which is tracked separately).
    """
    return float(
        qs.filter(tx_type=TransactionType.OUT).aggregate(total=Sum('quantity'))['total'] or 0
    )


def _waste_qty(qs):
    """
    Calculates the total quantity of materials wasted from a given queryset of inventory transactions.
    """
    return float(
        qs.filter(tx_type=TransactionType.WASTE).aggregate(total=Sum('quantity'))['total'] or 0
    )


def _received_qty(qs):
    """
    Calculates the total quantity of materials received from a given queryset of inventory transactions.
    """
    return float(qs.filter(tx_type=TransactionType.IN).aggregate(total=Sum('quantity'))['total'] or 0)


def material_consumption_list(
    project_id,
    *,
    material_id=None,
    activity_id=None,
    date_from=None,
    date_to=None,
):
    """
    Generates a list detailing per-material consumption against estimated totals,
    including calculated consumption and waste percentages, optionally filtered by material,
    activity, and date range.
    """
    qs = Material.objects.filter(project_id=project_id)
    if material_id:
        qs = qs.filter(pk=material_id)

    results = []
    for material in qs:
        txs = InventoryTransaction.objects.filter(material=material, is_deleted=False)
        if date_from:
            txs = txs.filter(tx_date__gte=date_from)
        if date_to:
            txs = txs.filter(tx_date__lte=date_to)
        if activity_id:
            txs = txs.filter(activity_id=activity_id)

        received = _received_qty(txs)
        issued = _issued_qty(txs)
        waste = _waste_qty(txs)
        estimated = float(material.estimated_total_qty) if material.estimated_total_qty else None
        consumption_pct = (issued / estimated * 100) if estimated and estimated > 0 else None
        waste_pct = (waste / received * 100) if received > 0 else None

        results.append(
            {
                'material_id': str(material.id),
                'material_code': material.material_code,
                'material_name': material.material_name,
                'estimated_total_qty': estimated,
                'total_received': received,
                'total_issued': issued,
                'total_waste': waste,
                'consumption_pct': round(consumption_pct, 2) if consumption_pct is not None else None,
                'waste_pct': round(waste_pct, 2) if waste_pct is not None else None,
            }
        )
    return results


def activity_consumption_list(
    project_id,
    *,
    activity_id=None,
    date_from=None,
    date_to=None,
):
    """
    Generates a list detailing per-activity material consumption against the total planned quantity
    for each activity, optionally filtered by activity and date range.
    """
    act_qs = Activity.objects.filter(project_id=project_id, is_deleted=False)
    if activity_id:
        act_qs = act_qs.filter(pk=activity_id)

    results = []
    for activity in act_qs:
        txs = InventoryTransaction.objects.filter(
            project_id=project_id,
            activity=activity,
            is_deleted=False,
            tx_type=TransactionType.OUT,
        )
        if date_from:
            txs = txs.filter(tx_date__gte=date_from)
        if date_to:
            txs = txs.filter(tx_date__lte=date_to)

        issued = _issued_qty(txs)
        planned = float(activity.total_quantity) if activity.total_quantity else None
        consumption_pct = (issued / planned * 100) if planned and planned > 0 else None

        results.append(
            {
                'activity_id': str(activity.id),
                'activity_code': activity.activity_code,
                'activity_name': activity.activity_name,
                'planned_quantity': planned,
                'total_issued': issued,
                'consumption_pct': round(consumption_pct, 2) if consumption_pct is not None else None,
            }
        )
    return results


def material_consumption_report(
    project_id,
    *,
    material_id=None,
    activity_id=None,
    date_from=None,
    date_to=None,
):
    """
    Generates a comprehensive consumption report for a project, combining both
    per-material and per-activity consumption analytics.
    """
    return {
        'materials': material_consumption_list(
            project_id,
            material_id=material_id,
            activity_id=activity_id,
            date_from=date_from,
            date_to=date_to,
        ),
        'activities': activity_consumption_list(
            project_id,
            activity_id=activity_id,
            date_from=date_from,
            date_to=date_to,
        ),
    }
