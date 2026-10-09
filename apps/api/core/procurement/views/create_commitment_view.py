"""Convert approved requisition into a draft cost commitment."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from cost_control.serializers import CommitmentSerializer
from cost_control.services.commitment_origin_service import create_commitment_from_requisition
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from rest_framework.exceptions import ValidationError


class CreateCommitmentFromRequisitionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_costs'

    @extend_schema(summary='Create commitment from approved requisition', tags=['Procurement'])
    def post(self, request, project_pk=None, pk=None):
        project = Project.objects.get(pk=project_pk)
        data = request.data
        if not data.get('commitment_number'):
            return Response({'commitment_number': 'Required.'}, status=400)
        if data.get('amount') is None:
            return Response({'amount': 'Required.'}, status=400)
        commitment_date = data.get('commitment_date')
        if not commitment_date:
            return Response({'commitment_date': 'Required.'}, status=400)
        try:
            parsed_date = parse_jalali_or_gregorian(commitment_date)
        except Exception:
            return Response({'commitment_date': 'Invalid date.'}, status=400)
        try:
            commitment = create_commitment_from_requisition(
                project=project,
                requisition_id=pk,
                user=request.user,
                commitment_number=data['commitment_number'],
                amount=data['amount'],
                commitment_date=parsed_date,
                currency=data.get('currency', 'IRR'),
                cbs_id=data.get('cbs'),
                wbs_id=data.get('wbs'),
                payment_terms=data.get('payment_terms', ''),
                contract_id=data.get('contract'),
                counterparty=data.get('counterparty', ''),
                description=data.get('description', ''),
                document_ref=data.get('document_ref', ''),
            )
        except ValidationError as exc:
            return Response(exc.detail, status=400)
        return Response(CommitmentSerializer(commitment).data, status=201)
