"""HTTP/serialization layers delegate all decision mathematics to services."""
from pathlib import Path
import re

APP = Path(__file__).resolve().parents[1]


def test_views_orchestrate_via_create_run_only():
    views = (APP / 'views.py').read_text(encoding='utf-8')
    assert 'create_run' in views
    assert not re.search(r'from decision_support.services.(saw|topsis|ahp|ism)_service', views)
    assert not re.search(r'compute_(ahp|saw|topsis|ism)|SAATY_RI|geom_mean|ideal_best|math\.(log|exp)', views)


def test_serializers_have_no_engine_math():
    source = (APP / 'serializers.py').read_text(encoding='utf-8')
    assert not re.search(r'compute_(ahp|saw|topsis|ism)|SAATY_RI|normalize_weights|ideal_best|math\.(log|exp)', source)
