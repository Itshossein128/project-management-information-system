from datetime import date
from decimal import Decimal
import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReportDerivedSource, DailyReportLabor, LaborCategory
from field_reports.serializers import DailyReportDetailSerializer
from field_reports.services.daily_report_aggregation import (
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    add_labor,
    add_machinery,
    add_material,
)
from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
from sub_reports.models import DisciplineSubReport, SubReportStatus


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


@pytest.mark.django_db
def test_derived_activity_retains_provenance(project, user):
    r = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=2)
    act = add_activity(r, description='Foundation concrete work')

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    derived_act = summary.activities.get(is_derived=True)

    sources = list(
        DailyReportDerivedSource.objects.filter(
            daily_report=summary,
            derived_kind='activity',
            derived_row_id=str(derived_act.id),
        )
    )
    assert len(sources) == 1
    src = sources[0]
    assert src.source_report == r
    assert src.source_report_id_snapshot == r.id
    assert src.source_report_version == 2
    assert src.source_unit == SpecialtyUnit.BUILDINGS
    assert src.source_row_kind == 'activity'
    assert src.source_row_id == str(act.id)


@pytest.mark.django_db
def test_multi_source_labor_totals_retain_all_contributing_sources(project, user):
    r1 = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=1)
    l1 = add_labor(r1, title='کارگر ساده', present=3, leave=0)

    r2 = make_unit_report(project, user, unit=SpecialtyUnit.ELECTRICAL, version_number=2)
    l2 = add_labor(r2, title='کارگر ساده', present=2, leave=1)

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    labor_row = summary.labor_entries.get(is_derived=True, job_title='کارگر ساده')
    assert labor_row.shift_1_count == 5
    assert labor_row.absence_count == 1

    sources = list(
        DailyReportDerivedSource.objects.filter(
            daily_report=summary,
            derived_kind='labor',
            derived_row_id=str(labor_row.id),
        ).order_by('ordinal')
    )
    assert len(sources) == 2

    # Verify no last-source-wins: both sources are present
    units = [s.source_unit for s in sources]
    assert SpecialtyUnit.BUILDINGS in units
    assert SpecialtyUnit.ELECTRICAL in units

    s_b = next(s for s in sources if s.source_unit == SpecialtyUnit.BUILDINGS)
    assert s_b.source_report_id_snapshot == r1.id
    assert s_b.source_report_version == 1
    assert s_b.source_row_id == str(l1.id)
    assert s_b.source_row_kind == 'labor'
    assert s_b.contribution_value == Decimal('3')

    s_e = next(s for s in sources if s.source_unit == SpecialtyUnit.ELECTRICAL)
    assert s_e.source_report_id_snapshot == r2.id
    assert s_e.source_report_version == 2
    assert s_e.source_row_id == str(l2.id)
    assert s_e.source_row_kind == 'labor'
    assert s_e.contribution_value == Decimal('2')


@pytest.mark.django_db
def test_serialized_provenance_disclosure_and_permissions(project, user):
    member, _ = ProjectMember.objects.get_or_create(project=project, user=user, defaults={'status': 'active'})
    member.status = 'active'
    member.save()
    role, _ = Role.objects.get_or_create(role_name='Reporter')
    RolePermission.objects.get_or_create(role=role, permission_codename='view_reports')
    ProjectMemberRole.objects.get_or_create(member=member, role=role)

    r = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=1)
    act = add_activity(r, description='Inspection task')

    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    # Serialized with user having view_reports
    context = {'request': type('Request', (), {'user': user, 'project_id': project.id})()}
    data = DailyReportDetailSerializer(summary, context=context).data
    act_data = next(a for a in data['activities'] if a['is_derived'])

    assert 'provenance' in act_data
    assert len(act_data['provenance']) == 1
    prov = act_data['provenance'][0]
    assert prov['unit'] == SpecialtyUnit.BUILDINGS
    assert prov['report_id'] == str(r.id)
    assert prov['report_version'] == 1
    assert prov['source_row_kind'] == 'activity'
    assert prov['source_row_id'] == str(act.id)
    assert prov['can_view_source'] is True


