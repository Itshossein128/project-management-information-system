"""T071 / quickstart §6: Real PostgreSQL concurrency tests.

Uses independent database connections and synchronization barriers to prove
database state after threads complete for:
1. Simultaneous open/create
2. Simultaneous approved-report corrections
3. Edit/delete racing submit
4. Approve racing reject
5. Two unit submissions rebuilding one project day
6. Rebuild racing an override update
"""
from __future__ import annotations

import threading
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReport, DailyReportDerivedSource, ReportShift
from field_reports.services.daily_report_aggregation import rebuild_daily_report_summary
from projects.models import Project, ProjectStatus
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    SubReportStatus,
    UnitReportEventType,
    UnitReportStatusEvent,
)
from sub_reports.unit_report_services import (
    UnitReportError,
    approve_unit_report,
    correct_unit_report,
    open_unit_report,
    reject_unit_report,
    submit_unit_report,
    update_unit_report,
)

User = get_user_model()


@pytest.fixture
def conc_user(db):
    u, _ = User.objects.get_or_create(
        username='cuser_preparer',
        defaults={'mobile': '+989129990001', 'full_name': 'Conc Preparer'},
    )
    u.set_password('testpass123')
    u.save()
    return u


@pytest.fixture
def conc_reviewer(db):
    u, _ = User.objects.get_or_create(
        username='cuser_reviewer',
        defaults={'mobile': '+989129990002', 'full_name': 'Conc Reviewer'},
    )
    u.set_password('testpass123')
    u.save()
    return u


@pytest.fixture
def conc_project(db, conc_user):
    p, _ = Project.objects.get_or_create(
        project_code='PRJ-CONC-001',
        defaults={
            'project_name': 'Concurrency Test Project',
            'employer': 'Employer Co',
            'start_date': '2024-01-01',
            'status': ProjectStatus.ACTIVE,
            'project_manager': conc_user,
        },
    )
    return p


def _run_in_threads(*targets):
    """Run targets in separate OS threads with clean database connections."""
    errors = []
    results = [None] * len(targets)

    def worker(idx, fn):
        connection.close()
        try:
            results[idx] = fn()
        except Exception as exc:
            errors.append(exc)
        finally:
            connection.close()

    threads = [
        threading.Thread(target=worker, args=(i, target))
        for i, target in enumerate(targets)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=25)
        assert not t.is_alive(), "Worker thread timed out"

    return results, errors


