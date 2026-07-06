from rest_framework import serializers

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from permissions.constants import PERMISSIONS
from permissions.services import get_effective_permissions, permissions_summary


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'role_name', 'description', 'permissions']

    def get_permissions(self, obj):
        # ⚡ Bolt: Iterate over .all() to utilize prefetch cache
        # Using .values_list() bypasses the cache and triggers N+1 queries.
        return [rp.permission_codename for rp in obj.role_permissions.all()]


class ProjectMemberListSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='user.id', read_only=True, allow_null=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMember
        fields = [
            'user_id',
            'full_name',
            'email',
            'mobile',
            'roles',
            'status',
            'joined_at',
            'last_login',
            'invited_email',
        ]

    def get_full_name(self, obj):
        if obj.user_id:
            return obj.user.full_name
        return obj.invited_email or ''

    def get_email(self, obj):
        if obj.user_id:
            return obj.user.email or ''
        return obj.invited_email or ''

    def get_mobile(self, obj):
        if obj.user_id:
            return obj.user.mobile or ''
        return ''

    def get_roles(self, obj):
        # ⚡ Bolt: Iterate over .all() to utilize prefetch cache
        # Using .select_related() on a prefetched related manager bypasses the cache and causes N+1 queries.
        return [mr.role.role_name for mr in obj.member_roles.all()]

    def get_last_login(self, obj):
        if obj.user_id and obj.user.last_login:
            return obj.user.last_login.isoformat()
        return None


class ProjectMemberCreateSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        email = (attrs.get('email') or '').strip()
        if not user_id and not email:
            raise serializers.ValidationError('Either user_id or email is required.')
        if not attrs.get('role_ids'):
            raise serializers.ValidationError({'role_ids': 'At least one role is required.'})
        return attrs


class ProjectMemberUpdateSerializer(serializers.Serializer):
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    status = serializers.ChoiceField(choices=MemberStatus.choices, required=False)


class PermissionOverrideSerializer(serializers.Serializer):
    permission_codename = serializers.ChoiceField(choices=list(PERMISSIONS.keys()))
    is_granted = serializers.BooleanField()


class MemberPermissionsSerializer(serializers.Serializer):
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, member):
        return permissions_summary(member)


class EffectivePermissionsSerializer(serializers.Serializer):
    effective = serializers.DictField()

    @staticmethod
    def from_member(member):
        effective = get_effective_permissions(member)
        return {
            'effective': {k: v for k, v in effective.items()},
            'permissions': permissions_summary(member),
        }
