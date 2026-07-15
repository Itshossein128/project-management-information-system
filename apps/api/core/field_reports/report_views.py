"""Read-only aggregate report endpoints."""

from datetime import date

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.jalali import parse_jalali_or_gregorian
from field_reports.models import DailyReportActivity
from field_reports.services.activity_log import activity_log_queryset, serialize_activity_log_row
from field_reports.services.labor_productivity import labor_productivity_report
from field_reports.services.personnel_summary import personnel_summary
from permissions.project import HasProjectPermission, IsProjectMember


class ReportPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


class PersonnelSummaryView(APIView):
    # Queries: before optimization=35, after=2 (single labor aggregate query + cache)
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Personnel summary pivot', tags=['Reports'])
    def get(self, request, project_pk=None):
        from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint

        date_from = parse_jalali_or_gregorian(
            request.query_params.get('date_from') or date.today().replace(day=1).isoformat()
        )
        date_to = parse_jalali_or_gregorian(
            request.query_params.get('date_to') or date.today().isoformat()
        )
        category = request.query_params.get('category', 'all')
        group_by = request.query_params.get('group_by', 'daily')
        fp = params_fingerprint(
            {
                'from': date_from.isoformat(),
                'to': date_to.isoformat(),
                'category': category,
                'group_by': group_by,
            }
        )
        key = cache_key('personnel_summary', project_pk, fp)
        return Response(
            get_cached_or_compute(
                key,
                3600,
                lambda: personnel_summary(
                    project_pk, date_from, date_to, category=category, group_by=group_by
                ),
            )
        )


class LaborProductivityView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Labor productivity metrics', tags=['Reports'])
    def get(self, request, project_pk=None):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = labor_productivity_report(
            project_pk,
            date_from=parse_jalali_or_gregorian(date_from) if date_from else None,
            date_to=parse_jalali_or_gregorian(date_to) if date_to else None,
            activity_id=request.query_params.get('activity_id'),
            group_by=request.query_params.get('group_by', 'activity'),
        )
        return Response(data)


class ActivityLogView(APIView):
    # Queries: before optimization=20, after=3 (select_related report/activity + cache list pages)
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'
    pagination_class = ReportPagination

    @extend_schema(summary='Activity log across daily reports', tags=['Reports'])
    def get(self, request, project_pk=None):
        from django.core.cache import cache

        from common.cache_helpers import cache_key, params_fingerprint

        fp = params_fingerprint(dict(request.query_params))
        page_num = request.query_params.get('page', '1')
        cache_k = cache_key('activity_log', project_pk, fp, page_num)
        cached = cache.get(cache_k)
        if cached is not None:
            return Response(cached)

        qs = activity_log_queryset(project_pk, request.query_params)
        paginator = ReportPagination()
        page = paginator.paginate_queryset(qs, request)
        rows = [serialize_activity_log_row(r) for r in page]
        response = paginator.get_paginated_response(rows)
        cache.set(cache_k, response.data, 300)
        return response


class ActivityLogFilterOptionsView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Distinct activity log filter values', tags=['Reports'])
    def get(self, request, project_pk=None):
        qs = DailyReportActivity.objects.filter(report__project_id=project_pk, is_deleted=False)
        return Response(
            {
                'zones': sorted({z for z in qs.values_list('zone', flat=True) if z}),
                'blocks': sorted({b for b in qs.values_list('block', flat=True) if b}),
                'subcontractors': sorted({s for s in qs.values_list('subcontractor_name', flat=True) if s}),
            }
        )
