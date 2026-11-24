"""B04 regression tests for the reporting selection and its consumers."""
from datetime import date

import pytest

from field_reports.models import DailyReport, DailyReportActivity, ReportStatus
from projects.models import Stakeholder
from projects.services import create_project_with_creator


pytestmark = pytest.mark.django_db
DAY = date(2027, 5, 22)


@pytest.fixture
def contractor(project, user):
    return Stakeholder.objects.create(project=project, name='Contractor A', role='contractor', created_by=user)


def daily_report(project, user, day=DAY, **overrides):
    fields = {'status': ReportStatus.APPROVED, **overrides}
    return DailyReport.objects.create(project=project, created_by=user, report_date=day, **fields)


def activity_row(report, contractor=None, **overrides):
    fields = {
        'source_discipline': 'CIVIL', 'block': 'Block 1', 'shift': 'shift_1',
        'activity_description': 'B04 reference activity', **overrides,
    }
    return DailyReportActivity.objects.create(report=report, contractor_ref=contractor, **fields)


def test_daily_filters_require_one_eligible_row_on_the_selected_version(auth_client, project, user, contractor):
    matching = daily_report(project, user)
    split = daily_report(project, user, date(2027, 5, 23))
    deleted = daily_report(project, user, date(2027, 5, 24))
    historical = daily_report(project, user, is_current=False, lineage_id=matching.lineage_id)
    activity_row(matching, contractor)
    activity_row(matching, contractor)
    activity_row(split, contractor, block='Block 2')
    activity_row(split)
    activity_row(deleted, contractor, is_deleted=True)
    activity_row(historical, contractor)
    url = f'/api/v1/projects/{project.pk}/daily-reports/'
    combined = {'discipline': 'civil', 'contractor': contractor.pk, 'block': 'Block 1'}

    def get_ids(params):
        response = auth_client.get(url, params)
        assert response.status_code == 200, response.data
        ids = [row['report_id'] for row in response.data['results']]
        assert response.data['count'] == len(ids)
        return ids

    assert get_ids(combined) == [str(matching.pk)]
    assert get_ids({**combined, 'is_current': 'false'}) == [str(historical.pk)]
    assert get_ids({'block': 'Block 1'}) == [str(split.pk), str(matching.pk)]
    assert get_ids({'contractor': contractor.pk}) == [str(split.pk), str(matching.pk)]
    assert get_ids({'discipline': 'CIVIL'}) == [str(split.pk), str(matching.pk)]
    assert get_ids({'date_from': '2027-05-23', 'status': 'approved'}) == [str(deleted.pk), str(split.pk)]
    assert get_ids({'date_to': '2027-05-22', 'status': 'draft'}) == []


def test_daily_filter_foreign_identity_cannot_broaden_selection(auth_client, project, user, other_user):
    report = daily_report(project, user)
    activity_row(report)
    other = create_project_with_creator(
        creator=other_user, project_code='B04-FOREIGN', project_name='B04 foreign',
        employer='Employer', start_date=DAY,
    )
    foreign = Stakeholder.objects.create(project=other, name='Foreign contractor', created_by=other_user)
    url = f'/api/v1/projects/{project.pk}/daily-reports/'
    for identity in (foreign.pk, 'invalid-id'):
        response = auth_client.get(url, {'contractor': identity})
        assert response.status_code == 400 or (
            response.status_code == 200 and response.data['count'] == 0
        )


