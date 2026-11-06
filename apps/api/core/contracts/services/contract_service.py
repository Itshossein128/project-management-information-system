from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import NotFound

from config.exceptions import CodedValidationError
from contracts.models import Contract, ContractItem, ChangeOrder, ChangeOrderStatus
from permissions.project import assert_same_project

# Maps field names in a contract item payload to their corresponding Django app/model labels.
# Used by _resolve_fk_fields to dynamically convert UUID strings into actual model instances.
FK_ITEM_FIELDS = {
    'activity': 'projects.Activity',
    'unit': 'master_data.Unit',
}


def _resolve_fk_fields(payload: dict) -> dict:
    """
    Convert UUID strings in FK fields to model instances for ORM create/update.
    It also ensures that numerical fields like 'unit_price' and 'quantity' are converted to Decimals.
    """
    from decimal import Decimal
    from django.apps import apps

    resolved = dict(payload)
    for field in ('unit_price', 'quantity'):
        if field in resolved and resolved[field] is not None and resolved[field] != '':
            resolved[field] = Decimal(str(resolved[field]))
    for field, model_label in FK_ITEM_FIELDS.items():
        if field not in resolved:
            continue
        raw = resolved.pop(field)
        if raw in (None, ''):
            resolved[f'{field}_id'] = None
            continue
        model = apps.get_model(model_label)
        resolved[f'{field}_id'] = raw if hasattr(raw, 'pk') else raw
    return resolved


@transaction.atomic
def bulk_upsert_contract_items(contract, rows, user):
    """
    Bulk creates or updates ContractItem records for a given contract.
    Iterates through the provided rows, resolves foreign keys using _resolve_fk_fields,
    and either updates existing items (if 'id' is present) or creates new ones.
    """
    saved = []
    for row in rows:
        item_id = row.get('id')
        payload = _resolve_fk_fields({k: v for k, v in row.items() if k != 'id'})
        if item_id:
            try:
                item = ContractItem.objects.get(pk=item_id, contract=contract)
            except ContractItem.DoesNotExist:
                raise NotFound(f"ContractItem with id {item_id} not found.")
            for k, v in payload.items():
                setattr(item, k, v)
            if item.activity_id:
                assert_same_project(contract.project_id, item.activity.project_id, field='activity')
            item.updated_by = user
            item.save()
        else:
            item = ContractItem.objects.create(
                contract=contract,
                created_by=user,
                updated_by=user,
                **payload,
            )
            if item.activity_id:
                assert_same_project(contract.project_id, item.activity.project_id, field='activity')
        saved.append(item)
    return saved


def _contract_adjusted_base(contract):
    """
    Calculates the base adjusted amount for a contract.
    Returns the adjusted_amount if it is set; otherwise falls back to original_amount (or 0).
    """
    return contract.adjusted_amount if contract.adjusted_amount is not None else (contract.original_amount or 0)



@transaction.atomic
def create_change_order(contract, description, amount_change, user):
    """
    Creates a new ChangeOrder for the specified contract in DRAFT status.
    Automatically assigns the next available change_number.
    """
    from contracts.services.ipc_service import next_change_number
    co = ChangeOrder.objects.create(
        contract=contract,
        change_number=next_change_number(contract.id),
        description=description,
        amount_change=amount_change,
        status=ChangeOrderStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )
    return co


@transaction.atomic
def approve_change_order(co, user, *, break_glass_reason: str | None = None):
    """
    Approves a ChangeOrder and updates the associated contract's adjusted_amount.
    Ensures that the resulting adjusted amount is not negative.
    """
    from permissions.role_services import record_access_change
    from permissions.sod import assert_not_self_final_approve

    if co.status == ChangeOrderStatus.APPROVED:
        return co
    if co.status != ChangeOrderStatus.SUBMITTED:
        raise CodedValidationError(
            detail=_('Only a submitted change order can be approved.'),
            code='change_order_invalid_status',
        )
    contract = co.contract
    before = {'status': co.status}
    decision = assert_not_self_final_approve(
        co.created_by_id,
        user,
        break_glass_reason=break_glass_reason,
        project=contract.project,
        record_id=str(co.id),
        record_type='change_order',
    )
    if decision.used_break_glass:
        record_access_change(
            actor=user,
            project=contract.project,
            subject_user=co.created_by,
            role=None,
            action='sod_break_glass',
            before=before,
            after={
                'reason': decision.reason,
                'exception': True,
                'record_id': str(co.id),
                'record_type': 'change_order',
            },
        )
    new_adjusted = _contract_adjusted_base(contract) + co.amount_change
    if new_adjusted < 0:
        raise ValueError('مبلغ تعدیل‌شده قرارداد نمی‌تواند منفی باشد')
    co.status = ChangeOrderStatus.APPROVED
    co.approved_date = date.today()
    co.updated_by = user
    co.save()
    contract.adjusted_amount = new_adjusted
    contract.updated_by = user
    contract.save(update_fields=['adjusted_amount', 'updated_by', 'updated_at'])
    return co


@transaction.atomic
def reject_change_order(co, user):
    """
    Rejects a ChangeOrder. If the change order was previously approved, it rolls back
    the contract's adjusted_amount by subtracting the change order's amount_change.
    """
    was_approved = co.status == ChangeOrderStatus.APPROVED
    co.status = ChangeOrderStatus.REJECTED
    co.approved_date = None
    co.updated_by = user
    co.save()
    if was_approved:
        contract = co.contract
        contract.adjusted_amount = _contract_adjusted_base(contract) - co.amount_change
        if contract.adjusted_amount < 0:
            contract.adjusted_amount = 0
        contract.updated_by = user
        contract.save(update_fields=['adjusted_amount', 'updated_by', 'updated_at'])
    return co
