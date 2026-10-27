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
)
from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
from projects.models import Stakeholder
from projects.services import create_project_with_creator
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
    """Provenance + full-site-column contracts for the derived activity row
    (feature 033, T013).

    Contracts/unit-report-sections-api.md §1 and daily-summary-sections-api.md
    §1.1/§4: the derived activity row carries the full FR-001 column set, keeps
    crew name and contractor distinct, and discloses source report/version/row
    per contributing row. Cross-project rows never contribute.
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
    def test_derived_activity_row_exposes_full_site_columns(self, project, user):
        """US1 mandatory scenario 1: an approved unit activity appears with all
        required columns and a source link; crew never substituted for contractor.
        """
        self._reporter(project, user)
        contractor = Stakeholder.objects.create(project=project, name='پارسیان', created_by=user)
        r = make_unit_report(
            project, user, unit=SpecialtyUnit.BUILDINGS,
            status=SubReportStatus.APPROVED, version_number=1,
        )
        act = add_activity(
            r, description='بلوک چینی', shift='shift_2', workers=4, foreman=1,
            zone='Z2', parcel='P-7', notes='با جرثقیل',
        )
        act.contractor_ref = contractor
        act.save()

        summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
        derived = summary.activities.get(is_derived=True)

        # FR-001 column set; null-preserving: unknown stays null (never zeroed).
        assert derived.activity_description == 'بلوک چینی'
        assert derived.shift == 'shift_2'  # never silently remapped to shift_1
        assert derived.parcel == 'P-7'
        assert derived.block == 'B1'
        assert derived.floor == '1'
        assert derived.zone == 'Z2'
        assert derived.location_detail is None  # unknown ≠ empty ≠ zero
        assert derived.headcount == 5
        assert derived.foreman_count == 1
        assert derived.worker_count == 4
        assert derived.crew_name == 'Crew'
        assert derived.contractor_ref == contractor
        assert derived.crew_name != derived.contractor_ref.name
        assert derived.notes == 'با جرثقیل'

        # Exactly one provenance row linking back to the source unit row.
        src = DailyReportDerivedSource.objects.get(
            daily_report=summary, derived_kind='activity',
            derived_row_id=str(derived.id),
        )
        assert src.source_report == r
        assert src.source_report_id_snapshot == r.id
        assert src.source_report_version == 1
        assert src.source_unit == SpecialtyUnit.BUILDINGS
        assert src.source_row_kind == 'activity'
        assert src.source_row_id == str(act.id)

        # Serialized view keeps crew/contractor distinct and exposes provenance.
        data = DailyReportDetailSerializer(summary, context=self._request(project, user)).data
        row = next(a for a in data['activities'] if a['is_derived'])
        assert row['crew_name'] == 'Crew'
        assert row['contractor'] == 'پارسیان'
        assert row['headcount'] == 5
        assert row['parcel'] == 'P-7'
        assert row['location'] == 'Z2'
        assert row['notes'] == 'با جرثقیل'
        assert len(row['provenance']) == 1
        assert row['provenance'][0]['source_row_id'] == str(act.id)
        assert row['provenance'][0]['report_id'] == str(r.id)
        assert row['provenance'][0]['can_view_source'] is True

    @pytest.mark.django_db
    def test_cross_project_source_contributes_nothing(self, project, user):
        other = create_project_with_creator(
            creator=user, project_code='PRJ-OTHER', project_name='Other Project',
            employer='Other Employer', start_date='2024-01-01',
        )
        foreign = make_unit_report(other, user, unit=SpecialtyUnit.ELECTRICAL, version_number=1)
        add_activity(foreign, description='Foreign work')

        summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)

        assert list(summary.activities.filter(is_derived=True)) == []
        assert not DailyReportDerivedSource.objects.filter(
            daily_report=summary, source_report_id_snapshot=foreign.id,
        ).exists()


@pytest.mark.django_db
def test_provenance_drilldown_endpoint_enforces_view_reports(project, user, other_user, api_client):
    member, _ = ProjectMember.objects.get_or_create(project=project, user=user, defaults={'status': 'active'})
    member.status = 'active'
    member.save()
    role, _ = Role.objects.get_or_create(role_name='Viewer')
    RolePermission.objects.get_or_create(role=role, permission_codename='view_reports')
    ProjectMemberRole.objects.create(member=member, role=role)

    r = make_unit_report(project, user, unit=SpecialtyUnit.BUILDINGS, version_number=1)
    act = add_activity(r, description='Provenance check')
    summary = rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    derived_act = summary.activities.get(is_derived=True)

    url = f'/api/v1/projects/{project.id}/daily-reports/{summary.id}/provenance/activity/{derived_act.id}/'

    # 1. Authorized user with view_reports gets can_view_source=True and source metadata
    api_client.force_authenticate(user=user)
    res_auth = api_client.get(url)
    assert res_auth.status_code == 200
    rows = res_auth.data['rows']
    assert len(rows) == 1
    assert rows[0]['can_view_source'] is True
    assert rows[0]['source_report'] == str(r.id)
    assert rows[0]['source_row_id'] == str(act.id)
    assert rows[0]['href'] is not None

    # 2. Member without view_reports is rejected by permission check (HTTP 403)
    no_rep_member = ProjectMember.objects.create(project=project, user=other_user, status='active')
    view_proj_role, _ = Role.objects.get_or_create(role_name='ProjectViewerOnly')
    RolePermission.objects.get_or_create(role=view_proj_role, permission_codename='view_project')
    ProjectMemberRole.objects.create(member=no_rep_member, role=view_proj_role)

    api_client.force_authenticate(user=other_user)
    res_unauth = api_client.get(url)
    assert res_unauth.status_code == 403
