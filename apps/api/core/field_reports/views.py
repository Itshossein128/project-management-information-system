from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response

from common.jalali import parse_date_optional
from common.viewsets import ProjectScopedViewSet
from config.exceptions import ConflictError
from config.pagination import DefaultPageNumberPagination
from field_reports.models import WeatherLog
from field_reports.serializers import WeatherLogCreateSerializer, WeatherLogSerializer


@extend_schema_view(
    list=extend_schema(summary='List weather logs', tags=['Weather']),
    create=extend_schema(summary='Create weather log', tags=['Weather']),
    retrieve=extend_schema(summary='Get weather log', tags=['Weather']),
    partial_update=extend_schema(summary='Update weather log', tags=['Weather']),
    destroy=extend_schema(summary='Soft-delete weather log', tags=['Weather']),
)
class WeatherLogViewSet(ProjectScopedViewSet):
    queryset = WeatherLog.objects.select_related('project').all()
    serializer_class = WeatherLogSerializer
    pagination_class = DefaultPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'create':
            return WeatherLogCreateSerializer
        return WeatherLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        date_from = parse_date_optional(params.get('date_from'))
        date_to = parse_date_optional(params.get('date_to'))
        if date_from:
            qs = qs.filter(log_date__gte=date_from)
        if date_to:
            qs = qs.filter(log_date__lte=date_to)

        ordering = params.get('ordering', '-log_date')
        allowed = {'log_date', '-log_date', 'temp_max', '-temp_max', 'temp_min', '-temp_min'}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by('-log_date')
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        log_date = serializer.validated_data['log_date']
        project_id = self.get_project_id()

        if WeatherLog.objects.filter(project_id=project_id, log_date=log_date).exists():
            raise ConflictError('گزارش جوی برای این تاریخ قبلاً ثبت شده است')

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
