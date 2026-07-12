import pytest
from rest_framework import status

from notifications.models import Notification

LIST_URL = '/api/v1/notifications/'


@pytest.fixture
def notifications(db, user, project):
    return [
        Notification.objects.create(
            user=user,
            project=project,
            notification_type='report_submitted',
            title='n1',
            message='m1',
        ),
        Notification.objects.create(
            user=user,
            project=project,
            notification_type='report_approved',
            title='n2',
            message='m2',
            is_read=True,
        ),
    ]


@pytest.mark.django_db
class TestNotificationsApi:
    def test_unauthenticated_rejected(self, api_client):
        assert api_client.get(LIST_URL).status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_only_own(self, api_client, notifications, user, other_user):
        Notification.objects.create(user=other_user, title='other', message='x')
        api_client.force_authenticate(user=user)
        response = api_client.get(LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_filter_unread(self, auth_client, notifications):
        response = auth_client.get(f'{LIST_URL}?is_read=false')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_unread_count(self, auth_client, notifications):
        response = auth_client.get(f'{LIST_URL}unread-count/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unread'] == 1

    def test_mark_read(self, auth_client, notifications):
        target = notifications[0]
        response = auth_client.post(f'{LIST_URL}{target.id}/mark-read/')
        assert response.status_code == status.HTTP_200_OK
        target.refresh_from_db()
        assert target.is_read is True
        assert target.read_at is not None

    def test_mark_all_read(self, auth_client, notifications):
        response = auth_client.post(f'{LIST_URL}mark-all-read/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['updated'] == 1
        assert Notification.objects.filter(is_read=False).count() == 0

    def test_cannot_read_others_notification(self, api_client, notifications, other_user):
        api_client.force_authenticate(user=other_user)
        response = api_client.post(f'{LIST_URL}{notifications[0].id}/mark-read/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
