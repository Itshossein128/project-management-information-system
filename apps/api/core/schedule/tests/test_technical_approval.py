"""Canonical feature-040 entry point for technical approval coverage."""

from test_progress_four_way import TestProgressFourWay


def test_canonical_technical_approval_suite_is_available():
    assert hasattr(TestProgressFourWay, 'test_photo_alone_is_not_technical_approval')
