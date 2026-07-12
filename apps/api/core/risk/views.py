from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response

from common.jalali import parse_date_optional
from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from risk.models import BarrierStatus, EventType, RiskEvent
from risk.serializers import BarrierCreateSerializer, BarrierSerializer


@extend_schema_view(
    list=extend_schema(summary='List barrier logs', tags=['Barriers']),
    create=extend_schema(summary='Create barrier log', tags=['Barriers']),
    retrieve=extend_schema(summary='Get barrier log', tags=['Barriers']),
    partial_update=extend_schema(summary='Update barrier log', tags=['Barriers']),
    destroy=extend_schema(summary='Soft-delete barrier log', tags=['Barriers']),
)
class BarrierLogViewSet(ProjectScopedViewSet):
    queryset = RiskEvent.objects.select_related('responsible_user').all()
    serializer_class = BarrierSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return BarrierCreateSerializer
        return BarrierSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(event_type=EventType.BARRIER)
        params = self.request.query_params
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        if params.get('category'):
            qs = qs.filter(category=params['category'])
        if params.get('impact_schedule', '').lower() in ('1', 'true', 'yes'):
            qs = qs.filter(impact_on_schedule=True)
        if params.get('impact_cost', '').lower() in ('1', 'true', 'yes'):
            qs = qs.filter(impact_on_cost=True)
        date_from = parse_date_optional(params.get('date_from'))
        date_to = parse_date_optional(params.get('date_to'))
        if date_from:
            qs = qs.filter(event_date__gte=date_from)
        if date_to:
            qs = qs.filter(event_date__lte=date_to)
        return qs.order_by('-event_date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            event_type=EventType.BARRIER,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('status') == BarrierStatus.RESOLVED:
            if not serializer.validated_data.get('resolved_date') and not instance.resolved_date:
                return Response(
                    {'error': {'message': 'برای وضعیت رفع شده، تاریخ رفع الزامی است.'}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        self.perform_update(serializer)
        return Response(serializer.data)
