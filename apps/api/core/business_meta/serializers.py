"""Serializers for project meta API."""
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from authentication.models import phone_regex
from master_data.models import ProjectMember, ProjectPosition, MemberStatus, WageType
from projects.models import Project
from .models import TableDefinition, FieldDefinition, RelationDefinition, FieldType

User = get_user_model()
SLUG_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')


def validate_slug(value: str) -> str:
    if not value or not SLUG_PATTERN.match(value):
        raise serializers.ValidationError(
            'Must start with a lowercase letter, then only lowercase letters, numbers, and underscores.'
        )
    return value


class ProjectNestedMiniSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'slug', 'project_name', 'project_code']


class TableDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableDefinition
        fields = ['id', 'project', 'name', 'slug', 'ordering', 'created_at', 'updated_at']
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
            raise serializers.ValidationError({'target_table': 'Target table is required for reference fields.'})
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
        if from_table and to_table and from_table.project_id != to_table.project_id:
            raise serializers.ValidationError('from_table and to_table must belong to the same project.')
        if from_field and from_table and from_field.table_id != from_table.id:
            raise serializers.ValidationError('from_field must belong to from_table.')
        to_field = attrs.get('to_field')
        if to_field and to_table and to_field.table_id != to_table.id:
            raise serializers.ValidationError('to_field must belong to to_table.')
        return attrs


class TableDefinitionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableDefinition
        fields = ['id', 'name', 'slug', 'ordering', 'created_at', 'updated_at']


class TableDefinitionWithFieldsSerializer(serializers.ModelSerializer):
    fields = FieldDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = TableDefinition
        fields = ['id', 'project', 'name', 'slug', 'ordering', 'fields', 'created_at', 'updated_at']


class ProjectPositionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='position_name', required=False)

    class Meta:
        model = ProjectPosition
        fields = ['id', 'project', 'slug', 'position_name', 'label', 'description', 'ordering', 'is_active']
        read_only_fields = ['id', 'project']

    def validate_slug(self, value: str) -> str:
        return validate_slug(value)

    def create(self, validated_data):
        if 'position_name' not in validated_data and 'label' in self.initial_data:
            validated_data['position_name'] = self.initial_data['label']
        return super().create(validated_data)


class PositionNestedSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='position_name', read_only=True)

    class Meta:
        model = ProjectPosition
        fields = ['id', 'slug', 'label', 'position_name', 'ordering']


class UserNestedMiniSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='mobile', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'phone_number', 'full_name', 'email']


class ProjectMemberReadSerializer(serializers.ModelSerializer):
    user = UserNestedMiniSerializer(read_only=True)
    project = ProjectNestedMiniSerializer(read_only=True)
    job_position = PositionNestedSerializer(source='position', read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            'id', 'user', 'project', 'job_position', 'position',
            'wage', 'wage_type', 'weekly_total', 'monthly_total', 'tools',
            'start_date', 'end_date', 'status', 'joined_at',
        ]
        read_only_fields = fields


class ProjectMemberWriteSerializer(serializers.ModelSerializer):
    job_position = serializers.PrimaryKeyRelatedField(source='position', queryset=ProjectPosition.objects.all())

    class Meta:
        model = ProjectMember
        fields = [
            'job_position', 'position', 'wage', 'wage_type', 'weekly_total', 'monthly_total',
            'tools', 'start_date', 'end_date', 'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_pk = self.context.get('project_pk')
        if project_pk is not None:
            self.fields['job_position'].queryset = ProjectPosition.objects.filter(project_id=project_pk)


class ProjectMemberCreateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    job_position = serializers.PrimaryKeyRelatedField(queryset=ProjectPosition.objects.none())
    wage = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    wage_type = serializers.ChoiceField(choices=WageType.choices, default=WageType.HOURLY)
    weekly_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    monthly_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    tools = serializers.JSONField(required=False, default=list)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=MemberStatus.choices, default=MemberStatus.ACTIVE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_pk = self.context.get('project_pk')
        if project_pk is not None:
            self.fields['job_position'].queryset = ProjectPosition.objects.filter(project_id=project_pk)

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        try:
            phone_regex(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data):
        from business_meta.assignment_services import create_assignment_for_user

        project_pk = self.context['project_pk']
        phone = validated_data['phone_number'].strip()
        full_name = validated_data.get('full_name') or ''
        position = validated_data['job_position']
        username = phone.lstrip('+').replace(' ', '')

        user, created = User.objects.get_or_create(
            mobile=phone,
            defaults={'username': username, 'full_name': full_name},
        )
        if not created and full_name:
            user.full_name = full_name
            user.save(update_fields=['full_name'])

        return create_assignment_for_user(
            project_id=project_pk,
            user=user,
            position=position,
            wage=validated_data.get('wage', 0),
            wage_type=validated_data.get('wage_type', WageType.HOURLY),
            weekly_total=validated_data.get('weekly_total', 0),
            monthly_total=validated_data.get('monthly_total', 0),
            tools=validated_data.get('tools') or [],
            start_date=validated_data.get('start_date'),
            end_date=validated_data.get('end_date'),
            status=validated_data.get('status', MemberStatus.ACTIVE),
        )


# Backward-compatible aliases
BusinessSerializer = ProjectNestedMiniSerializer
BusinessJobPositionSerializer = ProjectPositionSerializer
UserBusinessAssignmentReadSerializer = ProjectMemberReadSerializer
UserBusinessAssignmentWriteSerializer = ProjectMemberWriteSerializer
UserBusinessAssignmentCreateSerializer = ProjectMemberCreateSerializer
