"""Operation receipt contract: mutation and receipt share an atomic boundary."""
from copy import deepcopy
from importlib.util import find_spec
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied

from master_data.models import MemberStatus, ProjectMember
from sub_reports.models import OfflineOperationReceipt

pytestmark = pytest.mark.django_db


def service():
    assert find_spec('sub_reports.services.offline_sync') is not None, 'offline receipt service is required'
    from sub_reports.services.offline_sync import apply_idempotent_operation
    return apply_idempotent_operation


def operation():
    return {'operation_id': str(uuid4()), 'scope': {'kind': 'unit', 'unit': 'buildings'},
            'action': 'update', 'target': {'kind': 'header'}, 'payload': {'form_code': 'new'}}


def test_success_replay_and_changed_payload(project, user):
    apply = service()
    op = operation()
    calls = []
    def mutate():
        calls.append(True)
        project.scope_description = 'changed'
        project.save(update_fields=['scope_description'])
        return {'outcome': 'success', 'target': {'server_id': str(project.id)}}
    first = apply(project=project, actor=user, operation=op, mutate=mutate)
    assert apply(project=project, actor=user, operation=deepcopy(op), mutate=mutate) == first
    assert len(calls) == 1
    assert OfflineOperationReceipt.objects.filter(project=project, actor=user, operation_id=op['operation_id']).count() == 1
    changed = deepcopy(op)
    changed['payload']['form_code'] = 'changed payload'
    result = apply(project=project, actor=user, operation=changed, mutate=mutate)
    assert result['error']['code'] == 'operation_id_reused'
    assert result['outcome'] != 'success'
    assert len(calls) == 1


def test_mutation_failure_rolls_back_receipt_and_business_change(project, user):
    apply = service()
    op = operation()
    old = project.scope_description
    def mutate():
        project.scope_description = 'must roll back'
        project.save(update_fields=['scope_description'])
        raise RuntimeError('failure before receipt commit')
    with pytest.raises(RuntimeError):
        apply(project=project, actor=user, operation=op, mutate=mutate)
    project.refresh_from_db()
    assert project.scope_description == old
    assert not OfflineOperationReceipt.objects.filter(project=project, actor=user, operation_id=op['operation_id']).exists()


def test_receipt_replay_requires_current_permission(project, user, other_user):
    apply = service()
    op = operation()
    apply(project=project, actor=user, operation=op, mutate=lambda: {'outcome': 'success'})
    ProjectMember.objects.filter(project=project, user=user).update(status=MemberStatus.INACTIVE)
    with pytest.raises(PermissionDenied):
        apply(project=project, actor=user, operation=op, mutate=lambda: pytest.fail('must not replay'))
    with pytest.raises(PermissionDenied):
        apply(project=project, actor=other_user, operation=op, mutate=lambda: pytest.fail('must not execute'))


@pytest.mark.parametrize('outcome', ['validation_error', 'conflict', 'retryable_failure'])
def test_rejected_operation_rolls_back_business_writes(project, user, outcome):
    apply = service()
    op = operation()
    old = project.scope_description
    def mutate():
        project.scope_description = 'must roll back'
        project.save(update_fields=['scope_description'])
        return {'outcome': outcome, 'error': {'code': 'expected'}}
    result = apply(project=project, actor=user, operation=op, mutate=mutate)
    assert result['outcome'] == outcome
    project.refresh_from_db()
    assert project.scope_description == old
    receipts = OfflineOperationReceipt.objects.filter(project=project, actor=user, operation_id=op['operation_id'])
    assert receipts.exists() is (outcome != 'retryable_failure')
