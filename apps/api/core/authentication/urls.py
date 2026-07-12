"""Authentication URL configuration."""
from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView

from .views import (
    UserRegistrationView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
    TokenRefreshView,
    UserProfileView,
    UserListView,
    UserAssignmentsListView,
    SystemRolesListView,
)

# Application namespace for reversing URLs.
app_name = 'authentication'

# URL routing configurations for the authentication app.
# Defines endpoints for user authentication, registration, password management, profile management, user listing, role listing, and assignments.
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('system-roles/', SystemRolesListView.as_view(), name='system-roles-list'),
    path('users/<uuid:user_id>/assignments/', UserAssignmentsListView.as_view(), name='user-assignments-list'),
    path('users/', UserListView.as_view(), name='user-list'),
]
