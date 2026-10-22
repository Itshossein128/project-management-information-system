from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import PasswordResetToken
from authentication.services import PasswordChangeService, PasswordResetService, _hash_token
from authentication.utils import get_tokens_for_user


def issue_reset(user, token):
    return PasswordResetToken.objects.create(
        user=user, token_hash=_hash_token(token),
        expires_at=timezone.now() + timedelta(hours=1),
    )


def test_reset_tokens_have_sufficient_entropy():
    token = PasswordResetService().generate_reset_token()
    assert len(token) >= 32
    assert not token.isdecimal()


@pytest.mark.django_db
def test_legacy_six_digit_reset_cannot_select_another_account(user, other_user):
    issue_reset(user, '123456')
    issue_reset(other_user, '123456')
    with pytest.raises(ValidationError):
        PasswordResetService().reset_password('123456', 'Replacement-pass-492!')
    other_user.refresh_from_db()
    assert other_user.check_password('testpass123')


@pytest.mark.django_db
@pytest.mark.parametrize('invalid_state', ['expired', 'used', 'ambiguous'])
def test_unusable_reset_token_is_rejected(user, other_user, invalid_state):
    token = PasswordResetService().generate_reset_token()
    reset = issue_reset(user, token)
    if invalid_state == 'expired':
        reset.expires_at = timezone.now() - timedelta(seconds=1)
        reset.save()
    elif invalid_state == 'used':
        reset.used_at = timezone.now()
        reset.save()
    else:
        issue_reset(other_user, token)
    with pytest.raises(ValidationError):
        PasswordResetService().reset_password(token, 'Replacement-pass-492!')


def test_sms_placeholder_does_not_log_credentials(user, caplog):
    token = PasswordResetService().generate_reset_token()
    assert PasswordResetService().send_reset_sms(user, token) is False
    assert token not in caplog.text
    assert user.mobile not in caplog.text


@pytest.mark.django_db
@pytest.mark.parametrize('operation', ['change', 'reset'])
@pytest.mark.parametrize('credential', ['access', 'reset'])
def test_password_update_revokes_existing_credentials(user, operation, credential):
    access = get_tokens_for_user(user)['access']
    auth = JWTAuthentication()
    assert auth.get_user(auth.get_validated_token(access)).pk == user.pk
    outstanding = issue_reset(user, 'a' * 43)
    if operation == 'change':
        PasswordChangeService().change_password(user, 'testpass123', 'Replacement-pass-492!')
    else:
        issue_reset(user, 'b' * 43)
        PasswordResetService().reset_password('b' * 43, 'Replacement-pass-492!')
    outstanding.refresh_from_db()
    if credential == 'reset':
        assert outstanding.used_at is not None
    else:
        with pytest.raises(AuthenticationFailed):
            auth.get_user(auth.get_validated_token(access))
    user.refresh_from_db()
    fresh = get_tokens_for_user(user)['access']
    assert auth.get_user(auth.get_validated_token(fresh)).pk == user.pk


@pytest.mark.django_db
def test_reset_failure_rolls_back_password_and_token_consumption(user):
    reset = issue_reset(user, 'c' * 43)
    with patch('authentication.services.blacklist_user_tokens', side_effect=RuntimeError('unavailable')):
        with pytest.raises(RuntimeError):
            PasswordResetService().reset_password('c' * 43, 'Replacement-pass-492!')
    user.refresh_from_db()
    reset.refresh_from_db()
    assert user.check_password('testpass123')
    assert reset.used_at is None


@pytest.mark.django_db
def test_invalid_reset_returns_400(api_client):
    response = api_client.post(reverse('authentication:reset_password'), {
        'token': '123456', 'new_password': 'Replacement-pass-492!',
        'new_password_confirm': 'Replacement-pass-492!',
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_wrong_current_password_returns_400(auth_client):
    response = auth_client.post(reverse('authentication:change_password'), {
        'old_password': 'incorrect', 'new_password': 'Replacement-pass-492!',
        'new_password_confirm': 'Replacement-pass-492!',
    }, format='json')
    assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_reset_token_can_only_be_consumed_once_concurrently(user):
    token = PasswordResetService().generate_reset_token()
    issue_reset(user, token)
    barrier = Barrier(2)

    def reset(index):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            PasswordResetService().reset_password(token, f'Replacement-pass-{index}-492!')
            return True
        except ValidationError:
            return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(reset, range(2))) == [False, True]
