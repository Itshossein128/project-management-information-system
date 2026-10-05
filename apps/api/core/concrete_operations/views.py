import csv
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.viewsets import ProjectScopedViewSet
from concrete_operations.models import ConcreteBatch, ReadyMixDelivery
from concrete_operations.serializers import ConcreteBatchSerializer, ReadyMixDeliverySerializer
from field_reports.models import DailyReportConcreteLog
from permissions.project import HasProjectPermission, IsProjectMember
from rest_framework import serializers


class ConcreteBatchViewSet(ProjectScopedViewSet):
    queryset = ConcreteBatch.objects.all()
    serializer_class = ConcreteBatchSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']


class ReadyMixDeliveryViewSet(ProjectScopedViewSet):
    queryset = ReadyMixDelivery.objects.select_related('supplier').all()
    serializer_class = ReadyMixDeliverySerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']


def filtered_rows(project_pk, params):
    date_from = params.get('date_from')
    date_to = params.get('date_to')
    parser = serializers.DateField()
    start = parser.run_validation(date_from) if date_from is not None else None
    end = parser.run_validation(date_to) if date_to is not None else None
    if start and end and start > end:
        raise ValidationError({'date_to': 'Must be on or after date_from.'})
    batches = ConcreteBatch.objects.filter(project_id=project_pk)
    deliveries = ReadyMixDelivery.objects.filter(project_id=project_pk).select_related('supplier')
    poured = DailyReportConcreteLog.objects.filter(report__project_id=project_pk, is_deleted=False, report__is_deleted=False)
    if start:
        batches = batches.filter(date__gte=start)
        deliveries = deliveries.filter(date__gte=start)
        poured = poured.filter(report__report_date__gte=start)
    if end:
        batches = batches.filter(date__lte=end)
        deliveries = deliveries.filter(date__lte=end)
        poured = poured.filter(report__report_date__lte=end)
    return batches, deliveries, poured


def totals(batches, deliveries, poured):
    return {
        'produced_m3': batches.aggregate(total=Sum('volume_m3'))['total'] or Decimal('0'),
        'delivered_m3': deliveries.aggregate(total=Sum('volume_m3'))['total'] or Decimal('0'),
        'poured_m3': poured.aggregate(total=Sum('volume_m3'))['total'] or Decimal('0'),
    }


class ConcreteOperationsReportView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    def get(self, request, project_pk, export=False):
        batches, deliveries, poured = filtered_rows(project_pk, request.query_params)
        summary = totals(batches, deliveries, poured)
        if not export:
            return Response({key: str(value) for key, value in summary.items()})
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="concrete-operations.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['type', 'date', 'volume_m3', 'cement_kg', 'sand_kg', 'aggregate_kg', 'water_l', 'plasticizer_l', 'supplier', 'ticket_number'])
        for row in batches:
            writer.writerow(['batch', row.date, row.volume_m3, row.cement_kg, row.sand_kg, row.aggregate_kg, row.water_l, row.plasticizer_l, '', ''])
        for row in deliveries:
            writer.writerow(['delivery', row.date, row.volume_m3, '', '', '', '', '', row.supplier.supplier_name, row.ticket_number])
        for key, value in summary.items():
            writer.writerow([key, '', value])
        return response
