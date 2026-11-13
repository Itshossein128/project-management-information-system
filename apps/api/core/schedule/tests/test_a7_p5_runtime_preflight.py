"""Preflight must refuse a shared database and an empty passing matrix."""

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from schedule.management.commands.verify_import_runtime import claims_real_worker_success


@pytest.mark.django_db
def test_preflight_refuses_the_shared_test_database():
    with pytest.raises(CommandError):
        call_command('verify_import_runtime', '--preflight')


def test_eager_pass_labels_are_rejected():
    assert claims_real_worker_success({'eager': True, 'matrix': {'valid_native': 'pass'}}) is True
    assert claims_real_worker_success({'eager': False, 'matrix': {'valid_native': 'not-run'}}) is False
    assert claims_real_worker_success({'eager': True, 'matrix': {'valid_native': 'not-run'}}) is False
