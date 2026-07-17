from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint
from common.cache_utils import invalidate_project_caches
from permissions.project import HasProjectPermission, IsProjectMember
from subcontractors.models import Subcontractor, SubcontractorPerformanceScore, SubcontractorWarning
from subcontractors.serializers import (
    PerformanceScoreSerializer,
    SubcontractorDetailSerializer,
    SubcontractorSerializer,
    WarningSerializer,
)
from subcontractors.services.performance import SubcontractorPerformanceService
from subcontractors.services.risk_service import average_overall_score, compute_risk_flag, score_trend


def _invalidate_subcontractor_caches(project_id):
    invalidate_project_caches(project_id)


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
        return Subcontractor.objects.filter(
            project_id=self.kwargs['project_pk'],
            is_deleted=False
        ).prefetch_related('scores', 'warnings')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs['project_pk'],
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        _invalidate_subcontractor_caches(self.kwargs['project_pk'])

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        _invalidate_subcontractor_caches(self.kwargs['project_pk'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.updated_by = request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        _invalidate_subcontractor_caches(self.kwargs['project_pk'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubcontractorViewSet(SubScopedViewSet):
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcontractorDetailSerializer
        return SubcontractorSerializer

    def _filter_queryset(self, qs, request):
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        discipline = request.query_params.get('discipline')
        if discipline:
            qs = qs.filter(discipline__icontains=discipline)
        if request.query_params.get('risk_only') == 'true':
            at_risk_ids = []
            for sub in qs:
                if compute_risk_flag(sub)[0]:
                    at_risk_ids.append(sub.id)
            qs = qs.filter(id__in=at_risk_ids)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self._filter_queryset(self.get_queryset(), request)
        return Response({'results': SubcontractorSerializer(qs, many=True).data})


class ScoreListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.request.method == 'GET':
            return 'view_contracts'
        return 'edit_contracts'

    @extend_schema(summary='List performance scores', tags=['Subcontractors'])
    def get(self, request, project_pk=None, pk=None):
        sub = get_object_or_404(Subcontractor, pk=pk, project_id=project_pk, is_deleted=False)
        scores = sub.scores.filter(is_deleted=False).order_by('-score_date')
        return Response({
            'results': PerformanceScoreSerializer(scores, many=True).data,
            'average_overall': average_overall_score(sub),
            'trend': score_trend(sub),
        })

    @extend_schema(summary='Create performance score', tags=['Subcontractors'])
    def post(self, request, project_pk=None, pk=None):
        sub = get_object_or_404(Subcontractor, pk=pk, project_id=project_pk, is_deleted=False)
        ser = PerformanceScoreSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        service = SubcontractorPerformanceService()
        score = service.create_score(sub, ser.validated_data, request.user)
        _invalidate_subcontractor_caches(project_pk)
        return Response(PerformanceScoreSerializer(score).data, status=201)


class ScoreDetailView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def patch(self, request, project_pk=None, pk=None, scid=None):
        score = get_object_or_404(
            SubcontractorPerformanceScore,
            pk=scid,
            subcontractor_id=pk,
            subcontractor__project_id=project_pk,
            is_deleted=False,
        )
        ser = PerformanceScoreSerializer(score, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for attr, val in ser.validated_data.items():
            setattr(score, attr, val)
        score.updated_by = request.user
        score.save()
        _invalidate_subcontractor_caches(project_pk)
        return Response(PerformanceScoreSerializer(score).data)

    def delete(self, request, project_pk=None, pk=None, scid=None):
        score = get_object_or_404(
            SubcontractorPerformanceScore,
            pk=scid,
            subcontractor_id=pk,
            subcontractor__project_id=project_pk,
            is_deleted=False,
        )
        score.is_deleted = True
        score.deleted_at = timezone.now()
        score.updated_by = request.user
        score.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        _invalidate_subcontractor_caches(project_pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WarningListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.request.method == 'GET':
            return 'view_contracts'
        return 'edit_contracts'

    def get(self, request, project_pk=None, pk=None):
        sub = get_object_or_404(Subcontractor, pk=pk, project_id=project_pk, is_deleted=False)
        warnings = sub.warnings.filter(is_deleted=False).order_by('-warning_date')
        return Response({'results': WarningSerializer(warnings, many=True).data})

    def post(self, request, project_pk=None, pk=None):
        sub = get_object_or_404(Subcontractor, pk=pk, project_id=project_pk, is_deleted=False)
        ser = WarningSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        service = SubcontractorPerformanceService()
        w = service.create_warning(sub, ser.validated_data, request.user)
        _invalidate_subcontractor_caches(project_pk)
        return Response(WarningSerializer(w).data, status=201)


class WarningPatchView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_contracts'

    def patch(self, request, project_pk=None, pk=None, wid=None):
        w = get_object_or_404(
            SubcontractorWarning,
            pk=wid,
            subcontractor_id=pk,
            subcontractor__project_id=project_pk,
            is_deleted=False,
        )
        ser = WarningSerializer(w, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for attr, val in ser.validated_data.items():
            setattr(w, attr, val)
        if w.resolved and not w.resolved_date:
            w.resolved_date = date.today()
        w.updated_by = request.user
        w.save()
        _invalidate_subcontractor_caches(project_pk)
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
