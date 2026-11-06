import pytest
from rest_framework.test import APIClient
from master_data.models import Role, RolePermission, RoleAccessChange

def client(user):
    c=APIClient();c.force_authenticate(user=user);return c

@pytest.mark.django_db
def test_nonmember_cannot_read_local_role_via_global_route(project, other_user):
    role=Role.objects.create(role_name='P2 local private',project=project)
    response=client(other_user).get(f'/api/v1/roles/{role.pk}/')
    print('GLOBAL_READ_LOCAL_NONMEMBER',response.status_code)
    assert response.status_code in (403,404)

@pytest.mark.django_db
def test_staff_without_membership_cannot_edit_local_role_via_global_route(project, other_user):
    role=Role.objects.create(role_name='P2 local scoped',project=project)
    other_user.is_staff=True;other_user.save(update_fields=['is_staff'])
    response=client(other_user).patch(f'/api/v1/roles/{role.pk}/permissions/',{'permissions':['manage_members']},format='json')
    print('GLOBAL_WRITE_LOCAL_STAFF_NONMEMBER',response.status_code,'changed',RolePermission.objects.filter(role=role,permission_codename='manage_members').exists())
    assert response.status_code in (403,404)

@pytest.mark.django_db
def test_local_role_rename_keeps_base_history(project,user):
    role=Role.objects.create(role_name='P2 old role',project=project)
    response=client(user).patch(f'/api/v1/projects/{project.pk}/roles/{role.pk}/',{'role_name':'P2 renamed role'},format='json')
    assert response.status_code==200
    print('RENAME_BASE_HISTORY',RoleAccessChange.objects.filter(role_id=role.pk).count())
    assert RoleAccessChange.objects.filter(role_id=role.pk,actor=user).exists()
