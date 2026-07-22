from datetime import date
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db import transaction
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


@transaction.atomic
def bulk_upsert_contract_items(contract, rows, user):
    item_ids_to_update = [row['id'] for row in rows if row.get('id')]
    existing_items = {}
    if item_ids_to_update:
        existing_items = {item.id: item for item in ContractItem.objects.filter(id__in=item_ids_to_update, contract=contract)}

    items_to_create = []
    items_to_update = []
    update_fields = set()
    saved = []

    for row in rows:
        item_id = row.get('id')
        payload = _resolve_fk_fields({k: v for k, v in row.items() if k != 'id'})

        if item_id:
            item = existing_items.get(item_id)
            if not item:
                # Fallback, this shouldn't happen unless ID is wrong
                item = get_object_or_404(ContractItem, pk=item_id, contract=contract)

            from django.utils import timezone
            for k, v in payload.items():
                setattr(item, k, v)
                update_fields.add(k)
            item.updated_by = user
            item.updated_at = timezone.now()
            update_fields.add('updated_by')
            update_fields.add('updated_at')
            items_to_update.append(item)
            saved.append(item)
        else:
            item = ContractItem(
                contract=contract,
                created_by=user,
                updated_by=user,
                **payload,
            )
            items_to_create.append(item)
            saved.append(item)

    if items_to_create:
        ContractItem.objects.bulk_create(items_to_create)

    if items_to_update:
        ContractItem.objects.bulk_update(items_to_update, update_fields, batch_size=1000)

    # Note: `bulk_create` sets IDs for Postgres, so `saved` contains IDs if DB supports it.
    # Otherwise, it might need to refresh from DB, but usually for Postgres it handles it.

    return saved


def _contract_adjusted_base(contract):
    return contract.adjusted_amount if contract.adjusted_amount is not None else (contract.original_amount or 0)


@transaction.atomic
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


@transaction.atomic
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
