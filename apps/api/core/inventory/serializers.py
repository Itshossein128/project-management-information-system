from rest_framework import serializers
from .models import (
    Item,
    Category,
    SpaceMaterialRequest,
    DepartmentActivityRecord,
    department_uses_unit,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'quantity', 'category', 'category_name']
        read_only_fields = ['id']


class SpaceMaterialRequestSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='project.id', read_only=True)

    class Meta:
        model = SpaceMaterialRequest
        fields = [
            'id',
            'project_id',
            'block_number',
            'floor_number',
            'unit_number',
            'space_name',
            'material_code',
            'item_description',
            'technical_specs',
            'approved_quantity_technical_office',
            'deliverable_quantity_inventory_unit',
            'unit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'project_id', 'created_at', 'updated_at']


class DepartmentActivityRecordSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='project.id', read_only=True)

    class Meta:
        model = DepartmentActivityRecord
        fields = [
            'id',
            'project_id',
            'department',
            'date',
            'location',
            'activity_description',
            'contractor',
            'unit',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'project_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'unit': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        department = attrs.get('department')
        if department is None and self.instance is not None:
            department = self.instance.department

        unit = attrs.get(
            'unit',
            getattr(self.instance, 'unit', '') if self.instance else '',
        )
        unit_text = '' if unit is None else str(unit).strip()

        if not department_uses_unit(department or ''):
            attrs['unit'] = ''
        elif not unit_text:
            raise serializers.ValidationError({'unit': 'This field is required.'})
        else:
            attrs['unit'] = unit_text[:64]

        return attrs
