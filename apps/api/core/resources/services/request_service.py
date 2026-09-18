"""Material request calculation and workflow services."""

from __future__ import annotations

from django.db.models import Max
from django.utils import timezone

from resources.models import MaterialRequest

def compute_material_request_defaults(project_id, material, validated_data: dict) -> dict:
    unit = validated_data.get('unit') or (
        material.unit.symbol if getattr(material, 'unit_id', None) else ''
    )
    max_num = (
        MaterialRequest.objects.filter(project_id=project_id, material=material).aggregate(
            m=Max('request_number')
        )['m']
        or 0
    )
    return {
        'request_number': max_num + 1,
        'unit': unit or '—',
        'request_date': validated_data.get('request_date') or timezone.localdate(),
    }
