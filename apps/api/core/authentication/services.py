"""
Authentication services following SOLID principles.
Each service class has a single responsibility (Single Responsibility Principle).
Uses phone_number as identifier (no username/email).
"""
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

# Default role for new registrations; role groups created in migration 0001_add_role_groups.
DEFAULT_REGISTRATION_GROUP_NAME = "visitor"


class UserRegistrationService:
    """
    Service responsible for user registration logic.
    Single Responsibility: Handle user creation and validation.
    """

    def __init__(self):
        self.logger = logger

    def register_user(
        self,
        phone_number: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        **extra_fields
    ) -> User:
        """
        Register a new user with validation.

        Args:
            phone_number: Unique phone number
            password: User password (will be validated)
            first_name: User's first name
            last_name: User's last name
            **extra_fields: Additional user fields

        Returns:
            Created User instance

        Raises:
            ValidationError: If validation fails
        """
        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            self.logger.warning(f"Password validation failed: {e.messages}")
            raise ValidationError({'password': e.messages})

        # Check if user already exists
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError({'phone_number': 'A user with this phone number already exists.'})

        # Create user
        try:
            user = User.objects.create_user(
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra_fields
            )
            # Assign default role so new users have at least one role (e.g. visitor).
            try:
                default_group = Group.objects.get(name=DEFAULT_REGISTRATION_GROUP_NAME)
                user.groups.add(default_group)
            except Group.DoesNotExist:
                self.logger.warning(
                    f"Group '{DEFAULT_REGISTRATION_GROUP_NAME}' not found; "
                    "run authentication migration to create role groups."
                )
            self.logger.info(f"User registered successfully: {phone_number}")
            return user
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            raise ValidationError({'error': 'Failed to create user account.'})


class PasswordResetService:
    """
    Service responsible for password reset logic.
    Single Responsibility: Handle password reset tokens and SMS sending.
    """

    def __init__(self):
        self.logger = logger
        self.token_length = 6  # Short numeric code for SMS
        self.token_expiry_hours = 1

    def generate_reset_token(self) -> str:
        """Generate a secure random numeric token for password reset (SMS-friendly)."""
        return get_random_string(self.token_length, allowed_chars='0123456789')

    def send_reset_sms(self, user, reset_token: str) -> bool:
        """
        Send password reset SMS to user.

        Args:
            user: User instance
            reset_token: Reset token to include in SMS

        Returns:
            True if SMS sent successfully, False otherwise
        """
        # TODO: Implement actual SMS sending (e.g. via Twilio, Kavenegar, etc.)
        self.logger.info(f"Password reset code for {user.phone_number}: {reset_token}")
        return True

    def initiate_password_reset(self, phone_number: str) -> Dict[str, Any]:
        """
        Initiate password reset process for a user.

        Args:
            phone_number: User's phone number

        Returns:
            Dict with status and message
        """
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            # Don't reveal if phone exists (security best practice)
            self.logger.warning(f"Password reset requested for non-existent phone: {phone_number}")
            return {
                'success': True,
                'message': 'If an account exists with this phone number, a reset code has been sent.'
            }

        # Generate reset token
        reset_token = self.generate_reset_token()

        # TODO: Store token in database with expiration
        # PasswordResetToken.objects.create(
        #     user=user,
        #     token=reset_token,
        #     expires_at=timezone.now() + timedelta(hours=self.token_expiry_hours)
        # )

        # Send SMS
        sms_sent = self.send_reset_sms(user, reset_token)

        if sms_sent:
            return {
                'success': True,
                'message': 'Password reset code sent successfully.'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to send password reset code. Please try again later.'
            }


class PasswordChangeService:
    """
    Service responsible for password change logic.
    Single Responsibility: Handle password changes for authenticated users.
    """

    def __init__(self):
        self.logger = logger

    def change_password(
        self,
        user,
        old_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Change user's password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password

        Returns:
            Dict with status and message
        """
        # Verify old password
        if not user.check_password(old_password):
            self.logger.warning(f"Invalid old password attempt for user: {user.phone_number}")
            raise ValidationError({'old_password': 'Current password is incorrect.'})

        # Validate new password
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            self.logger.warning(f"New password validation failed for user {user.phone_number}: {e.messages}")
            raise ValidationError({'new_password': e.messages})

        # Check if new password is same as old
        if user.check_password(new_password):
            raise ValidationError({'new_password': 'New password must be different from current password.'})

        # Set new password
        user.set_password(new_password)
        user.save()

        self.logger.info(f"Password changed successfully for user: {user.phone_number}")
        return {
            'success': True,
            'message': 'Password changed successfully.'
        }
