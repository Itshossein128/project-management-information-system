from datetime import date
from decimal import Decimal
from django.shortcuts import get_object_or_404
from contracts.models import Contract, ContractItem, ChangeOrder, ChangeOrderStatus

FK_ITEM_FIELDS = {
    'activity': 'projects.Activity',
    'unit': 'master_data.Unit',
}


def _resolve_fk_fields(payload: dict) -> dict:
    """Convert UUID strings in FK fields to model instances for ORM create/update."""
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


def bulk_upsert_contract_items(contract, rows, user):
    saved = []
    for row in rows:
        item_id = row.get('id')
        payload = _resolve_fk_fields({k: v for k, v in row.items() if k != 'id'})
        if item_id:
            item = get_object_or_404(ContractItem, pk=item_id, contract=contract)
            for k, v in payload.items():
                setattr(item, k, v)
            item.updated_by = user
            item.save()
        else:
            item = ContractItem.objects.create(
                contract=contract,
                created_by=user,
                updated_by=user,
                **payload,
            )
        saved.append(item)
    return saved


def _contract_adjusted_base(contract):
    return contract.adjusted_amount if contract.adjusted_amount is not None else (contract.original_amount or 0)


def approve_change_order(co, user):
    if co.status == ChangeOrderStatus.APPROVED:
        return co
    contract = co.contract
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


def reject_change_order(co, user):
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
