import pytest
from rest_framework import status
from rest_framework.test import APIClient

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from projects.services import create_project_with_creator

BASE = '/api/v1/projects/{project_id}/decision-cases/'


@pytest.mark.django_db
class TestDecisionCaseAPI:
    def test_create_list_get_methods_and_lists(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        create = auth_client.post(
            url,
            {
                'title': 'انتخاب پیمانکار',
                'selected_methods': ['saw', 'topsis'],
                'criteria': ['تجربه', 'قیمت'],
                'alternatives': ['الف', 'ب'],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        assert create.data['selected_methods'] == ['saw', 'topsis']
        assert create.data['criteria'] == ['تجربه', 'قیمت']
        assert create.data['alternatives'] == ['الف', 'ب']

        listing = auth_client.get(url)
        assert listing.status_code == status.HTTP_200_OK
        assert listing.data['count'] >= 1

        detail = auth_client.get(f"{url}{create.data['id']}/")
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data['criteria'] == ['تجربه', 'قیمت']

    def test_patch_criteria_only_ahp_without_alternatives(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        create = auth_client.post(
            url,
            {'title': 'AHP only', 'selected_methods': ['ahp'], 'criteria': ['c1', 'c2']},
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED, create.data
        patch = auth_client.patch(
            f"{url}{create.data['id']}/",
            {'selected_methods': ['ahp', 'dematel'], 'alternatives': []},
            format='json',
        )
        assert patch.status_code == status.HTTP_200_OK, patch.data
        assert patch.data['alternatives'] == []
        assert 'dematel' in patch.data['selected_methods']

    def test_authz_and_idor(self, auth_client, project, user, other_user, viewer_role):
        url = BASE.format(project_id=project.id)
        create = auth_client.post(url, {'title': 'Owned', 'selected_methods': ['saw']}, format='json')
        assert create.status_code == status.HTTP_201_CREATED

        outsider = APIClient()
        outsider.force_authenticate(user=other_user)
        denied = outsider.get(url)
        assert denied.status_code == status.HTTP_403_FORBIDDEN

        # Viewer member: can GET, cannot POST
        ProjectMemberRole.objects.filter(member__user=other_user, member__project=project).delete()
        m = ProjectMember.objects.create(project=project, user=other_user, status=MemberStatus.ACTIVE)
        ProjectMemberRole.objects.create(member=m, role=viewer_role)
        viewer_client = APIClient()
        viewer_client.force_authenticate(user=other_user)
        ok_get = viewer_client.get(url)
        assert ok_get.status_code == status.HTTP_200_OK
        forbid_post = viewer_client.post(url, {'title': 'Nope'}, format='json')
        assert forbid_post.status_code == status.HTTP_403_FORBIDDEN

        other_project = create_project_with_creator(
            creator=user,
            project_code='PRJ-DS-2',
            project_name='Other',
            employer='E',
            start_date='2024-01-01',
        )
        missing = auth_client.get(f"/api/v1/projects/{other_project.id}/decision-cases/{create.data['id']}/")
        assert missing.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_title_method_names(self, auth_client, project):
        url = BASE.format(project_id=project.id)
        empty_title = auth_client.post(url, {'title': '  '}, format='json')
        assert empty_title.status_code == status.HTTP_400_BAD_REQUEST

        bad_method = auth_client.post(
            url,
            {'title': 'T', 'selected_methods': ['nope']},
            format='json',
        )
        assert bad_method.status_code == status.HTTP_400_BAD_REQUEST

        too_many = auth_client.post(
            url,
            {'title': 'T', 'criteria': [f'c{i}' for i in range(11)]},
            format='json',
        )
        assert too_many.status_code == status.HTTP_400_BAD_REQUEST

        dup = auth_client.post(
            url,
            {'title': 'T', 'criteria': ['c', 'c']},
            format='json',
        )
        assert dup.status_code == status.HTTP_400_BAD_REQUEST
