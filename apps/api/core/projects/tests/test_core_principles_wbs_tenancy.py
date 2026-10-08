"""US2: non-members cannot access WBS."""
import pytest
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_non_member_cannot_list_wbs(project, wbs):
    stranger = User.objects.create_user(
        username='stranger',
        mobile='+989129999999',
        full_name='Stranger',
        password='x',
    )
    client = APIClient()
    client.force_authenticate(user=stranger)
    resp = client.get(f'/api/v1/projects/{project.id}/wbs/')
    assert resp.status_code in (403, 404)