def test_activity_selection_is_shared_and_preserves_version_policy(
    auth_client, project, user, contractor, activity,
):
    from io import BytesIO
    from openpyxl import load_workbook

    other_contractor = Stakeholder.objects.create(project=project, name='Contractor A', created_by=user)
    approved = daily_report(project, user)
    expected = [
        activity_row(
            approved, contractor, activity_description=f'Expected work {index}', parcel=parcel,
            location_detail='Axis 1', zone='Zone 1', floor='Ground', headcount=1,
            quantity=2, unit='m²', activity_ref=activity,
        )
        for index, parcel in enumerate(('P1', 'P2'))
    ]
    activity_row(approved, other_contractor, activity_description='Other identity', parcel='P1', headcount=1)
    activity_row(approved, contractor, activity_description='Deleted', is_deleted=True)
    historical = daily_report(project, user, is_current=False, lineage_id=approved.lineage_id)
    activity_row(historical, contractor, activity_description='Historical')
    preview = daily_report(project, user, date(2027, 5, 23), status=ReportStatus.SUBMITTED)
    preview_row = activity_row(preview, contractor, activity_description='Preview')
    url = f'/api/v1/projects/{project.pk}/activity-log/'
    selection = {
        'source_discipline': 'electrical, civil', 'discipline': 'mechanical', 'parcel': 'p1,P2',
        'contractor_id': contractor.pk, 'status': 'approved', 'block': 'Block 1', 'zone': 'Zone 1',
        'floor': 'Ground', 'shift': 'shift_1', 'location': 'axis', 'q': activity.activity_code,
        'headcount': '1', 'quantity': '2.0000', 'unit': 'm²', 'report_id': approved.pk,
    }
    expected.sort(key=lambda row: row.pk)
    for number in (1, 2):
        params = {**selection, 'page': number, 'page_size': 1}
        response = auth_client.get(url, params)
        assert response.status_code == 200, response.data
        assert response.data['count'] == 2
        assert [row['id'] for row in response.data['results']] == [str(expected[number - 1].pk)]
        assert response.data['results'][0]['contractor_id'] == str(contractor.pk)
        download = auth_client.get(url + 'excel/', params)
        assert download.status_code == 200
        sheet = load_workbook(BytesIO(download.content), data_only=False).active
        assert [sheet[f'C{row}'].value for row in (2, 3)] == [record.activity_description for record in expected]
        assert [sheet.cell(2, col).value for col in range(5, 13)] == [
            'Contractor A', 1, expected[0].parcel, 'Block 1', 'Ground', 'Axis 1', 2, 'm²',
        ]
        assert sheet['F4'].value == '=SUM(F2:F3)'

    assert auth_client.get(url, {'status': 'submitted'}).data['count'] == 0
    response = auth_client.get(url, {'status': 'submitted', 'approved_only': 'false'})
    assert [row['id'] for row in response.data['results']] == [str(preview_row.pk)]
    for suffix in ('filters/', 'filter-options/'):
        selection_options = auth_client.get(url + suffix, {'contractor_id': contractor.pk})
        assert selection_options.status_code == 200
        assert selection_options.data['contractors'] == [{'id': str(contractor.pk), 'name': contractor.name}]


def test_activity_list_options_and_export_enforce_scope_before_warm_cache(
    auth_client, project, user, other_user, contractor,
):
    from django.contrib.auth import get_user_model
    from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
    from rest_framework.test import APIClient

    activity_row(daily_report(project, user), contractor)
    other_project = create_project_with_creator(
        creator=other_user, project_code='B04-PYTEST-OTHER', project_name='Other project',
        employer='Employer', start_date=DAY,
    )
    foreign = Stakeholder.objects.create(project=other_project, name='Other scope', created_by=other_user)
    no_reports = get_user_model().objects.create_user(username='b04-pytest-no-reports')
    role = Role.objects.create(role_name='b04-no-report-access')
    RolePermission.objects.create(role=role, permission_codename='view_project')
    member = ProjectMember.objects.create(project=project, user=no_reports, status='active')
    ProjectMemberRole.objects.create(member=member, role=role)
    url = f'/api/v1/projects/{project.pk}/activity-log/'
    selectable = {'contractor_id': contractor.pk}
    assert auth_client.get(url, selectable).data['count'] == 1
    for endpoint in ('', 'filters/', 'filter-options/', 'excel/'):
        assert auth_client.get(url + endpoint, selectable).status_code == 200
        for denied in (other_user, no_reports):
            client = APIClient()
            client.force_authenticate(user=denied)
            assert client.get(url + endpoint, selectable).status_code == 403
        for invalid in (str(foreign.pk), 'invalid-uuid'):
            response = auth_client.get(url + endpoint, {'contractor_id': invalid})
            if response.status_code == 400:
                continue
            assert response.status_code == 200
            if endpoint == '':
                assert response.data['count'] == 0
            elif endpoint != 'excel/':
                assert response.data['contractors'] == []
            else:
                from io import BytesIO
                from openpyxl import load_workbook
                assert load_workbook(BytesIO(response.content)).active['C2'].value is None