class TestSectionProvenance:
    """Provenance contracts for machinery/materials/crew-hours (feature 033, T013).

    Contracts/unit-report-sections-api.md §2: section rows whose values are
    derived disclose source-report/version/row/unit per contibuting row.
    """

    def _reporter(self, project, user):
        member, _ = ProjectMember.objects.get_or_create(
            project=project, user=user, defaults={'status': 'active'},
        )
        member.status = 'active'
        member.save()
        role, _ = Role.objects.get_or_create(role_name='Reporter033')
        RolePermission.objects.get_or_create(role=role, permission_codename='view_reports')
        ProjectMemberRole.objects.get_or_create(member=member, role=role)

    def _request(self, project, user):
        return {'request': type('Request', (), {'user': user, 'project_id': project.id})()}

    @pytest.mark.django_db
    def test_derived_machinery_rows_disclose_sources(self, project, user):
        self._reporter(project, user)
        r1 = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=1)
        r2 = make_unit_report(project, user, unit=SpecialtyUnit.ELECTRICAL, version_number=1)
        m1 = add_machinery(r1, name='Excavator', count=2)
        m2 = add_machinery(r2, name='Excavator', count=1)

        summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        row = next(r for r in summary.machinery_entries.all() if r.is_derived)

        data = DailyReportDetailSerializer(summary, context=self._request(project, user)).data
        assert data['machinery_section'] is not None
        row_data = next(
            r for r in data['machinery_section']['rows'] if r['is_derived'] and r['machinery_name'] == 'Excavator',
        )
        assert row_data['total_count'] == 3
        assert len(row_data['provenance']) == 2
        units = {p['unit'] for p in row_data['provenance']}
        assert units == {SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL}
        for p in row_data['provenance']:
            assert p['report_id'] in {str(r1.id), str(r2.id)}
            assert p['report_version'] == 1
            assert p['source_row_kind'] == 'machinery'
            assert p['source_row_id'] in {str(m1.id), str(m2.id)}
            assert p['can_view_source'] is True

    @pytest.mark.django_db
    def test_derived_material_totals_disclose_sources(self, project, user):
        self._reporter(project, user)
        r1 = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=3)
        r2 = make_unit_report(project, user, unit=SpecialtyUnit.ELECTRICAL, version_number=1)
        add_material(r1, name='سیمان', quantity=120)
        add_material(r2, name='سیمان', quantity=80)

        summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        row = next(r for r in summary.material_entries.all() if r.is_derived)

        data = DailyReportDetailSerializer(summary, context=self._request(project, user)).data
        row_data = next(
            r for r in data['materials_section']['rows'] if r['is_derived'] and r['material_name'] == 'سیمان',
        )
        assert Decimal(str(row_data['total_quantity'])) == Decimal('200')
        prov = {p['source_unit']: p for p in row_data['provenance']}
        assert set(prov) == {SpecialtyUnit.BUILDINGS, SpecialtyUnit.ELECTRICAL}
        b = prov[SpecialtyUnit.BUILDINGS]
        assert b['report_id'] == str(r1.id)
        assert b['report_version'] == 3
        assert b['contribution_value'] is not None

    @pytest.mark.django_db
    def test_derived_crew_hours_disclose_shift_sources(self, project, user):
        self._reporter(project, user)
        r = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=1)
        add_labor(r, title='اسکلت باز', present=6, leave=0)
        add_activity(r, description='بلوک چینی', shift='shift_2', workers=4)

        summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        assert summary.crew_hours_rows is not None
        rows = summary.crew_hours_rows.get('rows', [])
        assert rows, 'crew-hours rows must exist for shift_2 activities'
        row = next(r for r in rows if r.get('is_derived'))

        data = DailyReportDetailSerializer(summary, context=self._request(project, user)).data
        ch_rows = [
            r for r in data['crew_hours_section']['rows']
            if r.get('is_derived') and r.get('shift') == row['shift']
        ]
        assert ch_rows
        for p in ch_rows[0]['provenance']:
            assert p['unit'] == SpecialtyUnit.BUILDINGS
            assert p['report_id'] == str(r.id)
            assert p['source_row_kind'] in ('labor', 'activity')
            assert p['can_view_source'] is True
