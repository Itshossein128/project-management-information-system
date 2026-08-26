"""Report views: liquidity dashboard, material deviation, audit trail, procurement status."""
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project


class LiquidityDashboardView(APIView):
    """
    Requisitions on hold due to missing budget.
    GET /api/v1/projects/{pid}/reports/liquidity/
    """

    def get(self, request, project_pk=None):
        from django.db.models import Count, Sum
        from procurement.models import RequisitionHeader, ItemStatus

        project = get_object_or_404(Project, id=project_pk)

        on_hold_items = (
            __import__('procurement.models', fromlist=['RequisitionItem'])
            .RequisitionItem.objects.filter(
                header__project=project,
                status=ItemStatus.ON_HOLD,
                is_deleted=False,
            )
            .select_related('header__block', 'material')
        )

        data = []
        for item in on_hold_items:
            data.append({
                'requisition_number': item.header.requisition_number,
                'block_code': item.header.block.block_code,
                'block_name': item.header.block.block_name,
                'material_code': item.material.material_code,
                'material_name': item.material.material_name,
                'requested_qty': item.requested_qty,
                'status': item.status,
            })

        return Response({
            'project_id': str(project.id),
            'on_hold_count': len(data),
            'items': data,
        })


class MaterialDeviationReportView(APIView):
    """
    Requested vs purchased vs consumed per material per block.
    GET /api/v1/projects/{pid}/reports/material-deviation/
    """

    def get(self, request, project_pk=None):
        from django.db.models import Sum
        from procurement.models import RequisitionItem, InventoryAllocation

        project = get_object_or_404(Project, id=project_pk)

        # Requested quantities by block + material
        requested = (
            RequisitionItem.objects.filter(
                header__project=project,
                is_deleted=False,
            )
            .values(
                'header__block__block_code',
                'header__block__block_name',
                'material__material_code',
                'material__material_name',
            )
            .annotate(
                total_requested=Sum('requested_qty'),
                total_approved=Sum('approved_qty'),
                total_purchased=Sum('purchased_qty'),
            )
            .order_by('header__block__block_code', 'material__material_code')
        )

        # Issued quantities from allocations
        issued_map = {}
        issued_qs = (
            InventoryAllocation.objects.filter(
                block__project=project,
                is_deleted=False,
            )
            .values('block__block_code', 'material__material_code')
            .annotate(total_issued=Sum('issued_qty'))
        )
        for row in issued_qs:
            key = (row['block__block_code'], row['material__material_code'])
            issued_map[key] = row['total_issued']

        results = []
        for row in requested:
            block_code = row['header__block__block_code']
            material_code = row['material__material_code']
            total_issued = issued_map.get((block_code, material_code), 0)
            results.append({
                'block_code': block_code,
                'block_name': row['header__block__block_name'],
                'material_code': material_code,
                'material_name': row['material__material_name'],
                'total_requested': row['total_requested'],
                'total_approved': row['total_approved'],
                'total_purchased': row['total_purchased'],
                'total_issued': total_issued,
                'deviation': (row['total_requested'] or 0) - (row['total_purchased'] or 0),
            })

        return Response({'project_id': str(project.id), 'items': results})


class AuditTrailReportView(APIView):
    """
    Full approval audit trail for all requisitions in a project.
    GET /api/v1/projects/{pid}/reports/audit-trail/
    """

    def get(self, request, project_pk=None):
        from procurement.models import ApprovalLog
        from procurement.serializers import ApprovalLogSerializer

        project = get_object_or_404(Project, id=project_pk)

        # Optional filter by requisition
        req_id = request.query_params.get('requisition_id')
        logs_qs = ApprovalLog.objects.filter(
            requisition__project=project,
        ).select_related('requisition', 'performed_by').order_by('performed_at')

        if req_id:
            logs_qs = logs_qs.filter(requisition_id=req_id)

        serializer = ApprovalLogSerializer(logs_qs, many=True)
        return Response({
            'project_id': str(project.id),
            'count': logs_qs.count(),
            'logs': serializer.data,
        })


class ProcurementStatusReportView(APIView):
    """
    Items assigned to each procurement officer and purchase progress.
    GET /api/v1/projects/{pid}/reports/procurement-status/
    """

    def get(self, request, project_pk=None):
        from django.db.models import Count, Sum
        from procurement.models import RequisitionItem

        project = get_object_or_404(Project, id=project_pk)

        officer_summary = (
            RequisitionItem.objects.filter(
                header__project=project,
                assigned_to__isnull=False,
                is_deleted=False,
            )
            .values(
                'assigned_to',
                'assigned_to__full_name',
                'assigned_to__username',
                'status',
            )
            .annotate(
                item_count=Count('id'),
                total_requested=Sum('requested_qty'),
                total_purchased=Sum('purchased_qty'),
            )
            .order_by('assigned_to', 'status')
        )

        summary_list = []
        for row in officer_summary:
            full_name = row.get('assigned_to__full_name') or row.get('assigned_to__username') or ''
            row['assigned_to__full_name'] = full_name
            row['assigned_to__first_name'] = full_name
            row['assigned_to__last_name'] = ''
            summary_list.append(row)

        return Response({
            'project_id': str(project.id),
            'summary': summary_list,
        })
