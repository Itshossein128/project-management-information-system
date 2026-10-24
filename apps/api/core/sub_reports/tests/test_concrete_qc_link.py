"""Concrete pour contract and sampling → risk.Inspection linkage (feature 033, T040)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReportConcreteLog
from field_reports.services.daily_report_aggregation import rebuild_daily_report_summary
from projects.models import Project, Stakeholder
from risk.models import Inspection
from sub_reports.models import DisciplineSubReport, SamplingState, SubReportStatus
from sub_reports.services.qc_linkage import link_declared_concrete_sampling
from sub_reports.services.section_validation import SectionContractError, validate_concrete_rows

REPORT_DATE = date(2024, 6, 10)


@pytest.fixture
def unit_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        status=SubReportStatus.DRAFT,
        created_by=user,
    )


def _payload(**overrides):
    data = {
        'concrete_description': 'C30 slab',
        'volume_m3': '12.500',
        'structural_element': 'Slab S1',
        'zone': 'A',
        'parcel': 'P1',
        'block': 'B',
        'floor': '2',
        'batching_plant': 'Plant North',
        'truck_delivery_note_number': 'DN-10',
        'lab_sample_code': '',
        'sampling_state': SamplingState.NOT_SAMPLED,
        'test_sheet_count': None,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestConcreteContract:
    @pytest.mark.parametrize('volume', ['0', '-1.5'])
    def test_volume_must_be_positive(self, unit_report, volume):
        with pytest.raises(SectionContractError) as excinfo:
            validate_concrete_rows(unit_report, [_payload(volume_m3=volume)])
        assert VOLUME(excinfo) == ['volume_must_be_positive']

    def test_sampling_requires_test_information(self, unit_report, user):
        rows = validate_concrete_rows(unit_report, [_payload(
            sampling_state=SamplingState.SAMPLING_DECLARED,
            lab_sample_code='',
            test_sheet_count=None,
        )]) if False else None
        with pytest.raises(SectionContractError) as excinfo:
            validate_concrete_rows(unit_report, [_payload(
                sampling_state=SamplingState.SAMPLING_DECLARED,
                lab_sample_code='',
                test_sheet_count=None,
            )])
        assert any(e['code'] == 'sampling_requires_test_information' for e in excinfo.value.errors)
        assert rows is None

    def test_foreign_batching_plant_refused(self, unit_report, user):
        other = Project.objects.create(
            project_code='PRJ-CNC-F',
            project_name='Foreign',
            employer='Employer',
        )
        foreign = Stakeholder.objects.create(
            project=other, name='Foreign Plant', role='contractor', created_by=user,
        )
        with pytest.raises(SectionContractError) as excinfo:
            validate_concrete_rows(unit_report, [_payload(batching_plant=str(foreign.id))])
        assert any(e['code'] == 'reference_not_in_project_scope' for e in excinfo.value.errors)

    def test_declared_sampling_links_inspection_idempotently(self, unit_report, user):
        rows = validate_concrete_rows(unit_report, [_payload(
            sampling_state=SamplingState.SAMPLING_DECLARED,
            lab_sample_code='LAB-9',
            test_sheet_count=2,
        )])
        assert rows[0].qc_inspection_id is None
        link_declared_concrete_sampling(unit_report, user)
        link_declared_concrete_sampling(unit_report, user)
        rows[0].refresh_from_db()
        assert rows[0].qc_inspection_id is not None
        assert Inspection.objects.filter(project_id=unit_report.project_id).count() == 1
        assert rows[0].qc_inspection.project_id == unit_report.project_id

    def test_not_sampled_needs_no_link(self, unit_report, user):
        rows = validate_concrete_rows(unit_report, [_payload()])
        link_declared_concrete_sampling(unit_report, user)
        rows[0].refresh_from_db()
        assert rows[0].qc_inspection_id is None

    def test_derived_concrete_exposes_full_column_set(self, unit_report, user):
        validate_concrete_rows(unit_report, [_payload(
            sampling_state=SamplingState.SAMPLING_DECLARED,
            lab_sample_code='LAB-1',
            test_sheet_count=1,
        )])
        unit_report.status = SubReportStatus.SUBMITTED
        unit_report.save(update_fields=['status'])
        link_declared_concrete_sampling(unit_report, user)
        summary = rebuild_daily_report_summary(unit_report.project_id, REPORT_DATE, user=user)
        derived = DailyReportConcreteLog.objects.get(report=summary, is_derived=True)
        assert derived.batching_plant == 'Plant North'
        assert derived.truck_delivery_note_number == 'DN-10'
        assert derived.lab_sample_code == 'LAB-1'
        assert derived.sampling_state == SamplingState.SAMPLING_DECLARED
        assert derived.test_sheet_count == 1
        assert derived.qc_inspection_id is not None
        assert derived.volume_m3 == Decimal('12.500')


def VOLUME(excinfo):
    return excinfo.value.field_errors('volume_m3')
