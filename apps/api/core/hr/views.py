from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from hr.models import LeaveRequest, LeaveStatus, LeaveType, OvertimeRequest, OvertimeStatus
from hr.serializers import LeaveRequestSerializer, OvertimeRequestSerializer
from hr import services


class BaseHRRequestViewSet(ProjectScopedViewSet):
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    date_field_name = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('my_requests') == 'true':
            qs = qs.filter(requester=self.request.user)
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        if self.date_field_name:
            return qs.order_by(f'-{self.date_field_name}')
        return qs

    def perform_create(self, serializer):
        super().perform_create(serializer, requester=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        self._check_draft_status(obj)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self._check_draft_status(obj)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        obj = self._submit_request(obj, request.user)
        return Response(self.get_serializer(obj).data)

    def _check_draft_status(self, obj):
        raise NotImplementedError

    def _submit_request(self, obj, user):
        raise NotImplementedError


@extend_schema_view(
    list=extend_schema(summary='List overtime requests', tags=['HR']),
    create=extend_schema(summary='Create overtime request', tags=['HR']),
    partial_update=extend_schema(summary='Update overtime request', tags=['HR']),
    destroy=extend_schema(summary='Delete overtime request', tags=['HR']),
)
class OvertimeRequestViewSet(BaseHRRequestViewSet):
    queryset = OvertimeRequest.objects.select_related('requester').all()
    serializer_class = OvertimeRequestSerializer
    date_field_name = 'overtime_date'

    def _check_draft_status(self, obj):
        services.check_overtime_draft_status(obj)

    def _submit_request(self, obj, user):
        return services.submit_overtime(obj, user)

    @action(detail=True, methods=['post'], url_path='supervisor-approve')
    def supervisor_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        notes = request.data.get('notes', '')
        obj = services.supervisor_approve_overtime(obj, request.user, approved, notes)
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='manager-approve')
    def manager_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        approved_hours = request.data.get('approved_hours')
        obj = services.manager_approve_overtime(obj, request.user, approved, approved_hours)
        return Response(self.get_serializer(obj).data)


@extend_schema_view(
    list=extend_schema(summary='List leave requests', tags=['HR']),
    create=extend_schema(summary='Create leave request', tags=['HR']),
    partial_update=extend_schema(summary='Update leave request', tags=['HR']),
    destroy=extend_schema(summary='Delete leave request', tags=['HR']),
)
class LeaveRequestViewSet(BaseHRRequestViewSet):
    queryset = LeaveRequest.objects.select_related('requester', 'replacement_user').all()
    serializer_class = LeaveRequestSerializer
    date_field_name = 'leave_date'

    def _check_draft_status(self, obj):
        services.check_leave_draft_status(obj)

    def _submit_request(self, obj, user):
        return services.submit_leave(obj, user)

    @action(detail=True, methods=['post'], url_path='supervisor-approve')
    def supervisor_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj = services.supervisor_approve_leave(obj, request.user, approved)
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='manager-approve')
    def manager_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj = services.manager_approve_leave(obj, request.user, approved)
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='security-approve')
    def security_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj = services.security_approve_leave(obj, request.user, approved)
        return Response(self.get_serializer(obj).data)
