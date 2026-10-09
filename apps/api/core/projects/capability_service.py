"""Per-project capability toggles (FR-CORE-012)."""
from __future__ import annotations

from rest_framework.exceptions import APIException, ValidationError

from projects.models import (
    CAPABILITY_CATALOG,
    CapabilityMode,
    ProjectCapabilitySetting,
)


class CapabilityDisabled(APIException):
    status_code = 403
    default_code = 'capability_disabled'
    default_detail = {'code': 'capability_disabled', 'message': 'Capability disabled.'}


def list_capability_settings(project, user):
    """Return settings for catalog keys, seeding missing rows as enabled/optional."""
    existing = {
        s.capability_key: s
        for s in ProjectCapabilitySetting.objects.filter(project=project)
    }
    result = []
    for key in CAPABILITY_CATALOG:
        setting = existing.get(key)
        if setting is None:
            setting = ProjectCapabilitySetting.objects.create(
                project=project,
                capability_key=key,
                enabled=True,
                mode=CapabilityMode.OPTIONAL,
                created_by=user,
                updated_by=user,
            )
        result.append(setting)
    return result


def update_capability_setting(project, capability_key: str, *, enabled=None, mode=None, user):
    if capability_key not in CAPABILITY_CATALOG:
        raise ValidationError(
            {'code': 'unknown_capability_key', 'message': f'Unknown capability: {capability_key}'}
        )
    setting, _ = ProjectCapabilitySetting.objects.get_or_create(
        project=project,
        capability_key=capability_key,
        defaults={
            'enabled': True,
            'mode': CapabilityMode.OPTIONAL,
            'created_by': user,
            'updated_by': user,
        },
    )
    if enabled is not None:
        setting.enabled = bool(enabled)
    if mode is not None:
        if mode not in CapabilityMode.values:
            raise ValidationError({'mode': 'Invalid mode'})
        setting.mode = mode
        if mode == CapabilityMode.DISABLED:
            setting.enabled = False
    setting.updated_by = user
    setting.save()
    return setting


def capability_enabled(project, capability_key: str) -> bool:
    """Return False when the capability is explicitly disabled for the project."""
    if capability_key not in CAPABILITY_CATALOG:
        return True
    setting = ProjectCapabilitySetting.objects.filter(
        project=project,
        capability_key=capability_key,
    ).first()
    if setting is None:
        return True
    return not setting.is_effectively_disabled


def assert_capability_enabled(project, capability_key: str) -> None:
    """Raise PermissionDenied with capability_disabled when toggled off."""
    if capability_key not in CAPABILITY_CATALOG:
        return
    setting = ProjectCapabilitySetting.objects.filter(
        project=project,
        capability_key=capability_key,
    ).first()
    if setting is None:
        return
    if setting.is_effectively_disabled:
        raise CapabilityDisabled(
            detail={
                'code': 'capability_disabled',
                'message': f'Capability {capability_key} is disabled for this project.',
            }
        )
