"""JWT authentication that follows the visible account status."""

from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from authentication.services import account_can_authenticate


class AccountJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not account_can_authenticate(user):
            raise AuthenticationFailed(_('User account is disabled.'), code='user_inactive')
        return user
