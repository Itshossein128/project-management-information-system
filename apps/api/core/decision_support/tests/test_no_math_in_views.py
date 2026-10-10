"""Structural guard: presentation/HTTP layers must not embed SAW formulas."""

from __future__ import annotations

from pathlib import Path

APP = Path(__file__).resolve().parents[1]


def test_views_orchestrate_via_create_run_only():
    views = (APP / 'views.py').read_text(encoding='utf-8')
    assert 'create_run' in views
    assert 'from decision_support.services.saw_service' not in views
    assert 'ideal_best' not in views
    assert 'r[i,j]' not in views


def test_serializers_have_no_engine_math():
    src = (APP / 'serializers.py').read_text(encoding='utf-8')
    assert 'compute_saw' not in src
    assert 'ideal_best' not in src
    assert 'normalize_weights' not in src
