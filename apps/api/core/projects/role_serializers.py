import re

from rest_framework import serializers

from master_data.models import Role
from permissions.constants import ALL_PERMISSION_CODENAMES
from permissions.role_services import is_system_role, set_role_permissions


ROLE_NAME_RE = re.compile(r'^[a-z][a-z0-9_]*$')


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    is_system = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'role_name', 'description', 'permissions', 'is_system']

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
        name = value.strip()
        if not ROLE_NAME_RE.match(name):
            raise serializers.ValidationError(
                'Role name must start with a letter and contain only lowercase letters, numbers, and underscores.',
            )
        if Role.objects.filter(role_name=name).exists():
            raise serializers.ValidationError('A role with this name already exists.')
        return name


class RoleUpdateSerializer(serializers.Serializer):
    role_name = serializers.CharField(max_length=60, required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_role_name(self, value):
        name = value.strip()
        if not ROLE_NAME_RE.match(name):
            raise serializers.ValidationError(
                'Role name must start with a letter and contain only lowercase letters, numbers, and underscores.',
            )
        role = self.context['role']
        if Role.objects.filter(role_name=name).exclude(pk=role.pk).exists():
            raise serializers.ValidationError('A role with this name already exists.')
        return name


class RolePermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=list(ALL_PERMISSION_CODENAMES)),
        allow_empty=True,
    )

    def update(self, instance, validated_data):
        return set_role_permissions(instance, validated_data['permissions'])
