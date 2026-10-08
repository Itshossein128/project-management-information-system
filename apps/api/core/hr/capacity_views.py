from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from hr.models import ApprovedLaborRate, CapacityException, ResourceAllocation
from hr import services
from hr.serializers import (
    ApprovedLaborRateSerializer,
    ApprovedLaborRateWriteSerializer,
    CapacityExceptionSerializer,
    CapacityExceptionWriteSerializer,
    LaborCostEstimateRequestSerializer,
    PersonDossierSerializer,
    ResourceAllocationSerializer,
    ResourceAllocationWriteSerializer,
)
from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from projects.capability_service import assert_capability_enabled
from projects.models import Project

User = get_user_model()

WAGE_SENSITIVE_ESTIMATE_KEYS = ('amount', 'rate_amount', 'currency')


class HRProjectMixin:
    view_permission = 'view_hr'
    edit_permission = 'edit_hr'
    approve_permission = 'approve_hr'

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        assert_capability_enabled(project, 'hr')


class PersonDossierView(HRProjectMixin, APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    def get_permissions(self):
        # Self-read of non-sensitive dossier does not require view_hr (contract).
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            user_id = self.kwargs.get('user_id')
            if user_id is not None and str(user_id) == str(self.request.user.id):
                return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return self.view_permission
        return self.edit_permission

    def get_person(self, project_pk, user_id):
        person = get_object_or_404(User, pk=user_id)
        if not services.person_visible_in_project(person, project_pk):
            raise NotFound('User not visible in this project scope.')
        return person

    @extend_schema(summary='Get person dossier', tags=['HR'])
    def get(self, request, project_pk, user_id):
        person = self.get_person(project_pk, user_id)
        return Response(PersonDossierSerializer(person).data)

    @extend_schema(summary='Update person dossier', tags=['HR'])
    def patch(self, request, project_pk, user_id):
        person = self.get_person(project_pk, user_id)
        allowed_keys = {
            'skills',
            'qualifications',
            'org_unit_id',
            'supervisor_id',
            'status',
            'default_capacity_percent',
        }
        payload = {k: request.data[k] for k in allowed_keys if k in request.data}
        updated = services.update_dossier(person, payload)
        return Response(PersonDossierSerializer(updated).data)


@extend_schema_view(
    list=extend_schema(summary='List resource allocations', tags=['HR']),
    create=extend_schema(summary='Create resource allocation', tags=['HR']),
    retrieve=extend_schema(summary='Get resource allocation', tags=['HR']),
    partial_update=extend_schema(summary='Update resource allocation', tags=['HR']),
    destroy=extend_schema(summary='Soft-delete resource allocation', tags=['HR']),
)
class ResourceAllocationViewSet(HRProjectMixin, ProjectScopedViewSet):
    queryset = ResourceAllocation.objects.select_related('person', 'wbs', 'activity').all()
    serializer_class = ResourceAllocationSerializer
    pagination_class = DefaultPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('person_id'):
            qs = qs.filter(person_id=params['person_id'])
        if params.get('wbs_id'):
            qs = qs.filter(wbs_id=params['wbs_id'])
        if params.get('activity_id'):
            qs = qs.filter(activity_id=params['activity_id'])
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        from_date = params.get('from')
        to_date = params.get('to')
        if from_date and to_date:
            qs = qs.filter(start_date__lte=to_date, end_date__gte=from_date)
        return qs.order_by('-start_date')

    def create(self, request, *args, **kwargs):
        write = ResourceAllocationWriteSerializer(data=request.data)
        write.is_valid(raise_exception=True)
        project = get_object_or_404(Project, pk=self.get_project_id())
        allocation = services.create_allocation(
            project=project,
            person_id=write.validated_data['person_id'],
            user=request.user,
            data=write.validated_data,
        )
        return Response(ResourceAllocationSerializer(allocation).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        allocation = self.get_object()
        write = ResourceAllocationWriteSerializer(data=request.data, partial=True)
        write.is_valid(raise_exception=True)
        updated = services.update_allocation(allocation, request.user, write.validated_data)
        return Response(ResourceAllocationSerializer(updated).data)


class CapacityPreviewView(HRProjectMixin, APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return self.view_permission

    @extend_schema(summary='Preview person capacity commitment', tags=['HR'])
    def get(self, request, project_pk):
        person_id = request.query_params.get('person_id')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        capacity_percent = request.query_params.get('capacity_percent', '0')
        if not all([person_id, from_date, to_date]):
            return Response({'detail': 'person_id, from, and to are required.'}, status=400)
        person = get_object_or_404(User, pk=person_id)
        conflict = services.check_conflict(
            person,
            date.fromisoformat(from_date),
            date.fromisoformat(to_date),
            Decimal(capacity_percent),
        )
        def _fmt(value: Decimal) -> str:
            return f'{Decimal(value):.2f}'

        return Response(
            {
                'available': _fmt(conflict['available']),
                'committed': _fmt(conflict['committed']),
                'requested': _fmt(conflict['requested']),
                'would_conflict': conflict['would_conflict'],
                'overlapping_allocation_ids': conflict['overlapping_allocation_ids'],
            }
        )


@extend_schema_view(
    list=extend_schema(summary='List capacity exceptions', tags=['HR']),
    create=extend_schema(summary='Create capacity exception', tags=['HR']),
)
class CapacityExceptionViewSet(HRProjectMixin, ProjectScopedViewSet):
    queryset = CapacityException.objects.select_related('person').all()
    serializer_class = CapacityExceptionSerializer
    pagination_class = DefaultPageNumberPagination
    approve_actions = frozenset({'approve', 'reject'})
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        if self.action in self.approve_actions:
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return super().get_permissions()

    @property
    def required_permission(self):
        if self.action in self.approve_actions:
            return self.approve_permission
        if self.action in ('list', 'retrieve'):
            return self.view_permission
        return self.edit_permission

    def create(self, request, *args, **kwargs):
        write = CapacityExceptionWriteSerializer(data=request.data)
        write.is_valid(raise_exception=True)
        project = get_object_or_404(Project, pk=self.get_project_id())
        person = get_object_or_404(User, pk=write.validated_data['person_id'])
        exc = services.create_exception(
            project=project,
            person=person,
            user=request.user,
            data=write.validated_data,
        )
        return Response(CapacityExceptionSerializer(exc).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None, pk=None):
        exc = self.get_object()
        exc = services.submit_exception(exc, request.user)
        return Response(CapacityExceptionSerializer(exc).data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, project_pk=None, pk=None):
        exc = self.get_object()
        notes = request.data.get('decision_notes', '')
        exc, soft_sod_warn = services.approve_exception(exc, request.user, notes)
        data = CapacityExceptionSerializer(exc).data
        data['soft_sod_warn'] = soft_sod_warn
        return Response(data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, project_pk=None, pk=None):
        exc = self.get_object()
        notes = request.data.get('decision_notes', '')
        exc = services.reject_exception(exc, request.user, notes)
        return Response(CapacityExceptionSerializer(exc).data)


@extend_schema_view(
    list=extend_schema(summary='List approved labor rates', tags=['HR']),
    create=extend_schema(summary='Create approved labor rate', tags=['HR']),
    destroy=extend_schema(summary='Soft-delete approved labor rate', tags=['HR']),
)
class ApprovedLaborRateViewSet(HRProjectMixin, ProjectScopedViewSet):
    queryset = ApprovedLaborRate.objects.all()
    serializer_class = ApprovedLaborRateSerializer
    pagination_class = DefaultPageNumberPagination
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_pk'] = self.get_project_id()
        return ctx

    def create(self, request, *args, **kwargs):
        write = ApprovedLaborRateWriteSerializer(data=request.data)
        write.is_valid(raise_exception=True)
        if not member_has_codename(request.user, self.get_project_id(), 'edit_wage'):
            raise PermissionDenied('Approved labor rates require edit_wage.')
        data = write.validated_data
        rate = ApprovedLaborRate.objects.create(
            project_id=self.get_project_id(),
            person_id=data.get('person_id'),
            amount=data['amount'],
            currency=data.get('currency') or 'IRR',
            effective_from=data['effective_from'],
            effective_to=data.get('effective_to'),
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(
            ApprovedLaborRateSerializer(rate, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class LaborCostEstimateView(HRProjectMixin, APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return self.view_permission

    @extend_schema(summary='Estimate labor cost from approved rate', tags=['HR'])
    def post(self, request, project_pk):
        body = LaborCostEstimateRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        as_of = body.validated_data.get('as_of') or timezone.localdate()
        result = services.estimate_labor_cost(
            project_id=project_pk,
            person_id=body.validated_data['person_id'],
            approved_hours=body.validated_data['approved_hours'],
            as_of=as_of,
        )
        can_view_wage = member_has_codename(request.user, project_pk, 'view_wage')
        can_view_costs = member_has_codename(request.user, project_pk, 'view_costs')
        if not can_view_wage and not can_view_costs:
            for key in WAGE_SENSITIVE_ESTIMATE_KEYS:
                result[key] = None
        elif not can_view_wage:
            result.pop('rate_amount', None)
        return Response(result)
