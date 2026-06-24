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

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('system-roles/', SystemRolesListView.as_view(), name='system-roles-list'),
    path('users/<int:user_id>/assignments/', UserAssignmentsListView.as_view(), name='user-assignments-list'),
    path('users/', UserListView.as_view(), name='user-list'),
]
