"""Authentication utilities."""
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_tokens_for_user(user) -> dict:
    refresh = RefreshToken.for_user(user)
    role_names = list(user.groups.values_list('name', flat=True))
    refresh['groups'] = role_names
    refresh['is_staff'] = getattr(user, 'is_staff', False)
    access = refresh.access_token
    access['groups'] = role_names
    access['is_staff'] = getattr(user, 'is_staff', False)
    return {'access': str(access), 'refresh': str(refresh)}


def authenticate_user(login: str, password: str):
    user = authenticate(request=None, login=login, password=password)
    if user is not None:
        return user
    return authenticate(request=None, username=login, password=password)