def test_whole_selection_totals_reconcile_with_both_file1_downloads(auth_client, project, user, contractor):
    from collections import defaultdict
    from decimal import Decimal
    from io import BytesIO

    from openpyxl import load_workbook
    from field_reports.models import DailyReportLabor

    other = Stakeholder.objects.create(project=project, name='Contractor B', created_by=user)
    report = daily_report(project, user)
    controls = {
        0: (Decimal('0'), 'm²', True),
        1: (None, 'm²', True),
        2: (Decimal('555'), 'm²', False),
        3: (Decimal('777'), None, True),
        4: (None, 'kg', False),
    }
    rows = []
    for index in range(51):
        amount, unit, measured = controls.get(
            index, (Decimal('2.5'), 'm³', True) if index >= 41 else (Decimal('1.25'), 'm²', True),
        )
        rows.append(activity_row(
            report, contractor, activity_description=f'Independent row {index:02d}',
            quantity=amount, unit=unit, quantity_measured=measured, headcount=1,
        ))
    for company in (contractor, other):
        DailyReportLabor.objects.create(
            report=report, contractor_ref=company, labor_category='direct', job_title='Steel fixer', shift_1_count=12,
        )
    activity_row(report, other, headcount=7)
    activity_row(report, contractor, is_deleted=True, headcount=700)
    historical = daily_report(project, user, is_current=False, lineage_id=report.lineage_id)
    activity_row(historical, contractor, headcount=700)
    deleted = daily_report(project, user, date(2027, 5, 23), is_deleted=True)
    activity_row(deleted, contractor, headcount=700)
    ordered = sorted(rows, key=lambda item: item.pk)
    url = f'/api/v1/projects/{project.pk}/activity-log/'
    params = {'contractor_id': contractor.pk, 'page_size': 50}
    for number, slice_ in ((1, ordered[:50]), (2, ordered[50:])):
        response = auth_client.get(url, {**params, 'page': number})
        assert response.status_code == 200, response.data
        assert response.data['count'] == 51
        assert [row['id'] for row in response.data['results']] == [str(row.pk) for row in slice_]
        aggregates = response.data['aggregates']
        assert aggregates['headcount_sum'] == 51
        assert aggregates['unknown_quantity_without_unit_count'] == 1
        grouped = {record['unit']: record for record in aggregates['quantity_by_unit']}
        assert grouped['kg']['total'] is None
        assert (grouped['kg']['measured_count'], grouped['kg']['unknown_count']) == (0, 1)
        assert (grouped['m²']['measured_count'], grouped['m²']['unknown_count']) == (37, 2)
        assert (grouped['m³']['measured_count'], grouped['m³']['unknown_count']) == (10, 0)
        assert Decimal(grouped['m²']['total']) == Decimal('45')
        assert Decimal(grouped['m³']['total']) == Decimal('25')
        for record in response.data['results']:
            if record['id'] == str(rows[0].pk):
                assert record['quantity_measured'] is True and record['quantity'] == 0
            if record['id'] in {str(row.pk) for row in rows[1:5]}:
                assert record['quantity_measured'] is False and record['quantity'] is None

        download = auth_client.get(url + 'excel/', {**params, 'page': number})
        workbook = load_workbook(BytesIO(download.content), data_only=False).active
        assert [workbook[f'C{i}'].value for i in range(2, 53)] == [row.activity_description for row in ordered]
        assert sum(workbook[f'F{i}'].value for i in range(2, 53)) == 51
        assert workbook['F53'].value == '=SUM(F2:F52)'
        totals = defaultdict(Decimal)
        for index in range(2, 53):
            description = workbook[f'C{index}'].value
            cell = workbook[f'K{index}']
            assert cell.value != '*' or description in {row.activity_description for row in rows[1:5]}
            if description == rows[0].activity_description:
                assert cell.value == 0 and cell.data_type == 'n'
            if description in {row.activity_description for row in rows[1:5]}:
                assert cell.value == '*'
            if cell.data_type == 'n':
                totals[workbook[f'L{index}'].value] += Decimal(str(cell.value))
        assert dict(totals) == {'m²': Decimal('45'), 'm³': Decimal('25')}

    empty = auth_client.get(url, {**params, 'q': 'missing'}).data
    assert empty['count'] == 0 and empty['results'] == []
    assert empty['aggregates'] == {
        'headcount_sum': 0, 'quantity_by_unit': [], 'unknown_quantity_without_unit_count': 0,
    }


