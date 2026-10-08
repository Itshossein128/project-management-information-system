"""Sequential inventory lock / hard-stop behaviour."""
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
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


@pytest.fixture
def setup_inventory(db):
    user = User.objects.create(username='inv_lock_user', full_name='Inv Lock')
    project = Project.objects.create(project_name='Inv Lock', project_code='PRJ-INV-L')
    block = Block.objects.create(
        project=project,
        block_code='BLK-L',
        block_name='Lock Block',
        created_by=user,
    )
    target = Block.objects.create(
        project=project,
        block_code='BLK-T',
        block_name='Target Block',
        created_by=user,
    )
    material = Material.objects.create(
        project=project,
        material_code='MAT-L',
        material_name='Cement',
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
        received_qty=Decimal('50.0000'),
        issued_qty=Decimal('10.0000'),
        mr_tag=f'{header.requisition_number}-{block.block_code}',
        created_by=user,
    )
    return {
        'user': user,
        'block': block,
        'target': target,
        'material': material,
        'item': item,
        'allocation': allocation,
    }


@pytest.mark.django_db
class TestIssueStock:
    def test_issue_within_available(self, setup_inventory):
        data = setup_inventory
        result = issue_stock(data['allocation'], Decimal('20.0000'), data['user'])
        assert result.issued_qty == Decimal('30.0000')

    def test_issue_exceeding_available_raises(self, setup_inventory):
        data = setup_inventory
        with pytest.raises(HardStopError):
            issue_stock(data['allocation'], Decimal('41.0000'), data['user'])
        data['allocation'].refresh_from_db()
        assert data['allocation'].issued_qty == Decimal('10.0000')


@pytest.mark.django_db
class TestRecordGrn:
    def test_receipt_increments_received_and_purchased(self, setup_inventory):
        data = setup_inventory
        result = record_grn(data['item'], Decimal('12.0000'), data['user'])
        assert result.received_qty == Decimal('62.0000')
        data['item'].refresh_from_db()
        assert data['item'].purchased_qty == Decimal('12.0000')


@pytest.mark.django_db
class TestTransferStockConstraint:
    def test_transfer_exceeding_available_raises(self, setup_inventory):
        """Cannot transfer more than received - issued (available stock)."""
        data = setup_inventory
        # available = 50 - 10 = 40
        transfer = InternalTransfer.objects.create(
            source_block=data['block'],
            target_block=data['target'],
            material=data['material'],
            quantity=Decimal('41.0000'),
            reason='Oversell attempt',
            created_by=data['user'],
        )
        with pytest.raises(ValidationError):
            approve_transfer(transfer, data['user'])

        data['allocation'].refresh_from_db()
        assert data['allocation'].received_qty == Decimal('50.0000')
        assert not InventoryAllocation.objects.filter(
            block=data['target'],
            material=data['material'],
        ).exists()

    def test_transfer_within_available_succeeds(self, setup_inventory):
        data = setup_inventory
        transfer = InternalTransfer.objects.create(
            source_block=data['block'],
            target_block=data['target'],
            material=data['material'],
            quantity=Decimal('40.0000'),
            reason='Full available',
            created_by=data['user'],
        )
        approve_transfer(transfer, data['user'])
        data['allocation'].refresh_from_db()
        assert data['allocation'].received_qty == Decimal('10.0000')
        assert data['allocation'].issued_qty == Decimal('10.0000')
