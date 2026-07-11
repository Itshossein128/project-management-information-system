"""Authentication rate limit tests."""
import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status


@pytest.fixture(autouse=True)
def clear_ratelimit_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_login_rate_limit_returns_429(api_client, user):
    url = reverse('authentication:login')
    payload = {'login': user.mobile, 'password': 'wrong-password'}

    for _ in range(10):
        api_client.post(url, payload, format='json')

    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert 'تعداد درخواست' in response.json()['detail']


@pytest.mark.django_db
def test_forgot_password_rate_limit_returns_429(api_client):
    url = reverse('authentication:forgot_password')
    payload = {'phone_number': '+989000000000'}

    for _ in range(5):
        api_client.post(url, payload, format='json')

    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
