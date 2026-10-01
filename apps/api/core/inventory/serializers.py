from decimal import Decimal, InvalidOperation

from django.utils.translation import gettext as _
from rest_framework import serializers

from .models import (
    Item,
    Category,
    SpaceMaterialRequest,
    DepartmentActivityRecord,
    department_uses_unit,
    is_warehouse_department,
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


def _as_decimal(value, default: Decimal = Decimal('0')) -> Decimal:
    if value is None or value == '':
        return default
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise serializers.ValidationError(_('Enter a valid number.')) from exc


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
            'material_type',
            'quantity_in',
            'quantity_out',
            'consumption_location',
            'supplier',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'project_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'unit': {'required': False, 'allow_blank': True},
            'location': {'required': False, 'allow_blank': True},
            'activity_description': {'required': False, 'allow_blank': True},
            'contractor': {'required': False, 'allow_blank': True},
            'material_type': {'required': False, 'allow_blank': True},
            'consumption_location': {'required': False, 'allow_blank': True},
            'supplier': {'required': False, 'allow_blank': True},
            'quantity_in': {'required': False},
            'quantity_out': {'required': False},
            'description': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        department = attrs.get('department')
        if department is None and self.instance is not None:
            department = self.instance.department

        errors: dict[str, str] = {}

        def _merged(field: str, default=''):
            if field in attrs:
                return attrs[field]
            if self.instance is not None:
                return getattr(self.instance, field)
            return default

        if is_warehouse_department(department or ''):
            material_type = str(_merged('material_type', '') or '').strip()
            unit_text = str(_merged('unit', '') or '').strip()
            consumption_location = str(_merged('consumption_location', '') or '').strip()
            supplier = str(_merged('supplier', '') or '').strip()

            if not material_type:
                errors['material_type'] = _('This field is required.')
            elif len(material_type) > 255:
                errors['material_type'] = _(
                    'Ensure this field has no more than 255 characters.'
                )

            if not unit_text:
                errors['unit'] = _('This field is required.')
            elif len(unit_text) > 64:
                errors['unit'] = _('Ensure this field has no more than 64 characters.')

            if not consumption_location:
                errors['consumption_location'] = _('This field is required.')
            elif len(consumption_location) > 255:
                errors['consumption_location'] = _(
                    'Ensure this field has no more than 255 characters.'
                )

            if not supplier:
                errors['supplier'] = _('This field is required.')
            elif len(supplier) > 255:
                errors['supplier'] = _(
                    'Ensure this field has no more than 255 characters.'
                )

            try:
                quantity_in = _as_decimal(_merged('quantity_in', 0))
            except serializers.ValidationError:
                errors['quantity_in'] = _('Enter a valid number.')
                quantity_in = Decimal('0')

            try:
                quantity_out = _as_decimal(_merged('quantity_out', 0))
            except serializers.ValidationError:
                errors['quantity_out'] = _('Enter a valid number.')
                quantity_out = Decimal('0')

            if 'quantity_in' not in errors and quantity_in < 0:
                errors['quantity_in'] = _(
                    'Quantity must be greater than or equal to zero.'
                )
            if 'quantity_out' not in errors and quantity_out < 0:
                errors['quantity_out'] = _(
                    'Quantity must be greater than or equal to zero.'
                )
            if (
                'quantity_in' not in errors
                and 'quantity_out' not in errors
                and quantity_in <= 0
                and quantity_out <= 0
            ):
                msg = _(
                    'At least one of quantity_in or quantity_out must be greater than zero.'
                )
                errors['quantity_in'] = msg
                errors['quantity_out'] = msg

            if errors:
                raise serializers.ValidationError(errors)

            attrs['material_type'] = material_type
            attrs['unit'] = unit_text[:64]
            attrs['consumption_location'] = consumption_location
            attrs['supplier'] = supplier
            attrs['quantity_in'] = quantity_in
            attrs['quantity_out'] = quantity_out
            attrs['location'] = ''
            attrs['activity_description'] = ''
            attrs['contractor'] = ''
            return attrs

        # Non-warehouse: preserve prior required rules; clear warehouse fields.
        location = str(_merged('location', '') or '').strip()
        activity_description = str(_merged('activity_description', '') or '').strip()
        contractor = str(_merged('contractor', '') or '').strip()
        unit = _merged('unit', '')
        unit_text = '' if unit is None else str(unit).strip()

        if not location:
            errors['location'] = _('This field is required.')
        elif len(location) > 255:
            errors['location'] = _(
                'Ensure this field has no more than 255 characters.'
            )

        if not activity_description:
            errors['activity_description'] = _('This field is required.')
        elif len(activity_description) > 500:
            errors['activity_description'] = _(
                'Ensure this field has no more than 500 characters.'
            )

        if not contractor:
            errors['contractor'] = _('This field is required.')
        elif len(contractor) > 255:
            errors['contractor'] = _(
                'Ensure this field has no more than 255 characters.'
            )

        if not department_uses_unit(department or ''):
            attrs['unit'] = ''
        elif not unit_text:
            errors['unit'] = _('This field is required.')
        elif len(unit_text) > 64:
            errors['unit'] = _('Ensure this field has no more than 64 characters.')
        else:
            attrs['unit'] = unit_text[:64]

        if errors:
            raise serializers.ValidationError(errors)

        attrs['location'] = location
        attrs['activity_description'] = activity_description
        attrs['contractor'] = contractor
        attrs['material_type'] = ''
        attrs['quantity_in'] = Decimal('0')
        attrs['quantity_out'] = Decimal('0')
        attrs['consumption_location'] = ''
        attrs['supplier'] = ''
        return attrs
