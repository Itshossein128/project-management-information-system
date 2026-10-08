import pytest

from master_data.models import OrganizationUnit
from projects.models import Project


@pytest.mark.django_db
def test_patch_project_owning_unit(auth_client, project):
    unit = OrganizationUnit.objects.create(code='ENG', name='Engineering')
    resp = auth_client.patch(
        f'/api/v1/projects/{project.id}/',
        {'owning_unit': str(unit.id)},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    project.refresh_from_db()
    assert project.owning_unit_id == unit.id
    assert resp.json().get('owning_unit') == str(unit.id)
    assert Project.objects.get(pk=project.id).owning_unit_id == unit.id
