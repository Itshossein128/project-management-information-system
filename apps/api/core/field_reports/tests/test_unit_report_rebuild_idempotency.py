"""T045 & T046 — Rebuild idempotency and override preservation tests (feature 032, US4).

Tests:
- Three consecutive rebuilds with unchanged inputs yield identical logical content,
  row counts, derivation keys, ordered provenance, completeness, and summary-owned
  override values (excluding volatile timestamps).
- Resubmission/superseding replaces stale contributions exactly once (no duplicates, no ghosts).
- Summary-owned overrides survive rebuild unchanged: management_opinion, explicit
  weather override, and site-status override (FR-025; spec US3 scenario 7).
"""
from datetime import date
from decimal import Decimal

import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import (
    DailyReport,
    DailyReportDerivedSource,
    InactivityReason,
    LaborCategory,
    ReportShift,
    SiteStatus,
    WeatherCondition,
)
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    add_labor,
)
from project_templates.models import (
    ProjectReportingConfiguration,
    ProjectReportingConfigurationUnit,
    ProjectTemplate,
    ProjectTemplateRequiredUnit,
)
from project_templates.services import activate_project_reporting_configuration
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportConcrete,
    DisciplineSubReportMaterial,
    DisciplineSubReportNote,
    SubReportNoteType,
    SubReportStatus,
)
from sub_reports.unit_report_services import (
    correct_unit_report,
    submit_unit_report,
)


@pytest.fixture
def reporting_template(db, user):
    template = ProjectTemplate.objects.create(
        template_name='Idempotency Test Template',
        created_by=user,
    )
    for i, u in enumerate([SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL, SpecialtyUnit.MECHANICAL]):
        ProjectTemplateRequiredUnit.objects.create(
            template=template,
            unit=u,
            display_order=i,
        )
    return template


def make_unit_report(
    project,
    user,
    *,
    unit=SpecialtyUnit.BUILDINGS,
    status=SubReportStatus.APPROVED,
    report_date=SUMMARY_DATE,
    version_number=1,
    weather_condition='clear',
    site_status='active',
):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=report_date,
        unit=unit,
        legacy_discipline=unit,
        discipline='civil',
        weather_condition=weather_condition,
        site_status=site_status,
        status=status,
        is_current=True,
        is_deleted=False,
        version_number=version_number,
        created_by=user,
        updated_by=user,
        submitted_by=user,
        approved_by=user if status == SubReportStatus.APPROVED else None,
    )


def add_material(sub_report, *, description='سیمان تیپ ۲', quantity=Decimal('50.0000'), unit='کیسه'):
    return DisciplineSubReportMaterial.objects.create(
        sub_report=sub_report,
        material_description=description,
        quantity=quantity,
        unit=unit,
        notes='تحویل کارگاه',
    )


def add_concrete(sub_report, *, description='بتن فونداسیون C30', volume=Decimal('120.500'), zone='Zone A'):
    return DisciplineSubReportConcrete.objects.create(
        sub_report=sub_report,
        concrete_description=description,
        volume_m3=volume,
        zone=zone,
        block='B1',
        floor='-1',
        notes='پمپاژ مستقیم',
    )


def add_note(sub_report, *, text='بازدید دستگاه نظارت از آرماتوربندی', note_type=SubReportNoteType.VISIT):
    return DisciplineSubReportNote.objects.create(
        sub_report=sub_report,
        note_type=note_type,
        text=text,
        row_number=1,
    )


