"""Focused regression coverage for B02 version integrity guarantees."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connections
from openpyxl import load_workbook
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from common.reporting_units import SpecialtyUnit

from field_reports.models import (
    DailyReport, DailyReportActivity, DailyReportCorrectionRequest, DailyReportDerivedSource,
    DailyReportWorkedShift, ReportStatus,
)
from field_reports.services import correction_service
from field_reports.services.activity_log import activity_log_queryset
from field_reports.services.lifecycle_errors import LIFECYCLE_MESSAGES
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta, ensure_daily_report_summary, rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import add_activity, make_sub_report
from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
from project_templates.models import ProjectTemplate, ProjectTemplateRequiredUnit
from project_templates.services import activate_project_reporting_configuration
from projects.services import create_project_with_creator
from sub_reports.models import SubReportStatus
from sub_reports.services import submit_sub_report


DAY = date(2025, 1, 8)
REASON = 'Correction preserves all version data'


@pytest.fixture
def report_clients(project, auth_client, project_approver_client):
    def actor(name, permissions=None):
        user = get_user_model().objects.create_user(username=f'b02-{name}')
        client = APIClient()
        client.force_authenticate(user=user)
        if permissions is not None:
            role = Role.objects.create(role_name=f'b02-{name}')
            for permission in permissions:
                RolePermission.objects.create(role=role, permission_codename=permission)
            member = ProjectMember.objects.create(project=project, user=user, status='active')
            ProjectMemberRole.objects.create(member=member, role=role)
        return user, client

    _, viewer = actor('viewer', ['view_project', 'view_reports'])
    _, unauthorized = actor('unauthorized', ['view_project'])
    cross_user, cross_project = actor('cross-project')
    create_project_with_creator(
        creator=cross_user, project_code='B02-OTHER', project_name='Other B02 project',
        employer='Employer', start_date=DAY,
    )
    observer_user, observer = actor('observer')
    observer_user.groups.add(Group.objects.get_or_create(name='admin')[0])
    return {
        'preparer': auth_client, 'approver': project_approver_client,
        'viewer': viewer, 'unauthorized': unauthorized,
        'cross_project': cross_project, 'observer': observer,
    }


@pytest.fixture
def approved_summary(project, user):
    template = ProjectTemplate.objects.create(template_name='B02 baseline', created_by=user)
    for order, unit in enumerate((SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL)):
        ProjectTemplateRequiredUnit.objects.create(template=template, unit=unit, display_order=order)
    config = activate_project_reporting_configuration(
        project=project, template=template, effective_from=DAY, user=user,
    )
    source = DailyReport.objects.create(
        project=project, report_date=DAY, status=ReportStatus.APPROVED,
        is_current=True, is_auto_summary=True, management_opinion='Reviewed',
        weather_condition='cloudy', weather_override=True, site_status_override=True,
        aggregation_fingerprint='a' * 64, aggregated_at=timezone.now(),
        reporting_configuration=config, prepared_by=user, created_by=user, updated_by=user,
    )
    activity = DailyReportActivity.objects.create(
        report=source, activity_description='Derived activity', is_derived=True,
        source_discipline='buildings', quantity=Decimal('5'), quantity_measured=True, unit='m2', headcount=4,
    )
    for ordinal, unit in enumerate((SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL)):
        unit_report = make_sub_report(project, user, unit=unit, report_date=DAY, status=SubReportStatus.SUBMITTED)
        unit_row = add_activity(unit_report, description=f'{unit} source activity')
        DailyReportDerivedSource.objects.create(
            daily_report=source, derived_kind='activity', derived_row_id=str(activity.pk),
            source_report=unit_report, source_report_id_snapshot=unit_report.pk,
            source_report_version=1, source_unit=unit, source_row_kind='activity',
            source_row_id=str(unit_row.pk), contribution_value=Decimal('2.5'), ordinal=ordinal,
        )
    DailyReportWorkedShift.objects.create(report=source, shift_id=1, actual_duration_hours=Decimal('7.50'))
    return source


def report_url(report):
    return f'/api/v1/projects/{report.project_id}/daily-reports/{report.pk}/'


def open_revision(client, report):
    response = client.post(report_url(report) + 'correction-requests/', {'reason': REASON}, format='json')
    assert response.status_code == 201, response.data
    return response.data, DailyReport.objects.get(pk=response.data['result_report_id'])


def report_snapshot(report):
    return (
        DailyReport.all_objects.filter(pk=report.pk).values().get(),
        list(report.activities.order_by('pk').values()),
        list(report.derived_sources.order_by('pk').values()),
        list(report.worked_shifts.order_by('pk').values()),
    )



@pytest.mark.django_db
def test_correction_preserves_summary_metadata_provenance_and_worked_shifts(approved_summary, user):
    source = approved_summary
    source.worked_shifts.update(
        actual_start_at='2025-01-08T22:00:00+03:30', actual_end_at='2025-01-09T06:00:00+03:30',
    )
    correction = correction_service.open_correction(
        source_report=source, user=user, reason='Correction preserves all version data',
    )
    target = correction.result_report
    cloned_activity = target.activities.get()
    assert target.is_auto_summary is True
    assert target.management_opinion == 'Reviewed'
    assert target.weather_override and target.site_status_override
    assert target.aggregation_fingerprint == 'a' * 64
    copied_shift = target.worked_shifts.get()
    original_shift = source.worked_shifts.get()
    assert copied_shift.actual_duration_hours == Decimal('7.50')
    assert copied_shift.actual_start_at == original_shift.actual_start_at
    assert copied_shift.actual_end_at == original_shift.actual_end_at
    cloned_sources = list(target.derived_sources.order_by('ordinal'))
    assert len(cloned_sources) == 2
    assert {row.derived_row_id for row in cloned_sources} == {str(cloned_activity.pk)}
    assert [row.source_unit for row in cloned_sources] == ['buildings', 'electrical']
    assert source.derived_sources.count() == 2
    assert target.reporting_configuration_id == source.reporting_configuration_id
    assert target.aggregated_at == source.aggregated_at
    assert target.approved_by_id is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('overrides', 'code'),
    [
        ({'is_deleted': True}, 'rebuild_target_deleted'),
        ({'is_current': False}, 'historical_rebuild_rejected'),
        ({'status': ReportStatus.APPROVED}, 'report_locked'),
        ({'status': ReportStatus.SUBMITTED}, 'report_not_editable'),
    ],
)
def test_explicit_rebuild_rejects_ineligible_target(project, user, overrides, code):
    values = {'status': ReportStatus.DRAFT, 'is_current': True, 'is_auto_summary': True}
    values.update(overrides)
    report = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 9), created_by=user, updated_by=user, **values,
    )
    with pytest.raises(ValidationError) as exc:
        rebuild_daily_report_summary(
            project.id, report.report_date, user=user, report=report,
        )
    assert exc.value.get_codes()['detail'] == code


@pytest.mark.django_db
def test_official_activity_log_excludes_noncurrent_approved_version(project, user):
    old = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 10), status=ReportStatus.APPROVED,
        is_current=False, created_by=user, updated_by=user,
    )
    current = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 10), status=ReportStatus.APPROVED,
        is_current=True, lineage_id=old.lineage_id or old.id, version_number=2,
        supersedes=old, created_by=user, updated_by=user,
    )
    DailyReportActivity.objects.create(report=old, activity_description='old', quantity=5, headcount=4)
    DailyReportActivity.objects.create(report=current, activity_description='current', quantity=5, headcount=4)
    rows = list(activity_log_queryset(project.id, {}))
    assert len(rows) == 1
    assert rows[0].report_id == current.id


@pytest.mark.django_db
def test_submitter_cannot_approve_own_report(auth_client, project, user):
    report = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 11), status=ReportStatus.SUBMITTED,
        submitted_by=user, submitted_at=timezone.now(), created_by=user, updated_by=user,
    )
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{report.id}/approve/', format='json',
    )
    report.refresh_from_db()
    assert response.status_code == 400
    assert response.data['error']['code'] == 'sod_self_approval_forbidden'
    assert report.status == ReportStatus.SUBMITTED


@pytest.mark.django_db
def test_legacy_nested_payload_cannot_mutate_derived_revision(auth_client, project, user):
    report = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 12), status=ReportStatus.DRAFT,
        is_auto_summary=True, created_by=user, updated_by=user,
    )
    activity = DailyReportActivity.objects.create(
        report=report, activity_description='Read only', is_derived=True, quantity=5,
    )
    response = auth_client.patch(
        f'/api/v1/projects/{project.id}/daily-reports/{report.id}/',
        {'activities': [{'activity_description': 'Attempted overwrite', 'quantity': 9}]},
        format='json',
    )
    activity.refresh_from_db()
    assert response.status_code == 400
    assert activity.activity_description == 'Read only'
    assert activity.quantity == 5


@pytest.mark.django_db
def test_explicit_rebuild_endpoint_returns_code_for_approved_target(auth_client, project, user):
    report = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 13), status=ReportStatus.APPROVED,
        is_auto_summary=True, created_by=user, updated_by=user,
    )
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{report.id}/rebuild/', format='json',
    )
    assert response.status_code == 400
    assert response.data['error']['code'] == 'report_locked'


@pytest.mark.django_db
@pytest.mark.parametrize('status', [ReportStatus.SUBMITTED, ReportStatus.UNDER_REVIEW])
def test_implicit_ensure_does_not_rebuild_noneditable_snapshot(project, user, status):
    report = DailyReport.objects.create(
        project=project, report_date=date(2025, 1, 14), status=status,
        is_auto_summary=True, general_notes='snapshot note', aggregation_fingerprint='f' * 64,
        created_by=user, updated_by=user,
    )
    activity = DailyReportActivity.objects.create(
        report=report, activity_description='snapshot row', quantity=5, is_derived=True,
    )
    assert ensure_daily_report_summary(project.id, report.report_date, user=user).pk == report.pk
    result = rebuild_daily_report_summary(project.id, report.report_date, user=user)
    activity.refresh_from_db()
    report.refresh_from_db()
    assert result.pk == report.pk
    assert report.general_notes == 'snapshot note'
    assert activity.activity_description == 'snapshot row'
    assert report.aggregation_fingerprint == 'f' * 64


@pytest.mark.django_db
def test_provenance_is_version_bound_after_approval_and_cancel(approved_summary, report_clients):
    source = approved_summary
    preparer, approver = report_clients['preparer'], report_clients['approver']
    _, revision = open_revision(preparer, source)

    def drilldown(report):
        row = report.activities.get()
        response = preparer.get(report_url(report) + f'provenance/activity/{row.pk}/')
        assert response.status_code == 200, response.data
        return row, response.data['rows']

    old_row, original = drilldown(source)
    new_row, cloned = drilldown(revision)
    assert old_row.pk != new_row.pk
    assert len(original) == 2
    assert cloned == original
    assert all(row['source_report'] and row['href'] for row in cloned)
    assert preparer.get(report_url(revision) + f'provenance/activity/{old_row.pk}/').status_code == 404

    submitted = preparer.post(report_url(revision) + 'submit/', format='json')
    assert submitted.status_code == 200, submitted.data
    approved = approver.post(report_url(revision) + 'approve/', format='json')
    assert approved.status_code == 200, approved.data
    revision.refresh_from_db()
    source.refresh_from_db()
    assert (source.status, source.is_current) == (ReportStatus.APPROVED, False)
    assert (revision.status, revision.is_current) == (ReportStatus.APPROVED, True)
    assert drilldown(source)[1] == drilldown(revision)[1] == original
    assert revision.worked_shifts.get().actual_duration_hours == Decimal('7.50')
    assert set(source.project.discipline_sub_reports.values_list('status', flat=True)) == {SubReportStatus.SUBMITTED}

    before = report_snapshot(revision)
    correction, cancelled = open_revision(preparer, revision)
    response = preparer.post(
        f'/api/v1/projects/{source.project_id}/correction-requests/{correction["id"]}/cancel/',
        format='json',
    )
    assert response.status_code == 200, response.data
    cancelled.refresh_from_db()
    assert cancelled.is_deleted and not cancelled.is_current
    after = report_snapshot(revision)
    for field in ('updated_at', 'updated_by_id'):
        before[0].pop(field)
        after[0].pop(field)
    assert before == after


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('status', 'is_current', 'is_deleted', 'code'),
    [
        (ReportStatus.APPROVED, True, False, 'report_locked'),
        (ReportStatus.APPROVED, False, False, 'historical_rebuild_rejected'),
        (ReportStatus.DRAFT, False, False, 'historical_rebuild_rejected'),
        (ReportStatus.DRAFT, False, True, 'rebuild_target_deleted'),
        (ReportStatus.SUBMITTED, True, False, 'report_not_editable'),
        (ReportStatus.UNDER_REVIEW, True, False, 'report_not_editable'),
    ],
)
def test_rebuild_rejection_leaves_full_snapshot_untouched(
    approved_summary, auth_client, user, status, is_current, is_deleted, code,
):
    report = approved_summary
    report.status, report.is_current, report.is_deleted = status, is_current, is_deleted
    report.save(update_fields=['status', 'is_current', 'is_deleted'])
    before = report_snapshot(report)
    with pytest.raises(ValidationError) as exc:
        rebuild_daily_report_summary(report.project_id, report.report_date, user=user, report=report)
    assert exc.value.get_codes()['detail'] == code

    messages = []
    for language in ('fa', 'en'):
        response = auth_client.post(report_url(report) + 'rebuild/', HTTP_ACCEPT_LANGUAGE=language)
        assert response.status_code == 400, response.data
        assert response.data['error']['code'] == code
        message = response.data['error']['message']
        assert message == LIFECYCLE_MESSAGES[code][language]
        messages.append(message)
    assert messages[0] != messages[1]
    assert report_snapshot(report) == before


@pytest.mark.django_db
def test_rebuild_preserves_overrides_and_approved_snapshot_detects_drift(approved_summary, report_clients):
    preparer, approver = report_clients['preparer'], report_clients['approver']
    _, revision = open_revision(preparer, approved_summary)
    patched = preparer.patch(
        report_url(revision),
        {'management_opinion': 'Updated opinion', 'site_status': 'inactive', 'inactivity_reason': 'weather'},
        format='json',
    )
    assert patched.status_code == 200, patched.data
    buildings = approved_summary.derived_sources.get(source_unit=SpecialtyUnit.BUILDINGS).source_report
    buildings.activities.update(activity_description='Updated buildings activity')
    response = preparer.post(report_url(revision) + 'rebuild/')
    assert response.status_code == 200, response.data
    revision.refresh_from_db()
    assert revision.management_opinion == 'Updated opinion'
    assert revision.weather_override and revision.site_status_override
    assert revision.weather_condition == 'cloudy'
    assert (revision.site_status, revision.inactivity_reason) == ('inactive', 'weather')
    assert revision.reporting_configuration_id == approved_summary.reporting_configuration_id
    assert revision.aggregation_fingerprint != approved_summary.aggregation_fingerprint
    assert set(revision.activities.values_list('activity_description', flat=True)) == {
        'Updated buildings activity', 'electrical source activity',
    }
    sources = revision.derived_sources.filter(derived_kind='activity')
    assert sources.count() == 2
    assert sources.values('derived_row_id').distinct().count() == 2
    assert preparer.post(report_url(revision) + 'submit/').status_code == 200
    assert approver.post(report_url(revision) + 'approve/').status_code == 200

    before = report_snapshot(revision)
    unit = make_sub_report(
        revision.project, buildings.created_by, unit=SpecialtyUnit.MECHANICAL, report_date=DAY,
    )
    add_activity(unit, description='Submitted after summary approval')
    submit_sub_report(unit, buildings.created_by)
    assert build_aggregation_meta(revision.project_id, revision.report_date, report=revision)[
        'snapshot_source_comparison'
    ] == 'changed'
    assert report_snapshot(revision) == before
    assert before[0]['submitted_at'] is not None and before[0]['approved_at'] is not None


@pytest.mark.django_db(transaction=True)
def test_activity_log_json_and_excel_across_approval_and_cancellation(approved_summary, report_clients):
    preparer, approver = report_clients['preparer'], report_clients['approver']
    project_url = f'/api/v1/projects/{approved_summary.project_id}/'
    log_url = project_url + 'activity-log/'

    def assert_official_rows(expected):
        response = preparer.get(log_url)
        assert response.status_code == 200, response.data
        assert response.data['count'] == len(expected)
        assert [(r['quantity'], r['headcount']) for r in response.data['results']] == expected
        response = preparer.get(log_url + 'excel/')
        assert response.status_code == 200
        with BytesIO(response.content) as stream:
            workbook = load_workbook(stream, read_only=True)
            try:
                rows = workbook['ACTIVITY'].iter_rows(min_row=2, values_only=True)
                assert [(row[10], row[5]) for row in rows if isinstance(row[0], int)] == expected
            finally:
                workbook.close()

    assert_official_rows([(5, 4)])
    correction, draft = open_revision(preparer, approved_summary)
    assert_official_rows([])
    preview = preparer.get(log_url, {'approved_only': 'false'})
    assert [row['report_id'] for row in preview.data['results']] == [str(draft.pk)]
    assert preparer.post(
        project_url + f'correction-requests/{correction["id"]}/cancel/',
    ).status_code == 200
    assert_official_rows([(5, 4)])

    _, revision = open_revision(preparer, approved_summary)
    assert revision.pk != draft.pk
    assert preparer.post(report_url(revision) + 'submit/').status_code == 200
    assert approver.post(report_url(revision) + 'approve/').status_code == 200
    assert_official_rows([(5, 4)])
    history = preparer.get(report_url(revision) + 'versions/')
    assert history.status_code == 200, history.data
    assert {r['report_id'] for r in history.data} == {str(approved_summary.pk), str(revision.pk)}


@pytest.mark.django_db(transaction=True)
def test_concurrent_correction_has_one_winner(approved_summary, user):
    barrier = Barrier(2)

    def request_correction():
        try:
            client = APIClient()
            client.force_authenticate(user=user)
            barrier.wait(timeout=10)
            return client.post(
                report_url(approved_summary) + 'correction-requests/', {'reason': REASON}, format='json',
            )
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        first, second = sorted(pool.map(lambda _: request_correction(), range(2)), key=lambda r: r.status_code)
    assert first.status_code == 201, first.data
    assert second.status_code == 400, second.data
    assert second.data['error']['code'] == 'correction_already_open'
    assert DailyReportCorrectionRequest.objects.filter(source_report=approved_summary).count() == 1
    assert DailyReport.objects.filter(lineage_id=approved_summary.lineage_id, is_current=True).count() == 1


@pytest.mark.django_db
def test_roles_and_short_reasons_are_enforced_by_workflow_apis(approved_summary, report_clients):
    preparer, approver = report_clients['preparer'], report_clients['approver']
    url = report_url(approved_summary)
    assert preparer.post(url + 'correction-requests/', {'reason': 'too short'}).status_code == 400
    by_date = f'/api/v1/projects/{approved_summary.project_id}/daily-reports/by-date/'
    for _ in range(2):
        response = report_clients['viewer'].get(by_date, {'date': DAY.isoformat()})
        assert response.status_code == 200, response.data
        assert response.data['report_id'] == str(approved_summary.pk)
    assert DailyReport.objects.filter(project=approved_summary.project, report_date=DAY).count() == 1

    for role in ('viewer', 'unauthorized', 'cross_project', 'observer'):
        client = report_clients[role]
        assert client.post(url + 'correction-requests/', {'reason': REASON}).status_code == 403
        assert client.post(url + 'rebuild/').status_code == 403

    correction, revision = open_revision(preparer, approved_summary)
    cancel_url = f'/api/v1/projects/{revision.project_id}/correction-requests/{correction["id"]}/cancel/'
    for role in ('viewer', 'unauthorized', 'cross_project', 'observer'):
        assert report_clients[role].post(cancel_url).status_code == 403
    assert preparer.post(report_url(revision) + 'submit/').status_code == 200
    for role in ('viewer', 'unauthorized', 'cross_project', 'observer'):
        assert report_clients[role].post(report_url(revision) + 'approve/').status_code == 403
        assert report_clients[role].post(report_url(revision) + 'reject/', {'reason': REASON}).status_code == 403
    denied = approver.post(report_url(revision) + 'reject/', {'reason': 'too short'})
    assert denied.status_code == 400
    assert denied.data['error']['code'] == 'rejection_reason_min_length_10'
    revision.refresh_from_db()
    assert revision.status == ReportStatus.SUBMITTED


@pytest.mark.django_db
def test_effective_six_unit_configuration_filters_ineligible_sources(project, user):
    later = DAY + timedelta(days=1)
    units = list(SpecialtyUnit)
    assert len(units) == 6
    for day, ordered_units in ((DAY, units), (later, units[::-1])):
        template = ProjectTemplate.objects.create(template_name=f'B02 {day}', created_by=user)
        for order, unit in enumerate(ordered_units):
            ProjectTemplateRequiredUnit.objects.create(template=template, unit=unit, display_order=order)
        activate_project_reporting_configuration(project=project, template=template, effective_from=day, user=user)
    other_project = create_project_with_creator(
        creator=user, project_code='B02-SOURCE-OTHER', project_name='Other source project',
        employer='Employer', start_date=DAY,
    )
    candidates = (
        (project, DAY, units[0], SubReportStatus.APPROVED, True, False),
        (project, DAY, units[1], SubReportStatus.DRAFT, True, False),
        (project, DAY, units[2], SubReportStatus.REJECTED, True, False),
        (project, DAY, units[3], SubReportStatus.SUBMITTED, True, True),
        (project, DAY, units[4], SubReportStatus.SUBMITTED, False, False),
        (other_project, DAY, units[5], SubReportStatus.SUBMITTED, True, False),
        (project, later, units[5], SubReportStatus.SUBMITTED, True, False),
    )
    for source_project, day, unit, status, current, deleted in candidates:
        source = make_sub_report(source_project, user, report_date=day, unit=unit, status=status, is_current=current)
        add_activity(source, description=f'{unit} {status}')
        if deleted:
            source.soft_delete(user=user)

    configuration_ids = []
    for day, expected in ((DAY, [units[0]]), (later, [units[5]])):
        summary = ensure_daily_report_summary(project.id, day, user=user)
        completeness = build_aggregation_meta(project.id, day, report=summary)['completeness']
        assert completeness['expected_units'] == (units if day == DAY else units[::-1])
        assert completeness['contributing_units'] == expected
        assert set(completeness['missing_units']) == set(units) - set(expected)
        assert list(summary.activities.values_list('source_discipline', flat=True)) == expected
        configuration_ids.append(summary.reporting_configuration_id)
    assert None not in configuration_ids and configuration_ids[0] != configuration_ids[1]


@pytest.mark.django_db
@pytest.mark.parametrize('ownership', ['summary', 'row_flag', 'provenance'])
def test_revision_operational_rows_are_read_only_at_each_mutation_boundary(
    approved_summary, auth_client, ownership,
):
    _, revision = open_revision(auth_client, approved_summary)
    row = revision.activities.get()
    if ownership != 'summary':
        DailyReport.objects.filter(pk=revision.pk).update(is_auto_summary=False)
    if ownership == 'row_flag':
        revision.derived_sources.all().delete()
    if ownership == 'provenance':
        revision.activities.update(is_derived=False, source_sub_report=None)

    before = report_snapshot(revision)
    url = report_url(revision)
    collection = url + 'activities/'
    detail = collection + f'{row.pk}/'
    edit = {'activity_description': 'Untrusted manual edit'}
    responses = (
        (auth_client.post(collection, edit, format='json'), 'derived_collection_read_only'),
        (auth_client.patch(detail, edit, format='json'), 'derived_collection_read_only'),
        (auth_client.delete(detail), 'derived_collection_read_only'),
        (auth_client.post(url + 'labor/', [{'job_title': 'Manual'}], format='json'), 'derived_collection_read_only'),
        (auth_client.patch(url, {'activities': [edit]}, format='json'), 'derived_readonly'),
    )
    for response, code in responses:
        assert response.status_code == 400, response.data
        assert response.data['error']['code'] == code
    sync = auth_client.post(
        f'/api/v1/projects/{revision.project_id}/daily-reports/sync-batch/',
        [{'report_date': DAY.isoformat(), 'activities': [edit]}],
        format='json',
    )
    assert sync.status_code == 200
    assert sync.data['results'][0]['child_errors'] == [{'section': 'activities', 'code': 'derived_readonly'}]
    assert report_snapshot(revision) == before
