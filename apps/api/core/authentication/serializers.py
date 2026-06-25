"""Authentication serializers."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from master_data.models import ProjectMember
from .services import UserRegistrationService, PasswordResetService, PasswordChangeService

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    phone_number = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True, max_length=60)
    first_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    last_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'mobile', 'phone_number', 'full_name',
            'first_name', 'last_name', 'email', 'password', 'password_confirm',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'full_name': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': _('Password fields do not match.')})
        phone = attrs.get('phone_number') or attrs.get('mobile')
        if phone and not attrs.get('mobile'):
            attrs['mobile'] = phone.strip()
        if not attrs.get('full_name'):
            first = (attrs.pop('first_name', None) or '').strip()
            last = (attrs.pop('last_name', None) or '').strip()
            attrs['full_name'] = f'{first} {last}'.strip()
        else:
            attrs.pop('first_name', None)
            attrs.pop('last_name', None)
        if not attrs.get('username'):
            mobile = attrs.get('mobile', '')
            attrs['username'] = mobile.lstrip('+').replace(' ', '') or attrs.get('email', 'user')
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': _('Username already exists.')})
        if attrs.get('mobile') and User.objects.filter(mobile=attrs['mobile']).exists():
            raise serializers.ValidationError({'mobile': _('Mobile number is already registered.')})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        validated_data.pop('phone_number', None)
        validated_data.pop('first_name', None)
        validated_data.pop('last_name', None)
        service = UserRegistrationService()
        return service.register_user(password=password, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='mobile', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'phone_number', 'full_name', 'email', 'created_at', 'roles']
        read_only_fields = ['id', 'created_at', 'roles']

    def get_roles(self, obj):
        return list(obj.groups.values_list('name', flat=True))


class UserListSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='mobile', read_only=True, allow_null=True)
    assignments_preview = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'mobile', 'phone_number', 'full_name', 'email',
            'created_at', 'is_active', 'roles', 'assignments_preview',
        ]
        read_only_fields = fields

    def get_roles(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def get_assignments_preview(self, obj):
        rows = getattr(obj, 'prefetched_memberships', None)
        if rows is None:
            rows = list(
                ProjectMember.objects.filter(user=obj)
                .select_related('project', 'position')
                .order_by('project__project_name')
            )
        return [
            {'business_name': m.project.project_name, 'job_label': m.position.position_name if m.position else ''}
            for m in rows
        ]


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        login = attrs.get('phone_number') or attrs.get('username')
        if not login:
            raise serializers.ValidationError(_('Phone number or username is required.'))
        attrs['login'] = login.strip()
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': _('New password fields do not match.')})
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': _('Password fields do not match.')})
        return attrs
