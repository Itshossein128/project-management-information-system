"""Inflation mapping CRUD API tests."""

import pytest
from rest_framework import status

from economic.models import CostCategoryInflationMapping
from master_data.models import ProjectMember, ProjectMemberRole, Role

BASE = '/api/v1/projects/{project_id}/economic/inflation-mappings/'


@pytest.fixture
def finance_client(api_client, user, project):
    role = Role.objects.get(role_name='finance_manager')
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=role)
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestInflationMappingsAPI:
    def test_list_includes_global_mappings(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) >= 1
        assert any(r['is_global'] for r in resp.data['results'])

    def test_create_and_delete_project_mapping(self, finance_client, project):
        url = BASE.format(project_id=project.id)
        create = finance_client.post(
            url,
            {'cost_category': 'custom', 'index_name': 'CPI', 'weight': '0.8'},
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        mapping_id = create.data['id']
        assert create.data['is_global'] is False

        delete = finance_client.delete(f'{url}{mapping_id}/')
        assert delete.status_code == status.HTTP_204_NO_CONTENT
        assert not CostCategoryInflationMapping.objects.filter(id=mapping_id).exists()
