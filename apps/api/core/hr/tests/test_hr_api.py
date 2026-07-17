import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from hr.models import LeaveRequest, LeaveStatus, LeaveType, OvertimeRequest, OvertimeStatus
from projects.models import Project
from authentication.models import User
from master_data.models import ProjectMember, Role, ProjectMemberRole, RolePermission


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_data():
    project = Project.objects.create(project_code='HR-TEST', project_name='HR Project')

    requester = User.objects.create(username='requester', mobile='12345678901')
    supervisor = User.objects.create(username='supervisor', mobile='12345678902')
    manager = User.objects.create(username='manager', mobile='12345678903')

    role = Role.objects.create(role_name='member')
    RolePermission.objects.create(role=role, permission_codename='view_reports')
    RolePermission.objects.create(role=role, permission_codename='edit_reports')

    for u in [requester, supervisor, manager]:
        member = ProjectMember.objects.create(project=project, user=u)
        ProjectMemberRole.objects.create(member=member, role=role)

    return {
        'project': project,
        'requester': requester,
        'supervisor': supervisor,
        'manager': manager
    }


@pytest.mark.django_db
class TestOvertimeRequestViewSet:
    def test_create_overtime_request(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        url = reverse('overtime-list', kwargs={'project_pk': setup_data['project'].id})
        data = {
            'department': 'Engineering',
            'overtime_date': '1403-01-01',
            'requested_hours': '3.5',
            'reason': 'Urgent project release deadline',
            'requester': setup_data['requester'].id
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data['department'] == 'Engineering'
        assert response.data['status'] == OvertimeStatus.DRAFT

    def test_partial_update_draft(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = OvertimeRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            created_by=setup_data['requester'],
            overtime_date='2024-01-01',
            requested_hours='2.0',
            reason='Initial reason setup'
        )
        url = reverse('overtime-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        data = {'department': 'IT'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        req.refresh_from_db()
        assert req.department == 'IT'

    def test_partial_update_non_draft_fails(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = OvertimeRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            created_by=setup_data['requester'],
            overtime_date='2024-01-01',
            requested_hours='2.0',
            reason='Initial reason setup',
            status=OvertimeStatus.SUBMITTED
        )
        url = reverse('overtime-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        data = {'department': 'IT'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_draft(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = OvertimeRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            created_by=setup_data['requester'],
            overtime_date='2024-01-01',
            requested_hours='2.0',
            reason='Initial reason setup'
        )
        url = reverse('overtime-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not OvertimeRequest.objects.filter(id=req.id).exists()

    def test_delete_non_draft_fails(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = OvertimeRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            created_by=setup_data['requester'],
            overtime_date='2024-01-01',
            requested_hours='2.0',
            reason='Initial reason setup',
            status=OvertimeStatus.SUBMITTED
        )
        url = reverse('overtime-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert OvertimeRequest.objects.filter(id=req.id).exists()

    def test_list_and_filter(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason1', created_by=setup_data['requester']
        )
        OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D2', overtime_date='2024-01-02', requested_hours='2',
            reason='reason2', status=OvertimeStatus.SUBMITTED, created_by=setup_data['requester']
        )
        OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['supervisor'],
            department='D3', overtime_date='2024-01-03', requested_hours='2',
            reason='reason3', created_by=setup_data['supervisor']
        )

        url = reverse('overtime-list', kwargs={'project_pk': setup_data['project'].id})

        # All requests for project
        res = api_client.get(url)
        assert res.data['count'] == 3

        # my_requests filter
        res = api_client.get(url, {'my_requests': 'true'})
        assert res.data['count'] == 2

        # status filter
        res = api_client.get(url, {'status': OvertimeStatus.SUBMITTED})
        assert res.data['count'] == 1

    def test_custom_actions_workflow(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason1', created_by=setup_data['requester']
        )

        # Submit
        url_submit = reverse('overtime-submit', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_submit)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == OvertimeStatus.SUBMITTED

        # Supervisor Approve
        api_client.force_authenticate(user=setup_data['supervisor'])
        url_sup_approve = reverse('overtime-supervisor', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_sup_approve, {'approved': True, 'notes': 'Good'})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == OvertimeStatus.SUPERVISOR_APPROVED
        req.refresh_from_db()
        assert req.supervisor_notes == 'Good'
        assert req.supervisor_approved is True

        # Manager Approve
        api_client.force_authenticate(user=setup_data['manager'])
        url_mgr_approve = reverse('overtime-manager', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_mgr_approve, {'approved': True, 'approved_hours': '1.5'})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == OvertimeStatus.MANAGER_APPROVED
        req.refresh_from_db()
        assert req.manager_approved is True
        assert str(req.approved_hours) == '1.50'


@pytest.mark.django_db
class TestLeaveRequestViewSet:
    def test_create_leave_request(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        url = reverse('leave-list', kwargs={'project_pk': setup_data['project'].id})
        data = {
            'department': 'Engineering',
            'request_type': LeaveType.MISSION,
            'leave_date': '1403-01-01',
            'mission_subject': 'Site visit to client',
            'replacement_user': setup_data['supervisor'].id,
            'requester': setup_data['requester'].id
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data['department'] == 'Engineering'
        assert response.data['status'] == LeaveStatus.DRAFT

    def test_partial_update_draft(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = LeaveRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            request_type=LeaveType.DAILY,
            leave_date='2024-01-01',
            created_by=setup_data['requester']
        )
        url = reverse('leave-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        data = {'department': 'IT'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        req.refresh_from_db()
        assert req.department == 'IT'

    def test_partial_update_non_draft_fails(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = LeaveRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            request_type=LeaveType.DAILY,
            leave_date='2024-01-01',
            status=LeaveStatus.SUBMITTED,
            created_by=setup_data['requester']
        )
        url = reverse('leave-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        data = {'department': 'IT'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_draft(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = LeaveRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            request_type=LeaveType.DAILY,
            leave_date='2024-01-01',
            created_by=setup_data['requester']
        )
        url = reverse('leave-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not LeaveRequest.objects.filter(id=req.id).exists()

    def test_delete_non_draft_fails(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = LeaveRequest.objects.create(
            project=setup_data['project'],
            requester=setup_data['requester'],
            department='HR',
            request_type=LeaveType.DAILY,
            leave_date='2024-01-01',
            status=LeaveStatus.SUBMITTED,
            created_by=setup_data['requester']
        )
        url = reverse('leave-detail', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert LeaveRequest.objects.filter(id=req.id).exists()


    def test_list_and_filter(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            created_by=setup_data['requester']
        )
        LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D2', request_type=LeaveType.HOURLY, leave_date='2024-01-02',
            status=LeaveStatus.SUBMITTED, created_by=setup_data['requester']
        )
        LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['supervisor'],
            department='D3', request_type=LeaveType.MISSION, leave_date='2024-01-03',
            created_by=setup_data['supervisor']
        )

        url = reverse('leave-list', kwargs={'project_pk': setup_data['project'].id})

        # All requests for project
        res = api_client.get(url)
        assert res.data['count'] == 3

        # my_requests filter
        res = api_client.get(url, {'my_requests': 'true'})
        assert res.data['count'] == 2

        # status filter
        res = api_client.get(url, {'status': LeaveStatus.SUBMITTED})
        assert res.data['count'] == 1

    def test_custom_actions_workflow(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['requester'])
        req = LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', request_type=LeaveType.MISSION, leave_date='2024-01-01',
            created_by=setup_data['requester']
        )

        # Submit
        url_submit = reverse('leave-submit', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_submit)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == LeaveStatus.SUBMITTED

        # Supervisor Approve
        api_client.force_authenticate(user=setup_data['supervisor'])
        url_sup_approve = reverse('leave-supervisor', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_sup_approve, {'approved': True})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == LeaveStatus.SUPERVISOR_APPROVED
        req.refresh_from_db()
        assert req.supervisor_approved is True

        # Manager Approve
        api_client.force_authenticate(user=setup_data['manager'])
        url_mgr_approve = reverse('leave-manager', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_mgr_approve, {'approved': True})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == LeaveStatus.MANAGER_APPROVED
        req.refresh_from_db()
        assert req.manager_approved is True

        # Security Approve
        url_sec_approve = reverse('leave-security', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_sec_approve, {'approved': True})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == LeaveStatus.SECURITY_APPROVED
        req.refresh_from_db()
        assert req.security_approved is True

    def test_security_approve_fails_if_not_mission(self, api_client, setup_data):
        api_client.force_authenticate(user=setup_data['manager'])
        req = LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            status=LeaveStatus.MANAGER_APPROVED, created_by=setup_data['requester']
        )
        url_sec_approve = reverse('leave-security', kwargs={'project_pk': setup_data['project'].id, 'pk': req.id})
        res = api_client.post(url_sec_approve, {'approved': True})
        assert res.status_code == status.HTTP_400_BAD_REQUEST
