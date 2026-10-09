from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.viewsets import ProjectScopedViewSet
from cost_control.cbs_services import (
    CBSConflictError,
    approve_commitment,
    create_cbs_node,
    create_payment,
    delete_cbs_node,
    posted_payments_total,
)
from cost_control.models import Commitment, CostBreakdownNode, Payment
from cost_control.serializers import (
    CommitmentSerializer,
    CostBreakdownNodeSerializer,
    PaymentSerializer,
)
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from rest_framework.exceptions import ValidationError


class CBSListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    @extend_schema(summary='List CBS nodes', tags=['Central Data'])
    def get(self, request, project_pk=None):
        nodes = CostBreakdownNode.objects.filter(project_id=project_pk, is_deleted=False).order_by('path')
        return Response(CostBreakdownNodeSerializer(nodes, many=True).data)

    @extend_schema(summary='Create CBS node', tags=['Central Data'])
    def post(self, request, project_pk=None):
        ser = CostBreakdownNodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            node = create_cbs_node(
                project_id=project_pk,
                parent_id=request.data.get('parent_id'),
                cbs_code=data['cbs_code'],
                cbs_name=data['cbs_name'],
                cost_type=data.get('cost_type', ''),
                description=data.get('description', ''),
                created_by=request.user,
            )
        except ValidationError as exc:
            return Response(exc.detail, status=400)
        return Response(CostBreakdownNodeSerializer(node).data, status=201)


class CBSDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_costs'

    @extend_schema(summary='Soft-delete CBS node', tags=['Central Data'])
    def delete(self, request, project_pk=None, pk=None):
        node = get_object_or_404(CostBreakdownNode, pk=pk, project_id=project_pk, is_deleted=False)
        try:
            delete_cbs_node(node, user=request.user)
        except CBSConflictError as exc:
            return Response({'code': 'conflict', 'message': str(exc)}, status=409)
        return Response(status=204)


class CommitmentViewSet(ProjectScopedViewSet):
    queryset = Commitment.objects.all()
    serializer_class = CommitmentSerializer
    view_permission = 'view_costs'
    edit_permission = 'edit_costs'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        try:
            ctx['project'] = Project.objects.get(pk=self.get_project_id())
        except Exception:
            pass
        return ctx

    def perform_create(self, serializer, **kwargs):
        from projects.readiness import assert_project_allows_binding_commitment

        project = Project.objects.get(pk=self.get_project_id())
        assert_project_allows_binding_commitment(project)
        super().perform_create(serializer, **kwargs)

    @extend_schema(summary='Approve commitment', tags=['Central Data'])
    def approve(self, request, project_pk=None, pk=None):
        commitment = self.get_object()
        try:
            approve_commitment(commitment)
        except ValidationError as exc:
            return Response(exc.detail, status=400)
        return Response(CommitmentSerializer(commitment).data)


class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_costs' if self.request.method == 'GET' else 'edit_costs'

    def get(self, request, project_pk=None):
        rows = Payment.objects.filter(project_id=project_pk, is_deleted=False)
        return Response(PaymentSerializer(rows, many=True).data)

    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        ser = PaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        commitment = data.get('commitment')
        actual_cost = data.get('actual_cost')
        if commitment is not None and str(commitment.project_id) != str(project_pk):
            return Response({'commitment': 'Must belong to this project.'}, status=400)
        if actual_cost is not None and str(actual_cost.project_id) != str(project_pk):
            return Response({'actual_cost': 'Must belong to this project.'}, status=400)
        try:
            payment = create_payment(
                project=project,
                commitment=commitment,
                actual_cost=actual_cost,
                amount=data['amount'],
                paid_at=data['paid_at'],
                user=request.user,
                currency=data.get('currency', 'IRR'),
                document_ref=data.get('document_ref', ''),
                fx_rate=data.get('fx_rate'),
                acknowledge_duplicate_exception=bool(
                    data.get('acknowledge_duplicate_exception')
                ),
                exception_reason=data.get('exception_reason', ''),
            )
        except ValidationError as exc:
            return Response(exc.detail, status=400)
        return Response(PaymentSerializer(payment).data, status=201)


class LedgerReportView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_costs'

    @extend_schema(summary='Cost–commitment–payment ledger report', tags=['Cost Control'])
    def get(self, request, project_pk=None):
        from common.jalali import parse_jalali_or_gregorian
        from cost_control.services.ledger_report_service import build_ledger_report

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        return Response(
            build_ledger_report(
                project_pk,
                date_from=parse_jalali_or_gregorian(date_from) if date_from else None,
                date_to=parse_jalali_or_gregorian(date_to) if date_to else None,
                commitment_id=request.query_params.get('commitment_id'),
                document_ref=request.query_params.get('document_ref'),
            )
        )


class ContractCostRemainingView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_costs'

    @extend_schema(summary='Contract remaining via cost payments', tags=['Cost Control'])
    def get(self, request, project_pk=None):
        from cost_control.services.contract_remaining_service import contract_cost_remaining

        contract_id = request.query_params.get('contract_id')
        if not contract_id:
            return Response({'contract_id': 'Required.'}, status=400)
        return Response(contract_cost_remaining(project_pk, contract_id))
