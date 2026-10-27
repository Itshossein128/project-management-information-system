"""Labor-title catalog versioning, snapshot immutability, resolution order, and project isolation (feature 033, task T019)."""
from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from common.reporting_units import SpecialtyUnit
from master_data.models import Permission, ProjectMember, ProjectMemberRole, Role, RolePermission
from projects.models import Project
from project_templates.models import (
    LaborTitleCatalog,
    LaborTitleCatalogTitle,
    LaborTitleCategory,
    ProjectReportingConfiguration,
    ProjectReportingConfigurationLaborTitle,
    ProjectTemplate,
)
from project_templates.services import (
    activate_project_reporting_configuration,
    create_labor_catalog,
    resolve_labor_title,
)
from sub_reports.models import DisciplineSubReport, DisciplineSubReportLabor, SubReportStatus
from field_reports.services.daily_report_aggregation import resolve_project_reporting_configuration

User = get_user_model()


def _grant_project_permissions(user, project, codenames: list[str]):
    member, _ = ProjectMember.objects.get_or_create(
        project=project, user=user, defaults={'status': 'active'},
    )
    member.status = 'active'
    member.save()
    role, _ = Role.objects.get_or_create(role_name='test_catalog_viewer')
    ProjectMemberRole.objects.get_or_create(member=member, role=role)
    for codename in codenames:
        Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': codename, 'module': 'reports'},
        )
        RolePermission.objects.get_or_create(role=role, permission_codename=codename)


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username='catalog_admin',
        mobile='+989120001901',
        password='testpassword123',
        full_name='Catalog Admin',
    )
    admin_group, _ = Group.objects.get_or_create(name='admin')
    user.groups.add(admin_group)
    return user


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username='regular_member',
        mobile='+989120001902',
        password='testpassword123',
        full_name='Regular Member',
    )


@pytest.fixture
def outsider_user(db):
    return User.objects.create_user(
        username='outsider_user',
        mobile='+989120001903',
        password='testpassword123',
        full_name='Outsider User',
    )


@pytest.fixture
def draft_template(db, admin_user):
    return ProjectTemplate.objects.create(
        template_name='Draft Residential Template',
        project_type='residential',
        is_system=False,
        created_by=admin_user,
    )


