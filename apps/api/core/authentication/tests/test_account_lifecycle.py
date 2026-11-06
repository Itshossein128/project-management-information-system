"""Organizational account authority, status, and session boundary."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from authentication.admin import user_has_retained_history
from authentication.services import align_account_rows
from authentication.utils import get_tokens_for_user

User = get_user_model()


def _client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _payload(mobile):
    return {
        'phone_number': mobile,
        'first_name': 'New',
        'last_name': 'Person',
        'password': 'Replacement-pass-492!',
        'password_confirm': 'Replacement-pass-492!',
    }


@pytest.mark.django_db
def test_only_account_administrators_can_create_people(user):
    Group.objects.get_or_create(name='visitor')
    hr_group, _ = Group.objects.get_or_create(name='hr')
    hr = User.objects.create_user(
        username='hr-admin',
        mobile='+989120000501',
        full_name='HR Admin',
        password='testpass123',
    )
    hr.groups.add(hr_group)
    created = _client(hr).post('/api/auth/users/', _payload('+989120000502'), format='json')
    assert created.status_code == status.HTTP_201_CREATED
    person = User.objects.get(mobile='+989120000502')
    assert list(person.groups.values_list('name', flat=True)) == ['visitor']

    refused = _client(user).post('/api/auth/users/', _payload('+989120000503'), format='json')
    assert refused.status_code == status.HTTP_403_FORBIDDEN
    assert refused.data['error']['code'] == 'account_forbidden'

    duplicate = _client(hr).post('/api/auth/users/', _payload('+989120000502'), format='json')
    assert duplicate.status_code == status.HTTP_400_BAD_REQUEST
    mismatch = _payload('+989120000504')
    mismatch['password_confirm'] = 'Different-pass-492!'
    assert _client(hr).post('/api/auth/users/', mismatch, format='json').status_code == status.HTTP_400_BAD_REQUEST
    weak = _payload('+989120000505')
    weak['password'] = 'password'
    weak['password_confirm'] = 'password'
    assert _client(hr).post('/api/auth/users/', weak, format='json').status_code == status.HTTP_400_BAD_REQUEST

    edited = _client(person).patch('/api/auth/profile/', {'mobile': hr.mobile}, format='json')
    assert edited.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_account_status_controls_sign_in_and_later_requests(user):
    hr_group, _ = Group.objects.get_or_create(name='hr')
    hr = User.objects.create_user(
        username='status-hr',
        mobile='+989120000511',
        full_name='Status HR',
        password='testpass123',
    )
    hr.groups.add(hr_group)
    forbidden = _client(user).patch(
        f'/api/auth/users/{user.id}/account-status/',
        {'status': 'suspended'},
        format='json',
    )
    assert forbidden.status_code == status.HTTP_403_FORBIDDEN

    suspended = _client(hr).patch(
        f'/api/auth/users/{user.id}/account-status/',
        {'status': 'suspended'},
        format='json',
    )
    assert suspended.status_code == status.HTTP_200_OK
    assert suspended.data['can_sign_in'] is False
    user.refresh_from_db()
    assert user.status == 'suspended'
    assert user.is_active is False
    login = APIClient().post(
        '/api/auth/login/',
        {'username': user.username, 'password': 'testpass123'},
        format='json',
    )
    assert login.status_code == status.HTTP_401_UNAUTHORIZED

    user.status = 'suspended'
    user.is_active = True
    user.save(update_fields=['status', 'is_active'])
    access = get_tokens_for_user(user)['access']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
    assert client.get('/api/auth/profile/').status_code == status.HTTP_401_UNAUTHORIZED

    restored = _client(hr).patch(
        f'/api/auth/users/{user.id}/account-status/',
        {'status': 'active'},
        format='json',
    )
    assert restored.data['can_sign_in'] is True
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_alignment_does_not_reenable_a_blocked_person(user, other_user):
    user.status = 'active'
    user.is_active = False
    user.save(update_fields=['status', 'is_active'])
    other_user.status = 'suspended'
    other_user.is_active = True
    other_user.save(update_fields=['status', 'is_active'])
    align_account_rows(User)
    user.refresh_from_db()
    other_user.refresh_from_db()
    assert user.status == 'inactive'
    assert user.is_active is False
    assert other_user.status == 'suspended'
    assert other_user.is_active is False


@pytest.mark.django_db
def test_logout_refuses_refresh_and_access_expires_in_one_hour(user):
    tokens = get_tokens_for_user(user)
    client = APIClient()
    client.force_authenticate(user=user)
    logout = client.post('/api/auth/logout/', {'refresh': tokens['refresh']}, format='json')
    assert logout.status_code == status.HTTP_200_OK
    refreshed = APIClient().post('/api/auth/token/refresh/', {'refresh': tokens['refresh']}, format='json')
    assert refreshed.status_code == status.HTTP_401_UNAUTHORIZED
    from rest_framework_simplejwt.tokens import AccessToken
    access = AccessToken(tokens['access'])
    assert access['exp'] - access['iat'] == timedelta(hours=1).total_seconds()
    auth = JWTAuthentication()
    assert auth.get_user(auth.get_validated_token(tokens['access'])).pk == user.pk


@pytest.mark.django_db
def test_person_with_membership_is_not_deleted(user, project):
    assert user_has_retained_history(user) is True
    with pytest.raises(ProtectedError):
        user.delete()


@pytest.mark.django_db
def test_password_reset_does_not_claim_delivery_when_unconfigured(api_client, user):
    known = api_client.post('/api/auth/forgot-password/', {'phone_number': user.mobile}, format='json')
    unknown = api_client.post('/api/auth/forgot-password/', {'phone_number': '+989120000599'}, format='json')
    assert known.status_code == status.HTTP_200_OK
    assert unknown.status_code == status.HTTP_200_OK
    assert known.data['delivery_status'] == 'not_configured'
    assert unknown.data['delivery_status'] == 'not_configured'
    assert known.data['message'] == unknown.data['message']
    assert 'sent' not in known.data['message'].lower() or 'no message was sent' in known.data['message'].lower()


@pytest.mark.django_db
def test_staff_flag_alone_cannot_create_accounts():
    staff = User.objects.create_user(
        username='bare-staff',
        mobile='+989120000801',
        full_name='Bare Staff',
        password='testpass123',
        is_staff=True,
    )
    refused = _client(staff).post('/api/auth/users/', _payload('+989120000802'), format='json')
    assert refused.status_code == status.HTTP_403_FORBIDDEN
    assert refused.data['error']['code'] == 'account_forbidden'


@pytest.mark.django_db
def test_suspending_an_account_rejects_its_refresh_token(user):
    hr_group, _ = Group.objects.get_or_create(name='hr')
    hr = User.objects.create_user(
        username='refresh-hr',
        mobile='+989120000811',
        full_name='Refresh HR',
        password='testpass123',
    )
    hr.groups.add(hr_group)
    tokens = get_tokens_for_user(user)
    suspended = _client(hr).patch(
        f'/api/auth/users/{user.id}/account-status/',
        {'status': 'suspended'},
        format='json',
    )
    assert suspended.status_code == status.HTTP_200_OK
    refreshed = APIClient().post('/api/auth/token/refresh/', {'refresh': tokens['refresh']}, format='json')
    assert refreshed.status_code == status.HTTP_401_UNAUTHORIZED
