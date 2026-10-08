"""Concurrent inventory operations against PostgreSQL — lost-update / oversell guards."""
from __future__ import annotations

import threading
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.exceptions import ValidationError

from procurement.models import (
    Block,
    InternalTransfer,
    InventoryAllocation,
    RequisitionHeader,
    RequisitionItem,
)
from procurement.services.inventory_lock_service import HardStopError, issue_stock, record_grn
from procurement.services.transfer_service import approve_transfer
from projects.models import Project
from resources.models import Material

User = get_user_model()


def _run_concurrent(workers):
    """Run callables in parallel threads, each with a fresh DB connection."""
    barrier = threading.Barrier(len(workers))
    errors: list[BaseException] = []
    results: list[object] = []
    lock = threading.Lock()

    def wrap(fn):
        try:
            barrier.wait(timeout=10)
            out = fn()
            with lock:
                results.append(out)
        except BaseException as exc:  # noqa: BLE001 — collect all worker failures
            with lock:
                errors.append(exc)
        finally:
            connection.close()

    threads = [threading.Thread(target=wrap, args=(fn,)) for fn in workers]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    return results, errors


@pytest.fixture
def inventory_setup(db):
    user = User.objects.create(username='inv_conc_user', full_name='Inv Concurrent')
    project = Project.objects.create(project_name='Inv Concurrent', project_code='PRJ-INV-C')
    block = Block.objects.create(
        project=project,
        block_code='BLK-A',
        block_name='Block A',
        created_by=user,
    )
    material = Material.objects.create(
        project=project,
        material_code='MAT-INV',
        material_name='Rebar',
    )
    header = RequisitionHeader.objects.create(
        project=project,
        block=block,
        requested_by=user,
        request_date='2026-01-01',
        created_by=user,
    )
    item = RequisitionItem.objects.create(
        header=header,
        line_number=1,
        material=material,
        requested_qty=Decimal('100.0000'),
        approved_qty=Decimal('100.0000'),
        created_by=user,
    )
    allocation = InventoryAllocation.objects.create(
        requisition_item=item,
        block=block,
        material=material,
        allocated_qty=Decimal('100.0000'),
        received_qty=Decimal('20.0000'),
        issued_qty=Decimal('0.0000'),
        mr_tag=f'{header.requisition_number}-{block.block_code}',
        created_by=user,
    )
    return {
        'user': user,
        'project': project,
        'block': block,
        'material': material,
        'item': item,
        'allocation': allocation,
    }


@pytest.mark.django_db(transaction=True)
class TestIssueStockConcurrency:
    def test_concurrent_issues_accumulate_issued_qty(self, inventory_setup):
        """Two successful issues of 7 must leave issued_qty=14 (no lost update)."""
        data = inventory_setup
        alloc_id = data['allocation'].id
        user_id = data['user'].id

        def worker():
            user = User.objects.get(pk=user_id)
            allocation = InventoryAllocation.objects.get(pk=alloc_id)
            return issue_stock(allocation, Decimal('7.0000'), user)

        results, errors = _run_concurrent([worker, worker])

        assert not errors, f'unexpected errors: {errors}'
        assert len(results) == 2

        allocation = InventoryAllocation.objects.get(pk=alloc_id)
        assert allocation.issued_qty == Decimal('14.0000')

    def test_concurrent_issues_cannot_oversell(self, inventory_setup):
        """With received=10, two concurrent issues of 7: one succeeds, one HardStop."""
        data = inventory_setup
        allocation = data['allocation']
        allocation.received_qty = Decimal('10.0000')
        allocation.save(update_fields=['received_qty', 'updated_at'])

        alloc_id = allocation.id
        user_id = data['user'].id

        def worker():
            user = User.objects.get(pk=user_id)
            row = InventoryAllocation.objects.get(pk=alloc_id)
            return issue_stock(row, Decimal('7.0000'), user)

        results, errors = _run_concurrent([worker, worker])

        assert len(results) == 1
        assert len(errors) == 1
        assert isinstance(errors[0], HardStopError)

        allocation.refresh_from_db()
        assert allocation.issued_qty == Decimal('7.0000')


