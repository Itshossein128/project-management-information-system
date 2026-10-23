"""Machinery section contract tests (feature 033, task T026)."""
from __future__ import annotations

from datetime import date

import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import Equipment
from project_templates.models import ProjectReportingConfigurationStoppageReason
from sub_reports.models import DisciplineSubReport, SubReportStatus
from sub_reports.services import section_validation


REPORT_DATE = date(2024, 6, 10)


@pytest.fixture
def unit_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.MACHINERY,
        discipline='civil',
        status=SubReportStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def equipment(project, user):
    return Equipment.objects.create(
        project=project,
        equipment_code='EX-01',
        equipment_name='Excavator 01',
        equipment_type='excavator',
        created_by=user,
    )


@pytest.fixture
def stoppage_vocabulary(project, user):
    from project_templates.models import ProjectReportingConfiguration, ProjectTemplate

    template = ProjectTemplate.objects.create(
        template_name='Machinery contract template', created_by=user,
    )
    config = ProjectReportingConfiguration.objects.create(
        project=project,
        source_template=template,
        effective_from=REPORT_DATE,
        activated_by=user,
    )
    ProjectReportingConfigurationStoppageReason.objects.create(
        configuration=config,
        reason_code='breakdown',
        reason_label='Breakdown',
        reason_label_fa='خرابی',
        display_order=1,
    )
    return config


def _validate(report, rows, configuration):
    """Call the planned T028 boundary so RED failures identify the missing API."""
    validator = getattr(section_validation, 'validate_machinery_rows')
    return validator(report, rows, context={'configuration': configuration})


def _row(**overrides):
    payload = {
        'row_number': 1,
        'equipment_type': 'excavator',
        'status_total': 1,
        'status_active': 1,
        'status_ready': 0,
        'status_inactive': 0,
        'status_under_repair': 0,
        'operating_hours': '8.00',
        'stoppage_hours': '0.00',
        'repair_hours': '0.00',
        'stoppage_reason_code': '',
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
class TestMachinerySectionContract:
    def test_stoppage_reason_required_when_stoppage_gt_zero(
        self, unit_report, stoppage_vocabulary,
    ):
        with pytest.raises(Exception) as excinfo:
            _validate(unit_report, [_row(stoppage_hours='2.00')], stoppage_vocabulary)
        assert 'stoppage_reason_required_when_stoppage_gt_zero' in str(excinfo.value)

    @pytest.mark.parametrize(
        'operating,stoppage,repair',
        [('24.01', '0', '0'), ('8', '8', '8.01')],
    )
    def test_hours_exceed_day_limit(
        self, unit_report, stoppage_vocabulary, operating, stoppage, repair,
    ):
        with pytest.raises(Exception) as excinfo:
            _validate(
                unit_report,
                [_row(
                    operating_hours=operating,
                    stoppage_hours=stoppage,
                    repair_hours=repair,
                )],
                stoppage_vocabulary,
            )
        assert 'hours_exceed_day_limit' in str(excinfo.value)

    def test_hours_limit_is_checked_per_declared_item_identity(
        self, unit_report, stoppage_vocabulary, equipment,
    ):
        with pytest.raises(Exception) as excinfo:
            _validate(
                unit_report,
                [
                    _row(equipment_ref=str(equipment.id), operating_hours='12'),
                    _row(row_number=2, equipment_ref=str(equipment.id), operating_hours='12.01'),
                ],
                stoppage_vocabulary,
            )
        assert 'hours_exceed_day_limit' in str(excinfo.value)

    def test_stoppage_reason_not_in_vocabulary(
        self, unit_report, stoppage_vocabulary,
    ):
        with pytest.raises(Exception) as excinfo:
            _validate(
                unit_report,
                [_row(stoppage_hours='1.00', stoppage_reason_code='free text')],
                stoppage_vocabulary,
            )
        assert 'stoppage_reason_not_in_vocabulary' in str(excinfo.value)

    @pytest.mark.parametrize('field', [
        'status_total', 'status_active', 'status_ready',
        'status_inactive', 'status_under_repair',
    ])
    def test_status_count_must_be_non_negative(
        self, unit_report, stoppage_vocabulary, field,
    ):
        with pytest.raises(Exception) as excinfo:
            _validate(unit_report, [_row(**{field: -1})], stoppage_vocabulary)
        assert 'status_count_must_be_non_negative' in str(excinfo.value)

    def test_mixed_type_and_item_rows_must_have_consistent_status_sums(
        self, unit_report, stoppage_vocabulary, equipment,
    ):
        with pytest.raises(Exception) as excinfo:
            _validate(
                unit_report,
                [
                    _row(status_total=3, status_active=3),
                    _row(
                        row_number=2,
                        equipment_ref=str(equipment.id),
                        status_total=1,
                        status_active=1,
                    ),
                ],
                stoppage_vocabulary,
            )
        assert 'machinery_status_sums_inconsistent' in str(excinfo.value)

    def test_vocabulary_contains_localized_labels(
        self, unit_report, stoppage_vocabulary,
    ):
        result = _validate(unit_report, [], stoppage_vocabulary)
        assert result.vocabulary == [{
            'reason_code': 'breakdown',
            'reason_label': 'Breakdown',
            'reason_label_fa': 'خرابی',
        }]
