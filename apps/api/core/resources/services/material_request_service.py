from django.db.models import Max
from django.utils import timezone
from resources.models import MaterialRequest

def prepare_material_request_kwargs(project_id, validated_data):
    material = validated_data['material']
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
