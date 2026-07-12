from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class UsernameOrMobileBackend(ModelBackend):
    """Authenticate by username or mobile number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        login = kwargs.get('login') or username or kwargs.get('mobile') or kwargs.get('phone_number')
        if login is None or password is None:
            return None
        user = None
        try:
            user = User.objects.get(username=login)
        except User.DoesNotExist:
            try:
                user = User.objects.get(mobile=login)
            except User.DoesNotExist:
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
