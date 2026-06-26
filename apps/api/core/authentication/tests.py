from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='secure-pass-123',
            mobile='09123456789',
            full_name='Test User',
        )
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.refresh_url = reverse('authentication:token_refresh')

    def test_login_with_username_returns_tokens(self):
        response = self.client.post(
            self.login_url,
            {'username': 'testuser', 'password': 'secure-pass-123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(str(response.data['user']['id']), str(self.user.id))

    def test_login_with_mobile_returns_tokens(self):
        response = self.client.post(
            self.login_url,
            {'phone_number': '09123456789', 'password': 'secure-pass-123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_invalid_credentials_returns_401(self):
        response = self.client.post(
            self.login_url,
            {'username': 'testuser', 'password': 'wrong-password'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_tokens(self):
        login = self.client.post(
            self.login_url,
            {'username': 'testuser', 'password': 'secure-pass-123'},
            format='json',
        )
        old_refresh = login.data['refresh']
        refresh_response = self.client.post(
            self.refresh_url,
            {'refresh': old_refresh},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        self.assertIn('refresh', refresh_response.data)
        self.assertNotEqual(refresh_response.data['refresh'], old_refresh)

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(
            self.login_url,
            {'username': 'testuser', 'password': 'secure-pass-123'},
            format='json',
        )
        access = login.data['access']
        refresh = login.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        logout = self.client.post(self.logout_url, {'refresh': refresh}, format='json')
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        refresh_again = self.client.post(
            self.refresh_url,
            {'refresh': refresh},
            format='json',
        )
        self.assertEqual(refresh_again.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklisted_token_rejected(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.blacklist()
        response = self.client.post(
            self.refresh_url,
            {'refresh': str(refresh)},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