@pytest.mark.django_db(transaction=True)
class TestUnitReportConcurrency:
    """Threaded concurrency tests against real PostgreSQL."""

    def test_concurrent_open_or_create(self, conc_project, conc_user):
        """Simultaneous open/create requests resolve to exactly one current draft."""
        report_date = date(2026, 10, 20)
        barrier = threading.Barrier(2)

        def call_open():
            barrier.wait(timeout=10)
            rep, _ = open_unit_report(
                project=conc_project,
                unit=SpecialtyUnit.BUILDINGS,
                report_date=report_date,
                user=conc_user,
            )
            return rep

        results, errors = _run_in_threads(call_open, call_open)

        assert len(errors) == 0, f"Unexpected errors: {errors}"
        rep1, rep2 = results
        assert rep1.id == rep2.id

        # Database state: exactly one current report, one created status event
        reports = DisciplineSubReport.objects.filter(
            project=conc_project,
            unit=SpecialtyUnit.BUILDINGS,
            report_date=report_date,
            is_current=True,
        )
        assert reports.count() == 1
        created_events = UnitReportStatusEvent.objects.filter(
            report_version_id=rep1.id,
            event_type=UnitReportEventType.CREATED,
        )
        assert created_events.count() == 1

    def test_concurrent_approved_corrections(self, conc_project, conc_user, conc_reviewer):
        """Simultaneous corrections on an approved report: exactly one v2 draft created."""
        report_date = date(2026, 10, 21)
        # Create, submit, approve v1
        v1, _ = open_unit_report(
            project=conc_project,
            unit=SpecialtyUnit.ELECTRICAL,
            report_date=report_date,
            user=conc_user,
        )
        submit_unit_report(v1, user=conc_user, unit=SpecialtyUnit.ELECTRICAL)
        approve_unit_report(v1, user=conc_reviewer, unit=SpecialtyUnit.ELECTRICAL)

        barrier = threading.Barrier(2)

        def call_correct():
            barrier.wait(timeout=10)
            return correct_unit_report(v1, user=conc_user, unit=SpecialtyUnit.ELECTRICAL)

        results, errors = _run_in_threads(call_correct, call_correct)

        successful = [r for r in results if r is not None]
        assert len(successful) == 1
        assert len(errors) == 1
        assert isinstance(errors[0], UnitReportError)

        # DB state: exactly one current report (version 2 draft), v1 is no longer current
        current_reports = DisciplineSubReport.objects.filter(
            project=conc_project,
            unit=SpecialtyUnit.ELECTRICAL,
            report_date=report_date,
            is_current=True,
        )
        assert current_reports.count() == 1
        v2 = current_reports.first()
        assert v2.version_number == 2
        assert v2.status == SubReportStatus.DRAFT

        v1.refresh_from_db()
        assert v1.is_current is False
        assert v1.status == SubReportStatus.APPROVED

    def test_edit_or_delete_racing_submit(self, conc_project, conc_user):
        """Submit racing edit: result is valid and consistent; submitted report is immutable."""
        report_date = date(2026, 10, 22)
        report, _ = open_unit_report(
            project=conc_project,
            unit=SpecialtyUnit.MECHANICAL,
            report_date=report_date,
            user=conc_user,
        )

        barrier = threading.Barrier(2)

        def call_edit():
            barrier.wait(timeout=10)
            return update_unit_report(
                report,
                user=conc_user,
                unit=SpecialtyUnit.MECHANICAL,
                validated_fields={'weather_condition': 'rainy'},
            )

        def call_submit():
            barrier.wait(timeout=10)
            return submit_unit_report(
                report,
                user=conc_user,
                unit=SpecialtyUnit.MECHANICAL,
            )

        results, errors = _run_in_threads(call_edit, call_submit)

        report.refresh_from_db()
        assert report.status == SubReportStatus.SUBMITTED
        # Content remains immutable once submitted
        with pytest.raises(UnitReportError):
            update_unit_report(
                report,
                user=conc_user,
                unit=SpecialtyUnit.MECHANICAL,
                validated_fields={'weather_condition': 'sunny'},
            )

    def test_approve_racing_reject(self, conc_project, conc_user, conc_reviewer):
        """Approve racing reject: exactly one transition succeeds, report never in contradictory state."""
        report_date = date(2026, 10, 23)
        report, _ = open_unit_report(
            project=conc_project,
            unit=SpecialtyUnit.MACHINERY,
            report_date=report_date,
            user=conc_user,
        )
        submit_unit_report(report, user=conc_user, unit=SpecialtyUnit.MACHINERY)

        reviewer2, _ = User.objects.get_or_create(
            username='cuser_reviewer2',
            defaults={'mobile': '+989129990003', 'full_name': 'Reviewer 2'},
        )

        barrier = threading.Barrier(2)

        def call_approve():
            barrier.wait(timeout=10)
            return approve_unit_report(
                report,
                user=conc_reviewer,
                unit=SpecialtyUnit.MACHINERY,
            )

        def call_reject():
            barrier.wait(timeout=10)
            return reject_unit_report(
                report,
                user=reviewer2,
                rejection_reason='Needs revisions',
                unit=SpecialtyUnit.MACHINERY,
            )

        results, errors = _run_in_threads(call_approve, call_reject)

        successful = [r for r in results if r is not None]
        assert len(successful) == 1
        assert len(errors) == 1
        assert isinstance(errors[0], UnitReportError)

        report.refresh_from_db()
        assert report.status in (SubReportStatus.APPROVED, SubReportStatus.REJECTED)

    def test_two_unit_submissions_rebuilding_one_day(self, conc_project, conc_user):
        """Two unit submissions rebuilding the same project day: exactly one DailyReport and no duplicate rows."""
        report_date = date(2026, 10, 24)

        bld, _ = open_unit_report(
            project=conc_project,
            unit=SpecialtyUnit.BUILDINGS,
            report_date=report_date,
            user=conc_user,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=bld,
            row_number=1,
            shift='shift_1',
            crew_name='Bld Crew',
            worker_count=5,
            activity_description='Foundation excavation',
        )

        elec, _ = open_unit_report(
            project=conc_project,
            unit=SpecialtyUnit.ELECTRICAL,
            report_date=report_date,
            user=conc_user,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=elec,
            row_number=1,
            shift='shift_1',
            crew_name='Elec Crew',
            worker_count=3,
            activity_description='Conduit wiring',
        )

        barrier = threading.Barrier(2)

        def submit_bld():
            barrier.wait(timeout=10)
            return submit_unit_report(bld, user=conc_user, unit=SpecialtyUnit.BUILDINGS)

        def submit_elec():
            barrier.wait(timeout=10)
            return submit_unit_report(elec, user=conc_user, unit=SpecialtyUnit.ELECTRICAL)

        results, errors = _run_in_threads(submit_bld, submit_elec)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        # In DB: exactly one DailyReport for this project and date
        daily_reports = DailyReport.objects.filter(
            project=conc_project,
            report_date=report_date,
            shift=ReportShift.FULL,
        )
        assert daily_reports.count() == 1
        daily_report = daily_reports.first()

        derived_sources = DailyReportDerivedSource.objects.filter(
            source_report_id_snapshot__in=[bld.id, elec.id]
        )
        assert derived_sources.count() == 2
        assert daily_report.activities.count() == 2

    def test_rebuild_racing_override_update(self, conc_project, conc_user):
        """Rebuild racing override update: management opinion and weather overrides survive."""
        report_date = date(2026, 10, 25)

        summary = rebuild_daily_report_summary(
            project_id=conc_project.id,
            report_date=report_date,
            user=conc_user,
        )
        summary.management_opinion = 'Preserve this management opinion'
        summary.weather_override = True
        summary.weather_condition = 'rainy'
        summary.save(update_fields=['management_opinion', 'weather_override', 'weather_condition'])

        barrier = threading.Barrier(2)

        def call_rebuild():
            barrier.wait(timeout=10)
            return rebuild_daily_report_summary(
                project_id=conc_project.id,
                report_date=report_date,
                user=conc_user,
            )

        def call_update_override():
            barrier.wait(timeout=10)
            summary_ref = DailyReport.objects.get(id=summary.id)
            summary_ref.management_opinion = 'Updated opinion during race'
            summary_ref.save(update_fields=['management_opinion'])
            return summary_ref

        results, errors = _run_in_threads(call_rebuild, call_update_override)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

        summary.refresh_from_db()
        assert summary.management_opinion in (
            'Preserve this management opinion',
            'Updated opinion during race',
        )
        assert summary.management_opinion != ''
        assert summary.weather_override is True
        assert summary.weather_condition == 'rainy'

    def test_approve_and_sync_keep_the_locked_row(self, conc_project, conc_user, conc_reviewer):
        """Approve and a sync write share the parent lock. The sync cannot change the row."""
        from uuid import uuid4

        from sub_reports.services.offline_sync import dispatch_operations

        conc_user.is_superuser = True
        conc_user.save(update_fields=['is_superuser'])
        report = DisciplineSubReport.objects.create(
            project=conc_project, unit=SpecialtyUnit.BUILDINGS, discipline='civil',
            report_date=date(2026, 10, 21), status=SubReportStatus.SUBMITTED, is_current=True,
            created_by=conc_user, submitted_by=conc_user, lineage_id=uuid4(), version_number=1,
        )
        row = DisciplineSubReportActivity.objects.create(
            sub_report=report, row_number=1, shift='shift_1', crew_name='Crew',
            activity_description='original',
        )
        barrier = threading.Barrier(2)

        def do_approve():
            barrier.wait(timeout=10)
            return approve_unit_report(report, user=conc_reviewer)

        def do_sync():
            barrier.wait(timeout=10)
            return dispatch_operations(project=conc_project, actor=conc_user, body={
                'contract_version': 2,
                'operations': [{
                    'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
                    'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-21', 'report_id': str(report.id)},
                    'action': 'update',
                    'target': {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': str(row.id)},
                    'base_revision': None, 'depends_on': [],
                    'payload': {'activity_description': 'raced'},
                }],
            })

        results, errors = _run_in_threads(do_approve, do_sync)
        assert errors == [], errors
        report.refresh_from_db()
        row.refresh_from_db()
        assert report.status == SubReportStatus.APPROVED
        assert row.activity_description == 'original'
        assert results[1]['results'][0]['outcome'] == 'conflict'
        assert results[1]['results'][0]['status'] == 'sync_conflict'
        assert UnitReportStatusEvent.objects.filter(report_version=report, event_type=UnitReportEventType.APPROVED).exists()
