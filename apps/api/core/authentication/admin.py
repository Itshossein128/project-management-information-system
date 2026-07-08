"""
Admin configuration for authentication app.
Custom User model with phone_number as identifier.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model.
    Customizes the Django Admin interface to use phone_number instead of username.
    """

    # The fields to display in the user list view.
    list_display = ('phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')

    # Fields that can be used to filter the user list.
    list_filter = ('is_staff', 'is_active', 'groups')

    # Fields that can be searched in the user list view.
    search_fields = ('phone_number', 'first_name', 'last_name')

    # Default ordering for the user list view.
    ordering = ('phone_number',)

    # Configuration for the fieldsets displayed on the user edit page.
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Configuration for the fieldsets displayed on the user creation page.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
