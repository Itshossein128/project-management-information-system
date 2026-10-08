from datetime import date
from decimal import Decimal

import pytest

from cost_control.models import ActualCost, Budget, CostCategory
from documents.models import ProjectDocument
from projects.models import Activity
from schedule.models import ActivityProgress
from wbs.services import create_wbs_node


@pytest.mark.django_db
def test_delete_blocked_by_budget(auth_client, project, user):
    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    Budget.objects.create(
        project=project,
        wbs=node,
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('1000'),
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{node.id}/')
    assert resp.status_code == 409
    assert 'wbs_has_cost' in str(resp.json())


@pytest.mark.django_db
def test_delete_blocked_by_document(auth_client, project, user):
    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    ProjectDocument.objects.create(
        project=project,
        title='Spec',
        related_wbs=node,
        uploaded_by=user,
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{node.id}/')
    assert resp.status_code == 409
    assert 'wbs_has_documents' in str(resp.json())


@pytest.mark.django_db
def test_delete_blocked_by_progress(auth_client, project, user):
    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    act = Activity.objects.create(
        project=project,
        wbs=node,
        activity_code='A1',
        activity_name='Act',
        created_by=user,
        updated_by=user,
    )
    ActivityProgress.objects.create(
        activity=act,
        report_date=date(2024, 6, 1),
        actual_progress=Decimal('10'),
        updated_by=user,
    )
    resp = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{node.id}/')
    assert resp.status_code == 409
    # activities alone also block; accept either progress or activities code
    blob = str(resp.json())
    assert 'wbs_has_progress' in blob or 'wbs_has_activities' in blob


@pytest.mark.django_db
def test_delete_clean_leaf_soft_deletes(auth_client, project):
    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    resp = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{node.id}/')
    assert resp.status_code == 204
    node.refresh_from_db()
    assert node.is_deleted is True
