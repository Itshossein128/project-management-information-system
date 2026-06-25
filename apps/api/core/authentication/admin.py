from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'mobile', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups', 'status')
    search_fields = ('username', 'mobile', 'full_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'mobile', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'organization', 'status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'mobile', 'full_name', 'password1', 'password2'),
        }),
    )
