from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
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

    def get_queryset(self):
        qs = super().get_queryset()
        discipline = self.request.query_params.get('discipline')
        if discipline:
            qs = qs.filter(discipline=discipline)
        return qs.order_by('-report_date')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        obj.status = SubReportStatus.SUBMITTED
        obj.submitted_by = request.user
        obj.submitted_at = timezone.now()
        obj.save()
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        obj.status = SubReportStatus.APPROVED
        obj.approved_by = request.user
        obj.approved_at = timezone.now()
        obj.save()
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, project_pk=None, pk=None):
        obj = self.get_object()
        obj.status = SubReportStatus.REJECTED
        obj.rejection_reason = request.data.get('rejection_reason', '')
        obj.save()
        return Response(self.get_serializer(obj).data)
