import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from procurement.models import (
    Block,
    InternalTransfer,
    InventoryAllocation,
    RequisitionHeader,
    RequisitionItem,
    TransferStatus,
)
from procurement.services.transfer_service import approve_transfer, reject_transfer
from projects.models import Project
from resources.models import Material

User = get_user_model()


@pytest.mark.django_db
class TestTransferService:

    @pytest.fixture
    def setup_transfer_data(self):
        user = User.objects.create(username="transfer_user", full_name="Transfer User")
        project = Project.objects.create(
            project_name="Transfer Project",
            project_code="PRJ-TR",
        )
        source_block = Block.objects.create(
            project=project,
            block_code="BLK-SRC",
            block_name="Source Block",
            created_by=user,
        )
        target_block = Block.objects.create(
            project=project,
            block_code="BLK-TGT",
            block_name="Target Block",
            created_by=user,
        )
        material = Material.objects.create(
            project=project,
            material_code="MAT-TR",
            material_name="Cement",
        )
        req_header = RequisitionHeader.objects.create(
            project=project,
            block=source_block,
            requested_by=user,
            request_date="2026-01-01",
            created_by=user,
        )
        req_item = RequisitionItem.objects.create(
            header=req_header,
            line_number=1,
            material=material,
            requested_qty=Decimal('100.0000'),
            created_by=user,
        )
        source_allocation = InventoryAllocation.objects.create(
            requisition_item=req_item,
            block=source_block,
            material=material,
            allocated_qty=Decimal('100.0000'),
            received_qty=Decimal('100.0000'),
            issued_qty=Decimal('0.0000'),
            mr_tag="REQ-01-BLK-SRC",
            created_by=user,
        )
        return {
            'user': user,
            'project': project,
            'source_block': source_block,
            'target_block': target_block,
            'material': material,
            'req_item': req_item,
            'source_allocation': source_allocation,
        }

    def test_approve_transfer_creates_target_allocation(self, setup_transfer_data):
        data = setup_transfer_data
        user = data['user']
        source_block = data['source_block']
        target_block = data['target_block']
        material = data['material']
        source_alloc = data['source_allocation']

        transfer = InternalTransfer.objects.create(
            source_block=source_block,
            target_block=target_block,
            material=material,
            quantity=Decimal('30.0000'),
            reason="Material surplus at source",
            created_by=user,
        )

        approved = approve_transfer(transfer, user)

        assert approved.status == TransferStatus.APPROVED
        assert approved.approved_by == user
        assert approved.approved_at is not None

        # Verify source allocation decremented
        source_alloc.refresh_from_db()
        assert source_alloc.allocated_qty == Decimal('70.0000')
        assert source_alloc.received_qty == Decimal('70.0000')

        # Verify target allocation created
        target_alloc = InventoryAllocation.objects.get(
            block=target_block,
            material=material,
            is_deleted=False,
        )
        assert target_alloc.allocated_qty == Decimal('30.0000')
        assert target_alloc.received_qty == Decimal('30.0000')
        assert target_alloc.requisition_item == data['req_item']

    def test_approve_transfer_increments_existing_target_allocation(self, setup_transfer_data):
        data = setup_transfer_data
        user = data['user']
        source_block = data['source_block']
        target_block = data['target_block']
        material = data['material']
        source_alloc = data['source_allocation']

        # Existing target allocation
        target_alloc = InventoryAllocation.objects.create(
            requisition_item=data['req_item'],
            block=target_block,
            material=material,
            allocated_qty=Decimal('20.0000'),
            received_qty=Decimal('20.0000'),
            issued_qty=Decimal('0.0000'),
            mr_tag="REQ-01-BLK-TGT",
            created_by=user,
        )

        transfer = InternalTransfer.objects.create(
            source_block=source_block,
            target_block=target_block,
            material=material,
            quantity=Decimal('25.0000'),
            reason="Transfer extra stock",
            created_by=user,
        )

        approved = approve_transfer(transfer, user)
        assert approved.status == TransferStatus.APPROVED

        source_alloc.refresh_from_db()
        target_alloc.refresh_from_db()

        assert source_alloc.allocated_qty == Decimal('75.0000')
        assert source_alloc.received_qty == Decimal('75.0000')

        assert target_alloc.allocated_qty == Decimal('45.0000')
        assert target_alloc.received_qty == Decimal('45.0000')

    def test_approve_transfer_non_pending_raises_validation_error(self, setup_transfer_data):
        data = setup_transfer_data
        user = data['user']

        transfer = InternalTransfer.objects.create(
            source_block=data['source_block'],
            target_block=data['target_block'],
            material=data['material'],
            quantity=Decimal('10.0000'),
            reason="Test",
            status=TransferStatus.APPROVED,
            created_by=user,
        )

        with pytest.raises(ValidationError):
            approve_transfer(transfer, user)

    def test_reject_transfer(self, setup_transfer_data):
        data = setup_transfer_data
        user = data['user']
        source_alloc = data['source_allocation']

        transfer = InternalTransfer.objects.create(
            source_block=data['source_block'],
            target_block=data['target_block'],
            material=data['material'],
            quantity=Decimal('15.0000'),
            reason="Need transfer",
            created_by=user,
        )

        rejected = reject_transfer(transfer, user, reason="Not approved")

        assert rejected.status == TransferStatus.REJECTED
        assert rejected.cost_adjustment_notes == "Not approved"

        # Verify allocations unchanged
        source_alloc.refresh_from_db()
        assert source_alloc.allocated_qty == Decimal('100.0000')
        assert source_alloc.received_qty == Decimal('100.0000')
        assert not InventoryAllocation.objects.filter(block=data['target_block']).exists()

    def test_approve_transfer_clamped_at_zero(self, setup_transfer_data):
        data = setup_transfer_data
        user = data['user']
        source_alloc = data['source_allocation']

        # Transfer quantity greater than source allocation quantity
        transfer = InternalTransfer.objects.create(
            source_block=data['source_block'],
            target_block=data['target_block'],
            material=data['material'],
            quantity=Decimal('150.0000'),
            reason="Large transfer",
            created_by=user,
        )

        approve_transfer(transfer, user)

        source_alloc.refresh_from_db()
        assert source_alloc.allocated_qty == Decimal('0.0000')
        assert source_alloc.received_qty == Decimal('0.0000')

        target_alloc = InventoryAllocation.objects.get(
            block=data['target_block'],
            material=data['material'],
            is_deleted=False,
        )
        assert target_alloc.allocated_qty == Decimal('150.0000')
        assert target_alloc.received_qty == Decimal('150.0000')

