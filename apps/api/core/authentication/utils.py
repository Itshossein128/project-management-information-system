"""
Authentication utility functions.
"""
from typing import Optional
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# Function to handle get tokens for user
def get_tokens_for_user(user) -> dict:
    """
    Build JWT access and refresh tokens with custom claims (groups, is_staff).
    Single place for token payload so login and token refresh stay consistent.
    """
    refresh = RefreshToken.for_user(user)
    role_names = list(user.groups.values_list('name', flat=True))
    refresh['groups'] = role_names
    refresh['is_staff'] = getattr(user, 'is_staff', False)
    access = refresh.access_token
    access['groups'] = role_names
    access['is_staff'] = getattr(user, 'is_staff', False)
    return {
        'access': str(access),
        'refresh': str(refresh),
    }


# Function to handle authenticate user
def authenticate_user(phone_number: str, password: str) -> Optional[User]:
    """
    Authenticate user by phone number.

    Args:
        phone_number: User's phone number
        password: User password

    Returns:
        User instance if authenticated, None otherwise
    """
    try:
        user = User.objects.get(phone_number=phone_number)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
        pass
    return None
