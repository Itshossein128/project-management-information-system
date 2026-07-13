"""Equipment registry and utilization APIs."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from common.viewsets import ProjectScopedViewSet
from field_reports.models import Equipment
from field_reports.services.equipment_utilization import (
    equipment_utilization_list,
    equipment_utilization_summary,
)
from permissions.project import HasProjectPermission, IsProjectMember
from rest_framework import serializers


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = [
            'id',
            'equipment_code',
            'equipment_name',
            'equipment_type',
            'ownership_type',
            'plate_number',
            'default_hourly_rate',
            'is_active',
        ]
        read_only_fields = ['id']


@extend_schema_view(
    list=extend_schema(summary='List equipment registry', tags=['Equipment']),
    create=extend_schema(summary='Create equipment', tags=['Equipment']),
    partial_update=extend_schema(summary='Update equipment', tags=['Equipment']),
    destroy=extend_schema(summary='Delete equipment', tags=['Equipment']),
)
class EquipmentViewSet(ProjectScopedViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def get_queryset(self):
        qs = super().get_queryset().filter(is_deleted=False)
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs.order_by('equipment_name')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class EquipmentUtilizationView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Equipment utilization by fleet', tags=['Equipment'])
    def get(self, request, project_pk=None):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = equipment_utilization_list(
            project_pk,
            date_from=parse_jalali_or_gregorian(date_from) if date_from else None,
            date_to=parse_jalali_or_gregorian(date_to) if date_to else None,
            equipment_name=request.query_params.get('equipment_name'),
        )
        return Response(data)


class EquipmentUtilizationSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Fleet utilization summary KPIs', tags=['Equipment'])
    def get(self, request, project_pk=None):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = equipment_utilization_summary(
            project_pk,
            date_from=parse_jalali_or_gregorian(date_from) if date_from else None,
            date_to=parse_jalali_or_gregorian(date_to) if date_to else None,
        )
        return Response(data)
