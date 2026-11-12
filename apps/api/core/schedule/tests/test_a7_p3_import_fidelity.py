"""Import fidelity for parents, units, dates, and warnings.

Uses project codes that start with A7P3-IMPORT-FIDELITY only.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from projects.models import Activity, ActivityRelation, ProjectStatus, RelationType, WBS
from projects.services import create_project_with_creator
from schedule.models import BaselineActivity, BaselineSchedule
from schedule.services.critical_path_validity import evaluate_critical_path_validity
from schedule.services.gantt_service import get_gantt_data
from schedule.services.import_fidelity import ImportFidelityError
from schedule.services.msp_import import build_preview, execute_msp_import, parse_msp_xml
from schedule.services.p6_import import execute_p6_import, parse_p6_xer
from schedule.services.status_report_service import build_schedule_status

FIXTURES = Path(__file__).resolve().parents[5] / 'specs/051-a7-p1-project-reference/evidence/fixtures'
MPP_FIXTURES = Path(__file__).parent / 'fixtures' / 'mpp'


def _convert_reference_mpp(raw):
    from schedule.services.mpp_convert import convert_mpp_to_mspdi
    from schedule.services.mpp_errors import CONVERSION_FAILED, MppImportError

    try:
        return convert_mpp_to_mspdi(raw)
    except MppImportError as exc:
        if exc.code == CONVERSION_FAILED and exc.message in {
            'MPP conversion is unavailable (MPXJ/JRE not configured).',
            'Java runtime is required to process MPP files.',
        }:
            pytest.skip(f'MPP converter unavailable: {exc.message}')
        raise


def _project(user, suffix):
    project = create_project_with_creator(
        creator=user,
        project_code=f'A7P3-IMPORT-FIDELITY-{suffix}',
        project_name=f'Import fidelity {suffix}',
        employer='Fidelity Co',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


def _xml(body: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Project xmlns="http://schemas.microsoft.com/project"><Tasks>'
        f'{body}</Tasks></Project>'
    ).encode()


def _task(**parts) -> str:
    inner = ''.join(f'<{key}>{value}</{key}>' for key, value in parts.items())
    return f'<Task>{inner}</Task>'


def _codes(project):
    return {
        'wbs': WBS.objects.filter(project=project, is_deleted=False).count(),
        'activities': Activity.objects.filter(project=project, is_deleted=False).count(),
        'relations': ActivityRelation.objects.filter(
            successor__project=project, is_deleted=False,
        ).count(),
    }


def test_branch_parents_follow_the_file_not_row_order(user):
    project = _project(user, 'BR')
    original = (FIXTURES / 'branch.xml').read_bytes()
    reordered = _xml(
        _task(UID='3', Name='Branch B', OutlineLevel='2', OutlineNumber='1.2', WBS='1.2', Summary='0', Duration='PT8H0M0S')
        + _task(UID='1', Name='Parent', OutlineLevel='1', OutlineNumber='1', WBS='1', Summary='1')
        + _task(UID='2', Name='Branch A', OutlineLevel='2', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT16H0M0S')
    )
    preview = build_preview(parse_msp_xml(original))
    execute_msp_import(project, reordered, filename='branch.xml', replace=False, user=user)
    parent = WBS.objects.get(project=project, wbs_code='1')
    for code, days in (('1.1', 2), ('1.2', 1)):
        activity = Activity.objects.get(project=project, activity_code=code)
        assert activity.wbs_id == parent.id
        assert activity.duration_days == days
        assert any(item['activity_code'] == code for item in preview['activities'])
    xer = _project(user, 'BRX')
    execute_p6_import(xer, (FIXTURES / 'branch.xer').read_bytes(), filename='branch.xer', replace=False, user=user)
    phase = WBS.objects.get(project=xer, wbs_code='1.1')
    assert phase.get_parent().wbs_code == '1'
    work = Activity.objects.get(project=xer, activity_code='A')
    assert work.wbs_id == phase.id


def test_root_leaves_stay_unattached(user):
    project = _project(user, 'OR')
    before = _codes(project)
    result = execute_msp_import(
        project, (FIXTURES / 'relation.xml').read_bytes(), filename='relation.xml', replace=False, user=user,
    )
    assert _codes(project) == before
    assert any(item.startswith('activity_without_parent:') for item in result['warnings'])
    xer_project = _project(user, 'ORX')
    xer_result = execute_p6_import(
        xer_project, (FIXTURES / 'relation.xer').read_bytes(), filename='relation.xer', replace=False, user=user,
    )
    assert _codes(xer_project) == _codes(project)
    assert any(item.startswith('activity_without_parent:') for item in xer_result['warnings'])


def test_blocking_cases_write_nothing_even_on_replace(user):
    cases = {
        'FS': _xml(
            _task(UID='1', Name='Parent', OutlineNumber='1', WBS='1', Summary='1')
            + _task(
                UID='2', Name='Bad', OutlineNumber='1.1', WBS='1.1', Summary='0',
                Start='2026-02-02T08:00:00', Finish='2026-02-01T08:00:00',
            )
        ),
        'CY': None,
        'DUP': _xml(
            _task(UID='1', Name='One', OutlineNumber='1', WBS='1', Summary='1')
            + _task(UID='2', Name='Two', OutlineNumber='1', WBS='1', Summary='1')
        ),
        'SELF': _xml(
            _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
            + _task(UID='2', Name='Loop', OutlineNumber='1.1', WBS='1.1', Summary='0')
            .replace('</Task>', '<PredecessorLink><PredecessorUID>2</PredecessorUID><Type>1</Type></PredecessorLink></Task>')
        ),
    }
    cycle = (
        'ERMHDR\t18.8\t2026-01-01\tProject\n'
        '%T\tPROJWBS\n%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\n'
        '%R\t1\t2\tA\tA\n%R\t2\t1\tB\tB\n'
    ).encode()
    for code, payload in cases.items():
        project = _project(user, code.upper())
        WBS.add_root(project_id=project.id, wbs_code='KEEP', wbs_name='Keep', created_by=user, updated_by=user)
        before = _codes(project)
        data = cycle if code == 'CY' else payload
        expected = {
            'FS': 'finish_before_start',
            'CY': 'structure_cycle',
            'DUP': 'duplicate_in_file',
            'SELF': 'structure_cycle',
        }[code]
        runner = execute_p6_import if code == 'CY' else execute_msp_import
        with pytest.raises(ImportFidelityError) as exc:
            runner(project, data, filename='bad.file', replace=True, user=user)
        assert exc.value.code == expected
        assert _codes(project) == before
        if code != 'CY':
            preview = build_preview(parse_msp_xml(payload))
            assert any(item['code'] == expected for item in preview['blocking'])


def test_warning_rows_are_omitted_without_reparenting(user):
    project = _project(user, 'WARN')
    project.max_depth = 1
    project.save(update_fields=['max_depth', 'updated_at'])
    body = (
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
        + _task(
            UID='2', Name='Leaf', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT8H0M0S',
            PredecessorLink='<PredecessorUID>99</PredecessorUID><Type>9</Type>',
        )
    )
    # Type 9 is invalid, and the leaf is also past depth 1, so it is omitted for depth.
    result = execute_msp_import(project, _xml(body), filename='warn.xml', replace=False, user=user)
    assert Activity.objects.filter(project=project).count() == 0
    assert WBS.objects.filter(project=project, wbs_code='1').exists()
    assert any(item.startswith('depth_exceeded:') for item in result['warnings'])
    shallow = _project(user, 'PRED')
    linked = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
        + _task(
            UID='2', Name='Leaf', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT8H0M0S',
        ).replace('</Task>', '<PredecessorLink><PredecessorUID>99</PredecessorUID><Type>9</Type></PredecessorLink></Task>')
    )
    linked_result = execute_msp_import(shallow, linked, filename='link.xml', replace=False, user=user)
    assert Activity.objects.filter(project=shallow, activity_code='1.1').exists()
    assert ActivityRelation.objects.filter(successor__project=shallow).count() == 0
    assert any(item.startswith('relation_type_invalid:') for item in linked_result['warnings'])
    missing = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
        + _task(UID='2', Name='Leaf', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT8H0M0S')
        .replace('</Task>', '<PredecessorLink><PredecessorUID>99</PredecessorUID><Type>1</Type></PredecessorLink></Task>')
    )
    missing_project = _project(user, 'P99')
    missing_result = execute_msp_import(missing_project, missing, filename='pred.xml', replace=False, user=user)
    assert any(item.startswith('predecessor_missing:') for item in missing_result['warnings'])
    empty = _project(user, 'EMPTY')
    empty_result = execute_msp_import(empty, _xml(''), filename='empty.xml', replace=False, user=user)
    assert empty_result['nothing_changed'] is True
    assert any(item.startswith('empty_import') for item in empty_result['warnings'])


def test_duration_milestone_lag_percent_and_calendar_land_on_the_activity(user):
    project = _project(user, 'MILE')
    execute_msp_import(
        project, (FIXTURES / 'milestone.xml').read_bytes(), filename='milestone.xml', replace=False, user=user,
    )
    milestone = Activity.objects.get(project=project, activity_code='1.1')
    assert milestone.duration_days == 0
    assert milestone.is_milestone is True
    assert milestone.working_calendar_id is None
    assert milestone.weight is None
    xer = _project(user, 'MX')
    execute_p6_import(
        xer, (FIXTURES / 'milestone.xer').read_bytes(), filename='milestone.xer', replace=False, user=user,
    )
    xer_milestone = Activity.objects.get(project=xer, activity_code='MS')
    assert xer_milestone.duration_days == 0
    assert xer_milestone.is_milestone is False

    lag_project = _project(user, 'LAG')
    lag_xml = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
        + _task(UID='2', Name='Pred', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT8H0M0S')
        + _task(UID='3', Name='Succ', OutlineNumber='1.2', WBS='1.2', Summary='0', Duration='PT8H0M0S', Milestone='1')
        .replace(
            '</Task>',
            '<PredecessorLink><PredecessorUID>2</PredecessorUID><Type>1</Type><LinkLag>4800</LinkLag></PredecessorLink></Task>',
        )
    )
    lag_result = execute_msp_import(lag_project, lag_xml, filename='lag.xml', replace=False, user=user)
    relation = ActivityRelation.objects.get(successor__project=lag_project)
    assert relation.relation_type == RelationType.FS
    assert relation.lag_days == 1
    conflict = Activity.objects.get(project=lag_project, activity_code='1.2')
    assert conflict.duration_days == 1
    assert conflict.is_milestone is False
    assert any(item.startswith('milestone_duration_conflict:') for item in lag_result['warnings'])

    odd = _project(user, 'ODD')
    odd_xml = lag_xml.replace(b'<LinkLag>4800</LinkLag>', b'<LinkLag>100</LinkLag>')
    odd_result = execute_msp_import(odd, odd_xml, filename='odd.xml', replace=False, user=user)
    assert ActivityRelation.objects.filter(successor__project=odd).count() == 0
    assert any(item.startswith('lag_not_whole_days:') for item in odd_result['warnings'])

    calendar = _project(user, 'CAL')
    calendar_xml = (
        b'<?xml version="1.0"?><Project><Calendars><Calendar><Name>Shamsi</Name></Calendar></Calendars><Tasks>'
        + _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1').encode()
        + _task(UID='2', Name='Leaf', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT4H0M0S', PercentComplete='140').encode()
        + b'</Tasks></Project>'
    )
    calendar_result = execute_msp_import(calendar, calendar_xml, filename='cal.xml', replace=False, user=user)
    leaf = Activity.objects.get(project=calendar, activity_code='1.1')
    assert leaf.duration_days is None
    assert leaf.planned_percent is None
    assert leaf.working_calendar_id is None
    assert any(item.startswith('calendar_not_applied') for item in calendar_result['warnings'])
    assert any(item.startswith('duration_not_whole_days:') for item in calendar_result['warnings'])
    assert any(item.startswith('invalid_percent:') for item in calendar_result['warnings'])


def test_dates_stay_separate_and_append_keeps_actuals(user):
    project = _project(user, 'DATES')
    body = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
        + _task(
            UID='2', Name='Leaf', OutlineNumber='1.1', WBS='1.1', Summary='0', Duration='PT8H0M0S',
            Start='2026-03-01T08:00:00', Finish='2026-03-02T08:00:00',
            ActualStart='2026-03-03T08:00:00', ActualFinish='2026-03-04T08:00:00',
        )
    )
    execute_msp_import(project, body, filename='dates.xml', replace=False, user=user)
    created = Activity.objects.get(project=project, activity_code='1.1')
    assert created.planned_start == date(2026, 3, 1)
    assert created.planned_finish == date(2026, 3, 2)
    assert created.actual_start == date(2026, 3, 3)
    assert created.actual_finish == date(2026, 3, 4)
    assert created.forecast_start is None
    assert created.forecast_finish is None
    copy = BaselineSchedule.objects.get(project=project)
    assert copy.is_locked is False
    assert copy.approved_at is None

    created.actual_start = date(2026, 4, 1)
    created.save(update_fields=['actual_start', 'updated_at'])
    execute_msp_import(project, body, filename='dates.xml', replace=False, user=user)
    created.refresh_from_db()
    assert created.actual_start == date(2026, 4, 1)

    prima = _project(user, 'P6D')
    xer = (
        'ERMHDR\t18.8\t2026-01-01\tProject\n'
        '%T\tPROJWBS\n%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\n'
        '%R\t1\t\t1\tRoot\n'
        '%T\tTASK\n%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt\tact_start_date\n'
        '%R\t10\t1\tA\tOnly actual\t\t2026-05-01 08:00\n'
    ).encode()
    execute_p6_import(prima, xer, filename='dates.xer', replace=False, user=user)
    actual_only = Activity.objects.get(project=prima, activity_code='A')
    assert actual_only.planned_start is None
    assert actual_only.actual_start == date(2026, 5, 1)


def test_milestone_report_and_critical_gate(user):
    project = _project(user, 'GATE')
    execute_msp_import(
        project, (FIXTURES / 'milestone.xml').read_bytes(), filename='milestone.xml', replace=False, user=user,
    )
    status = build_schedule_status(project.id)
    assert any(item['activity_code'] == '1.1' for item in status['milestones'])
    gantt = get_gantt_data(project.id)
    assert any(task['is_milestone'] for task in gantt['tasks'])
    incomplete = Activity.objects.create(
        project=project,
        wbs=WBS.objects.get(project=project, wbs_code='1'),
        activity_code='OPEN',
        activity_name='Open',
        duration_days=None,
        is_milestone=False,
        is_critical=True,
        created_by=user,
        updated_by=user,
    )
    baseline = BaselineSchedule.objects.get(project=project)
    BaselineActivity.objects.create(
        baseline=baseline,
        activity=incomplete,
        is_critical=True,
    )
    validity = evaluate_critical_path_validity(project.id)
    assert validity['valid'] is False
    assert validity['critical_activity_ids'] == []


def test_summary_predecessors_and_zero_duration_names(user):
    project = _project(user, 'SUM')
    summaries = ''.join(
        _task(UID=uid, Name=f'Summary {uid}', OutlineNumber=f'1.{index}', WBS=f'1.{index}', Summary='1')
        for index, uid in enumerate(('8055', '8084', '8102', '8120'), start=1)
    )
    body = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='1', Summary='1')
        + summaries
        + _task(UID='9', Name='شروع', OutlineNumber='1.9', WBS='1.9', Summary='0', Duration='PT0H0M0S')
        + _task(UID='10', Name='پایان', OutlineNumber='1.10', WBS='1.10', Summary='0', Duration='PT0H0M0S')
        .replace(
            '</Task>',
            '<PredecessorLink><PredecessorUID>8055</PredecessorUID><Type>1</Type></PredecessorLink>'
            '<PredecessorLink><PredecessorUID>8084</PredecessorUID><Type>1</Type></PredecessorLink>'
            '<PredecessorLink><PredecessorUID>8102</PredecessorUID><Type>1</Type></PredecessorLink>'
            '<PredecessorLink><PredecessorUID>8120</PredecessorUID><Type>1</Type></PredecessorLink></Task>',
        )
    )
    preview = build_preview(parse_msp_xml(body))
    result = execute_msp_import(project, body, filename='summary-links.xml', replace=False, user=user)
    assert ActivityRelation.objects.filter(successor__project=project).count() == 0
    for uid in ('8055', '8084', '8102', '8120'):
        assert WBS.objects.filter(project=project, wbs_code=f'1.{["8055", "8084", "8102", "8120"].index(uid) + 1}').exists()
        assert any(uid in item for item in result['warnings'] if item.startswith('predecessor_is_summary:'))
        assert any(item['code'] == 'predecessor_is_summary' and uid in item['row'] for item in preview['warning_items'])
    assert Activity.objects.get(project=project, activity_name='شروع').duration_days == 0
    assert Activity.objects.get(project=project, activity_name='پایان').duration_days == 0
    assert not Activity.objects.filter(project=project, activity_code__in=['8055', '8084', '8102', '8120']).exists()


@pytest.mark.django_db
def test_stored_mpp_xml_match_when_converter_runs(user):
    mpp_path = Path(__file__).resolve().parents[5] / 'real-data' / 'plan.mpp'
    if not mpp_path.is_file():
        pytest.skip('employer file missing')
    raw = mpp_path.read_bytes()
    xml_bytes = _convert_reference_mpp(raw)
    left = _project(user, 'MPP')
    right = _project(user, 'XMLT')
    left_result = execute_msp_import(left, raw, filename='plan.mpp', replace=False, user=user)
    right_result = execute_msp_import(right, xml_bytes, filename='plan.xml', replace=False, user=user)
    assert Activity.objects.filter(project=left, is_deleted=False).exists()
    assert WBS.objects.filter(project=left, is_deleted=False).exists()

    def snapshot(project):
        nodes = sorted(
            (node.wbs_code, node.get_parent().wbs_code if node.get_parent() else None)
            for node in WBS.objects.filter(project=project, is_deleted=False)
        )
        activities = sorted(
            (
                act.activity_code, act.wbs.wbs_code, act.duration_days, act.is_milestone,
                act.planned_start, act.planned_finish, act.actual_start, act.actual_finish,
                act.forecast_start, act.forecast_finish, act.planned_percent,
                act.is_critical, act.total_slack_days, act.free_slack_days,
                act.working_calendar_id, act.weight,
            )
            for act in Activity.objects.filter(project=project, is_deleted=False).select_related('wbs')
        )
        links = sorted(
            (rel.predecessor.activity_code, rel.successor.activity_code, rel.relation_type, rel.lag_days)
            for rel in ActivityRelation.objects.filter(successor__project=project, is_deleted=False).select_related('predecessor', 'successor')
        )
        return nodes, activities, links

    assert snapshot(left) == snapshot(right)
    assert snapshot(left)[1]
    assert snapshot(left)[2]
    assert sorted((item['code'], item['row']) for item in left_result['warning_items']) == sorted(
        (item['code'], item['row']) for item in right_result['warning_items']
    )
    assert sorted(left_result['warnings']) == sorted(right_result['warnings'])


def test_empty_replace_keeps_existing_nodes(user):
    project = _project(user, 'EMPTY2')
    WBS.add_root(project_id=project.id, wbs_code='KEEP', wbs_name='Keep', created_by=user, updated_by=user)
    before = _codes(project)
    result = execute_msp_import(project, _xml(''), filename='empty.xml', replace=True, user=user)
    assert _codes(project) == before
    assert result['nothing_changed'] is True
    assert BaselineSchedule.objects.filter(project=project).count() == 0
    orphan = _xml(
        _task(UID='2', Name='Loose', OutlineNumber='1', WBS='1.2', Summary='0', Duration='PT8H0M0S')
    )
    orphan_result = execute_msp_import(project, orphan, filename='loose.xml', replace=True, user=user)
    assert _codes(project) == before
    assert orphan_result['nothing_changed'] is True
    assert any(item.startswith('empty_import') or item.startswith('activity_without_parent:') for item in orphan_result['warnings'])


def test_reordered_nested_parents_survive_sorted_insert(user):
    body = _xml(
        _task(UID='B', Name='Root B', OutlineNumber='2', WBS='B', Summary='1')
        + _task(UID='B1', Name='Summary B.1', OutlineNumber='2.1', WBS='B.1', Summary='1')
        + _task(UID='A', Name='Root A', OutlineNumber='1', WBS='A', Summary='1')
        + _task(UID='B11', Name='Summary B.1.1', OutlineNumber='2.1.1', WBS='B.1.1', Summary='1')
        + _task(UID='LEAF', Name='Leaf', OutlineNumber='2.1.1.1', WBS='B.1.1.1', Summary='0', Duration='PT8H0M0S')
    )
    project = _project(user, 'NEST')
    preview = build_preview(parse_msp_xml(body))
    execute_msp_import(project, body, filename='nest.xml', replace=False, user=user)
    summary = WBS.objects.get(project=project, wbs_code='B.1.1')
    assert summary.get_parent().wbs_code == 'B.1'
    assert summary.get_parent().get_parent().wbs_code == 'B'
    leaf = Activity.objects.get(project=project, activity_code='B.1.1.1')
    assert leaf.wbs_id == summary.id
    assert any(item['activity_code'] == 'B.1.1.1' for item in preview['activities'])
    xer = (
        'ERMHDR\t18.8\t2026-01-01\tProject\n'
        '%T\tPROJWBS\n%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\n'
        '%R\t2\t\tB\tRoot B\n'
        '%R\t21\t2\tB.1\tSummary B.1\n'
        '%R\t1\t\tA\tRoot A\n'
        '%R\t211\t21\tB.1.1\tSummary B.1.1\n'
        '%T\tTASK\n%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt\n'
        '%R\t9\t211\tB.1.1.1\tLeaf\t8\n'
    ).encode()
    xer_project = _project(user, 'NESTX')
    execute_p6_import(xer_project, xer, filename='nest.xer', replace=False, user=user)
    xer_leaf = Activity.objects.get(project=xer_project, activity_code='B.1.1.1')
    assert xer_leaf.wbs.wbs_code == 'B.1.1'
    assert xer_leaf.wbs.get_parent().wbs_code == 'B.1'


def test_missing_outline_does_not_use_wbs_dots(user):
    body = _xml(_task(UID='9', Name='Dotted', WBS='1.2.3', Summary='0', Duration='PT8H0M0S'))
    project = _project(user, 'NOOUT')
    preview = build_preview(parse_msp_xml(body))
    result = execute_msp_import(project, body, filename='no-outline.xml', replace=False, user=user)
    assert Activity.objects.filter(project=project).count() == 0
    assert any(item['code'] == 'activity_without_parent' and item['row'] == '9' for item in preview['warning_items'])
    assert any(item.startswith('activity_without_parent: 9') for item in result['warnings'])


def test_blocking_notes_keep_every_row_identifier(user):
    body = _xml(
        _task(UID='1', Name='One', OutlineNumber='1', WBS='1', Summary='0', Start='2026-02-02T08:00:00', Finish='2026-02-01T08:00:00')
        + _task(UID='2', Name='Two', OutlineNumber='2', WBS='2', Summary='0', Start='2026-03-02T08:00:00', Finish='2026-03-01T08:00:00')
    )
    project = _project(user, 'ROWS')
    preview = build_preview(parse_msp_xml(body))
    with pytest.raises(ImportFidelityError) as exc:
        execute_msp_import(project, body, filename='rows.xml', replace=False, user=user)
    assert {note['row'] for note in exc.value.as_dicts()} >= {'1', '2'}
    assert {item['row'] for item in preview['blocking']} >= {'1', '2'}


def test_p6_critical_and_float_are_stored(user):
    xer = (
        'ERMHDR\t18.8\t2026-01-01\tProject\n'
        '%T\tPROJWBS\n%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\n'
        '%R\t1\t\tP\tParent\n'
        '%T\tTASK\n%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt\ttotal_float_hr_cnt\tfree_float_hr_cnt\tcrit_path_flag\n'
        '%R\t10\t1\tC\tCritical\t8\t0\t0\tN\n'
    ).encode()
    project = _project(user, 'P6C')
    execute_p6_import(project, xer, filename='crit.xer', replace=False, user=user)
    activity = Activity.objects.get(project=project, activity_code='C')
    assert activity.is_critical is False
    assert activity.total_slack_days == 0
    assert activity.free_slack_days == 0
    row = BaselineActivity.objects.get(activity=activity)
    assert row.total_float == 0
    assert row.is_critical is False


def test_missing_duration_and_omitted_link_invalidate_the_gate(user):
    project = _project(user, 'GATE2')
    body = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='R', Summary='1')
        + _task(
            UID='2', Name='Dated', OutlineNumber='1.1', WBS='R.1', Summary='0',
            Start='2026-04-01T08:00:00', Finish='2026-04-02T08:00:00',
        ).replace('</Task>', '<PredecessorLink><PredecessorUID>99</PredecessorUID><Type>1</Type></PredecessorLink></Task>')
    )
    result = execute_msp_import(project, body, filename='gate.xml', replace=False, user=user)
    from schedule.models import MspImportJob, MspImportStatus
    MspImportJob.objects.create(
        project=project,
        status=MspImportStatus.DONE,
        result={'warnings': result['warnings']},
        created_by=user,
    )
    validity = evaluate_critical_path_validity(project.id)
    assert validity['valid'] is False
    assert 'incomplete_durations' in validity['reason_codes']
    assert 'omitted_relationships' in validity['reason_codes']
    assert validity['critical_activity_ids'] == []


def test_invalid_weight_is_warned_and_not_stored(user):
    body = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='W', Summary='1')
        + _task(UID='2', Name='Heavy', OutlineNumber='1.1', WBS='W.1', Summary='0', Duration='PT8H0M0S', Weight='2')
    )
    project = _project(user, 'WT')
    result = execute_msp_import(project, body, filename='weight.xml', replace=False, user=user)
    activity = Activity.objects.get(project=project, activity_code='W.1')
    assert activity.weight is None
    assert any(item.startswith('invalid_weight:') for item in result['warnings'])


def test_activity_detail_exposes_imported_facts(user):
    from rest_framework.test import APIClient

    project = _project(user, 'DET')
    body = _xml(
        _task(UID='1', Name='Root', OutlineNumber='1', WBS='D', Summary='1')
        + _task(
            UID='2', Name='Leaf', OutlineNumber='1.1', WBS='D.1', Summary='0', Duration='PT8H0M0S',
            PercentComplete='25', Critical='0', TotalSlack='0', FreeSlack='4800',
        )
    )
    execute_msp_import(project, body, filename='detail.xml', replace=False, user=user)
    activity = Activity.objects.get(project=project, activity_code='D.1')
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get(f'/api/v1/projects/{project.id}/activities/{activity.id}/')
    assert response.status_code == 200
    assert response.data['planned_percent'] == '25.000'
    assert response.data['is_critical'] is False
    assert response.data['total_slack_days'] == 0
    assert response.data['free_slack_days'] == 1


def test_employer_summary_links_keep_the_file_unchanged(user):
    import hashlib

    path = Path(__file__).resolve().parents[5] / 'real-data' / 'plan.mpp'
    if not path.is_file():
        pytest.skip('employer file missing')
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == '3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553'
    xml_bytes = _convert_reference_mpp(raw)
    parsed = parse_msp_xml(xml_bytes)
    preview = build_preview(parsed)
    project = _project(user, 'EMP')
    result = execute_msp_import(project, raw, filename='plan.mpp', replace=False, user=user)
    employer_edges = [task for task in parsed.tasks if task.name in ('شروع', 'پایان')]
    assert {task.name for task in employer_edges} == {'شروع', 'پایان'}
    for task in employer_edges:
        assert not task.parent_key
        assert task.duration_days == 0
        assert not task.duration_inexact
        note = {'code': 'activity_without_parent', 'row': task.uid}
        assert note in preview['warning_items']
        assert note in result['warning_items']
        assert f'activity_without_parent: {task.uid}' in result['warnings']
    for uid in ('8055', '8084', '8102', '8120'):
        assert any(item['code'] == 'predecessor_is_summary' and uid in item['row'] for item in preview['warning_items'])
        assert any(item.startswith('predecessor_is_summary:') and uid in item for item in result['warnings'])
    assert ActivityRelation.objects.filter(successor__project=project, predecessor__activity_code__in=['8055', '8084', '8102', '8120']).count() == 0
    assert not Activity.objects.filter(project=project, activity_name__in=['شروع', 'پایان']).exists()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
