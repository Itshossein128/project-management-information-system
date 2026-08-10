"""Material request workflow: PR → approval → PO → delivery."""

from __future__ import annotations

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from common.jalali import parse_jalali_or_gregorian
from resources.models import (
    InventoryTransaction,
    MaterialRequest,
    MaterialRequestStatus,
    PurchaseOrder,
    TransactionType,
)


def compute_material_request_defaults(project_id, validated_data):
    """
    Computes derived fields for a new material request.
    Extracts the unit from the material, calculates the next request_number,
    and ensures a request_date is set.
    """
    material = validated_data['material']
    unit = validated_data.get('unit') or (
        material.unit.symbol if getattr(material, 'unit_id', None) else ''
    )
    max_num = (
        MaterialRequest.objects.filter(project_id=project_id, material=material).aggregate(
            m=Max('request_number')
        )['m']
        or 0
    )
    return {
        'request_number': max_num + 1,
        'unit': unit or '—',
        'request_date': validated_data.get('request_date') or timezone.localdate(),
    }


class ProcurementWorkflowError(ValidationError):
    pass


def _ensure_status(request: MaterialRequest, expected: str | tuple[str, ...], action: str):
    """
    Validates that a material request is in the expected state before performing an action,
    raising a ValidationError if it is not.
    """
    allowed = (expected,) if isinstance(expected, str) else expected
    if request.status not in allowed:
        raise ProcurementWorkflowError(
            {'detail': f'Cannot {action} while status is {request.status}'}
        )


@transaction.atomic
def approve_material_request(request: MaterialRequest, user) -> MaterialRequest:
    _ensure_status(request, MaterialRequestStatus.PENDING, 'approve')
    request.status = MaterialRequestStatus.APPROVED
    request.approved_by = user
    request.approved_at = timezone.now()
    request.updated_by = user
    request.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at'])
    return request


def _parse_date(value):
    """
    Parses a date string (Jalali or Gregorian) or returns an existing date object,
    handling None or empty string values gracefully.
    """
    if value is None or value == '':
        return None
    if hasattr(value, 'isoformat'):
        return value
    return parse_jalali_or_gregorian(str(value))


@transaction.atomic
def place_purchase_order(
    request: MaterialRequest,
    user,
    *,
    supplier_id,
    order_date,
    expected_delivery_date=None,
    unit_price=None,
    notes='',
) -> PurchaseOrder:
    """
    Creates a new purchase order for an approved material request,
    advancing the material request status to ORDERED.
    """
    _ensure_status(request, MaterialRequestStatus.APPROVED, 'place order')
    if not supplier_id:
        raise ProcurementWorkflowError({'supplier': ['Supplier is required']})
    max_po = (
        PurchaseOrder.objects.filter(project_id=request.project_id).aggregate(m=Max('po_number'))['m'] or 0
    )
    po = PurchaseOrder.objects.create(
        project_id=request.project_id,
        material_request=request,
        supplier_id=supplier_id,
        po_number=max_po + 1,
        order_date=_parse_date(order_date) or timezone.localdate(),
        expected_delivery_date=_parse_date(expected_delivery_date),
        ordered_qty=request.requested_qty,
        unit_price=unit_price,
        notes=notes,
        created_by=user,
        updated_by=user,
    )
    request.status = MaterialRequestStatus.ORDERED
    request.updated_by = user
    request.save(update_fields=['status', 'updated_by', 'updated_at'])
    return po


@transaction.atomic
def deliver_purchase_order(
    request: MaterialRequest,
    user,
    *,
    actual_delivery_date,
    document_ref='',
) -> MaterialRequest:
    """
    Records the delivery of a purchase order by creating an IN inventory transaction
    and advancing the material request status to DELIVERED.
    """
    _ensure_status(request, MaterialRequestStatus.ORDERED, 'deliver')
    try:
        po = request.purchase_order
    except PurchaseOrder.DoesNotExist as exc:
        raise ProcurementWorkflowError({'detail': 'Purchase order not found'}) from exc

    delivery_date = _parse_date(actual_delivery_date) or timezone.localdate()
    InventoryTransaction.objects.create(
        project_id=request.project_id,
        material=request.material,
        tx_date=delivery_date,
        tx_type=TransactionType.IN,
        quantity=po.ordered_qty,
        unit_cost=po.unit_price,
        supplier_id=po.supplier_id,
        activity_id=request.activity_id,
        document_ref=document_ref or f'PO-{po.po_number}',
        notes=f'Delivery for material request #{request.request_number}',
        created_by=user,
        updated_by=user,
    )
    po.actual_delivery_date = delivery_date
    po.updated_by = user
    po.save(update_fields=['actual_delivery_date', 'updated_by', 'updated_at'])

    request.status = MaterialRequestStatus.DELIVERED
    request.updated_by = user
    request.save(update_fields=['status', 'updated_by', 'updated_at'])
    return request


@transaction.atomic
def cancel_material_request(request: MaterialRequest, user) -> MaterialRequest:
    """
    Cancels a material request that is either PENDING or APPROVED,
    updating its status to CANCELLED.
    """
    _ensure_status(
        request,
        (MaterialRequestStatus.PENDING, MaterialRequestStatus.APPROVED),
        'cancel',
    )
    request.status = MaterialRequestStatus.CANCELLED
    request.updated_by = user
    request.save(update_fields=['status', 'updated_by', 'updated_at'])
    return request