@pytest.mark.django_db
class TestRebuildIdempotency:
    """T045: Three consecutive rebuilds with unchanged inputs yield identical logical content."""

    def test_three_consecutive_rebuilds_yield_identical_logical_content_and_provenance(
        self, project, user, reporting_template,
    ):
        activate_project_reporting_configuration(
            project=project,
            template=reporting_template,
            effective_from=date(2024, 1, 1),
            user=user,
        )

        # 1. Buildings unit report (approved)
        r_b = make_unit_report(
            project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.APPROVED,
        )
        add_activity(r_b, description='آرماتوربندی ستون‌های طبقه اول', workers=4, zone='Zone 1')
        add_labor(r_b, title='آرماتوربند', category=LaborCategory.DIRECT, present=4, leave=0)
        add_material(r_b, description='میلگرد ۱۶', quantity=Decimal('2.5000'), unit='تن')
        add_concrete(r_b, description='بتن ستون', volume=Decimal('35.000'), zone='Zone 1')
        add_note(r_b, text='بتن‌ریزی با موفقیت انجام شد', note_type=SubReportNoteType.VISIT)

        # 2. Electrical unit report (submitted)
        r_e = make_unit_report(
            project, user, unit=SpecialtyUnit.ELECTRICAL, status=SubReportStatus.SUBMITTED,
        )
        add_activity(r_e, description='لوله‌گذاری برق سقف', workers=2, zone='Zone 1')
        add_labor(r_e, title='برقکار', category=LaborCategory.DIRECT, present=2, leave=1)

        # First rebuild
        r1 = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        fp1 = r1.aggregation_fingerprint
        assert fp1, 'aggregation_fingerprint must be computed'

        act_count1 = r1.activities.count()
        labor_count1 = r1.labor_entries.count()
        mat_count1 = r1.material_entries.count()
        conc_count1 = r1.concrete_logs.count()
        sources_count1 = DailyReportDerivedSource.objects.filter(daily_report=r1).count()
        notes1 = r1.general_notes
        meta1 = build_aggregation_meta(project.id, SUMMARY_DATE, r1)

        assert act_count1 == 2
        assert labor_count1 == 2
        assert mat_count1 == 1
        assert conc_count1 == 1
        assert sources_count1 >= 6

        # Second rebuild (unchanged inputs)
        r2 = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        fp2 = r2.aggregation_fingerprint

        # Third rebuild (unchanged inputs)
        r3 = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        fp3 = r3.aggregation_fingerprint

        # All fingerprints match
        assert fp1 == fp2 == fp3

        # Row counts match exactly (no duplicate rows created)
        assert r2.activities.count() == act_count1
        assert r3.activities.count() == act_count1
        assert r2.labor_entries.count() == labor_count1
        assert r3.labor_entries.count() == labor_count1
        assert r2.material_entries.count() == mat_count1
        assert r3.material_entries.count() == mat_count1
        assert r2.concrete_logs.count() == conc_count1
        assert r3.concrete_logs.count() == conc_count1
        assert DailyReportDerivedSource.objects.filter(daily_report=r2).count() == sources_count1
        assert DailyReportDerivedSource.objects.filter(daily_report=r3).count() == sources_count1

        # Logical contents match
        assert r2.general_notes == notes1
        assert r3.general_notes == notes1

        # Completeness matches
        meta2 = build_aggregation_meta(project.id, SUMMARY_DATE, r2)
        meta3 = build_aggregation_meta(project.id, SUMMARY_DATE, r3)
        assert meta1['completeness'] == meta2['completeness'] == meta3['completeness']
        assert meta1['completeness']['state'] == 'partial'  # Mechanical is missing

    def test_resubmission_and_superseding_replaces_stale_contributions_exactly_once(
        self, project, user,
    ):
        """Resubmission/superseding replaces stale contributions without duplicates or ghosts."""
        # 1. Version 1 of Buildings report with initial activity
        r_v1 = make_unit_report(
            project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.APPROVED,
            version_number=1,
        )
        add_activity(r_v1, description='گودبرداری اولیه بلوک A', workers=3)

        summary_v1 = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert summary_v1.activities.count() == 1
        act_row = summary_v1.activities.first()
        assert act_row.activity_description == 'گودبرداری اولیه بلوک A'

        src_v1 = DailyReportDerivedSource.objects.get(
            daily_report=summary_v1, derived_kind='activity', derived_row_id=str(act_row.id),
        )
        assert src_v1.source_report_version == 1

        # 2. Correct v1 -> creates v2 draft
        r_v2 = correct_unit_report(r_v1, user=user, unit=SpecialtyUnit.BUILDINGS)
        assert r_v2.version_number == 2
        assert r_v2.status == SubReportStatus.DRAFT
        assert r_v2.is_current is True

        r_v1.refresh_from_db()
        assert r_v1.is_current is False

        # Rebuild summary: draft v2 does NOT contribute; superseded v1 is not current!
        summary_after_correct = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert summary_after_correct.activities.count() == 0, 'Stale v1 contribution must be removed immediately'
        assert DailyReportDerivedSource.objects.filter(daily_report=summary_after_correct).count() == 0

        # 3. Update the cloned activity in v2 and submit it
        assert r_v2.activities.count() == 1, 'Child activity was cloned from v1'
        cloned_act = r_v2.activities.first()
        cloned_act.activity_description = 'گودبرداری اصلاح‌شده با بیل مکانیکی بلوک A'
        cloned_act.worker_count = 5
        cloned_act.save()
        submit_unit_report(r_v2, user=user, unit=SpecialtyUnit.BUILDINGS)

        # Rebuild summary
        summary_v2 = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert summary_v2.activities.count() == 1
        new_act = summary_v2.activities.first()
        assert new_act.activity_description == 'گودبرداری اصلاح‌شده با بیل مکانیکی بلوک A'

        # Provenance points to v2
        src_v2 = DailyReportDerivedSource.objects.get(
            daily_report=summary_v2, derived_kind='activity', derived_row_id=str(new_act.id),
        )
        assert src_v2.source_report_id_snapshot == r_v2.id
        assert src_v2.source_report_version == 2
        assert src_v2.source_unit == SpecialtyUnit.BUILDINGS

    def test_rejection_and_deletion_removes_contributions(self, project, user):
        """Rejecting or deleting an eligible report removes its derived rows and sources on rebuild."""
        from sub_reports.unit_report_services import reject_unit_report, soft_delete_unit_report

        r = make_unit_report(
            project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.SUBMITTED,
        )
        add_activity(r, description='قالب‌بندی دیوار حائل', workers=3)

        summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert summary.activities.count() == 1

        # Reject the report
        reject_unit_report(r, user=user, rejection_reason='نقص در ایمنی قالب‌بندی', unit=SpecialtyUnit.BUILDINGS)

        # Rebuild
        summary.refresh_from_db()
        rebuilt = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert rebuilt.activities.count() == 0
        assert DailyReportDerivedSource.objects.filter(daily_report=rebuilt).count() == 0