def test_daily_selection_uses_version_bound_unit_and_department_projections(auth_client, project, user, contractor):
    from common.reporting_units import SpecialtyUnit
    from field_reports.services.daily_report_aggregation import rebuild_daily_report_summary
    from field_reports.tests.daily_report_summary_helpers import add_activity, make_sub_report
    from inventory.models import Department, DepartmentActivityRecord
    from sub_reports.models import SubReportStatus

    parent = daily_report(project, user, status=ReportStatus.DRAFT, is_auto_summary=True)
    unit = make_sub_report(project, user, report_date=DAY, status=SubReportStatus.SUBMITTED)
    unit_row = add_activity(unit)
    unit_row.contractor_ref = contractor
    unit_row.save(update_fields=['contractor_ref'])
    department = make_sub_report(
        project, user, report_date=DAY, status=SubReportStatus.SUBMITTED, unit=SpecialtyUnit.WAREHOUSE,
    )
    department_row = DepartmentActivityRecord.objects.create(
        project=project, unit_report=department, date=DAY, department=Department.WAREHOUSE,
        contractor_ref=contractor, activity_description='Department record', location='Magazine',
    )
    rebuild_daily_report_summary(project.pk, DAY, user=user, report=parent)
    provenance = set(parent.derived_sources.filter(derived_kind='activity').values_list(
        'source_row_kind', 'source_row_id', 'source_report_id_snapshot', 'source_report_version',
    ))
    assert provenance == {
        ('activity', str(unit_row.pk), unit.pk, 1),
        ('department_activity', str(department_row.pk), department.pk, 1),
    }
    url = f'/api/v1/projects/{project.pk}/daily-reports/'
    for discipline, block, expected in (
        (SpecialtyUnit.BUILDINGS, 'B1', 1),
        (SpecialtyUnit.WAREHOUSE, '', 1),
        (SpecialtyUnit.WAREHOUSE, 'B1', 0),
    ):
        response = auth_client.get(url, {'discipline': discipline, 'contractor': contractor.pk, 'block': block})
        assert response.status_code == 200, response.data
        assert response.data['count'] == expected


def test_official_cache_follows_correction_and_cancellation(
    auth_client, project, user, contractor, django_capture_on_commit_callbacks,
):
    from django.core.cache import cache
    from field_reports.services.correction_service import cancel_correction, open_correction

    report = daily_report(project, user)
    activity_row(report, contractor, quantity=2, unit='m²', headcount=1)
    url = f'/api/v1/projects/{project.pk}/activity-log/'
    version = f'activity_log_version:{project.pk}'
    before = cache.get(version)
    initial = auth_client.get(url).data
    assert initial['count'] == 1
    assert initial['aggregates']['headcount_sum'] == 1
    with django_capture_on_commit_callbacks(execute=True):
        correction = open_correction(source_report=report, user=user, reason='B04 verify correction cache visibility')
        assert cache.get(version) == before
    revised = cache.get(version)
    assert revised != before
    assert auth_client.get(url).data['count'] == 0

    with django_capture_on_commit_callbacks(execute=True):
        cancel_correction(correction=correction, user=user)
        assert cache.get(version) == revised
    assert cache.get(version) != revised
    restored = auth_client.get(url).data
    assert restored['count'] == 1
    assert restored['aggregates'] == initial['aggregates']
