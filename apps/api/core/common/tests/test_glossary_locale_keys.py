"""US1: glossary keys must be present and distinct in FA/EN locale files."""
import json
from pathlib import Path

import pytest

WEB_LOCALES = (
    Path(__file__).resolve().parents[4]  # apps/
    / 'web'
    / 'src'
    / 'app'
    / 'locales'
)


def _load(name: str) -> dict:
    path = WEB_LOCALES / name
    assert path.is_file(), f'Missing locale file: {path}'
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def fa():
    return _load('fa.json')


@pytest.fixture(scope='module')
def en():
    return _load('en.json')


REQUIRED_KEYS = (
    'wbs',
    'commitment',
    'actualCost',
    'ipc',
    'ev',
    'pv',
    'ac',
    'risk',
    'issue',
    'baseline',
    'cbs',
    'obs',
)


def test_fa_glossary_keys(fa):
    glossary = fa.get('glossary') or {}
    for key in REQUIRED_KEYS:
        assert key in glossary and glossary[key], f'Missing fa glossary.{key}'
    assert 'WBS' in glossary['wbs'] or 'ساختار شکست کار' in glossary['wbs']
    assert 'صورت' in glossary['ipc']
    assert fa['projectOverview']['moduleWbs'] == 'ساختار شکست کار (WBS)'


def test_en_glossary_keys(en):
    glossary = en.get('glossary') or {}
    for key in REQUIRED_KEYS:
        assert key in glossary and glossary[key], f'Missing en glossary.{key}'
    assert 'WBS' in glossary['wbs']
    assert 'Payment certificate' in glossary['ipc'] or 'IPC' in glossary['ipc']


def test_commitment_and_actual_cost_are_distinct(fa, en):
    assert fa['glossary']['commitment'] != fa['glossary']['actualCost']
    assert en['glossary']['commitment'] != en['glossary']['actualCost']
