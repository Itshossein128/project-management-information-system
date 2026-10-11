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
from risk.models import (
    BarrierStatus,
    CorrectiveAction,
    EventType,
    HseEvent,
    Inspection,
    Nonconformity,
    RiskAction,
    RiskActionStatus,
    RiskEvent,
    RiskStatus,
    SafetyTraining,
    WorkPermit,
)
from risk.serializers import (
    BarrierCreateSerializer,
    BarrierSerializer,
    CorrectiveActionSerializer,
    HseEventSerializer,
    InspectionSerializer,
    NonconformitySerializer,
    RiskActionSerializer,
    RiskEventSerializer,
    SafetyTrainingSerializer,
    WorkPermitSerializer,
)
from risk.services.matrix_service import build_risk_matrix
from risk.services.period_report_service import build_quality_safety_period_report
from risk.services.score_service import normalize_status

IMPACT_FILTER_MAP = {
    'schedule': 'impact_on_schedule',
    'cost': 'impact_on_cost',
    'quality': 'impact_on_quality',
    'safety': 'impact_on_safety',
    'contract': 'impact_on_contract',
    'liquidity': 'impact_on_liquidity',
}


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
            st = normalize_status(params['status']) or params['status']
            qs = qs.filter(status=st)
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
        new_status = serializer.validated_data.get('status')
        if new_status in (RiskStatus.CLOSED, BarrierStatus.RESOLVED):
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
        'cost_item',
        'contract',
    ).prefetch_related('actions').all()
    serializer_class = RiskEventSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def perform_create(self, serializer, **kwargs):
        from projects.capability_service import assert_capability_enabled
        from projects.models import Project

        project = Project.objects.get(pk=self.get_project_id())
        assert_capability_enabled(project, 'risk')
        super().perform_create(serializer, **kwargs)

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
            st = normalize_status(params['status']) or params['status']
            qs = qs.filter(status=st)
        impact = params.get('impact')
        if impact and impact in IMPACT_FILTER_MAP:
            qs = qs.filter(**{IMPACT_FILTER_MAP[impact]: True})
        if params.get('search'):
            term = params['search']
            qs = qs.filter(
                Q(description__icontains=term)
                | Q(responsible_party__icontains=term)
                | Q(category__icontains=term)
                | Q(cause__icontains=term)
            )
        date_from = parse_date_optional(params.get('date_from'))
        date_to = parse_date_optional(params.get('date_to'))
        if date_from:
            qs = qs.filter(Q(event_date__gte=date_from) | Q(due_date__gte=date_from))
        if date_to:
            qs = qs.filter(Q(event_date__lte=date_to) | Q(due_date__lte=date_to))
        return qs.order_by('-event_date', '-created_at')

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data.get('status')
        if new_status == RiskStatus.CLOSED:
            open_count = instance.actions.filter(
                status=RiskActionStatus.OPEN,
                is_deleted=False,
            ).count()
            ack = bool(request.data.get('acknowledge_open_actions'))
            if open_count and not ack:
                return Response(
                    {
                        'code': 'open_actions_warning',
                        'error': {
                            'code': 'open_actions_warning',
                            'message': 'اقدامات باز وجود دارد. برای بستن، تأیید کنید.',
                            'open_actions_count': open_count,
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        self.perform_update(serializer)
        return Response(serializer.data)


class RiskMatrixView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Risk matrix probability × severity', tags=['Risk'])
    def get(self, request, project_pk=None):
        return Response(build_risk_matrix(project_pk))


@extend_schema_view(
    list=extend_schema(summary='List risk actions', tags=['Risk']),
    create=extend_schema(summary='Create risk action', tags=['Risk']),
    retrieve=extend_schema(summary='Get risk action', tags=['Risk']),
    partial_update=extend_schema(summary='Update risk action', tags=['Risk']),
    destroy=extend_schema(summary='Soft-delete risk action', tags=['Risk']),
)
class RiskActionViewSet(ProjectScopedViewSet):
    queryset = RiskAction.objects.select_related('risk_event', 'owner').all()
    serializer_class = RiskActionSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.get_project_id()
        return ctx

    def get_queryset(self):
        return self.queryset.filter(risk_event__project_id=self.get_project_id())


@extend_schema_view(
    list=extend_schema(summary='List inspections', tags=['Quality']),
    create=extend_schema(summary='Create inspection', tags=['Quality']),
    retrieve=extend_schema(summary='Get inspection', tags=['Quality']),
    partial_update=extend_schema(summary='Update inspection', tags=['Quality']),
    destroy=extend_schema(summary='Soft-delete inspection', tags=['Quality']),
)
class InspectionViewSet(ProjectScopedViewSet):
    queryset = Inspection.objects.select_related('wbs', 'responsible_user', 'activity').all()
    serializer_class = InspectionSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.get_project_id()
        return ctx


@extend_schema_view(
    list=extend_schema(summary='List nonconformities', tags=['Quality']),
    create=extend_schema(summary='Create nonconformity', tags=['Quality']),
    retrieve=extend_schema(summary='Get nonconformity', tags=['Quality']),
    partial_update=extend_schema(summary='Update nonconformity', tags=['Quality']),
    destroy=extend_schema(summary='Soft-delete nonconformity', tags=['Quality']),
)
class NonconformityViewSet(ProjectScopedViewSet):
    queryset = Nonconformity.objects.select_related('inspection', 'wbs').all()
    serializer_class = NonconformitySerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.get_project_id()
        return ctx


@extend_schema_view(
    list=extend_schema(summary='List corrective actions', tags=['Quality']),
    create=extend_schema(summary='Create corrective action', tags=['Quality']),
    retrieve=extend_schema(summary='Get corrective action', tags=['Quality']),
    partial_update=extend_schema(summary='Update corrective action', tags=['Quality']),
    destroy=extend_schema(summary='Soft-delete corrective action', tags=['Quality']),
)
class CorrectiveActionViewSet(ProjectScopedViewSet):
    queryset = CorrectiveAction.objects.select_related('nonconformity', 'responsible_user').all()
    serializer_class = CorrectiveActionSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.get_project_id()
        return ctx


@extend_schema_view(
    list=extend_schema(summary='List HSE events', tags=['HSE']),
    create=extend_schema(summary='Create HSE event', tags=['HSE']),
    retrieve=extend_schema(summary='Get HSE event', tags=['HSE']),
    partial_update=extend_schema(summary='Update HSE event', tags=['HSE']),
    destroy=extend_schema(summary='Soft-delete HSE event', tags=['HSE']),
)
class HseEventViewSet(ProjectScopedViewSet):
    queryset = HseEvent.objects.select_related('wbs').all()
    serializer_class = HseEventSerializer
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
        if params.get('kind'):
            qs = qs.filter(kind=params['kind'])
        date_from = parse_date_optional(params.get('date_from'))
        date_to = parse_date_optional(params.get('date_to'))
        if date_from:
            qs = qs.filter(event_date__gte=date_from)
        if date_to:
            qs = qs.filter(event_date__lte=date_to)
        return qs.order_by('-event_date', '-created_at')


@extend_schema_view(
    list=extend_schema(summary='List work permits', tags=['HSE']),
    create=extend_schema(summary='Create work permit', tags=['HSE']),
    retrieve=extend_schema(summary='Get work permit', tags=['HSE']),
    partial_update=extend_schema(summary='Update work permit', tags=['HSE']),
    destroy=extend_schema(summary='Soft-delete work permit', tags=['HSE']),
)
class WorkPermitViewSet(ProjectScopedViewSet):
    queryset = WorkPermit.objects.select_related('responsible_user').all()
    serializer_class = WorkPermitSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


@extend_schema_view(
    list=extend_schema(summary='List safety trainings', tags=['HSE']),
    create=extend_schema(summary='Create safety training', tags=['HSE']),
    retrieve=extend_schema(summary='Get safety training', tags=['HSE']),
    partial_update=extend_schema(summary='Update safety training', tags=['HSE']),
    destroy=extend_schema(summary='Soft-delete safety training', tags=['HSE']),
)
class SafetyTrainingViewSet(ProjectScopedViewSet):
    queryset = SafetyTraining.objects.select_related('responsible_user').all()
    serializer_class = SafetyTrainingSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']


class QualitySafetyPeriodReportView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Quality & safety period report', tags=['Quality'])
    def get(self, request, project_pk=None):
        date_from = parse_date_optional(request.query_params.get('date_from'))
        date_to = parse_date_optional(request.query_params.get('date_to'))
        if not date_from or not date_to:
            return Response(
                {'error': {'message': 'date_from و date_to الزامی هستند.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            build_quality_safety_period_report(project_pk, date_from, date_to),
        )
