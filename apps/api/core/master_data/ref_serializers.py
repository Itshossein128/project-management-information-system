from django.utils.translation import gettext as _
from rest_framework import serializers

from master_data.models import ManagedContractType, OrganizationUnit, Unit


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

    def validate(self, attrs):
        parent = attrs.get('parent')
        if self.instance is not None and parent is not None and parent.pk == self.instance.pk:
            raise serializers.ValidationError(
                {'parent': _('An organization unit cannot be its own parent.')}
            )
        return attrs


class ManagedContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagedContractType
        fields = ['id', 'code', 'name_fa', 'name_en', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'unit_name', 'unit_symbol']
        read_only_fields = ['id']

    def validate_unit_name(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError(_('Unit name is required.'))
        existing = Unit.objects.filter(unit_name__iexact=value)
        if self.instance is not None:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError(_('A measurement unit with this name already exists.'))
        return value

    def validate_unit_symbol(self, value):
        return (value or '').strip()
