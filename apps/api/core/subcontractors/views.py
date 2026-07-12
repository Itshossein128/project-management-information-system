from datetime import date

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint
from permissions.project import HasProjectPermission, IsProjectMember
from subcontractors.models import Subcontractor, SubcontractorPerformanceScore, SubcontractorWarning
from subcontractors.serializers import (
    PerformanceScoreSerializer,
    SubcontractorDetailSerializer,
    SubcontractorSerializer,
    WarningSerializer,
)
from subcontractors.services.risk_service import compute_risk_flag
from subcontractors.services.performance import SubcontractorPerformanceService


class SubScopedViewSet(viewsets.ModelViewSet):
    view_permission = 'view_contracts'
    edit_permission = 'edit_contracts'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return self.view_permission
        return self.edit_permission

    def get_queryset(self):
        return Subcontractor.objects.filter(project_id=self.kwargs['project_pk'], is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs['project_pk'],
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.updated_by = request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubcontractorViewSet(SubScopedViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcontractorDetailSerializer
        return SubcontractorSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return Response({'results': SubcontractorSerializer(qs, many=True).data})


class ScoreCreateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def post(self, request, project_pk=None, pk=None):
        sub = Subcontractor.objects.get(pk=pk, project_id=project_pk, is_deleted=False)
        ser = PerformanceScoreSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        service = SubcontractorPerformanceService()
        score = service.create_score(sub, ser.validated_data, request.user)
        return Response(PerformanceScoreSerializer(score).data, status=201)


class WarningCreateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def post(self, request, project_pk=None, pk=None):
        sub = Subcontractor.objects.get(pk=pk, project_id=project_pk, is_deleted=False)
        ser = WarningSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        service = SubcontractorPerformanceService()
        w = service.create_warning(sub, ser.validated_data, request.user)
        return Response(WarningSerializer(w).data, status=201)


class WarningPatchView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def patch(self, request, project_pk=None, pk=None, wid=None):
        w = SubcontractorWarning.objects.get(
            pk=wid, subcontractor_id=pk, subcontractor__project_id=project_pk, is_deleted=False
        )
        ser = WarningSerializer(w, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        if ser.validated_data.get('resolved') and not w.resolved_date:
            w.resolved_date = date.today()
        ser.save(updated_by=request.user)
        return Response(WarningSerializer(w).data)


class RiskSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_contracts'

    @extend_schema(summary='At-risk subcontractors', tags=['Subcontractors'])
    def get(self, request, project_pk=None):
        fp = params_fingerprint({})
        key = cache_key('subcontractor_risk', project_pk, fp)

        def compute():
            results = []
            for sub in Subcontractor.objects.filter(project_id=project_pk, is_deleted=False):
                flag, reasons = compute_risk_flag(sub)
                if flag:
                    results.append({
                        'id': str(sub.id),
                        'company_name': sub.company_name,
                        'risk_reasons': reasons,
                    })
            return results

        data = get_cached_or_compute(key, 3600, compute)
        return Response({'results': data})


def _fire_risk_alert(sub, reasons):
    try:
        from alerts.services.evaluation import fire_subcontractor_at_risk
        fire_subcontractor_at_risk(sub, reasons)
    except Exception:
        pass
