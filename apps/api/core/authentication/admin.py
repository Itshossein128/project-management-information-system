from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from authentication.models import PasswordResetToken
from authentication.services import blacklist_user_tokens
from permissions.role_services import record_access_change

User = get_user_model()


def user_has_retained_history(user) -> bool:
    """True when deleting the person would remove or detach retained history."""
    if user.project_memberships.exists():
        return True
    if user.audit_logs.exists():
        return True
    if user.subject_role_access_changes.exists() or user.role_access_changes.exists():
        return True
    for rel in user._meta.get_fields():
        if not getattr(rel, 'auto_created', False) or not (rel.one_to_many or rel.one_to_one):
            continue
        if getattr(rel, 'related_name', None) in (None, '+'):
            continue
        if rel.related_model is PasswordResetToken:
            continue
        manager = getattr(user, rel.get_accessor_name(), None)
        if manager is not None and hasattr(manager, 'exists') and manager.exists():
            return True
    return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'mobile', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups', 'status')
    search_fields = ('username', 'mobile', 'full_name', 'email')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        if obj.status not in ('active', 'inactive', 'suspended'):
            raise PermissionDenied(_('Status must be active, inactive, or suspended.'))
        if change and 'is_active' in form.changed_data and 'status' in form.changed_data:
            expected_sign_in = form.cleaned_data.get('status') == 'active'
            if bool(form.cleaned_data.get('is_active')) != expected_sign_in:
                raise PermissionDenied(_('Status must be active, inactive, or suspended.'))
        previous = User.objects.filter(pk=obj.pk).values_list('status', flat=True).first() if change else None
        obj.is_active = obj.status == 'active'
        super().save_model(request, obj, form, change)
        if change and previous != obj.status:
            record_access_change(
                actor=request.user,
                project=None,
                subject_user=obj,
                role=None,
                action='account_status_changed',
                before={'status': previous},
                after={'status': obj.status},
            )
            if obj.status in ('inactive', 'suspended'):
                blacklist_user_tokens(obj)

    def delete_model(self, request, obj):
        if user_has_retained_history(obj):
            messages.error(request, _('This person has history and was not deleted.'))
            raise PermissionDenied(_('This person has history and was not deleted.'))
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        blocked = [user for user in queryset if user_has_retained_history(user)]
        if blocked:
            messages.error(request, _('This person has history and was not deleted.'))
            raise PermissionDenied(_('This person has history and was not deleted.'))
        super().delete_queryset(request, queryset)

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
