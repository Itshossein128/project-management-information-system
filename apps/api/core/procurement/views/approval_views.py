"""Approval workflow action views (approve / reject / return / submit)."""
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from procurement.models import ApprovalLog, RequisitionHeader
from procurement.serializers import ApprovalActionSerializer, ApprovalLogSerializer, RequisitionHeaderSerializer


class _BaseApprovalActionView(APIView):
    """Base class for approval action views."""
    action: str = ''

    def post(self, request, project_pk=None, pk=None):
        from procurement.services.approval_engine import transition

        requisition = get_object_or_404(
            RequisitionHeader,
            id=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        requisition = transition(
            requisition,
            action=self.action,
            performed_by=request.user,
            comments=serializer.validated_data.get('comments', ''),
        )
        return Response(RequisitionHeaderSerializer(requisition).data)


class RequisitionSubmitView(_BaseApprovalActionView):
    """Submit a DRAFT requisition → moves to technical_review."""
    action = 'approve'


class RequisitionApproveView(_BaseApprovalActionView):
    """Approve the current step (generic approve action)."""
    action = 'approve'


class RequisitionRejectView(_BaseApprovalActionView):
    """Reject the requisition at the current step."""
    action = 'reject'


class RequisitionReturnView(_BaseApprovalActionView):
    """Return the requisition to the previous step."""
    action = 'return'


class ApprovalLogListView(APIView):
    """List all approval log entries for a requisition."""

    def get(self, request, project_pk=None, pk=None):
        requisition = get_object_or_404(
            RequisitionHeader,
            id=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        logs = ApprovalLog.objects.filter(requisition=requisition).order_by('performed_at')
        serializer = ApprovalLogSerializer(logs, many=True)
        return Response(serializer.data)
