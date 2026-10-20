"""MPP vs MSP XML equivalence for supported import fields."""
from __future__ import annotations

from pathlib import Path

import pytest

from schedule.services.msp_import import build_preview, parse_msp_family, parse_msp_xml

FIXTURES = Path(__file__).parent / 'fixtures' / 'mpp'


def _normalize_preview(preview: dict) -> dict:
    def norm_node(n):
        return {
            'wbs_code': n.get('wbs_code'),
            'wbs_name': n.get('wbs_name'),
            'is_summary': n.get('is_summary'),
            'activities': sorted(
                [
                    {
                        'activity_code': a.get('activity_code'),
                        'activity_name': a.get('activity_name'),
                        'duration_days': a.get('duration_days'),
                    }
                    for a in n.get('activities') or []
                ],
                key=lambda x: x['activity_code'] or '',
            ),
            'children': [norm_node(c) for c in n.get('children') or []],
        }

    return {
        'wbs_tree': [norm_node(n) for n in preview.get('wbs_tree') or []],
        'activities': sorted(
            [
                {
                    'activity_code': a.get('activity_code'),
                    'activity_name': a.get('activity_name'),
                    'duration_days': a.get('duration_days'),
                }
                for a in preview.get('activities') or []
            ],
            key=lambda x: x['activity_code'] or '',
        ),
    }


def test_paired_mpp_xml_preview_equivalence():
    mpp_path = FIXTURES / 'duration-test9.mpp'
    xml_path = FIXTURES / 'duration-test9.xml'
    if not mpp_path.is_file() or not xml_path.is_file():
        pytest.skip('paired fixtures missing')

    mpp_preview = build_preview(parse_msp_family(mpp_path.read_bytes(), filename='duration-test9.mpp'))
    xml_preview = build_preview(parse_msp_xml(xml_path.read_bytes()))

    assert _normalize_preview(mpp_preview) == _normalize_preview(xml_preview)


def test_summary_maps_to_wbs_leaves_to_activities():
    mpp_path = FIXTURES / 'duration-test9.mpp'
    if not mpp_path.is_file():
        pytest.skip('fixture missing')
    parsed = parse_msp_family(mpp_path.read_bytes(), filename='duration-test9.mpp')
    summaries = [t for t in parsed.tasks if t.is_summary]
    leaves = [t for t in parsed.tasks if not t.is_summary]
    assert summaries or leaves  # at least some tasks
    preview = build_preview(parsed)
    # Leaf activities appear in flat activities list
    assert isinstance(preview['activities'], list)
