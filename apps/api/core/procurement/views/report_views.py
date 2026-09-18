"""Report views: liquidity dashboard, material deviation, audit trail, procurement status."""
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.mixins import PROJECT_MEMBER_PERMISSIONS
from projects.models import Project


class LiquidityDashboardView(APIView):
    """
    Requisitions on hold due to missing budget & block liquidity status.
    GET /api/v1/projects/{pid}/reports/liquidity/
    """
    permission_classes = PROJECT_MEMBER_PERMISSIONS

    def get(self, request, project_pk=None):
        from django.db.models import Sum
        from procurement.models import Block, ItemStatus, RequisitionItem

        project = get_object_or_404(Project, id=project_pk)

        blocks = Block.objects.filter(project=project, is_deleted=False)

        req_by_block = (
            RequisitionItem.objects.filter(
                header__project=project,
                is_deleted=False,
            )
            .values('header__block_id')
            .annotate(total_req=Sum('requested_qty'))
        )
        req_map = {row['header__block_id']: float(row['total_req'] or 0) for row in req_by_block}

        on_hold_items = (
            RequisitionItem.objects.filter(
                header__project=project,
                status=ItemStatus.ON_HOLD,
                is_deleted=False,
            )
            .select_related('header__block', 'material')
        )

        on_hold_data = []
        for item in on_hold_items:
            header = item.header
            on_hold_data.append({
                'requisition_number': header.requisition_number,
                'scope': header.scope,
                'scope_display': header.get_scope_display(),
                'block_code': header.block.block_code,
                'block_name': header.block.block_name,
                'material_code': item.material.material_code,
                'material_name': item.material.material_name,
                'requested_qty': float(item.requested_qty),
                'status': item.status,
            })

        liquidity_status = []
        for block in blocks:
            budget = float(block.budget or 0)
            total_requested_value = req_map.get(block.id, 0.0)
            remaining_liquidity = budget - total_requested_value
            liquidity_status.append({
                'block_code': block.block_code,
                'block_name': block.block_name,
                'block_kind': getattr(block, 'block_kind', 'standard'),
                'budget': budget,
                'total_requested_value': total_requested_value,
                'remaining_liquidity': remaining_liquidity,
            })

        return Response({
            'project_id': str(project.id),
            'on_hold_count': len(on_hold_data),
            'items': on_hold_data,
            'liquidity_status': liquidity_status,
        })


class MaterialDeviationReportView(APIView):
    """
    Requested vs purchased vs consumed per material per block with deviation calculation.
    GET /api/v1/projects/{pid}/reports/material-deviation/
    """
    permission_classes = PROJECT_MEMBER_PERMISSIONS

    def get(self, request, project_pk=None):
        from django.db.models import Sum
        from procurement.models import InventoryAllocation, RequisitionItem

        project = get_object_or_404(Project, id=project_pk)

        # Requested quantities by block + material
        requested = (
            RequisitionItem.objects.filter(
                header__project=project,
                is_deleted=False,
            )
            .values(
                'header__scope',
                'header__block__block_code',
                'header__block__block_name',
                'header__block__block_kind',
                'material__material_code',
                'material__material_name',
                'material__estimated_total_qty',
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
            issued_map[key] = float(row['total_issued'] or 0)

        deviation_data = []
        for row in requested:
            block_code = row['header__block__block_code']
            material_code = row['material__material_code']
            material_name = row['material__material_name']
            est_raw = row['material__estimated_total_qty']
            estimated_qty = float(est_raw) if est_raw is not None else None
            requested_qty = float(row['total_requested'] or 0)
            total_approved = float(row['total_approved'] or 0)
            total_purchased = float(row['total_purchased'] or 0)
            total_issued = issued_map.get((block_code, material_code), 0.0)

            if estimated_qty is not None and estimated_qty > 0:
                deviation_qty = requested_qty - estimated_qty
                deviation_percent = ((requested_qty - estimated_qty) / estimated_qty) * 100.0
            else:
                deviation_qty = requested_qty
                deviation_percent = 0.0

            deviation_data.append({
                'scope': row['header__scope'],
                'block_code': block_code,
                'block_name': row['header__block__block_name'],
                'block_kind': row['header__block__block_kind'],
                'material_code': material_code,
                'material_name': material_name,
                'estimated_qty': estimated_qty,
                'requested_qty': requested_qty,
                'deviation_qty': deviation_qty,
                'deviation_percent': deviation_percent,
                'total_approved': total_approved,
                'total_purchased': total_purchased,
                'total_issued': total_issued,
                'deviation': requested_qty - total_purchased,
            })

        return Response({
            'project_id': str(project.id),
            'deviation_data': deviation_data,
            'items': deviation_data,
        })


class AuditTrailReportView(APIView):
    """
    Full approval audit trail for all requisitions in a project.
    GET /api/v1/projects/{pid}/reports/audit-trail/
    """
    permission_classes = PROJECT_MEMBER_PERMISSIONS

    def get(self, request, project_pk=None):
        from procurement.models import ApprovalAction, ApprovalLog
        from procurement.serializers import ApprovalLogSerializer

        project = get_object_or_404(Project, id=project_pk)

        req_id = request.query_params.get('requisition_id')
        action_filter = request.query_params.get('action')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        logs_qs = ApprovalLog.objects.filter(
            requisition__project=project,
        ).select_related('requisition', 'performed_by').order_by('performed_at')

        if req_id:
            logs_qs = logs_qs.filter(requisition_id=req_id)
        if action_filter:
            logs_qs = logs_qs.filter(action=action_filter)
        if date_from:
            logs_qs = logs_qs.filter(performed_at__date__gte=date_from)
        if date_to:
            logs_qs = logs_qs.filter(performed_at__date__lte=date_to)

        total_actions = logs_qs.count()
        approved_actions = logs_qs.filter(action=ApprovalAction.APPROVE).count()
        rejected_actions = logs_qs.filter(action=ApprovalAction.REJECT).count()

        summary = {
            'total_actions': total_actions,
            'approved_actions': approved_actions,
            'rejected_actions': rejected_actions,
        }

        logs = list(logs_qs)
        payload = ApprovalLogSerializer(logs, many=True).data
        previous_at: dict = {}
        for index, log in enumerate(logs):
            req_id_key = str(log.requisition_id)
            delay_hours = None
            prev_at = previous_at.get(req_id_key)
            if prev_at is not None:
                delay_hours = round((log.performed_at - prev_at).total_seconds() / 3600.0, 2)
            previous_at[req_id_key] = log.performed_at
            payload[index]['delay_hours'] = delay_hours

        return Response({
            'project_id': str(project.id),
            'count': total_actions,
            'summary': summary,
            'logs': payload,
        })


class ProcurementStatusReportView(APIView):
    """
    Items assigned to each procurement officer and purchase progress.
    GET /api/v1/projects/{pid}/reports/procurement-status/
    """
    permission_classes = PROJECT_MEMBER_PERMISSIONS

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
