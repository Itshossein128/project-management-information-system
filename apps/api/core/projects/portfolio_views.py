"""Portfolio summary across projects the user can view."""
from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cost_control.models import ActualCost, Budget, Commitment, CommitmentStatus
from master_data.models import MemberStatus, ProjectMember
from projects.models import Project


class PortfolioSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Portfolio summary for accessible projects', tags=['Central Data'])
    def get(self, request):
        project_ids = ProjectMember.objects.filter(
            user=request.user,
            status=MemberStatus.ACTIVE,
        ).values_list('project_id', flat=True)
        projects = Project.objects.filter(id__in=project_ids).order_by('project_name')

        rows = []
        by_currency: dict[str, dict] = {}
        for project in projects:
            budget = (
                Budget.objects.filter(project=project, is_deleted=False).aggregate(
                    t=Sum('budget_amount')
                )['t']
                or 0
            )
            actual = (
                ActualCost.objects.filter(project=project, is_deleted=False).aggregate(
                    t=Sum('amount')
                )['t']
                or 0
            )
            commitment = (
                Commitment.objects.filter(
                    project=project,
                    is_deleted=False,
                    status=CommitmentStatus.APPROVED,
                ).aggregate(t=Sum('amount'))['t']
                or 0
            )
            currency = project.currency or 'IRR'
            row = {
                'project_id': str(project.id),
                'project_code': project.project_code,
                'project_name': project.project_name,
                'currency': currency,
                'total_budget': float(budget),
                'total_commitment': float(commitment),
                'total_actual': float(actual),
                'spi': None,
                'cpi': None,
            }
            rows.append(row)
            bucket = by_currency.setdefault(
                currency,
                {'total_budget': 0.0, 'total_commitment': 0.0, 'total_actual': 0.0, 'project_count': 0},
            )
            bucket['total_budget'] += row['total_budget']
            bucket['total_commitment'] += row['total_commitment']
            bucket['total_actual'] += row['total_actual']
            bucket['project_count'] += 1

        return Response(
            {
                'projects': rows,
                'totals_by_currency': by_currency,
                'totals': {
                    'project_count': len(rows),
                    'note': 'Use totals_by_currency; mixed currencies are not silently summed.',
                },
            }
        )
