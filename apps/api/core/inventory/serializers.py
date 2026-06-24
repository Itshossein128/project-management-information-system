from rest_framework import serializers
from .models import (
    Item,
    Category,
    SpaceMaterialRequest,
    DepartmentActivityRecord,
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
    business_id = serializers.IntegerField(source='business.id', read_only=True)

    class Meta:
        model = SpaceMaterialRequest
        fields = [
            'id',
            'business_id',
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
        read_only_fields = ['id', 'business_id', 'created_at', 'updated_at']


class DepartmentActivityRecordSerializer(serializers.ModelSerializer):
    business_id = serializers.IntegerField(source='business.id', read_only=True)

    class Meta:
        model = DepartmentActivityRecord
        fields = [
            'id',
            'business_id',
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
        read_only_fields = ['id', 'business_id', 'created_at', 'updated_at']