@pytest.mark.django_db(transaction=True)
class TestRecordGrnConcurrency:
    def test_concurrent_receipts_accumulate_received_qty(self, inventory_setup):
        data = inventory_setup
        item_id = data['item'].id
        user_id = data['user'].id
        alloc_id = data['allocation'].id
        # Start from known base so final assertion is exact
        data['allocation'].received_qty = Decimal('0.0000')
        data['allocation'].save(update_fields=['received_qty', 'updated_at'])
        data['item'].purchased_qty = Decimal('0.0000')
        data['item'].save(update_fields=['purchased_qty', 'updated_at'])

        def worker():
            user = User.objects.get(pk=user_id)
            item = RequisitionItem.objects.get(pk=item_id)
            return record_grn(item, Decimal('5.0000'), user)

        results, errors = _run_concurrent([worker, worker])

        assert not errors, f'unexpected errors: {errors}'
        assert len(results) == 2

        allocation = InventoryAllocation.objects.get(pk=alloc_id)
        item = RequisitionItem.objects.get(pk=item_id)
        assert allocation.received_qty == Decimal('10.0000')
        assert item.purchased_qty == Decimal('10.0000')


@pytest.mark.django_db(transaction=True)
class TestTransferConcurrency:
    @pytest.fixture
    def transfer_setup(self, inventory_setup):
        data = inventory_setup
        user = data['user']
        project = data['project']
        target = Block.objects.create(
            project=project,
            block_code='BLK-B',
            block_name='Block B',
            created_by=user,
        )
        data['allocation'].received_qty = Decimal('100.0000')
        data['allocation'].allocated_qty = Decimal('100.0000')
        data['allocation'].save(update_fields=['received_qty', 'allocated_qty', 'updated_at'])
        data['target_block'] = target
        return data

    def test_concurrent_transfers_from_same_source_accumulate(self, transfer_setup):
        """Two transfers of 30 from received=100 must leave source received=40."""
        data = transfer_setup
        user = data['user']
        source = data['block']
        target = data['target_block']
        material = data['material']
        alloc_id = data['allocation'].id

        t1 = InternalTransfer.objects.create(
            source_block=source,
            target_block=target,
            material=material,
            quantity=Decimal('30.0000'),
            reason='A',
            created_by=user,
        )
        t2 = InternalTransfer.objects.create(
            source_block=source,
            target_block=target,
            material=material,
            quantity=Decimal('30.0000'),
            reason='B',
            created_by=user,
        )
        user_id = user.id

        def make_worker(transfer_id):
            def worker():
                u = User.objects.get(pk=user_id)
                transfer = InternalTransfer.objects.get(pk=transfer_id)
                return approve_transfer(transfer, u)

            return worker

        results, errors = _run_concurrent([make_worker(t1.id), make_worker(t2.id)])

        assert not errors, f'unexpected errors: {errors}'
        assert len(results) == 2

        source_alloc = InventoryAllocation.objects.get(pk=alloc_id)
        assert source_alloc.received_qty == Decimal('40.0000')
        assert source_alloc.allocated_qty == Decimal('40.0000')

        target_alloc = InventoryAllocation.objects.get(
            block=target,
            material=material,
            is_deleted=False,
        )
        assert target_alloc.received_qty == Decimal('60.0000')

    def test_concurrent_transfer_rejects_when_insufficient_stock(self, transfer_setup):
        data = transfer_setup
        user = data['user']
        data['allocation'].received_qty = Decimal('50.0000')
        data['allocation'].allocated_qty = Decimal('50.0000')
        data['allocation'].save(update_fields=['received_qty', 'allocated_qty', 'updated_at'])

        t1 = InternalTransfer.objects.create(
            source_block=data['block'],
            target_block=data['target_block'],
            material=data['material'],
            quantity=Decimal('40.0000'),
            reason='A',
            created_by=user,
        )
        t2 = InternalTransfer.objects.create(
            source_block=data['block'],
            target_block=data['target_block'],
            material=data['material'],
            quantity=Decimal('40.0000'),
            reason='B',
            created_by=user,
        )
        user_id = user.id
        alloc_id = data['allocation'].id

        def make_worker(transfer_id):
            def worker():
                u = User.objects.get(pk=user_id)
                transfer = InternalTransfer.objects.get(pk=transfer_id)
                return approve_transfer(transfer, u)

            return worker

        results, errors = _run_concurrent([make_worker(t1.id), make_worker(t2.id)])

        assert len(results) == 1
        assert len(errors) == 1
        assert isinstance(errors[0], ValidationError)

        source_alloc = InventoryAllocation.objects.get(pk=alloc_id)
        assert source_alloc.received_qty == Decimal('10.0000')
