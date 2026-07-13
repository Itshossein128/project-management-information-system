import pytest
import uuid
from rest_framework.exceptions import ValidationError
from hr.models import LeaveType, LeaveStatus, OvertimeStatus, LeaveRequest, OvertimeRequest
from hr import services

@pytest.fixture
def setup_data(project, user, other_user):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    supervisor = User.objects.create_user(mobile='09120000003', username='sup', password='123')
    manager = User.objects.create_user(mobile='09120000004', username='mgr', password='123')
    return {
        'project': project,
        'requester': user,
        'supervisor': supervisor,
        'manager': manager
    }

@pytest.mark.django_db
class TestHRServices:
    def test_check_overtime_draft_status_success(self, setup_data):
        req = OvertimeRequest(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason', status=OvertimeStatus.DRAFT
        )
        services.check_overtime_draft_status(req)

    def test_check_overtime_draft_status_fail(self, setup_data):
        req = OvertimeRequest(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason', status=OvertimeStatus.SUBMITTED
        )
        with pytest.raises(ValidationError):
            services.check_overtime_draft_status(req)

    def test_submit_overtime(self, setup_data):
        req = OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason', status=OvertimeStatus.DRAFT
        )
        services.submit_overtime(req, setup_data['requester'])
        req.refresh_from_db()
        assert req.status == OvertimeStatus.SUBMITTED
        assert req.updated_by == setup_data['requester']

    def test_supervisor_approve_overtime(self, setup_data):
        req = OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason', status=OvertimeStatus.SUBMITTED
        )
        services.supervisor_approve_overtime(req, setup_data['supervisor'], True, 'notes')
        req.refresh_from_db()
        assert req.status == OvertimeStatus.SUPERVISOR_APPROVED
        assert req.supervisor_approved is True
        assert req.supervisor_notes == 'notes'

    def test_manager_approve_overtime(self, setup_data):
        req = OvertimeRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', overtime_date='2024-01-01', requested_hours='2',
            reason='reason', status=OvertimeStatus.SUPERVISOR_APPROVED
        )
        services.manager_approve_overtime(req, setup_data['manager'], True, '1.5')
        req.refresh_from_db()
        assert req.status == OvertimeStatus.MANAGER_APPROVED
        assert req.manager_approved is True
        assert str(req.approved_hours) == '1.50'

    def test_check_leave_draft_status_success(self, setup_data):
        req = LeaveRequest(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            status=LeaveStatus.DRAFT
        )
        services.check_leave_draft_status(req)

    def test_check_leave_draft_status_fail(self, setup_data):
        req = LeaveRequest(
            project=setup_data['project'], requester=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            status=LeaveStatus.SUBMITTED
        )
        with pytest.raises(ValidationError):
            services.check_leave_draft_status(req)

    def test_submit_leave(self, setup_data):
        req = LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            status=LeaveStatus.DRAFT
        )
        services.submit_leave(req, setup_data['requester'])
        req.refresh_from_db()
        assert req.status == LeaveStatus.SUBMITTED
        assert req.updated_by == setup_data['requester']

    def test_supervisor_approve_leave(self, setup_data):
        req = LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            status=LeaveStatus.SUBMITTED
        )
        services.supervisor_approve_leave(req, setup_data['supervisor'], True)
        req.refresh_from_db()
        assert req.status == LeaveStatus.SUPERVISOR_APPROVED
        assert req.supervisor_approved is True

    def test_manager_approve_leave(self, setup_data):
        req = LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', request_type=LeaveType.DAILY, leave_date='2024-01-01',
            status=LeaveStatus.SUPERVISOR_APPROVED
        )
        services.manager_approve_leave(req, setup_data['manager'], True)
        req.refresh_from_db()
        assert req.status == LeaveStatus.MANAGER_APPROVED
        assert req.manager_approved is True

    def test_security_approve_leave(self, setup_data):
        req = LeaveRequest.objects.create(
            project=setup_data['project'], requester=setup_data['requester'], created_by=setup_data['requester'],
            department='D1', request_type=LeaveType.MISSION, leave_date='2024-01-01',
            status=LeaveStatus.MANAGER_APPROVED
        )
        services.security_approve_leave(req, setup_data['manager'], True)
        req.refresh_from_db()
        assert req.status == LeaveStatus.SECURITY_APPROVED
        assert req.security_approved is True
