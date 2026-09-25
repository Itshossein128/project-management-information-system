import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from procurement.models import Block, RequisitionHeader, RequisitionScope, RequisitionStatus
from procurement.permissions import ProcurementStepPermission, has_procurement_step_role
from procurement.services.approval_engine import get_required_role
from procurement.services.workshop_block_service import ensure_workshop_block
from projects.models import Project

User = get_user_model()


@pytest.mark.django_db
class TestHasProcurementStepRole:
    def test_superuser_has_role(self, db):
        superuser = User.objects.create_superuser(username='admin_user', password='pass')
        assert has_procurement_step_role(superuser, None, 'block_engineer') is True

    def test_staff_has_role(self, db):
        staff = User.objects.create_user(username='staff_user', password='pass', is_staff=True)
        assert has_procurement_step_role(staff, None, 'block_engineer') is True

    def test_admin_group_has_role(self, db):
        user = User.objects.create_user(username='admin_grp', password='pass')
        admin_group, _ = Group.objects.get_or_create(name='admin')
        user.groups.add(admin_group)
        assert has_procurement_step_role(user, None, 'block_engineer') is True

    def test_django_group_role_match(self, db):
        user = User.objects.create_user(username='eng_user', password='pass')
        group, _ = Group.objects.get_or_create(name='block_engineer')
        user.groups.add(group)
        assert has_procurement_step_role(user, None, 'block_engineer') is True
        assert has_procurement_step_role(user, None, 'technical_office') is False

    def test_project_member_role_match(self, db):
        user = User.objects.create_user(username='pm_user', password='pass')
        project = Project.objects.create(project_name='Test Project', project_code='TP-1')
        role, _ = Role.objects.get_or_create(role_name='technical_office')
        
        member = ProjectMember.objects.create(
            project=project,
            user=user,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=role)

        assert has_procurement_step_role(user, str(project.id), 'technical_office') is True
        assert has_procurement_step_role(user, str(project.id), 'block_engineer') is False

    def test_inactive_project_member_denied(self, db):
        user = User.objects.create_user(username='inactive_user', password='pass')
        project = Project.objects.create(project_name='Test Project 2', project_code='TP-2')
        role, _ = Role.objects.get_or_create(role_name='block_engineer')
        
        member = ProjectMember.objects.create(
            project=project,
            user=user,
            status=MemberStatus.INACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=role)

        assert has_procurement_step_role(user, str(project.id), 'block_engineer') is False

    def test_or_role_handling(self, db):
        user = User.objects.create_user(username='ceo_user', password='pass')
        project = Project.objects.create(project_name='Test Project 3', project_code='TP-3')
        role, _ = Role.objects.get_or_create(role_name='ceo')
        
        member = ProjectMember.objects.create(
            project=project,
            user=user,
            status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=member, role=role)

        assert has_procurement_step_role(user, str(project.id), 'ceo_or_pm_budget') is True


