"""Tests for remaining coverage gaps in contracts module."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

from contracts.models import ContractItem, IPCDeduction
from contracts.services.contract_service import _resolve_fk_fields
from contracts.services.ipc_service import _invalidate

BASE = '/api/v1/projects/{project_id}'


def test_resolve_fk_fields_null_and_empty():
    payload = _resolve_fk_fields({'activity': None, 'unit': '', 'unit_price': '10', 'quantity': '2'})
    assert payload['activity_id'] is None
    assert payload['unit_id'] is None
    assert payload['unit_price'] == Decimal('10')


def test_invalidate_swallows_cache_errors():
    with patch('common.cache_utils.invalidate_project_caches', side_effect=RuntimeError('cache down')):
        _invalidate('00000000-0000-0000-0000-000000000001')


def test_contract_list_status_filter(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/contracts/?status=active'
    resp = finance_client.get(url)
    assert resp.status_code == 200


def test_bulk_update_existing_item(finance_client, project, contract, contract_item):
    url = f'{BASE.format(project_id=project.id)}/contracts/{contract.id}/items/'
    resp = finance_client.post(
        url,
        [
            {
                'id': str(contract_item.id),
                'description': 'Updated earthworks',
                'unit_price': '12000',
                'quantity': '90',
            }
        ],
        format='json',
    )
    assert resp.status_code == 200
    contract_item.refresh_from_db()
    assert contract_item.description == 'Updated earthworks'


def test_ipc_create_async_path(finance_client, project, contract):
    url = f'{BASE.format(project_id=project.id)}/ipcs/'
    with patch('contracts.tasks.populate_ipc_async.delay') as mock_delay:
        resp = finance_client.post(
            url,
            {'contract_id': str(contract.id), 'period_start': '2024-05-01', 'period_end': '2024-05-31'},
            format='json',
        )
    assert resp.status_code == 201
    mock_delay.assert_called_once()


def test_ipc_partial_update_success(finance_client, project, ipc):
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}/'
    resp = finance_client.patch(
        url,
        {'notes': 'Updated notes', 'period_start': '2024-03-01', 'period_end': '2024-03-31'},
        format='json',
    )
    assert resp.status_code == 200
    assert resp.data['notes'] == 'Updated notes'


def test_ipc_retrieve(finance_client, project, ipc):
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc.id}/'
    resp = finance_client.get(url)
    assert resp.status_code == 200


def test_deduction_patch_delete_blocked_not_draft(finance_client, project, ipc_with_item, user):
    ded = IPCDeduction.objects.create(
        ipc=ipc_with_item,
        deduction_type='other',
        amount=Decimal('100'),
        created_by=user,
        updated_by=user,
    )
    ipc_with_item.status = 'submitted'
    ipc_with_item.save(update_fields=['status'])
    base = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/deductions/{ded.id}/'
    assert finance_client.patch(base, {'amount': '200'}, format='json').status_code == 400
    assert finance_client.delete(base).status_code == 400


def test_contract_item_total_amount_none():
    item = ContractItem(unit_price=None, quantity=Decimal('1'))
    assert item.total_amount == 0


def test_pay_invalidates_cache(finance_client, project, ipc_with_item):
    ipc_with_item.status = 'approved'
    ipc_with_item.net_amount = Decimal('1000')
    ipc_with_item.save()
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/pay/'
    with patch('contracts.services.ipc_service._invalidate') as mock_inv:
        resp = finance_client.post(url)
    assert resp.status_code == 200
    mock_inv.assert_called_once()


def test_contract_list_serializer_without_ipc_stats(contract):
    from contracts.serializers import ContractListSerializer

    data = ContractListSerializer(contract).data
    assert data['total_ipc_count'] == 0


def test_deduction_patch_description_only(finance_client, project, ipc_with_item, user):
    ded = IPCDeduction.objects.create(
        ipc=ipc_with_item,
        deduction_type='other',
        amount=Decimal('100'),
        description='Before',
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/ipcs/{ipc_with_item.id}/deductions/{ded.id}/'
    resp = finance_client.patch(url, {'description': 'After'}, format='json')
    assert resp.status_code == 200


def test_contract_viewset_helpers(user, project):
    from contracts.views import ContractViewSet, IPCViewSet

    contract_vs = ContractViewSet()
    contract_vs.action = 'retrieve'
    assert contract_vs.get_serializer_class().__name__ == 'ContractDetailSerializer'
    contract_vs.action = 'create'
    assert contract_vs.get_serializer_class().__name__ == 'ContractWriteSerializer'
    contract_vs.action = 'update'
    assert contract_vs.get_serializer_class().__name__ == 'ContractWriteSerializer'
    contract_vs.action = 'list'
    assert contract_vs.get_serializer_class().__name__ == 'ContractListSerializer'

    contract_vs.request = MagicMock(user=user)
    contract_vs.kwargs = {'project_pk': str(project.id)}
    serializer = MagicMock()
    contract_vs.perform_create(serializer)
    contract_vs.perform_update(serializer)
    assert serializer.save.call_count == 2

    ipc_vs = IPCViewSet()
    ipc_vs.action = 'approve'
    assert ipc_vs.required_permission == 'approve_ipcs'
    ipc_vs.action = 'pay'
    assert ipc_vs.required_permission == 'approve_ipcs'
    ipc_vs.action = 'reject'
    assert ipc_vs.required_permission == 'approve_ipcs'
