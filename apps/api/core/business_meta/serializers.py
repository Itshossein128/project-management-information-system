"""
Serializers for business meta API. Validate slugs/names with allowlist.
"""
import re
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from authentication.models import phone_regex
from .models import (
    Business,
    BusinessJobPosition,
    TableDefinition,
    FieldDefinition,
    RelationDefinition,
    FieldType,
    RelationKind,
    UserBusinessAssignment,
    WageType,
    AssignmentStatus,
)

SLUG_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')


def validate_slug(value: str) -> str:
    if not value or not SLUG_PATTERN.match(value):
        raise serializers.ValidationError(
            'Must start with a lowercase letter, then only lowercase letters, numbers, and underscores.'
        )
    return value


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_slug(self, value):
        return validate_slug(value)


class TableDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableDefinition
        fields = ['id', 'business', 'name', 'slug', 'ordering', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_slug(self, value):
        return validate_slug(value)


class FieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = [
            'id', 'table', 'name', 'slug', 'field_type', 'required',
            'target_table', 'ordering', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_slug(self, value):
        return validate_slug(value)

    def validate(self, attrs):
        if attrs.get('field_type') == FieldType.REFERENCE and not attrs.get('target_table'):
            raise serializers.ValidationError(
                {'target_table': 'Target table is required for reference fields.'}
            )
        return attrs


class RelationDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationDefinition
        fields = ['id', 'from_table', 'to_table', 'from_field', 'to_field', 'kind', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        from_table = attrs.get('from_table')
        to_table = attrs.get('to_table')
        from_field = attrs.get('from_field')
        if from_table and to_table and from_table.business_id != to_table.business_id:
            raise serializers.ValidationError(
                'from_table and to_table must belong to the same business.'
            )
        if from_field and from_table and from_field.table_id != from_table.id:
            raise serializers.ValidationError(
                'from_field must belong to from_table.'
            )
        to_field = attrs.get('to_field')
        if to_field and to_table and to_field.table_id != to_table.id:
            raise serializers.ValidationError(
                'to_field must belong to to_table.'
            )
        return attrs


class TableDefinitionListSerializer(serializers.ModelSerializer):
    """Light serializer for listing tables (e.g. under a business)."""
    class Meta:
        model = TableDefinition
        fields = ['id', 'name', 'slug', 'ordering', 'created_at', 'updated_at']


class TableDefinitionWithFieldsSerializer(serializers.ModelSerializer):
    """Table with nested field definitions for schema-aware UI."""
    fields = FieldDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = TableDefinition
        fields = ['id', 'business', 'name', 'slug', 'ordering', 'fields', 'created_at', 'updated_at']


class BusinessJobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessJobPosition
        fields = ['id', 'business', 'slug', 'label', 'ordering', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'business']

    def validate_slug(self, value: str) -> str:
        return validate_slug(value)

    def validate(self, attrs):
        business = attrs.get('business') or getattr(self.instance, 'business', None)
        slug = attrs.get('slug') or getattr(self.instance, 'slug', None)
        if business and slug:
            qs = BusinessJobPosition.objects.filter(business=business, slug=slug)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'slug': 'A job position with this slug already exists for this business.'})
        return attrs


class JobPositionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessJobPosition
        fields = ['id', 'slug', 'label', 'ordering']


class BusinessNestedMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'slug']


class UserNestedMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'phone_number', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj) -> str:
        return obj.get_full_name()


class UserBusinessAssignmentReadSerializer(serializers.ModelSerializer):
    user = UserNestedMiniSerializer(read_only=True)
    business = BusinessNestedMiniSerializer(read_only=True)
    job_position = JobPositionNestedSerializer(read_only=True)

    class Meta:
        model = UserBusinessAssignment
        fields = [
            'id',
            'user',
            'business',
            'job_position',
            'wage',
            'wage_type',
            'weekly_total',
            'monthly_total',
            'tools',
            'start_date',
            'end_date',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'business',
            'job_position',
            'wage',
            'wage_type',
            'weekly_total',
            'monthly_total',
            'tools',
            'start_date',
            'end_date',
            'status',
            'created_at',
            'updated_at',
        ]


class UserBusinessAssignmentWriteSerializer(serializers.ModelSerializer):
    """Update an existing assignment (job position + work details)."""

    class Meta:
        model = UserBusinessAssignment
        fields = [
            'job_position',
            'wage',
            'wage_type',
            'weekly_total',
            'monthly_total',
            'tools',
            'start_date',
            'end_date',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        business_pk = self.context.get('business_pk')
        if business_pk is not None:
            self.fields['job_position'].queryset = BusinessJobPosition.objects.filter(
                business_id=business_pk
            )

    def validate_job_position(self, jp: BusinessJobPosition) -> BusinessJobPosition:
        business_pk = self.context.get('business_pk')
        if business_pk is not None and jp.business_id != int(business_pk):
            raise serializers.ValidationError('Job position must belong to this business.')
        return jp


class UserBusinessAssignmentCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=17)
    first_name = serializers.CharField(max_length=150, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, allow_blank=True, default='')
    job_position = serializers.PrimaryKeyRelatedField(queryset=BusinessJobPosition.objects.none())
    wage = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    wage_type = serializers.ChoiceField(choices=WageType.choices, default=WageType.HOURLY)
    weekly_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    monthly_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    tools = serializers.JSONField(required=False, default=list)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=AssignmentStatus.choices, default=AssignmentStatus.ACTIVE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        business_pk = self.context.get('business_pk')
        if business_pk is not None:
            self.fields['job_position'].queryset = BusinessJobPosition.objects.filter(
                business_id=business_pk
            )

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        try:
            phone_regex(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate_job_position(self, jp: BusinessJobPosition) -> BusinessJobPosition:
        business_pk = self.context['business_pk']
        if jp.business_id != int(business_pk):
            raise serializers.ValidationError('Job position must belong to this business.')
        return jp

    def create(self, validated_data):
        from business_meta.assignment_services import create_assignment_for_user

        business_pk = int(self.context['business_pk'])
        phone = validated_data['phone_number'].strip()
        first_name = validated_data.get('first_name') or ''
        last_name = validated_data.get('last_name') or ''
        job_position = validated_data['job_position']

        User = get_user_model()
        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={'first_name': first_name, 'last_name': last_name},
        )
        if not created:
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save(update_fields=['first_name', 'last_name'])

        extra = {
            'wage': validated_data.get('wage', 0),
            'wage_type': validated_data.get('wage_type', WageType.HOURLY),
            'weekly_total': validated_data.get('weekly_total', 0),
            'monthly_total': validated_data.get('monthly_total', 0),
            'tools': validated_data.get('tools') or [],
            'start_date': validated_data.get('start_date'),
            'end_date': validated_data.get('end_date'),
            'status': validated_data.get('status', AssignmentStatus.ACTIVE),
        }
        return create_assignment_for_user(
            business_id=business_pk,
            user=user,
            job_position=job_position,
            **extra,
        )
