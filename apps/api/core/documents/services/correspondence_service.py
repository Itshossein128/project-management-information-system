"""Correspondence numbering and document helpers."""

from __future__ import annotations

import jdatetime
from datetime import date

from common.jalali import parse_date_optional
from documents.models import Correspondence, CorrStatus, CorrType


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


def respond_correspondence(corr: Correspondence, user, data: dict) -> Correspondence:
    corr.response_date = parse_date_optional(data.get('response_date')) or date.today()
    corr.status = CorrStatus.RESPONDED
    if data.get('file_url'):
        corr.file_url = data['file_url']
    corr.updated_by = user
    corr.save()
    return corr
