"""Correspondence numbering and document helpers."""

from __future__ import annotations

import jdatetime

from documents.models import Correspondence, CorrType


def build_correspondence_create_kwargs(project_id, corr_type: str, provided_corr_number: str | None = None) -> dict:
    """Computes derived fields for new correspondence."""
    corr_number = provided_corr_number or generate_corr_number(project_id, corr_type)
    return {'corr_number': corr_number}


def generate_corr_number(project_id, corr_type: str) -> str:
    prefix_map = {
        CorrType.OUTGOING: 'OUT',
        CorrType.INCOMING: 'IN',
        CorrType.INTERNAL: 'INT',
    }
    prefix = prefix_map.get(corr_type, 'INT')
    year = jdatetime.date.today().year
    seq = Correspondence.objects.filter(
        project_id=project_id,
        corr_type=corr_type,
        corr_number__startswith=f'{prefix}-{year}-',
        is_deleted=False,
    ).count() + 1
    return f'{prefix}-{year}-{seq:03d}'
