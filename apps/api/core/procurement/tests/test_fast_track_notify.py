"""Fast-track requisition live notifications."""

from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status

from alerts.models import AlertLog, AlertRule
from alerts.services.alert_engine import check_and_fire_for_project
from master_data.models import ProjectMember, ProjectMemberRole
from notifications.models import Notification
from procurement.models import (
    Block,
    RequisitionHeader,
    RequisitionItem,
    RequisitionScope,
    RequisitionStatus,
    RequisitionType,
)
from procurement.services.approval_engine import transition
from procurement.services.fast_track_notify import (
    fast_track_link,
    notify_fast_track_requisition,
)


@pytest.fixture
def material(db, project):
    from resources.models import Material

    return Material.objects.create(
        project=project,
        material_code='MAT-FT',
        material_name='Cement',
        estimated_total_qty=1000,
    )


@pytest.fixture
def block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-FT',
        block_name='Fast Track Block',
        created_by=user,
        updated_by=user,
    )


def _make_requisition(project, user, block, material, req_type=RequisitionType.FAST_TRACK, status=RequisitionStatus.DRAFT):
    req = RequisitionHeader.objects.create(
        project=project,
        block=block,
        scope=RequisitionScope.BLOCK,
        requisition_type=req_type,
        requested_by=user,
        request_date=date.today(),
        status=status,
        urgency='توقف بتن‌ریزی',
        created_by=user,
        updated_by=user,
    )
    RequisitionItem.objects.create(
        header=req,
        line_number=1,
        material=material,
        requested_qty=10,
        created_by=user,
        updated_by=user,
    )
    return req


@pytest.mark.django_db
def test_create_fast_track_via_api_notifies_pm(auth_client, project, user, material, block):
    url = reverse('procurement-req-list', kwargs={'project_pk': project.id})
    resp = auth_client.post(
        url,
        {
            'project': str(project.id),
            'scope': RequisitionScope.BLOCK,
            'block': str(block.id),
            'requisition_type': RequisitionType.FAST_TRACK,
            'request_date': '2026-01-15',
            'urgency': 'توقف کار',
            'items': [{'material': str(material.id), 'requested_qty': '12'}],
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.data
    req_id = resp.data['id']
    log = AlertLog.objects.filter(
        project=project,
        trigger_reference=f'fast_track:{req_id}',
    ).first()
    assert log is not None
    assert log.notifications_sent >= 1
    note = Notification.objects.filter(user=user, project=project).order_by('-created_at').first()
    assert note is not None
    assert req_id in note.link
    assert note.link == f'/projects/{project.id}/procurement/req/{req_id}'
    assert 'فورس‌ماژور' in note.message


@pytest.mark.django_db
def test_create_planned_does_not_notify(auth_client, project, material, block):
    url = reverse('procurement-req-list', kwargs={'project_pk': project.id})
    resp = auth_client.post(
        url,
        {
            'project': str(project.id),
            'scope': RequisitionScope.BLOCK,
            'block': str(block.id),
            'requisition_type': RequisitionType.PLANNED,
            'request_date': '2026-01-15',
            'items': [{'material': str(material.id), 'requested_qty': '5'}],
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.data
    assert not AlertLog.objects.filter(trigger_reference__startswith='fast_track:').exists()


@pytest.mark.django_db
def test_submit_fast_track_notifies_when_created_outside_api(project, user, material, block):
    req = _make_requisition(project, user, block, material)
    assert not AlertLog.objects.filter(trigger_reference=f'fast_track:{req.id}').exists()

    transition(req, action='approve', performed_by=user, comments='submit')
    log = AlertLog.objects.filter(trigger_reference=f'fast_track:{req.id}').first()
    assert log is not None
    note = Notification.objects.filter(user=user, project=project).first()
    assert note is not None
    assert note.link == fast_track_link(req)


@pytest.mark.django_db
def test_fast_track_notify_respects_cooldown(project, user, material, block):
    req = _make_requisition(project, user, block, material)
    first = notify_fast_track_requisition(req)
    second = notify_fast_track_requisition(req)
    assert first is not None
    assert second is None
    assert AlertLog.objects.filter(trigger_reference=f'fast_track:{req.id}').count() == 1
    assert Notification.objects.filter(project=project).count() == 1


@pytest.mark.django_db
def test_fast_track_notifies_project_manager_fk_without_member_role(project, user, material, block):
    ProjectMemberRole.objects.filter(
        member__project=project,
        role__role_name='project_manager',
    ).delete()
    ProjectMember.objects.filter(project=project, user=user).delete()
    project.project_manager = user
    project.save(update_fields=['project_manager'])

    req = _make_requisition(project, user, block, material)
    log = notify_fast_track_requisition(req)
    assert log is not None
    assert log.notifications_sent >= 1
    assert Notification.objects.filter(user=user, project=project).exists()


@pytest.mark.django_db
def test_checker_catchup_fires_for_existing_fast_track(project, user, material, block):
    AlertRule.objects.filter(alert_type='procurement_fast_track').delete()
    AlertRule.objects.create(
        project=None,
        alert_type='procurement_fast_track',
        name='Fast-track',
        notify_roles='project_manager',
        is_active=True,
        cooldown_hours=24,
    )
    req = _make_requisition(project, user, block, material, status=RequisitionStatus.TECHNICAL_REVIEW)
    check_and_fire_for_project(project.id)
    assert AlertLog.objects.filter(
        project=project,
        trigger_reference=f'fast_track:{req.id}',
    ).exists()
