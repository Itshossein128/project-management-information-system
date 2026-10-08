from rest_framework import serializers

from master_data.models import ManagedContractType, OrganizationUnit


class OrganizationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationUnit
        fields = [
            'id',
            'code',
            'name',
            'parent',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ManagedContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagedContractType
        fields = ['id', 'code', 'name_fa', 'name_en', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
