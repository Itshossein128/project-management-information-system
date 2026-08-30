"""Provisioning and lookup for the reserved workshop block per project."""
from django.contrib.auth import get_user_model

from procurement.models.block import (
    WORKSHOP_BLOCK_CODE,
    WORKSHOP_BLOCK_NAME,
    Block,
    BlockKind,
)

User = get_user_model()


def ensure_workshop_block(project, *, created_by=None) -> Block:
    """Get or create the single system workshop block for a project."""
    existing = Block.objects.filter(
        project=project,
        block_kind=BlockKind.WORKSHOP,
        is_deleted=False,
    ).first()
    if existing:
        return existing

    actor = created_by or project.project_manager
    if actor is None:
        actor = User.objects.filter(is_superuser=True).order_by('id').first()

    return Block.objects.create(
        project=project,
        block_code=WORKSHOP_BLOCK_CODE,
        block_name=WORKSHOP_BLOCK_NAME,
        block_kind=BlockKind.WORKSHOP,
        created_by=actor,
        updated_by=actor,
    )
