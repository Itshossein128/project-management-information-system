import pytest
from decimal import Decimal
from rest_framework import status

from projects.models import Activity, ActivityRelation, RelationType
from schedule.models import ActivityProgress
from wbs.services import create_wbs_node


def _create_activity(project, wbs, user, code='A1', name='Activity 1', **kwargs):
    return Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code=code,
        activity_name=name,
        created_by=user,
        updated_by=user,
        **kwargs,
    )


@pytest.mark.django_db
class TestActivitiesAPI:
    def test_list_activities(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        _create_activity(project, wbs, user)
        response = auth_client.get(f'/api/v1/projects/{project.id}/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['activity_code'] == 'A1'

    def test_create_activity(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/activities/',
            {
                'activity_code': 'A2',
                'activity_name': 'New Activity',
                'wbs_id': str(wbs.id),
                'status': 'not_started',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['activity_code'] == 'A2'
        assert 'planned_duration' in response.data

    def test_weight_summary(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        _create_activity(project, wbs, user, code='A1', weight=Decimal('0.6'))
        _create_activity(project, wbs, user, code='A2', weight=Decimal('0.37'))
        response = auth_client.get(f'/api/v1/projects/{project.id}/activities/weight-summary/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_weight'] == pytest.approx(0.97, abs=0.001)
        assert response.data['is_balanced'] is False
        assert response.data['warning'] is not None

    def test_delete_with_progress_returns_409(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        act = _create_activity(project, wbs, user)
        ActivityProgress.objects.create(
            activity=act,
            report_date='2024-06-01',
            actual_progress=Decimal('10'),
        )
        response = auth_client.delete(f'/api/v1/projects/{project.id}/activities/{act.id}/')
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_soft_delete_activity(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        act = _create_activity(project, wbs, user)
        response = auth_client.delete(f'/api/v1/projects/{project.id}/activities/{act.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Activity.objects.filter(pk=act.id).count() == 0
        assert Activity.all_objects.filter(pk=act.id, is_deleted=True).exists()

    def test_network_endpoint(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        _create_activity(project, wbs, user)
        response = auth_client.get(f'/api/v1/projects/{project.id}/activities/network/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['nodes']) == 1
        assert response.data['edges'] == []

    def test_viewer_can_list(self, api_client, project, member):
        api_client.force_authenticate(user=member.user)
        response = api_client.get(f'/api/v1/projects/{project.id}/activities/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestActivityRelationsAPI:
    def test_create_relation(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        a1 = _create_activity(project, wbs, user, code='A1')
        a2 = _create_activity(project, wbs, user, code='A2')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/activities/{a1.id}/relations/',
            {
                'role': 'predecessor',
                'successor_id': str(a2.id),
                'relation_type': 'FS',
                'lag_days': 0,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_cycle_rejected(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        a = _create_activity(project, wbs, user, code='A1')
        b = _create_activity(project, wbs, user, code='A2')
        c = _create_activity(project, wbs, user, code='A3')

        ActivityRelation.objects.create(
            predecessor=a,
            successor=b,
            relation_type=RelationType.FS,
            created_by=user,
            updated_by=user,
        )
        ActivityRelation.objects.create(
            predecessor=b,
            successor=c,
            relation_type=RelationType.FS,
            created_by=user,
            updated_by=user,
        )

        response = auth_client.post(
            f'/api/v1/projects/{project.id}/activities/{c.id}/relations/',
            {
                'role': 'predecessor',
                'successor_id': str(a.id),
                'relation_type': 'FS',
                'lag_days': 0,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'حلقه' in response.data['error']['message']

    def test_duplicate_relation_rejected(self, auth_client, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        a1 = _create_activity(project, wbs, user, code='A1')
        a2 = _create_activity(project, wbs, user, code='A2')
        ActivityRelation.objects.create(
            predecessor=a1,
            successor=a2,
            created_by=user,
            updated_by=user,
        )
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/activities/{a1.id}/relations/',
            {
                'role': 'predecessor',
                'successor_id': str(a2.id),
                'relation_type': 'SS',
                'lag_days': 1,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_409_CONFLICT
