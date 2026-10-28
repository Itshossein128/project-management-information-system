"""Canonical feature-040 entry point for four-way progress coverage."""

from test_progress_four_way import TestProgressFourWay


def test_canonical_four_way_suite_is_available():
    """Keep the feature contract's canonical test path importable."""
    assert TestProgressFourWay
