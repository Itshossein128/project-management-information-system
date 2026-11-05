from rest_framework.exceptions import ValidationError
from procurement.models.block import Block, BlockKind
from procurement.models.requisition import RequisitionHeader

def assert_block_editable(block: Block) -> None:
    if block.block_kind == BlockKind.WORKSHOP:
        raise ValidationError({'detail': 'System workshop block cannot be modified.'})

def assert_block_deletable(block: Block) -> None:
    if block.block_kind == BlockKind.WORKSHOP:
        raise ValidationError({'detail': 'System workshop block cannot be deleted.'})
    if RequisitionHeader.objects.filter(block=block, is_deleted=False).exists():
        raise ValidationError(
            {'detail': 'Cannot delete a block that has purchase requisitions.'}
        )
