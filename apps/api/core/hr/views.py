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


@extend_schema_view(
    list=extend_schema(summary='List overtime requests', tags=['HR']),
    create=extend_schema(summary='Create overtime request', tags=['HR']),
    partial_update=extend_schema(summary='Update overtime request', tags=['HR']),
    destroy=extend_schema(summary='Delete overtime request', tags=['HR']),
)
class OvertimeRequestViewSet(ProjectScopedViewSet):
    queryset = OvertimeRequest.objects.select_related('requester').all()
    serializer_class = OvertimeRequestSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    # Retrieves the list of overtime requests, filtering by current user or status if requested.
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('my_requests') == 'true':
            qs = qs.filter(requester=self.request.user)
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs.order_by('-overtime_date')

    # Assigns the project and current user when creating a new overtime request.
    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            requester=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    # Updates an overtime request, but only if it's currently in draft status.
    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        services.check_overtime_draft_status(obj)
        return super().partial_update(request, *args, **kwargs)

    # Deletes an overtime request, ensuring it's only allowed if in draft status.
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        services.check_overtime_draft_status(obj)
        return super().destroy(request, *args, **kwargs)

    # Custom action to submit a draft overtime request for supervisor review.
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        obj = services.submit_overtime(obj, request.user)
        return Response(self.get_serializer(obj).data)

    # Custom action for a supervisor to either approve or reject the overtime request.
    @action(detail=True, methods=['post'], url_path='supervisor-approve')
    def supervisor_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        notes = request.data.get('notes', '')
        obj = services.supervisor_approve_overtime(obj, request.user, approved, notes)
        return Response(self.get_serializer(obj).data)

    # Custom action for a manager to final approve or reject the overtime request, potentially adjusting hours.
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
class LeaveRequestViewSet(ProjectScopedViewSet):
    queryset = LeaveRequest.objects.select_related('requester', 'replacement_user').all()
    serializer_class = LeaveRequestSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    # Retrieves the list of leave requests, filtering by current user or status if requested.
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('my_requests') == 'true':
            qs = qs.filter(requester=self.request.user)
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs.order_by('-leave_date')

    # Assigns the project and current user when creating a new leave request.
    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            requester=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    # Updates a leave request, ensuring it's only allowed if in draft status.
    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        services.check_leave_draft_status(obj)
        return super().partial_update(request, *args, **kwargs)

    # Deletes a leave request, ensuring it's only allowed if in draft status.
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        services.check_leave_draft_status(obj)
        return super().destroy(request, *args, **kwargs)

    # Custom action to submit a draft leave request for supervisor review.
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        obj = services.submit_leave(obj, request.user)
        return Response(self.get_serializer(obj).data)

    # Custom action for a supervisor to either approve or reject the leave request.
    @action(detail=True, methods=['post'], url_path='supervisor-approve')
    def supervisor_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj = services.supervisor_approve_leave(obj, request.user, approved)
        return Response(self.get_serializer(obj).data)

    # Custom action for a manager to final approve or reject the leave request.
    @action(detail=True, methods=['post'], url_path='manager-approve')
    def manager_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj = services.manager_approve_leave(obj, request.user, approved)
        return Response(self.get_serializer(obj).data)

    # Custom action for security to approve or reject the physical exit of the user.
    @action(detail=True, methods=['post'], url_path='security-approve')
    def security_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj = services.security_approve_leave(obj, request.user, approved)
        return Response(self.get_serializer(obj).data)
