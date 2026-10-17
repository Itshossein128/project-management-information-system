"""Approval response contracts consumed by the overview's activation guidance.

These tests use the real API, exception handler, permissions and PostgreSQL;
the browser suite separately tests presentation and simulated transport failures.
"""

from decimal import Decimal
from itertools import combinations
from uuid import uuid4

import pytest
from django.utils import timezone

from master_data.models import ProjectMemberPermissionOverride
from projects.models import ProjectStatus


pytestmark = pytest.mark.django_db
GATES = ('project_manager', 'scope_description', 'budget_approved')
MISSING_SETS = [subset for size in range(1, 4) for subset in combinations(GATES, size)]


@pytest.fixture(params=['fa', 'en'])
def language(request):
    return {'HTTP_ACCEPT_LANGUAGE': request.param}


@pytest.fixture
def pending_project(project):
    project.status = ProjectStatus.PENDING_APPROVAL
    project.budget_approved_at = None
    project.budget_approved_by = None
    project.save()
    return project


def approval_url(project):
    return f'/api/v1/projects/{project.id}/approve/'


def approval_state(project):
    project.refresh_from_db()
    return (project.status, project.budget_approved_at, project.budget_approved_by_id, project.updated_at)


def error_payload(response, expected_status, expected_code):
    assert response.status_code == expected_status
    payload = response.json()
    assert set(payload) == {'error'}
    error = payload['error']
    assert set(error) == {'code', 'message', 'details'}
    assert error['code'] == expected_code
    assert isinstance(error['message'], str) and error['message'].strip()
    assert isinstance(error['details'], dict)
    return error


@pytest.mark.parametrize('missing', MISSING_SETS, ids=lambda fields: '+'.join(fields))
def test_approval_reports_all_and_only_missing_requirements(auth_client, pending_project, language, missing):
    project = pending_project
    if 'project_manager' in missing:
        project.project_manager = None
    if 'scope_description' in missing:
        project.scope_description = ''
    if 'budget_approved' in missing:
        project.contract_amount = None
    project.save()
    before = approval_state(project)

    error = error_payload(auth_client.post(approval_url(project), **language), 400, 'activation_gates_failed')

    assert error['message'] == 'Activation requirements not met.'
    assert error['details'] == {
        'code': 'activation_gates_failed',
        'detail': 'Activation requirements not met.',
        'missing': list(missing),
    }
    assert approval_state(project) == before


def test_whitespace_scope_is_missing(auth_client, pending_project, language):
    pending_project.scope_description = ' \n\t '
    pending_project.save()
    error = error_payload(auth_client.post(approval_url(pending_project), **language), 400, 'activation_gates_failed')
    assert error['details']['missing'] == ['scope_description']


@pytest.mark.parametrize('amount', [Decimal('0'), Decimal('1000.50')])
def test_success_returns_active_project_and_records_approver(auth_client, pending_project, user, language, amount):
    pending_project.contract_amount = amount
    pending_project.save()

    response = auth_client.post(approval_url(pending_project), **language)

    assert response.status_code == 200
    payload = response.json()
    assert 'error' not in payload
    assert payload['project_id'] == str(pending_project.id)
    assert payload['status'] == 'active'
    assert payload['budget_approved_at']
    assert payload['budget_approved_by'] == str(user.id)
    pending_project.refresh_from_db()
    assert pending_project.status == ProjectStatus.ACTIVE
    assert pending_project.budget_approved_at is not None
    assert pending_project.budget_approved_by_id == user.id


def test_success_preserves_existing_budget_approval(auth_client, pending_project, other_user, language):
    pending_project.budget_approved_at = timezone.now()
    pending_project.budget_approved_by = other_user
    pending_project.save()
    approved_at = pending_project.budget_approved_at

    response = auth_client.post(approval_url(pending_project), **language)

    assert response.status_code == 200
    pending_project.refresh_from_db()
    assert pending_project.budget_approved_at == approved_at
    assert pending_project.budget_approved_by_id == other_user.id


