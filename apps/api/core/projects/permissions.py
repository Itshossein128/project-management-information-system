"""Backward-compatible re-exports; prefer permissions.project."""

from permissions.project import HasProjectPermission, IsProjectMember

__all__ = ['HasProjectPermission', 'IsProjectMember']
