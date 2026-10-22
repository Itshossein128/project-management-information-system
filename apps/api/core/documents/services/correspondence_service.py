"""Correspondence numbering and document helpers."""

from __future__ import annotations

import jdatetime
from datetime import date

from common.jalali import parse_date_optional
from documents.models import Correspondence, CorrStatus, CorrType
from documents.services.upload_service import validate_attachment_url


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


def respond_to_correspondence(corr: Correspondence, data: dict, user) -> Correspondence:
    """Respond to a correspondence and update its state."""
    attachment = data.get('file_url')
    if attachment:
        validate_attachment_url(attachment)
    corr.response_date = parse_date_optional(data.get('response_date')) or date.today()
    corr.status = CorrStatus.RESPONDED
    if attachment:
        corr.file_url = attachment
    corr.updated_by = user
    corr.save()
    return corr
