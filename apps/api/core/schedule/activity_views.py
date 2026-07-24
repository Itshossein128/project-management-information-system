"""Activity CRUD and relation API views."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.exceptions import ConflictError
from config.pagination import DefaultPageNumberPagination
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Activity, ActivityRelation
from schedule.serializers import (
    ActivityCreateUpdateSerializer,
    ActivityDetailSerializer,
    ActivityListSerializer,
    ActivityRelationCreateSerializer,
    WeightSummarySerializer,
)
from schedule.services.activity_service import (
    assert_can_delete_activity,
    base_activity_queryset,
    compute_weight_summary,
    filter_activities_queryset,
    get_activity_network,
)
from schedule.services.relation_service import create_relation_from_anchor, soft_delete_relation


@extend_schema_view(
    list=extend_schema(summary='List project activities', tags=['Activities']),
    create=extend_schema(summary='Create activity', tags=['Activities']),
    retrieve=extend_schema(summary='Get activity detail', tags=['Activities']),
    partial_update=extend_schema(summary='Update activity', tags=['Activities']),
    destroy=extend_schema(summary='Soft-delete activity', tags=['Activities']),
)
class ActivityViewSet(viewsets.ModelViewSet):
    lookup_url_kwarg = 'activity_id'
    pagination_class = DefaultPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    view_permission = 'view_activities'
    edit_permission = 'edit_activities'

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'weight_summary', 'network'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve', 'weight_summary', 'network'):
            return self.view_permission
        return self.edit_permission

    def get_queryset(self):
        project_id = self.kwargs['project_pk']
        qs = base_activity_queryset(project_id)
        if self.action == 'list':
            qs = filter_activities_queryset(qs, project_id, self.request.query_params)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ActivityDetailSerializer
        if self.action in ('create', 'partial_update'):
            return ActivityCreateUpdateSerializer
        return ActivityListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.kwargs['project_pk']
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = serializer.save()
        output = ActivityDetailSerializer(
            base_activity_queryset(self.kwargs['project_pk']).get(pk=activity.pk),
        )
        return Response(output.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        activity = serializer.save()
        output = ActivityDetailSerializer(
            base_activity_queryset(self.kwargs['project_pk']).get(pk=activity.pk),
        )
        return Response(output.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        assert_can_delete_activity(instance)

        instance.soft_delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Activity weight summary', tags=['Activities'])
    @action(detail=False, methods=['get'], url_path='weight-summary')
    def weight_summary(self, request, project_pk=None):
        data = compute_weight_summary(project_pk)
        return Response(WeightSummarySerializer(data).data)

    @extend_schema(summary='Activity network graph', tags=['Activities'])
    @action(detail=False, methods=['get'], url_path='network')
    def network(self, request, project_pk=None):
        return Response(get_activity_network(project_pk))

    @extend_schema(summary='Add activity relation', tags=['Activities'])
    @action(detail=True, methods=['post'], url_path='relations')
    def relations(self, request, project_pk=None, activity_id=None):
        serializer = ActivityRelationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role = data['role']
        other_id = data.get('successor_id') if role == 'predecessor' else data.get('predecessor_id')

        try:
            relation = create_relation_from_anchor(
                project_id=project_pk,
                anchor_activity_id=activity_id,
                role=role,
                other_activity_id=other_id,
                relation_type=data['relation_type'],
                lag_days=data['lag_days'],
                user=request.user,
            )
        except ConflictError as exc:
            raise exc
        except ValidationError as exc:
            raise exc

        if role == 'predecessor':
            link = {
                'relation_id': str(relation.id),
                'activity_id': str(relation.successor_id),
                'relation_type': relation.relation_type,
                'lag_days': relation.lag_days,
            }
        else:
            link = {
                'relation_id': str(relation.id),
                'activity_id': str(relation.predecessor_id),
                'relation_type': relation.relation_type,
                'lag_days': relation.lag_days,
            }
        return Response(link, status=status.HTTP_201_CREATED)

    @extend_schema(summary='Delete activity relation', tags=['Activities'])
    @action(
        detail=True,
        methods=['delete'],
        url_path=r'relations/(?P<relation_id>[^/.]+)',
    )
    def delete_relation(self, request, project_pk=None, activity_id=None, relation_id=None):
        activity = get_object_or_404(Activity, pk=activity_id, project_id=project_pk)
        relation = get_object_or_404(
            ActivityRelation,
            pk=relation_id,
        )
        if relation.predecessor_id != activity.id and relation.successor_id != activity.id:
            return Response(status=status.HTTP_404_NOT_FOUND)
        soft_delete_relation(relation, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
