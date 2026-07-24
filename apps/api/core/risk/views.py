from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_date_optional
from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from permissions.project import HasProjectPermission, IsProjectMember
from risk.models import BarrierStatus, EventType, RiskEvent
from risk.serializers import BarrierCreateSerializer, BarrierSerializer, RiskEventSerializer
from risk.services.matrix_service import build_risk_matrix


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
        super().perform_create(serializer, event_type=EventType.BARRIER)

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


@extend_schema_view(
    list=extend_schema(summary='List risk/delay events', tags=['Risk']),
    create=extend_schema(summary='Create risk/delay event', tags=['Risk']),
    retrieve=extend_schema(summary='Get risk/delay event', tags=['Risk']),
    partial_update=extend_schema(summary='Update risk/delay event', tags=['Risk']),
    destroy=extend_schema(summary='Soft-delete risk/delay event', tags=['Risk']),
)
class RiskEventViewSet(ProjectScopedViewSet):
    queryset = RiskEvent.objects.select_related(
        'owner',
        'responsible_user',
        'activity',
        'related_daily_report',
        'related_correspondence',
    ).all()
    serializer_class = RiskEventSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.get_project_id()
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('event_type'):
            qs = qs.filter(event_type=params['event_type'])
        if params.get('severity'):
            qs = qs.filter(severity=params['severity'])
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        if params.get('search'):
            term = params['search']
            qs = qs.filter(
                Q(description__icontains=term)
                | Q(responsible_party__icontains=term)
                | Q(category__icontains=term)
            )
        date_from = parse_date_optional(params.get('date_from'))
        date_to = parse_date_optional(params.get('date_to'))
        if date_from:
            qs = qs.filter(event_date__gte=date_from)
        if date_to:
            qs = qs.filter(event_date__lte=date_to)
        return qs.order_by('-event_date', '-created_at')


class RiskMatrixView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Risk matrix probability × severity', tags=['Risk'])
    def get(self, request, project_pk=None):
        return Response(build_risk_matrix(project_pk))
