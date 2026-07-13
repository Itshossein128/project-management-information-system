from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenVerifyView

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

app_name = 'authentication'

# Authentication endpoints
urlpatterns = [
    # User Registration
    path('register/', UserRegistrationView.as_view(), name='register'),

    # User Login (Obtain JWT tokens)
    path('login/', LoginView.as_view(), name='login'),

    # Logout (blacklist refresh token)
    path('logout/', LogoutView.as_view(), name='logout'),

    # Refresh expired JWT access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Verify validity of a JWT token
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Blacklist token
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Change Password for authenticated users
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Initiate Password Reset flow
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),

    # Complete Password Reset flow with token
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Current User Profile CRUD
    path('profile/', UserProfileView.as_view(), name='profile'),

    # List available system roles
    path('system-roles/', SystemRolesListView.as_view(), name='system-roles-list'),

    # List project assignments for a specific user
    path('users/<uuid:user_id>/assignments/', UserAssignmentsListView.as_view(), name='user-assignments-list'),

    # List all users (HR/Admin)
    path('users/', UserListView.as_view(), name='user-list'),
]
