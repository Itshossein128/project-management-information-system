"""
Authentication URL configuration.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    LoginView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
    UserProfileView,
    UserListView,
    UserAssignmentsListView,
    SystemRolesListView,
)

app_name = 'authentication'

# URL routing for authentication and user management endpoints
urlpatterns = [
    # User registration endpoint
    path('register/', UserRegistrationView.as_view(), name='register'),

    # User login endpoint (issues JWT tokens)
    path('login/', LoginView.as_view(), name='login'),

    # Endpoint to refresh JWT access tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint for an authenticated user to change their password
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Endpoint to initiate a password reset (e.g., send email/SMS)
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),

    # Endpoint to complete the password reset using a token
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Retrieve or update the authenticated user's profile
    path('profile/', UserProfileView.as_view(), name='profile'),

    # List all available system roles
    path('system-roles/', SystemRolesListView.as_view(), name='system-roles-list'),

    # List all business assignments for a specific user
    path('users/<int:user_id>/assignments/', UserAssignmentsListView.as_view(), name='user-assignments-list'),

    # List all users in the system (typically for HR/Admin)
    path('users/', UserListView.as_view(), name='user-list'),
]