@pytest.mark.parametrize('current_status,code', [
    ('draft', 'invalid_status_transition'),
    ('active', 'invalid_status_transition'),
    ('suspended', 'invalid_status_transition'),
    ('completed', 'invalid_status_transition'),
    ('archived', 'project_archived'),
    ('handed_over', 'invalid_status_transition'),
])
def test_wrong_status_reports_transition_error_without_mutation(
    auth_client, pending_project, language, current_status, code, user,
):
    if current_status == 'archived':
        from projects.lifecycle_service import archive
        pending_project.status = 'active'
        pending_project.save()
        pending_project = archive(pending_project, user)
    elif current_status in ('suspended', 'completed'):
        from projects import lifecycle_service
        pending_project.status = 'active'
        pending_project.save()
        pending_project = getattr(lifecycle_service, 'suspend' if current_status == 'suspended' else 'complete')(pending_project, user)
    else:
        pending_project.status = current_status
        pending_project.save()
    before = approval_state(pending_project)

    error = error_payload(auth_client.post(approval_url(pending_project), **language), 400, code)

    assert 'missing' not in error['details']
    if code == 'invalid_status_transition':
        assert error['details']['from'] == current_status
        assert error['details']['to'] == 'active'
    assert approval_state(pending_project) == before


def test_repeat_approval_is_rejected_and_keeps_original_approval(auth_client, pending_project, language):
    assert auth_client.post(approval_url(pending_project), **language).status_code == 200
    before = approval_state(pending_project)
    error_payload(auth_client.post(approval_url(pending_project), **language), 400, 'invalid_status_transition')
    assert approval_state(pending_project) == before


@pytest.mark.parametrize('actor', ['anonymous', 'outsider', 'viewer', 'inactive', 'editor_without_approval'])
def test_denied_approval_does_not_leak_missing_fields_or_change_project(
    api_client, pending_project, user, other_user, member, language, actor,
):
    pending_project.contract_amount = None
    pending_project.save()
    if actor == 'anonymous':
        api_client.force_authenticate(user=None)
    elif actor == 'editor_without_approval':
        from master_data.models import ProjectMember

        manager = ProjectMember.objects.get(project=pending_project, user=user)
        ProjectMemberPermissionOverride.objects.create(
            member=manager, permission_codename='approve_project', is_granted=False,
        )
        api_client.force_authenticate(user=user)
    else:
        if actor == 'outsider':
            member.delete()
        elif actor == 'inactive':
            member.status = 'inactive'
            member.save()
        api_client.force_authenticate(user=other_user)
    before = approval_state(pending_project)

    error = error_payload(
        api_client.post(approval_url(pending_project), **language),
        401 if actor == 'anonymous' else 403,
        'not_authenticated' if actor == 'anonymous' else 'permission_denied',
    )

    assert 'missing' not in error['details']
    assert approval_state(pending_project) == before


def test_approver_does_not_need_edit_permission(api_client, pending_project, other_user, member, language):
    for codename, granted in [('approve_project', True), ('edit_project', False)]:
        ProjectMemberPermissionOverride.objects.create(
            member=member, permission_codename=codename, is_granted=granted,
        )
    api_client.force_authenticate(user=other_user)
    response = api_client.post(approval_url(pending_project), **language)
    assert response.status_code == 200
    assert response.json()['budget_approved_by'] == str(other_user.id)


def test_missing_project_reports_not_found(auth_client, user, language):
    user.is_superuser = True
    user.save()
    error_payload(auth_client.post(f'/api/v1/projects/{uuid4()}/approve/', **language), 404, 'not_found')


def test_complete_missing_information_then_retry_approval(auth_client, pending_project, language):
    pending_project.scope_description = ''
    pending_project.contract_amount = None
    pending_project.save()
    error = error_payload(auth_client.post(approval_url(pending_project), **language), 400, 'activation_gates_failed')
    assert error['details']['missing'] == ['scope_description', 'budget_approved']

    saved = auth_client.patch(
        f'/api/v1/projects/{pending_project.id}/',
        {'scope_description': 'Confirmed scope', 'contract_amount': '1000.50'},
        format='json', **language,
    )
    assert saved.status_code == 200
    assert saved.json()['scope_description'] == 'Confirmed scope'
    assert Decimal(saved.json()['contract_amount']) == Decimal('1000.50')
    assert auth_client.get(f'/api/v1/projects/{pending_project.id}/', **language).json()['status'] == 'pending_approval'
    approved = auth_client.post(approval_url(pending_project), **language)
    assert approved.status_code == 200
    assert approved.json()['status'] == 'active'
