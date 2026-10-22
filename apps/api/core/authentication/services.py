"""Authentication services."""
import hashlib
import logging
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from authentication.models import PasswordResetToken
from .utils import get_tokens_for_user

logger = logging.getLogger(__name__)
User = get_user_model()
DEFAULT_REGISTRATION_GROUP_NAME = 'visitor'


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def blacklist_user_tokens(user) -> None:
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


class UserRegistrationService:
    def register_user(self, password: str, **fields) -> User:
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError({'password': e.messages}) from e
        user = User.objects.create_user(password=password, **fields)
        try:
            user.groups.add(Group.objects.get(name=DEFAULT_REGISTRATION_GROUP_NAME))
        except Group.DoesNotExist:
            logger.warning("Group '%s' not found", DEFAULT_REGISTRATION_GROUP_NAME)
        return user

    def register_and_generate_tokens(self, **validated_data) -> tuple[User, dict]:
        # Pop standard items that aren't user fields (as the serializer validation handles them but keeps them in validated_data)
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        validated_data.pop('phone_number', None)
        validated_data.pop('first_name', None)
        validated_data.pop('last_name', None)

        user = self.register_user(password=password, **validated_data)
        tokens = get_tokens_for_user(user)
        return user, tokens

class LoginService:
    def authenticate_and_issue_tokens(self, login: str, password: str):
        from authentication.utils import authenticate_user, get_tokens_for_user
        from rest_framework.exceptions import ValidationError
        from django.utils.translation import gettext_lazy as _

        user = authenticate_user(login, password)
        if not user:
            raise ValidationError({'error': _('Invalid credentials. Please check your phone number and password.')})
        if not user.is_active:
            raise ValidationError({'error': _('User account is disabled.')})
        tokens = get_tokens_for_user(user)
        return user, tokens


class PasswordResetService:
    token_expiry_hours = 1

    def generate_reset_token(self) -> str:
        return secrets.token_urlsafe(32)

    def send_reset_sms(self, user, reset_token: str) -> bool:
        logger.warning('Password reset SMS delivery is not configured')
        return False

    def initiate_password_reset(self, phone_number: str) -> dict:
        response = {
            'success': True,
            'message': _('If an account exists with this phone number, a reset code has been sent.'),
        }
        try:
            user = User.objects.get(mobile=phone_number)
        except User.DoesNotExist:
            return response
        reset_token = self.generate_reset_token()
        PasswordResetToken.objects.create(
            user=user,
            token_hash=_hash_token(reset_token),
            expires_at=timezone.now() + timedelta(hours=self.token_expiry_hours),
        )
        self.send_reset_sms(user, reset_token)
        return response

    @transaction.atomic
    def reset_password(self, token: str, new_password: str) -> dict:
        # Retire legacy six-digit credentials; they cannot safely identify an account.
        if len(token) != 43:
            raise ValidationError({'token': _('Invalid or expired reset token.')})
        token_hash = _hash_token(token)
        candidates = list(PasswordResetToken.objects.filter(
            token_hash=token_hash, used_at__isnull=True,
            expires_at__gt=timezone.now(),
        )[:2])
        if len(candidates) != 1:
            raise ValidationError({'token': _('Invalid or expired reset token.')})
        prt = candidates[0]
        # Serialize all password changes for this account, then recheck the token.
        user = User.objects.select_for_update().get(pk=prt.user_id)
        prt.refresh_from_db()
        if prt.used_at is not None or prt.expires_at <= timezone.now():
            raise ValidationError({'token': _('Invalid or expired reset token.')})
        validate_password(new_password, user=user)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        blacklist_user_tokens(user)
        return {'success': True, 'message': _('Password reset successfully.')}


class PasswordChangeService:
    @transaction.atomic
    def change_password(self, user, old_password: str, new_password: str) -> dict:
        user = User.objects.select_for_update().get(pk=user.pk)
        if not user.check_password(old_password):
            raise ValidationError({'old_password': _('Current password is incorrect.')})
        validate_password(new_password, user=user)
        if user.check_password(new_password):
            raise ValidationError(
                {'new_password': _('New password must be different from the current password.')}
            )
        user.set_password(new_password)
        user.save(update_fields=['password'])
        PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        blacklist_user_tokens(user)
        return {'success': True, 'message': _('Password changed successfully.')}
