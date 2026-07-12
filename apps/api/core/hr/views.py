from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from hr.models import LeaveRequest, LeaveStatus, LeaveType, OvertimeRequest, OvertimeStatus
from hr.serializers import LeaveRequestSerializer, OvertimeRequestSerializer


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

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('my_requests') == 'true':
            qs = qs.filter(requester=self.request.user)
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs.order_by('-overtime_date')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            requester=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != OvertimeStatus.DRAFT:
            return Response({'error': {'message': 'فقط درخواست‌های پیش‌نویس قابل ویرایش هستند.'}}, status=400)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != OvertimeStatus.DRAFT:
            return Response({'error': {'message': 'فقط درخواست‌های پیش‌نویس قابل حذف هستند.'}}, status=400)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        if obj.status != OvertimeStatus.DRAFT:
            return Response({'error': {'message': 'وضعیت نامعتبر'}}, status=400)
        obj.status = OvertimeStatus.SUBMITTED
        obj.updated_by = request.user
        obj.save(update_fields=['status', 'updated_by', 'updated_at'])
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='supervisor-approve')
    def supervisor_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj.supervisor_approved = approved
        obj.supervisor_notes = request.data.get('notes', '')
        obj.status = OvertimeStatus.SUPERVISOR_APPROVED if approved else OvertimeStatus.REJECTED
        obj.updated_by = request.user
        obj.save()
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='manager-approve')
    def manager_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        if approved:
            approved_hours = request.data.get('approved_hours', obj.requested_hours)
            if float(approved_hours) > float(obj.requested_hours):
                return Response({'error': {'message': 'ساعات تأییدشده نمی‌تواند بیشتر از درخواست باشد.'}}, status=400)
            obj.approved_hours = approved_hours
            obj.status = OvertimeStatus.MANAGER_APPROVED
        else:
            obj.status = OvertimeStatus.REJECTED
        obj.manager_approved = approved
        obj.updated_by = request.user
        obj.save()
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

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('my_requests') == 'true':
            qs = qs.filter(requester=self.request.user)
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        return qs.order_by('-leave_date')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            requester=self.request.user,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != LeaveStatus.DRAFT:
            return Response({'error': {'message': 'فقط درخواست‌های پیش‌نویس قابل ویرایش هستند.'}}, status=400)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status != LeaveStatus.DRAFT:
            return Response({'error': {'message': 'فقط درخواست‌های پیش‌نویس قابل حذف هستند.'}}, status=400)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        if obj.status != LeaveStatus.DRAFT:
            return Response({'error': {'message': 'وضعیت نامعتبر'}}, status=400)
        obj.status = LeaveStatus.SUBMITTED
        obj.updated_by = request.user
        obj.save(update_fields=['status', 'updated_by', 'updated_at'])
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='supervisor-approve')
    def supervisor_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj.supervisor_approved = approved
        obj.status = LeaveStatus.SUPERVISOR_APPROVED if approved else LeaveStatus.REJECTED
        obj.updated_by = request.user
        obj.save()
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='manager-approve')
    def manager_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        approved = request.data.get('approved', True)
        obj.manager_approved = approved
        obj.status = LeaveStatus.MANAGER_APPROVED if approved else LeaveStatus.REJECTED
        obj.updated_by = request.user
        obj.save()
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'], url_path='security-approve')
    def security_approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        if obj.request_type != LeaveType.MISSION or obj.status != LeaveStatus.MANAGER_APPROVED:
            return Response({'error': {'message': 'فقط مأموریت‌های تأییدشده توسط مدیر قابل تأیید حراست هستند.'}}, status=400)
        approved = request.data.get('approved', True)
        obj.security_approved = approved
        obj.status = LeaveStatus.SECURITY_APPROVED if approved else LeaveStatus.REJECTED
        obj.updated_by = request.user
        obj.save()
        return Response(self.get_serializer(obj).data)
