import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username='+989120000000',
        mobile='+989120000000',
        password='testpassword123',
        full_name='Test User'
    )
    return user

@pytest.mark.django_db
class TestAuthenticationAPI:
    def test_login_success(self, api_client, test_user):
        url = reverse('authentication:login')
        payload = {
            'phone_number': test_user.mobile,
            'password': 'testpassword123'
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['mobile'] == test_user.mobile

    def test_login_invalid_password(self, api_client, test_user):
        url = reverse('authentication:login')
        payload = {
            'phone_number': test_user.mobile,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_login_nonexistent_user(self, api_client):
        url = reverse('authentication:login')
        payload = {
            'phone_number': '+989120000001',
            'password': 'testpassword123'
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_password_reset_flow(self, api_client, test_user):
        from unittest.mock import patch
        from authentication.services import PasswordResetService

        captured = {}

        def capture_token(self, user, token):
            captured['token'] = token
            return True

        forgot_url = reverse('authentication:forgot_password')
        with patch.object(PasswordResetService, 'send_reset_sms', capture_token):
            forgot = api_client.post(
                forgot_url,
                {'phone_number': test_user.mobile},
                format='json',
            )
        assert forgot.status_code == status.HTTP_200_OK
        assert 'token' in captured

        reset_url = reverse('authentication:reset_password')
        reset = api_client.post(
            reset_url,
            {
                'token': captured['token'],
                'new_password': 'newpass123!',
                'new_password_confirm': 'newpass123!',
            },
            format='json',
        )
        assert reset.status_code == status.HTTP_200_OK
        test_user.refresh_from_db()
        assert test_user.check_password('newpass123!')
