"""TDD: inspection WBS/responsible/date validation and NCR/CA chain."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import WBS


INSPECT = '/api/v1/projects/{project_id}/inspections/'
NCR = '/api/v1/projects/{project_id}/nonconformities/'
CA = '/api/v1/projects/{project_id}/corrective-actions/'


@pytest.fixture
def wbs_node(db, project, user):
    return WBS.add_root(
        project_id=project.id,
        wbs_code='Q1',
        wbs_name='Quality package',
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestInspectionValidation:
    def test_missing_required_fields_rejected(self, auth_client, project, user, wbs_node):
        url = INSPECT.format(project_id=project.id)
        for body in (
            {'responsible_user': str(user.id), 'inspection_date': '2026-10-09'},
            {'wbs': str(wbs_node.id), 'inspection_date': '2026-10-09'},
            {'wbs': str(wbs_node.id), 'responsible_user': str(user.id)},
        ):
            resp = auth_client.post(url, body, format='json')
            assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_inspection_happy_path(self, auth_client, project, user, wbs_node):
        url = INSPECT.format(project_id=project.id)
        resp = auth_client.post(
            url,
            {
                'wbs': str(wbs_node.id),
                'responsible_user': str(user.id),
                'inspection_date': '2026-10-09',
                'stage': 'result',
                'result': 'fail',
                'description': 'Rebar spacing',
            },
            format='json',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert str(resp.data['wbs']) == str(wbs_node.id)
        assert resp.data['inspection_date']

    def test_ncr_and_corrective_action_chain(self, auth_client, project, user, wbs_node):
        insp = auth_client.post(
            INSPECT.format(project_id=project.id),
            {
                'wbs': str(wbs_node.id),
                'responsible_user': str(user.id),
                'inspection_date': '2026-10-09',
                'result': 'fail',
                'description': 'Failed check',
            },
            format='json',
        )
        assert insp.status_code == status.HTTP_201_CREATED, insp.data
        ncr = auth_client.post(
            NCR.format(project_id=project.id),
            {
                'inspection': insp.data['id'],
                'description': 'Spacing exceeds tolerance',
                'raised_date': '2026-10-09',
            },
            format='json',
        )
        assert ncr.status_code == status.HTTP_201_CREATED, ncr.data
        ca = auth_client.post(
            CA.format(project_id=project.id),
            {
                'nonconformity': ncr.data['id'],
                'description': 'Re-tie and re-inspect',
                'responsible_user': str(user.id),
                'due_date': '2026-10-12',
            },
            format='json',
        )
        assert ca.status_code == status.HTTP_201_CREATED, ca.data
        assert str(ca.data['nonconformity']) == str(ncr.data['id'])
        assert ca.data['due_date'] is not None
