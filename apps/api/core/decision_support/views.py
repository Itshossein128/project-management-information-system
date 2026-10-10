from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from common.viewsets import ProjectScopedViewSet
from config.exceptions import CodedValidationError
from config.pagination import DefaultPageNumberPagination
from decision_support.models import DecisionCase, DecisionRun
from decision_support.serializers import (
    DecisionCaseListSerializer,
    DecisionCaseSerializer,
    DecisionRunCreateSerializer,
    DecisionRunSerializer,
)
from decision_support.services.case_service import create_case, update_case
from decision_support.services.execution_service import create_stub_run
from permissions.project import HasProjectPermission, IsProjectMember


@extend_schema_view(
    list=extend_schema(summary='List decision cases', tags=['Decision Support']),
    create=extend_schema(summary='Create decision case', tags=['Decision Support']),
    retrieve=extend_schema(summary='Get decision case', tags=['Decision Support']),
    partial_update=extend_schema(summary='Update decision case', tags=['Decision Support']),
    destroy=extend_schema(summary='Delete decision case', tags=['Decision Support']),
)
class DecisionCaseViewSet(ProjectScopedViewSet):
    queryset = DecisionCase.objects.all()
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_decision_support'
    edit_permission = 'edit_decision_support'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'list':
            return DecisionCaseListSerializer
        return DecisionCaseSerializer

    def create(self, request, *args, **kwargs):
        case = create_case(self.get_project_id(), request.user, request.data)
        return Response(DecisionCaseSerializer(case).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        case = self.get_object()
        case = update_case(case, request.user, request.data)
        return Response(DecisionCaseSerializer(case).data)


@extend_schema_view(
    list=extend_schema(summary='List decision runs', tags=['Decision Support']),
    create=extend_schema(summary='Create stub decision run', tags=['Decision Support']),
    retrieve=extend_schema(summary='Get decision run', tags=['Decision Support']),
)
class DecisionRunViewSet(viewsets.ViewSet):
    """Append-only runs nested under a case. No update/delete."""

    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    pagination_class = DefaultPageNumberPagination

    def get_permissions(self):
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return 'view_decision_support'
        return 'edit_decision_support'

    def get_project_id(self):
        return self.kwargs['project_pk']

    def get_case(self) -> DecisionCase:
        return get_object_or_404(
            DecisionCase.objects.filter(project_id=self.get_project_id()),
            pk=self.kwargs['case_pk'],
        )

    def list(self, request, project_pk=None, case_pk=None):
        case = self.get_case()
        qs = DecisionRun.objects.filter(case=case).select_related('extracted_by')
        paginator = DefaultPageNumberPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(DecisionRunSerializer(page, many=True).data)
        return Response(DecisionRunSerializer(qs, many=True).data)

    def retrieve(self, request, project_pk=None, case_pk=None, pk=None):
        case = self.get_case()
        run = get_object_or_404(DecisionRun.objects.filter(case=case), pk=pk)
        return Response(DecisionRunSerializer(run).data)

    def create(self, request, project_pk=None, case_pk=None):
        case = self.get_case()
        ser = DecisionRunCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        run = create_stub_run(case, ser.validated_data['method'], request.user)
        return Response(DecisionRunSerializer(run).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, project_pk=None, case_pk=None, pk=None):
        raise CodedValidationError(detail=_('Decision runs are immutable.'), code='run_immutable')

    def update(self, request, project_pk=None, case_pk=None, pk=None):
        raise CodedValidationError(detail=_('Decision runs are immutable.'), code='run_immutable')

    def destroy(self, request, project_pk=None, case_pk=None, pk=None):
        raise CodedValidationError(detail=_('Decision runs are immutable.'), code='run_immutable')
