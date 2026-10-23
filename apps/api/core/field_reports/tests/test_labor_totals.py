"""Labor aggregation, man-hours calculation, multi-source provenance, and totals (feature 033, task T020)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReportDerivedSource, LaborCategory
from field_reports.serializers import DailyReportDetailSerializer, DailyReportLaborSerializer
from field_reports.services.daily_report_aggregation import (
    compute_aggregation_fingerprint,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import SUMMARY_DATE
from project_templates.models import ProjectTemplate
from project_templates.services import (
    activate_project_reporting_configuration,
    create_labor_catalog,
)
from sub_reports.models import DisciplineSubReport, DisciplineSubReportLabor, SubReportStatus


def make_unit_report(
    project,
    user,
    *,
    unit=SpecialtyUnit.BUILDINGS,
    status=SubReportStatus.SUBMITTED,
    report_date=SUMMARY_DATE,
    version_number=1,
):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=report_date,
        unit=unit,
        legacy_discipline=unit,
        discipline='civil',
        status=status,
        is_current=True,
        is_deleted=False,
        version_number=version_number,
        created_by=user,
        updated_by=user,
        submitted_by=user,
    )


@pytest.fixture
def configured_project(db, project, user):
    template = ProjectTemplate.objects.create(
        template_name='Labor Totals Template',
        project_type='residential',
        is_system=False,
        created_by=user,
    )
    create_labor_catalog(
        template,
        version_name='v1',
        titles=[
            {
                'title_code': 'site_super',
                'title_label': 'Site Superintendent',
                'title_label_fa': 'سرپرست کارگاه',
                'category': 'indirect',
                'display_order': 1,
                'active': True,
                'legacy_alias': 'رئیس کارگاه قدیم',
                'project_specific': False,
            },
            {
                'title_code': 'rebar_worker',
                'title_label': 'Rebar Worker',
                'title_label_fa': 'آرماتوربند',
                'category': 'direct',
                'display_order': 1,
                'active': True,
                'legacy_alias': '',
                'project_specific': False,
            },
            {
                'title_code': 'electrician',
                'title_label': 'Electrician',
                'title_label_fa': 'برقکار',
                'category': 'direct',
                'display_order': 2,
                'active': True,
                'legacy_alias': '',
                'project_specific': False,
            },
        ],
    )
    config = activate_project_reporting_configuration(
        project=project,
        template=template,
        effective_from=date(2024, 6, 1),
        user=user,
    )
    config.standard_shift_hours = Decimal('8.0')
    config.save(update_fields=['standard_shift_hours'])
    return project


@pytest.mark.django_db
class TestLaborAggregationAndTotals:
    def test_multi_source_title_aggregation_retains_both_sources_and_sets_complete(
        self, configured_project, user,
    ):
        r_b = make_unit_report(
            configured_project,
            user,
            unit=SpecialtyUnit.BUILDINGS,
            status=SubReportStatus.APPROVED,
            version_number=1,
        )
        l_b = DisciplineSubReportLabor.objects.create(
            sub_report=r_b,
            labor_category=LaborCategory.DIRECT,
            job_title='آرماتوربند',
            present_count=4,
            leave_count=1,
            overtime_hours=Decimal('2.50'),
        )

        r_m = make_unit_report(
            configured_project,
            user,
            unit=SpecialtyUnit.MECHANICAL,
            status=SubReportStatus.APPROVED,
            version_number=1,
        )
        l_m = DisciplineSubReportLabor.objects.create(
            sub_report=r_m,
            labor_category=LaborCategory.DIRECT,
            job_title='آرماتوربند',
            present_count=3,
            leave_count=0,
            overtime_hours=Decimal('1.50'),
        )

        summary = rebuild_daily_report_summary(
            configured_project.id, SUMMARY_DATE, user=user,
        )
        labor_row = summary.labor_entries.get(
            is_derived=True, labor_category=LaborCategory.DIRECT, job_title='آرماتوربند',
        )
        assert labor_row.total_count == 7
        assert labor_row.shift_1_count == 7
        assert labor_row.absence_count == 1
        assert labor_row.overtime_hours == Decimal('4.00')
        # Man-hours = 7 * 8.0 + 4.00 = 60.00
        assert labor_row.work_hours == Decimal('60.00')
        assert labor_row.source_set_complete is True

        sources = list(
            DailyReportDerivedSource.objects.filter(
                daily_report=summary,
                derived_kind='labor',
                derived_row_id=str(labor_row.id),
            ).order_by('ordinal')
        )
        assert len(sources) == 2
        assert [s.source_unit for s in sources] == [
            SpecialtyUnit.BUILDINGS,
            SpecialtyUnit.MECHANICAL,
        ]
        assert [s.source_row_id for s in sources] == [str(l_b.id), str(l_m.id)]

        # Serialized row exposes source_count > 1 and per_unit_breakdown
        serialized = DailyReportLaborSerializer(labor_row).data
        assert serialized['source_count'] == 2
        assert serialized['has_multiple_sources'] is True
        assert serialized['man_hours'] == '60.00'
        assert serialized['title_code'] == 'rebar_worker'
        assert serialized['display_order'] == 1
        assert len(serialized['per_unit_breakdown']) == 2
        assert [b['source_unit'] for b in serialized['per_unit_breakdown']] == [
            SpecialtyUnit.BUILDINGS,
            SpecialtyUnit.MECHANICAL,
        ]

    def test_man_hours_and_indirect_direct_overall_totals_calculable_and_deterministic(
        self, configured_project, user,
    ):
        r_b = make_unit_report(
            configured_project,
            user,
            unit=SpecialtyUnit.BUILDINGS,
            status=SubReportStatus.APPROVED,
        )
        # Indirect row: 2 present * 8h + 3h overtime = 19.00 man-hours
        DisciplineSubReportLabor.objects.create(
            sub_report=r_b,
            labor_category=LaborCategory.INDIRECT,
            job_title='سرپرست کارگاه',
            present_count=2,
            leave_count=0,
            overtime_hours=Decimal('3.00'),
        )
        # Direct row 1 (Buildings): 5 present * 8h + 2h overtime = 42.00 man-hours
        DisciplineSubReportLabor.objects.create(
            sub_report=r_b,
            labor_category=LaborCategory.DIRECT,
            job_title='آرماتوربند',
            present_count=5,
            leave_count=1,
            overtime_hours=Decimal('2.00'),
        )

        r_e = make_unit_report(
            configured_project,
            user,
            unit=SpecialtyUnit.ELECTRICAL,
            status=SubReportStatus.APPROVED,
        )
        # Direct row 2 (Electrical): 3 present * 8h + 0h overtime = 24.00 man-hours
        DisciplineSubReportLabor.objects.create(
            sub_report=r_e,
            labor_category=LaborCategory.DIRECT,
            job_title='برقکار',
            present_count=3,
            leave_count=1,
            overtime_hours=Decimal('0.00'),
        )

        summary_1 = rebuild_daily_report_summary(
            configured_project.id, SUMMARY_DATE, user=user,
        )
        data_1 = DailyReportDetailSerializer(summary_1).data

        summary_2 = rebuild_daily_report_summary(
            configured_project.id, SUMMARY_DATE, user=user,
        )
        data_2 = DailyReportDetailSerializer(summary_2).data

        assert 'labor_summary' in data_1
        ls = data_1['labor_summary']
        assert len(ls['indirect_summary']) == 1
        assert len(ls['direct_summary']) == 2
        assert len(ls['overall_summary']) == 3

        totals = ls['totals']
        assert totals['indirect_total_count'] == 2
        assert totals['direct_total_count'] == 8
        assert totals['overall_total_count'] == 10
        assert Decimal(str(totals['indirect_man_hours'])) == Decimal('19.00')
        assert Decimal(str(totals['direct_man_hours'])) == Decimal('66.00')
        assert Decimal(str(totals['overall_man_hours'])) == Decimal('85.00')
        assert totals['source_count'] == 3
        assert totals['has_multiple_sources'] is True

        # Determinism across consecutive rebuilds
        assert ls == data_2['labor_summary']

    def test_fingerprint_includes_labor_overtime_and_contractor(
        self, configured_project, user,
    ):
        r_b = make_unit_report(
            configured_project,
            user,
            unit=SpecialtyUnit.BUILDINGS,
            status=SubReportStatus.APPROVED,
        )
        row = DisciplineSubReportLabor.objects.create(
            sub_report=r_b,
            labor_category=LaborCategory.DIRECT,
            job_title='آرماتوربند',
            present_count=4,
            leave_count=0,
            overtime_hours=Decimal('1.00'),
        )
        fp1 = compute_aggregation_fingerprint(None, [r_b])
        row.overtime_hours = Decimal('5.00')
        row.save(update_fields=['overtime_hours'])
        fp2 = compute_aggregation_fingerprint(None, [r_b])
        assert fp1 != fp2