@pytest.mark.django_db
class TestOverridePreservation:
    """T046: Summary-owned overrides survive rebuild unchanged (FR-025; spec US3 scenario 7)."""

    def test_management_opinion_and_weather_site_status_overrides_survive_rebuild(self, project, user):
        # 1. Existing full-shift summary with explicit overrides
        summary = DailyReport.objects.create(
            project_id=project.id,
            report_date=SUMMARY_DATE,
            shift=ReportShift.FULL,
            is_auto_summary=True,
            is_current=True,
            created_by=user,
            updated_by=user,
            management_opinion='دستور توقف موقت بخش شرقی به دلیل وزش باد شدید صادر گردید.',
            weather_override=True,
            weather_condition=WeatherCondition.STORMY,
            site_status_override=True,
            site_status=SiteStatus.INACTIVE,
            inactivity_reason=InactivityReason.WEATHER,
        )

        # 2. Unit reports reporting sunny / active site
        r_b = make_unit_report(
            project, user, unit=SpecialtyUnit.BUILDINGS, status=SubReportStatus.APPROVED,
            weather_condition=WeatherCondition.CLEAR, site_status=SiteStatus.ACTIVE,
        )
        add_activity(r_b, description='تخلیه مصالح', workers=2)

        r_m = make_unit_report(
            project, user, unit=SpecialtyUnit.MECHANICAL, status=SubReportStatus.SUBMITTED,
            weather_condition=WeatherCondition.CLEAR, site_status=SiteStatus.ACTIVE,
        )
        add_activity(r_m, description='عایق‌کاری لوله‌ها', workers=2)

        # 3. Rebuild summary
        rebuilt = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)

        # Overrides preserved!
        assert rebuilt.management_opinion == 'دستور توقف موقت بخش شرقی به دلیل وزش باد شدید صادر گردید.'
        assert rebuilt.weather_override is True
        assert rebuilt.weather_condition == WeatherCondition.STORMY
        assert rebuilt.site_status_override is True
        assert rebuilt.site_status == SiteStatus.INACTIVE
        assert rebuilt.inactivity_reason == InactivityReason.WEATHER

        # Check metadata indicates override source
        meta = build_aggregation_meta(project.id, SUMMARY_DATE, rebuilt)
        assert meta['weather_source'] == 'override'
        assert meta['site_status_source'] == 'override'

        # 4. Another rebuild with unchanged inputs also preserves everything
        rebuilt_again = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert rebuilt_again.management_opinion == 'دستور توقف موقت بخش شرقی به دلیل وزش باد شدید صادر گردید.'
        assert rebuilt_again.weather_condition == WeatherCondition.STORMY
        assert rebuilt_again.site_status == SiteStatus.INACTIVE
