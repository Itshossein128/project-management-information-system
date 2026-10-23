from datetime import date
import pytest
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from common.reporting_units import SpecialtyUnit
from project_templates.models import (
    ProjectReportingConfiguration,
    ProjectReportingConfigurationUnit,
    ProjectTemplate,
    ProjectTemplateRequiredUnit,
)
from project_templates.serializers import (
    ProjectTemplateCreateSerializer,
    ProjectTemplateDetailSerializer,
)
from project_templates.services import activate_project_reporting_configuration


@pytest.fixture
def sample_template(db, user):
    return ProjectTemplate.objects.create(
        template_name='Test Template',
        description='Test description',
        created_by=user,
    )


@pytest.mark.django_db
def test_project_template_required_unit_uniqueness(sample_template):
    ProjectTemplateRequiredUnit.objects.create(
        template=sample_template,
        unit=SpecialtyUnit.BUILDINGS,
        display_order=0,
    )
    with pytest.raises(IntegrityError):
        ProjectTemplateRequiredUnit.objects.create(
            template=sample_template,
            unit=SpecialtyUnit.BUILDINGS,
            display_order=1,
        )


@pytest.mark.django_db
def test_all_canonical_units_supported(sample_template):
    for i, unit_choice in enumerate(SpecialtyUnit.values):
        ProjectTemplateRequiredUnit.objects.create(
            template=sample_template,
            unit=unit_choice,
            display_order=i,
        )
    assert sample_template.required_units.count() == 6


@pytest.mark.django_db
def test_template_serializer_requires_at_least_one_unit():
    serializer = ProjectTemplateCreateSerializer(
        data={
            'template_name': 'Empty Units Template',
            'required_daily_report_units': [],
        }
    )
    assert not serializer.is_valid()
    assert 'required_daily_report_units' in serializer.errors
    err = serializer.errors['required_daily_report_units']
    codes = [e.code if hasattr(e, 'code') else e for e in (err if isinstance(err, list) else [err])]
    assert 'invalid_required_units' in codes or any('invalid_required_units' in str(c) for c in codes)


@pytest.mark.django_db
def test_template_serializer_rejects_duplicate_units():
    serializer = ProjectTemplateCreateSerializer(
        data={
            'template_name': 'Duplicate Units Template',
            'required_daily_report_units': [SpecialtyUnit.BUILDINGS, SpecialtyUnit.BUILDINGS],
        }
    )
    assert not serializer.is_valid()
    assert 'required_daily_report_units' in serializer.errors
    err = serializer.errors['required_daily_report_units']
    codes = [e.code if hasattr(e, 'code') else e for e in (err if isinstance(err, list) else [err])]
    assert 'invalid_required_units' in codes or any('invalid_required_units' in str(c) for c in codes)


@pytest.mark.django_db
def test_template_serializer_rejects_non_canonical_units():
    serializer = ProjectTemplateCreateSerializer(
        data={
            'template_name': 'Invalid Units Template',
            'required_daily_report_units': ['civil', 'plumbing'],
        }
    )
    assert not serializer.is_valid()
    assert 'required_daily_report_units' in serializer.errors
    err = serializer.errors['required_daily_report_units']
    codes = [e.code if hasattr(e, 'code') else e for e in (err if isinstance(err, list) else [err])]
    assert 'invalid_required_units' in codes or any('invalid_required_units' in str(c) for c in codes)


@pytest.mark.django_db
def test_template_serializer_preserves_display_order(sample_template):
    units = [SpecialtyUnit.SECURITY, SpecialtyUnit.BUILDINGS, SpecialtyUnit.MECHANICAL]
    for i, u in enumerate(units):
        ProjectTemplateRequiredUnit.objects.create(
            template=sample_template,
            unit=u,
            display_order=i,
        )

    data = ProjectTemplateDetailSerializer(sample_template).data
    assert 'required_daily_report_units' in data
    assert data['required_daily_report_units'] == units


@pytest.mark.django_db
def test_editing_template_never_changes_activated_configuration(project, sample_template, user):
    # Setup initial units on template
    for i, u in enumerate([SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL]):
        ProjectTemplateRequiredUnit.objects.create(
            template=sample_template,
            unit=u,
            display_order=i,
        )

    # Activate configuration on project
    config = activate_project_reporting_configuration(
        project=project,
        template=sample_template,
        effective_from=date(2026, 10, 1),
        user=user,
    )
    assert list(config.required_units.values_list('unit', flat=True)) == [
        SpecialtyUnit.BUILDINGS,
        SpecialtyUnit.ELECTRICAL,
    ]

    # Mutate the template
    sample_template.required_units.all().delete()
    for i, u in enumerate([SpecialtyUnit.MECHANICAL, SpecialtyUnit.WAREHOUSE]):
        ProjectTemplateRequiredUnit.objects.create(
            template=sample_template,
            unit=u,
            display_order=i,
        )

    # Verify activated configuration snapshot remains unchanged
    config.refresh_from_db()
    assert list(config.required_units.values_list('unit', flat=True)) == [
        SpecialtyUnit.BUILDINGS,
        SpecialtyUnit.ELECTRICAL,
    ]


@pytest.mark.django_db
def test_no_hard_coded_fallback_list(project, user):
    """When a project has no reporting configuration, resolving configuration for
    a date must return configuration_incomplete with no required units, and NEVER
    fall back to legacy civil/electrical/mechanical or all six units (report-template-api.md).
    """
    from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
    from rest_framework.test import APIClient

    client = APIClient()
    member, _ = ProjectMember.objects.get_or_create(project=project, user=user, defaults={'status': 'active'})
    member.status = 'active'
    member.save()
    role, _ = Role.objects.get_or_create(role_name='Viewer')
    RolePermission.objects.get_or_create(role=role, permission_codename='view_reports')
    ProjectMemberRole.objects.get_or_create(member=member, role=role)

    client.force_authenticate(user=user)
    resp = client.get(f'/api/v1/projects/{project.id}/reporting-configurations/?date=2026-10-23')
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('state') == 'configuration_incomplete'
    assert data.get('configuration') is None
    assert data.get('required_units') == []
    assert data.get('message_code') == 'daily_report_template_required'
