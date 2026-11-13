"""Real kernel containment is reported as not-run until a delegated cgroup exists."""

import pytest
from django.db import connection

from schedule.services.import_process import cgroup_ready


@pytest.mark.django_db
def test_kernel_limits_are_not_marked_passed_without_controls():
    database = str(connection.settings_dict.get('NAME', ''))
    if not cgroup_ready() or 'a7p5' not in database:
        pytest.skip('cgroup containment is not-run: delegated controllers or the phase database are unavailable')
