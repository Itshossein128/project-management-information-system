"""
Authentication serializers following SOLID principles.
Each serializer has a single responsibility for data validation and transformation.
Uses phone_number as identifier (no username/email).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .services import (
    UserRegistrationService,
    PasswordResetService,
    PasswordChangeService
)

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Single Responsibility: Validate and transform registration data.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password must meet Django's password validation requirements."
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Must match the password field."
    )

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'password', 'password_confirm', 'first_name', 'last_name']
        read_only_fields = ['id']
        extra_kwargs = {
            'phone_number': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_phone_number(self, value: str) -> str:
        """Validate phone number uniqueness."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate(self, attrs: dict) -> dict:
        """Validate password confirmation matches password."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Password fields do not match.'
            })
        return attrs

    def create(self, validated_data: dict) -> User:
        """Create user using registration service."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        service = UserRegistrationService()
        return service.register_user(
            password=password,
            **validated_data
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read-only for authenticated endpoints).
    Single Responsibility: Serialize user data for API responses.
    Exposes roles (group names) for frontend permission-aware UI.
    """
    roles = serializers.SerializerMethodField(
        help_text="List of role names (Django group names) for this user."
    )
    full_name = serializers.SerializerMethodField(
        help_text="Display name: first_name + last_name"
    )

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'first_name', 'last_name', 'full_name',
            'date_joined', 'roles'
        ]
        read_only_fields = ['id', 'date_joined', 'roles', 'full_name']

    def get_roles(self, obj) -> list[str]:
        """Retrieve the list of role names (Django group names) assigned to the user."""
        return list(obj.groups.values_list('name', flat=True))

    def get_full_name(self, obj) -> str:
        """Retrieve the user's full name."""
        return obj.get_full_name()


class UserListSerializer(serializers.ModelSerializer):
    """
    User row for HR / admin list endpoint (read-only, includes account status).
    """
    roles = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    assignments_preview = serializers.SerializerMethodField(
        help_text="All business–job lines for the user, ordered by business name (UI may show first 2).",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "date_joined",
            "is_active",
            "roles",
            "assignments_preview",
        ]
        read_only_fields = (
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "date_joined",
            "is_active",
            "roles",
            "assignments_preview",
        )

    def get_roles(self, obj) -> list[str]:
        """Retrieve the list of role names (Django group names) assigned to the user."""
        return list(obj.groups.values_list("name", flat=True))

    def get_full_name(self, obj) -> str:
        """Retrieve the user's full name."""
        return obj.get_full_name()

    def get_assignments_preview(self, obj) -> list[dict]:
        """
        Retrieve a preview of the user's business assignments.
        Uses pre-fetched assignments if available to optimize queries.
        """
        from business_meta.models import UserBusinessAssignment

        rows = getattr(obj, "prefetched_assignments", None)
        if rows is None:
            rows = list(
                UserBusinessAssignment.objects.filter(user=obj)
                .select_related("business", "job_position")
                .order_by("business__name")
            )
        return [
            {"business_name": a.business.name, "job_label": a.job_position.label}
            for a in rows
        ]


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login credentials.
    Single Responsibility: Validate login input.
    """
    phone_number = serializers.CharField(required=True, help_text="Phone number")
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password"
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    Single Responsibility: Validate password change input.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Current password"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password (must meet Django's password validation requirements)"
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs: dict) -> dict:
        """Validate password confirmation matches."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New password fields do not match.'
            })
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password request.
    Single Responsibility: Validate phone input for password reset.
    """
    phone_number = serializers.CharField(
        required=True,
        help_text="Phone number associated with the account"
    )


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset with token.
    Single Responsibility: Validate password reset input.
    """
    token = serializers.CharField(
        required=True,
        help_text="Password reset token received via SMS"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password"
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs: dict) -> dict:
        """Validate password confirmation matches."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Password fields do not match.'
            })
        return attrs
