"""Authentication serializers."""
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from master_data.models import ProjectMember
from .services import UserRegistrationService, PasswordResetService, PasswordChangeService

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, max_length=128, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, max_length=128, style={'input_type': 'password'})
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    username = serializers.CharField(required=False, allow_blank=True, max_length=60)
    first_name = serializers.CharField(required=False, allow_blank=True, write_only=True, max_length=120)
    last_name = serializers.CharField(required=False, allow_blank=True, write_only=True, max_length=120)
    status = serializers.ChoiceField(
        choices=['active', 'inactive', 'suspended'],
        required=False,
        default='active',
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'mobile', 'phone_number', 'full_name',
            'first_name', 'last_name', 'email', 'password', 'password_confirm', 'status',
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
        if not (attrs.get('mobile') or '').strip():
            raise serializers.ValidationError({'mobile': _('Mobile number is required.')})
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': _('Username already exists.')})
        if User.objects.filter(mobile=attrs['mobile']).exists():
            raise serializers.ValidationError({'mobile': _('Mobile number is already registered.')})
        try:
            validate_password(attrs['password'])
        except ValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        validated_data.pop('phone_number', None)
        validated_data.pop('first_name', None)
        validated_data.pop('last_name', None)
        account_status = validated_data.pop('status', 'active')
        service = UserRegistrationService()
        user = service.register_user(password=password, **validated_data)
        if account_status != 'active':
            user.status = account_status
            user.is_active = False
            user.save(update_fields=['status', 'is_active'])
        return user


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='mobile', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'phone_number', 'full_name', 'email', 'created_at', 'roles', 'is_superuser']
        read_only_fields = ['id', 'created_at', 'roles', 'is_superuser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('username', 'mobile'):
            field = self.fields.get(name)
            if field is None:
                continue
            field.validators = [
                validator for validator in field.validators
                if not isinstance(validator, UniqueValidator)
            ]

    def validate_username(self, value):
        if value is not None and not str(value).strip():
            raise serializers.ValidationError(_('This field may not be blank.'))
        if not value:
            return value
        qs = User.objects.filter(username=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(_('Username already exists.'))
        return value

    def validate_mobile(self, value):
        if value is not None and not str(value).strip():
            raise serializers.ValidationError(_('This field may not be blank.'))
        if not value:
            return value
        qs = User.objects.filter(mobile=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(_('Mobile number is already registered.'))
        return value

    def get_roles(self, obj):
        # ⚡ Bolt: Iterating over .all() instead of .values_list() to utilize prefetch cache
        # and avoid N+1 database queries.
        return [group.name for group in obj.groups.all()]


class UserListSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='mobile', read_only=True, allow_null=True)
    assignments_preview = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'mobile', 'phone_number', 'full_name', 'email',
            'created_at', 'is_active', 'status', 'roles', 'assignments_preview',
        ]
        read_only_fields = fields

    def get_roles(self, obj):
        # ⚡ Bolt: Iterating over .all() instead of .values_list() to utilize prefetch cache
        # and avoid N+1 database queries.
        return [group.name for group in obj.groups.all()]

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
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=60)
    username = serializers.CharField(required=False, allow_blank=True, max_length=60)
    password = serializers.CharField(required=True, write_only=True, max_length=128, style={'input_type': 'password'})

    def validate(self, attrs):
        login = attrs.get('phone_number') or attrs.get('username')
        if not login:
            raise serializers.ValidationError(_('Phone number or username is required.'))
        attrs['login'] = login.strip()
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, max_length=128, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, max_length=128, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, max_length=128, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': _('New password fields do not match.')})
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=20)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=128)
    new_password = serializers.CharField(required=True, write_only=True, max_length=128, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, write_only=True, max_length=128, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': _('Password fields do not match.')})
        return attrs


class AccountTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        from datetime import datetime, timezone as datetime_timezone

        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from rest_framework_simplejwt.settings import api_settings
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        from rest_framework_simplejwt.utils import get_md5_hash_password

        from authentication.services import account_can_authenticate

        try:
            refresh = self.token_class(attrs['refresh'])
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        user_id = refresh.get(api_settings.USER_ID_CLAIM)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise InvalidToken(_('User account is disabled.')) from exc
        if not account_can_authenticate(user):
            raise InvalidToken(_('User account is disabled.'))
        if api_settings.CHECK_REVOKE_TOKEN:
            expected = get_md5_hash_password(user.password)
            if refresh.get(api_settings.REVOKE_TOKEN_CLAIM) != expected:
                raise InvalidToken(_('The user\'s password has been changed.'))
        data = super().validate(attrs)
        rotated = data.get('refresh')
        if rotated:
            new_token = self.token_class(rotated)
            OutstandingToken.objects.get_or_create(
                jti=new_token[api_settings.JTI_CLAIM],
                defaults={
                    'user': user,
                    'token': rotated,
                    'created_at': new_token.current_time,
                    'expires_at': datetime.fromtimestamp(new_token['exp'], tz=datetime_timezone.utc),
                },
            )
        return data
