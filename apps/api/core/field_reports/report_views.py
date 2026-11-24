"""Read-only aggregate report endpoints."""

from datetime import date

from django.db import connection, transaction
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.jalali import parse_jalali_or_gregorian
from field_reports.services.activity_log import (
    activity_log_aggregates, activity_log_queryset, activity_log_selection, serialize_activity_log_row,
)
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
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'
    pagination_class = ReportPagination

    @extend_schema(summary='Activity log across daily reports', tags=['Reports'])
    def get(self, request, project_pk=None):
        from django.core.cache import cache

        from common.cache_helpers import cache_key, params_fingerprint

        qs, selection = activity_log_selection(project_pk, request.query_params)
        paginator = ReportPagination()
        page_num = request.query_params.get('page') or '1'
        ver = cache.get(f'activity_log_version:{project_pk}') or 0
        cache_k = cache_key(
            'activity_log_v3', project_pk, ver, params_fingerprint(selection), page_num, paginator.get_page_size(request),
        )
        cacheable = selection['approved_only']
        cached = cache.get(cache_k) if cacheable else None
        if cached is not None:
            # Recreate navigation links with this request's aliases, scheme and host.
            paginator.paginate_queryset(range(cached['count']), request)
            response = paginator.get_paginated_response(cached['results'])
            response.data['aggregates'] = cached['aggregates']
            return response

        # A lifecycle commit must not split the totals/count and rows across snapshots.
        outer_transaction = connection.in_atomic_block
        with transaction.atomic():
            if connection.vendor == 'postgresql' and not outer_transaction:
                with connection.cursor() as cursor:
                    cursor.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            aggregates = activity_log_aggregates(qs)
            page = paginator.paginate_queryset(qs, request)
            rows = [serialize_activity_log_row(row) for row in page]
        response = paginator.get_paginated_response(rows)
        response.data['aggregates'] = aggregates
        if cacheable:
            cache.set(cache_k, {'count': response.data['count'], 'results': rows, 'aggregates': aggregates}, 300)
        return response


class ActivityLogFilterOptionsView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Distinct activity log filter values', tags=['Reports'])
    def get(self, request, project_pk=None):
        qs = activity_log_queryset(project_pk, request.query_params).order_by()
        values = {}
        for key, field in (
            ('zones', 'zone'), ('blocks', 'block'), ('subcontractors', 'subcontractor_name'),
            ('disciplines', 'source_discipline'), ('parcels', 'parcel'), ('floors', 'floor'),
            ('shifts', 'shift'), ('units', 'unit'),
        ):
            values[key] = list(
                qs.exclude(**{field: ''}).exclude(**{f'{field}__isnull': True})
                .order_by(field).values_list(field, flat=True).distinct()
            )
        values['contractors'] = [
            {'id': str(identity), 'name': name}
            for identity, name in qs.filter(
                contractor_ref__project_id=project_pk, contractor_ref__is_deleted=False,
            ).order_by('contractor_ref__name', 'contractor_ref_id').values_list(
                'contractor_ref_id', 'contractor_ref__name',
            ).distinct()
        ]
        return Response(values)


class ActivityLogExcelView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    @extend_schema(summary='Export filtered activity log as Shiraz FILE 1 Excel', tags=['Reports'])
    def get(self, request, project_pk=None):
        from django.http import HttpResponse
        from field_reports.shiraz_file1_excel import ShirazFile1ExcelBuilder

        qs = activity_log_queryset(project_pk, request.query_params)
        builder = ShirazFile1ExcelBuilder(qs)
        excel_bytes, filename = builder.build()

        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