@pytest.mark.django_db
class TestProcurementStepRBACViews:
    @pytest.fixture
    def setup_data(self):
        user_creator = User.objects.create_user(username='creator', password='pass')
        user_eng = User.objects.create_user(username='eng', password='pass')
        user_tech = User.objects.create_user(username='tech', password='pass')
        user_unauth = User.objects.create_user(username='unauth', password='pass')

        project = Project.objects.create(project_name='RBAC Project', project_code='PRJ-RBAC')
        block = Block.objects.create(
            project=project,
            block_code='B1',
            block_name='Block 1',
            created_by=user_creator,
        )

        role_eng, _ = Role.objects.get_or_create(role_name='block_engineer')
        role_tech, _ = Role.objects.get_or_create(role_name='technical_office')

        m_eng = ProjectMember.objects.create(project=project, user=user_eng, status=MemberStatus.ACTIVE)
        ProjectMemberRole.objects.create(member=m_eng, role=role_eng)

        m_tech = ProjectMember.objects.create(project=project, user=user_tech, status=MemberStatus.ACTIVE)
        ProjectMemberRole.objects.create(member=m_tech, role=role_tech)

        requisition = RequisitionHeader.objects.create(
            project=project,
            block=block,
            requested_by=user_creator,
            request_date='2026-01-01',
            status=RequisitionStatus.DRAFT,
            created_by=user_creator,
        )

        return {
            'project': project,
            'block': block,
            'requisition': requisition,
            'user_eng': user_eng,
            'user_tech': user_tech,
            'user_unauth': user_unauth,
        }

    def test_submit_draft_denied_without_role(self, setup_data):
        client = APIClient()
        data = setup_data
        client.force_authenticate(user=data['user_unauth'])

        url = f"/api/v1/projects/{data['project'].id}/requisitions/{data['requisition'].id}/submit/"
        response = client.post(url, {}, format='json')
        if response.status_code == 404:
            # Fallback if v1 prefix differs in test router
            url = f"/api/projects/{data['project'].id}/requisitions/{data['requisition'].id}/submit/"
            response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_submit_draft_allowed_with_role(self, setup_data):
        client = APIClient()
        data = setup_data
        client.force_authenticate(user=data['user_eng'])

        url = f"/api/v1/projects/{data['project'].id}/requisitions/{data['requisition'].id}/submit/"
        response = client.post(url, {'comments': 'Submitting draft'}, format='json')
        if response.status_code == 404:
            url = f"/api/projects/{data['project'].id}/requisitions/{data['requisition'].id}/submit/"
            response = client.post(url, {'comments': 'Submitting draft'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        data['requisition'].refresh_from_db()
        assert data['requisition'].status == RequisitionStatus.TECHNICAL_REVIEW

    def test_technical_review_step_rbac(self, setup_data):
        client = APIClient()
        data = setup_data
        req = data['requisition']
        req.status = RequisitionStatus.TECHNICAL_REVIEW
        req.save()

        url_approve = f"/api/v1/projects/{data['project'].id}/requisitions/{req.id}/approve/"

        # Engineer user (block_engineer) is denied at technical_review step
        client.force_authenticate(user=data['user_eng'])
        res_denied = client.post(url_approve, {}, format='json')
        if res_denied.status_code == 404:
            url_approve = f"/api/projects/{data['project'].id}/requisitions/{req.id}/approve/"
            res_denied = client.post(url_approve, {}, format='json')
        assert res_denied.status_code == status.HTTP_403_FORBIDDEN

        # Technical office user is allowed at technical_review step
        client.force_authenticate(user=data['user_tech'])
        res_allowed = client.post(url_approve, {'comments': 'Approved tech review'}, format='json')
        assert res_allowed.status_code == status.HTTP_200_OK
        req.refresh_from_db()
        assert req.status == RequisitionStatus.WORKSHOP_APPROVAL


@pytest.mark.django_db
class TestWorkshopDraftPermissions:
    @pytest.fixture
    def workshop_setup(self, db):
        user_creator = User.objects.create_user(username='ws_creator', password='pass')
        user_supervisor = User.objects.create_user(username='ws_super', password='pass')
        user_engineer = User.objects.create_user(username='ws_eng', password='pass')
        user_unauth = User.objects.create_user(username='ws_unauth', password='pass')

        project = Project.objects.create(project_name='Workshop RBAC', project_code='PRJ-WS')
        workshop_block = ensure_workshop_block(project, created_by=user_creator)

        role_supervisor, _ = Role.objects.get_or_create(role_name='workshop_supervisor')
        role_engineer, _ = Role.objects.get_or_create(role_name='block_engineer')

        m_super = ProjectMember.objects.create(
            project=project, user=user_supervisor, status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=m_super, role=role_supervisor)

        m_eng = ProjectMember.objects.create(
            project=project, user=user_engineer, status=MemberStatus.ACTIVE,
        )
        ProjectMemberRole.objects.create(member=m_eng, role=role_engineer)

        workshop_req = RequisitionHeader.objects.create(
            project=project,
            block=workshop_block,
            scope=RequisitionScope.WORKSHOP,
            requested_by=user_creator,
            request_date='2026-01-01',
            status=RequisitionStatus.DRAFT,
            created_by=user_creator,
        )

        return {
            'project': project,
            'workshop_req': workshop_req,
            'user_supervisor': user_supervisor,
            'user_engineer': user_engineer,
            'user_unauth': user_unauth,
        }

    def test_workshop_draft_requires_workshop_supervisor(self, workshop_setup):
        req = workshop_setup['workshop_req']
        assert get_required_role(req) == 'workshop_supervisor'
        assert has_procurement_step_role(
            workshop_setup['user_supervisor'], str(workshop_setup['project'].id), 'workshop_supervisor',
        )
        assert not has_procurement_step_role(
            workshop_setup['user_engineer'], str(workshop_setup['project'].id), 'workshop_supervisor',
        )

    def test_workshop_submit_allowed_for_supervisor(self, workshop_setup):
        client = APIClient()
        data = workshop_setup
        client.force_authenticate(user=data['user_supervisor'])

        url = f"/api/v1/projects/{data['project'].id}/requisitions/{data['workshop_req'].id}/submit/"
        response = client.post(url, {'comments': 'Submit workshop draft'}, format='json')
        if response.status_code == 404:
            url = f"/api/projects/{data['project'].id}/requisitions/{data['workshop_req'].id}/submit/"
            response = client.post(url, {'comments': 'Submit workshop draft'}, format='json')
        assert response.status_code == status.HTTP_200_OK, response.data
        data['workshop_req'].refresh_from_db()
        assert data['workshop_req'].status == RequisitionStatus.TECHNICAL_REVIEW

    def test_workshop_submit_denied_for_block_engineer(self, workshop_setup):
        client = APIClient()
        data = workshop_setup
        client.force_authenticate(user=data['user_engineer'])

        url = f"/api/v1/projects/{data['project'].id}/requisitions/{data['workshop_req'].id}/submit/"
        response = client.post(url, {}, format='json')
        if response.status_code == 404:
            url = f"/api/projects/{data['project'].id}/requisitions/{data['workshop_req'].id}/submit/"
            response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_approval_log_list_requires_project_permission(self, workshop_setup):
        client = APIClient()
        data = workshop_setup
        url = f"/api/v1/projects/{data['project'].id}/requisitions/{data['workshop_req'].id}/approval-logs/"

        # Unauthenticated request returns 401
        res = client.get(url)
        if res.status_code == 404:
            url = f"/api/projects/{data['project'].id}/requisitions/{data['workshop_req'].id}/approval-logs/"
            res = client.get(url)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

        # Authenticated non-project member returns 403
        client.force_authenticate(user=data['user_unauth'])
        res = client.get(url)
        assert res.status_code == status.HTTP_403_FORBIDDEN

        # Authenticated project member returns 200
        client.force_authenticate(user=data['user_supervisor'])
        res = client.get(url)
        assert res.status_code == status.HTTP_200_OK, res.data