@pytest.mark.django_db
class TestLaborCatalogCRUDAndPermissions:
    def test_draft_only_crud_permission_matrix(
        self, draft_template, admin_user, regular_user,
    ):
        anon_client = APIClient()
        reg_client = APIClient()
        reg_client.force_authenticate(user=regular_user)
        admin_client = APIClient()
        admin_client.force_authenticate(user=admin_user)

        base_url = f'/api/v1/project-templates/{draft_template.id}/labor-catalogs/'

        # 1. Unauthenticated -> 401
        assert anon_client.get(base_url).status_code == status.HTTP_401_UNAUTHORIZED
        assert anon_client.post(base_url, {'version_name': 'v1'}, format='json').status_code == status.HTTP_401_UNAUTHORIZED

        # 2. Non-admin -> 403
        assert reg_client.get(base_url).status_code == status.HTTP_403_FORBIDDEN
        assert reg_client.post(base_url, {'version_name': 'v1'}, format='json').status_code == status.HTTP_403_FORBIDDEN

        # 3. Admin creates draft catalog -> 201
        create_resp = admin_client.post(
            base_url,
            {
                'version_name': 'v1-initial',
                'notes': 'Initial draft catalog',
                'titles': [
                    {
                        'title_code': 'site_mgr',
                        'title_label': 'Site Manager',
                        'title_label_fa': 'رئیس کارگاه',
                        'category': 'indirect',
                        'display_order': 1,
                        'active': True,
                        'legacy_alias': 'سرپرست کارگاه قدیم',
                        'project_specific': False,
                    },
                ],
            },
            format='json',
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        catalog_id = create_resp.data['id']
        assert len(create_resp.data['titles']) == 1

        # 4. Title CRUD on draft template
        titles_url = f'{base_url}{catalog_id}/titles/'
        add_title_resp = admin_client.post(
            titles_url,
            {
                'title_code': 'rebar_worker',
                'title_label': 'Rebar Worker',
                'title_label_fa': 'آرماتوربند',
                'category': 'direct',
                'display_order': 1,
                'active': True,
                'project_specific': False,
            },
            format='json',
        )
        assert add_title_resp.status_code == status.HTTP_201_CREATED
        title_id = add_title_resp.data['id']

        # Non-admin denied on title detail
        title_detail_url = f'{titles_url}{title_id}/'
        assert reg_client.patch(title_detail_url, {'display_order': 2}, format='json').status_code == status.HTTP_403_FORBIDDEN
        assert reg_client.delete(title_detail_url).status_code == status.HTTP_403_FORBIDDEN

        # Admin updates and deletes title
        patch_resp = admin_client.patch(title_detail_url, {'display_order': 2}, format='json')
        assert patch_resp.status_code == status.HTTP_200_OK
        assert patch_resp.data['display_order'] == 2

        # Cross-template lookup resolves nothing (404)
        other_template = ProjectTemplate.objects.create(
            template_name='Other Template', is_system=False, created_by=admin_user,
        )
        assert (
            admin_client.get(f'/api/v1/project-templates/{other_template.id}/labor-catalogs/{catalog_id}/').status_code
            == status.HTTP_404_NOT_FOUND
        )

        # System (non-draft) template refuses catalog mutations with 403
        draft_template.is_system = True
        draft_template.save(update_fields=['is_system'])
        assert (
            admin_client.post(base_url, {'version_name': 'v2-blocked'}, format='json').status_code
            == status.HTTP_403_FORBIDDEN
        )
        assert (
            admin_client.patch(title_detail_url, {'display_order': 5}, format='json').status_code
            == status.HTTP_403_FORBIDDEN
        )


@pytest.mark.django_db
class TestLaborCatalogSnapshotAndResolution:
    def test_activation_snapshots_titles_and_display_order_immutably(
        self, project, draft_template, admin_user,
    ):
        catalog = create_labor_catalog(
            draft_template,
            version_name='v1',
            titles=[
                {
                    'title_code': 'carpenter',
                    'title_label': 'Carpenter',
                    'title_label_fa': 'نجار',
                    'category': 'direct',
                    'display_order': 2,
                    'active': True,
                    'legacy_alias': 'قالب‌بند چوبی',
                    'project_specific': False,
                },
                {
                    'title_code': 'welder',
                    'title_label': 'Welder',
                    'title_label_fa': 'جوشکار',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': False,
                },
                {
                    'title_code': 'retired_role',
                    'title_label': 'Retired Role',
                    'title_label_fa': 'نقش غیرفعال',
                    'category': 'direct',
                    'display_order': 3,
                    'active': False,
                    'legacy_alias': '',
                    'project_specific': False,
                },
            ],
        )

        config = activate_project_reporting_configuration(
            project=project,
            template=draft_template,
            effective_from=date(2024, 6, 1),
            user=admin_user,
        )

        snapshot_titles = list(
            config.labor_titles.all().order_by('category', 'display_order', 'title_code')
        )
        # Only active titles are snapshotted, ordered by display_order
        assert [t.title_code for t in snapshot_titles] == ['welder', 'carpenter']
        assert [t.display_order for t in snapshot_titles] == [1, 2]
        assert all(t.source_catalog_version == 'v1' for t in snapshot_titles)

        # Mutating the draft catalog afterwards does NOT alter the activated snapshot
        LaborTitleCatalogTitle.objects.filter(catalog=catalog, title_code='welder').update(
            title_label='Mutated Welder', display_order=99,
        )
        snapshot_titles_after = list(
            config.labor_titles.all().order_by('category', 'display_order', 'title_code')
        )
        assert [t.title_label for t in snapshot_titles_after] == ['Welder', 'Carpenter']
        assert [t.display_order for t in snapshot_titles_after] == [1, 2]

        # Direct mutation of an activated snapshot row is refused
        snap_row = snapshot_titles_after[0]
        snap_row.title_label = 'Tampered Label'
        with pytest.raises(ValidationError):
            snap_row.save()
        with pytest.raises(ValidationError):
            snap_row.delete()

    def test_resolution_order_legacy_alias_then_exact_label_then_project_specific(
        self, project, draft_template, admin_user,
    ):
        create_labor_catalog(
            draft_template,
            version_name='v1-order',
            titles=[
                # 1. Has legacy_alias='SharedName'
                {
                    'title_code': 'from_alias',
                    'title_label': 'Modern Supervisor',
                    'title_label_fa': 'سرپرست مدرن',
                    'category': 'indirect',
                    'display_order': 1,
                    'active': True,
                    'legacy_alias': 'SharedName',
                    'project_specific': False,
                },
                # 2. Has exact title_label='SharedName' (should lose to legacy_alias)
                #    and title_label_fa='عنوان استاندارد'
                {
                    'title_code': 'from_exact',
                    'title_label': 'SharedName',
                    'title_label_fa': 'عنوان استاندارد',
                    'category': 'indirect',
                    'display_order': 2,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': False,
                },
                # 3. Standard exact label vs project-specific title
                {
                    'title_code': 'std_specialist',
                    'title_label': 'OverlapSpecialist',
                    'title_label_fa': 'متخصص استاندارد',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': False,
                },
                {
                    'title_code': 'proj_specialist',
                    'title_label': 'OverlapSpecialist',
                    'title_label_fa': 'متخصص اختصاصی پروژه',
                    'category': 'direct',
                    'display_order': 2,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': True,
                },
                {
                    'title_code': 'tunnel_grouter',
                    'title_label': 'Tunnel Grouter',
                    'title_label_fa': 'تزریق‌کار تونل',
                    'category': 'direct',
                    'display_order': 3,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': True,
                },
            ],
        )
        config = activate_project_reporting_configuration(
            project=project,
            template=draft_template,
            effective_from=date(2024, 6, 1),
            user=admin_user,
        )

        # Priority 1: legacy_alias beats exact title_label
        resolved_1 = resolve_labor_title(config, 'SharedName')
        assert resolved_1 is not None
        assert resolved_1.title_code == 'from_alias'

        # Priority 2: standard exact label beats project-specific title
        resolved_2 = resolve_labor_title(config, 'OverlapSpecialist')
        assert resolved_2 is not None
        assert resolved_2.title_code == 'std_specialist'

        # Priority 3: project-specific title resolves when no alias or standard label matches
        resolved_3 = resolve_labor_title(config, 'تزریق‌کار تونل')
        assert resolved_3 is not None
        assert resolved_3.title_code == 'tunnel_grouter'

        # Unrecognized title returns None
        assert resolve_labor_title(config, 'Completely Unknown Role') is None

    def test_historical_rows_keep_former_evidence_after_catalog_revision(
        self, project, draft_template, admin_user,
    ):
        create_labor_catalog(
            draft_template,
            version_name='v1',
            titles=[
                {
                    'title_code': 'ironworker',
                    'title_label': 'Ironworker V1',
                    'title_label_fa': 'آهنگر قدیم',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': False,
                },
            ],
        )
        config_v1 = activate_project_reporting_configuration(
            project=project,
            template=draft_template,
            effective_from=date(2024, 6, 1),
            user=admin_user,
        )

        report_june = DisciplineSubReport.objects.create(
            project=project,
            report_date=date(2024, 6, 10),
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            status=SubReportStatus.APPROVED,
            created_by=admin_user,
        )
        hist_row = DisciplineSubReportLabor.objects.create(
            sub_report=report_june,
            labor_category='direct',
            job_title='آهنگر قدیم',
            present_count=6,
            leave_count=1,
        )

        # Create catalog v2 that renames and reorders 'ironworker' while keeping legacy_alias
        create_labor_catalog(
            draft_template,
            version_name='v2',
            titles=[
                {
                    'title_code': 'crane_rig',
                    'title_label': 'Crane Rigger',
                    'title_label_fa': 'ریگر جرثقیل',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'legacy_alias': '',
                    'project_specific': True,
                },
                {
                    'title_code': 'ironworker',
                    'title_label': 'Structural Steel Specialist V2',
                    'title_label_fa': 'استادکار اسکلت فلزی',
                    'category': 'direct',
                    'display_order': 2,
                    'active': True,
                    'legacy_alias': 'آهنگر قدیم',
                    'project_specific': False,
                },
            ],
        )
        config_v2 = activate_project_reporting_configuration(
            project=project,
            template=draft_template,
            effective_from=date(2024, 7, 1),
            user=admin_user,
        )

        # Historical row keeps original job_title and resolves against June snapshot
        hist_row.refresh_from_db()
        assert hist_row.job_title == 'آهنگر قدیم'
        eff_june = resolve_project_reporting_configuration(project.id, date(2024, 6, 10))
        assert eff_june.id == config_v1.id
        resolved_june = resolve_labor_title(eff_june, hist_row.job_title)
        assert resolved_june.title_code == 'ironworker'
        assert resolved_june.display_order == 1
        assert resolved_june.source_catalog_version == 'v1'

        # Under July snapshot, the legacy string still resolves via legacy_alias
        resolved_july = resolve_labor_title(config_v2, hist_row.job_title)
        assert resolved_july.title_code == 'ironworker'
        assert resolved_july.display_order == 2
        assert resolved_july.source_catalog_version == 'v2'

    def test_two_projects_get_different_catalogs_and_frustrate_cross_project_reads(
        self, project, admin_user, regular_user, outsider_user,
    ):
        project_b = Project.objects.create(
            project_code='PRJ-CAT-B',
            project_name='Project B',
            employer='Employer B',
        )
        _grant_project_permissions(regular_user, project, ['view_reports'])
        _grant_project_permissions(outsider_user, project_b, ['view_reports'])

        tpl_a = ProjectTemplate.objects.create(
            template_name='Template A', is_system=False, created_by=admin_user,
        )
        create_labor_catalog(
            tpl_a,
            version_name='vA',
            titles=[
                {
                    'title_code': 'mason_a',
                    'title_label': 'Mason A',
                    'title_label_fa': 'بنا پروژه الف',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'project_specific': False,
                },
            ],
        )
        activate_project_reporting_configuration(
            project=project, template=tpl_a, effective_from=date(2024, 6, 1), user=admin_user,
        )

        tpl_b = ProjectTemplate.objects.create(
            template_name='Template B', is_system=False, created_by=admin_user,
        )
        create_labor_catalog(
            tpl_b,
            version_name='vB',
            titles=[
                {
                    'title_code': 'lineman_b',
                    'title_label': 'Lineman B',
                    'title_label_fa': 'سیم‌کش پروژه ب',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'project_specific': True,
                },
            ],
        )
        activate_project_reporting_configuration(
            project=project_b, template=tpl_b, effective_from=date(2024, 6, 1), user=admin_user,
        )

        client_a = APIClient()
        client_a.force_authenticate(user=regular_user)

        resp_a = client_a.get(
            f'/api/v1/projects/{project.id}/reporting-configuration/?date=2024-06-10',
        )
        assert resp_a.status_code == status.HTTP_200_OK
        assert [t['title_code'] for t in resp_a.data['labor_titles']] == ['mason_a']

        # User of Project A cannot read Project B's reporting configuration
        resp_cross = client_a.get(
            f'/api/v1/projects/{project_b.id}/reporting-configuration/?date=2024-06-10',
        )
        assert resp_cross.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_fresh_project_resolves_legacy_catalog_titles(admin_user):
    from projects.services import create_project_with_creator
    from project_templates.models import ProjectTemplate
    from project_templates.services import activate_project_reporting_configuration, resolve_labor_title

    fresh_project = create_project_with_creator(
        creator=admin_user,
        project_code='PRJ-FRESH-CAT',
        project_name='Fresh Project With Default Catalog',
        employer='Employer Co',
        start_date='2024-01-01',
    )
    template = ProjectTemplate.objects.create(
        template_name='Fresh System Template',
        project_type='residential',
        is_system=True,
        created_by=admin_user,
    )
    config = activate_project_reporting_configuration(
        project=fresh_project,
        template=template,
        effective_from=date(2024, 6, 1),
        user=admin_user,
    )
    resolved_0002 = resolve_labor_title(config, 'مهندس عمران')
    assert resolved_0002 is not None
    assert resolved_0002.category == 'indirect'

    resolved_0010 = resolve_labor_title(config, 'مدیرشعبه')
    assert resolved_0010 is not None
    assert resolved_0010.category == 'indirect'
