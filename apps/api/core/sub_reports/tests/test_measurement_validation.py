"""Canonical feature-040 entry point for sub-report validation coverage."""

import pytest

from schedule.services.measurement_service import ProgressValidationError, require_approved_version


@pytest.mark.django_db
def test_unapproved_activity_is_rejected_at_measurement_boundary(activity):
    with pytest.raises(ProgressValidationError) as exc:
        require_approved_version(activity)
    assert exc.value.code == 'measurement_not_approved'
