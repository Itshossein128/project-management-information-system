import re

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from master_data.models import Role
from permissions.constants import ALL_PERMISSION_CODENAMES
from permissions.role_services import is_system_role, set_role_permissions


# Letters (any script, e.g. Persian), digits, spaces, hyphens, underscores.
ROLE_NAME_RE = re.compile(r'^[\w]([\w\s\-]*[\w])?$', re.UNICODE)


def _normalize_role_name(value: str) -> str:
    return ' '.join(value.split())


def _validate_role_name_format(name: str) -> None:
    if not name:
        raise serializers.ValidationError(_('Role name is required.'))
    if not ROLE_NAME_RE.match(name):
        raise serializers.ValidationError(
            _('Role name may only contain letters, numbers, spaces, hyphens, and underscores.'),
        )


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    is_system = serializers.SerializerMethodField()
    project_id = serializers.UUIDField(allow_null=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'role_name', 'description', 'permissions', 'is_system', 'project_id']

    def get_permissions(self, obj):
        return [rp.permission_codename for rp in obj.role_permissions.all()]

    def get_is_system(self, obj):
        return is_system_role(obj)


class RoleCreateSerializer(serializers.Serializer):
    role_name = serializers.CharField(max_length=60)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=list(ALL_PERMISSION_CODENAMES)),
        required=False,
        default=list,
    )

    def validate_role_name(self, value):
        name = _normalize_role_name(value)
        _validate_role_name_format(name)
        project = self.context.get('project')
        existing = Role.objects.filter(role_name=name)
        if project is None:
            existing = existing.filter(project__isnull=True)
        else:
            existing = existing.filter(project=project)
        if existing.exists():
            raise serializers.ValidationError(_('A role with this name already exists.'))
        return name


class RoleUpdateSerializer(serializers.Serializer):
    role_name = serializers.CharField(max_length=60, required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_role_name(self, value):
        name = _normalize_role_name(value)
        _validate_role_name_format(name)
        role = self.context['role']
        existing = Role.objects.filter(role_name=name).exclude(pk=role.pk)
        if role.project_id is None:
            existing = existing.filter(project__isnull=True)
        else:
            existing = existing.filter(project_id=role.project_id)
        if existing.exists():
            raise serializers.ValidationError(_('A role with this name already exists.'))
        return name


class RolePermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=list(ALL_PERMISSION_CODENAMES)),
        allow_empty=True,
    )

    def update(self, instance, validated_data):
        return set_role_permissions(instance, validated_data['permissions'])
