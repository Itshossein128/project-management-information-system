from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from permissions.project import HasProjectPermission, IsProjectMember
from sub_reports.models import DisciplineSubReport, SubReportStatus
from sub_reports.serializers import DisciplineSubReportSerializer


@extend_schema_view(
    list=extend_schema(summary='List discipline sub-reports', tags=['Sub-reports']),
    create=extend_schema(summary='Create discipline sub-report', tags=['Sub-reports']),
    retrieve=extend_schema(summary='Get discipline sub-report', tags=['Sub-reports']),
    partial_update=extend_schema(summary='Update discipline sub-report', tags=['Sub-reports']),
    destroy=extend_schema(summary='Delete discipline sub-report', tags=['Sub-reports']),
)
class DisciplineSubReportViewSet(ProjectScopedViewSet):
    queryset = DisciplineSubReport.objects.prefetch_related('activities').all()
    serializer_class = DisciplineSubReportSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    approve_permission = 'approve_reports'

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return self.view_permission
        if self.action in ('approve', 'reject'):
            return self.approve_permission
        return self.edit_permission

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    def get_queryset(self):
        qs = super().get_queryset()
        discipline = self.request.query_params.get('discipline')
        if discipline:
            qs = qs.filter(discipline=discipline)
        return qs.order_by('-report_date')

    @action(detail=True, methods=['post'])
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        if obj.status != SubReportStatus.DRAFT:
            raise ValidationError('فقط گزارش‌های پیش‌نویس قابل ارسال هستند')
        obj.status = SubReportStatus.SUBMITTED
        obj.submitted_by = request.user
        obj.submitted_at = timezone.now()
        obj.updated_by = request.user
        obj.save(update_fields=['status', 'submitted_by', 'submitted_at', 'updated_by', 'updated_at'])
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        if obj.status != SubReportStatus.SUBMITTED:
            raise ValidationError('فقط گزارش‌های ارسال شده قابل تأیید هستند')
        obj.status = SubReportStatus.APPROVED
        obj.approved_by = request.user
        obj.approved_at = timezone.now()
        obj.updated_by = request.user
        obj.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_by', 'updated_at'])
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        if obj.status != SubReportStatus.SUBMITTED:
            raise ValidationError('فقط گزارش‌های ارسال شده قابل رد هستند')
        reason = (request.data.get('rejection_reason') or '').strip()
        if len(reason) < 10:
            raise ValidationError({'rejection_reason': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد'})
        obj.status = SubReportStatus.REJECTED
        obj.rejection_reason = reason
        obj.updated_by = request.user
        obj.save(update_fields=['status', 'rejection_reason', 'updated_by', 'updated_at'])
        return Response(self.get_serializer(obj).data)
