"""WBS tree API views."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import WBS
from wbs.serializers import (
    WBSCreateSerializer,
    WBSFlatSerializer,
    WBSTreeSerializer,
    WBSMoveSerializer,
    WBSUpdateSerializer,
)
from wbs.services import (
    WBSConflictError,
    WBSValidationError,
    build_tree_queryset,
    create_wbs_node,
    delete_wbs_node,
    move_wbs_node,
    update_wbs_node,
)


def _build_children_map(nodes):
    by_id = {str(n.id): n for n in nodes}
    children_map: dict[str, list] = {nid: [] for nid in by_id}

    for node in nodes:
        parent = node.get_parent()
        if parent is not None:
            children_map[str(parent.id)].append(node)

    for key in children_map:
        children_map[key].sort(key=lambda n: n.wbs_code)

    return children_map


def _serialize_tree(project_id):
    nodes = list(build_tree_queryset(project_id))
    children_map = _build_children_map(nodes)
    roots = [n for n in nodes if n.depth == 1]
    roots.sort(key=lambda n: n.wbs_code)
    serializer = WBSTreeSerializer(
        roots,
        many=True,
        context={'children_map': children_map},
    )
    return serializer.data


@extend_schema_view(
    list=extend_schema(summary='Get WBS tree', tags=['WBS']),
    create=extend_schema(summary='Create WBS node', tags=['WBS']),
)
class WBSViewSet(viewsets.ViewSet):
    lookup_url_kwarg = 'wbs_id'

    def get_permissions(self):
        if self.action in ('list', 'flat'):
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        return 'edit_wbs'

    def list(self, request, project_pk=None):
        tree = _serialize_tree(project_pk)
        return Response(tree)

    @extend_schema(summary='Flat WBS list', tags=['WBS'])
    @action(detail=False, methods=['get'], url_path='flat')
    def flat(self, request, project_pk=None):
        nodes = build_tree_queryset(project_pk)
        return Response(WBSFlatSerializer(nodes, many=True).data)

    def create(self, request, project_pk=None):
        serializer = WBSCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            node, warnings = create_wbs_node(
                project_id=project_pk,
                parent_id=data.get('parent_id'),
                wbs_code=data['wbs_code'],
                wbs_name=data['wbs_name'],
                weight_physical=data.get('weight_physical'),
                weight_financial=data.get('weight_financial'),
                description=data.get('description', ''),
            )
        except WBSValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = WBSTreeSerializer(node, context={'children_map': {str(node.id): []}}).data
        if warnings:
            response_data['warnings'] = warnings
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(summary='Update WBS node', tags=['WBS'])
    def partial_update(self, request, project_pk=None, wbs_id=None):
        node = get_object_or_404(WBS, pk=wbs_id, project_id=project_pk)
        serializer = WBSUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            node, warnings = update_wbs_node(node, **serializer.validated_data)
        except WBSValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = WBSTreeSerializer(node, context={'children_map': {str(node.id): []}}).data
        if warnings:
            response_data['warnings'] = warnings
        return Response(response_data)

    @extend_schema(summary='Delete WBS node', tags=['WBS'])
    def destroy(self, request, project_pk=None, wbs_id=None):
        node = get_object_or_404(WBS, pk=wbs_id, project_id=project_pk)
        try:
            delete_wbs_node(node)
        except WBSConflictError as exc:
            return Response(
                {'error': {'code': 'conflict', 'message': str(exc), 'details': {}}},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Move WBS node', tags=['WBS'])
    @action(detail=True, methods=['post'], url_path='move')
    def move(self, request, project_pk=None, wbs_id=None):
        node = get_object_or_404(WBS, pk=wbs_id, project_id=project_pk)
        serializer = WBSMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            moved = move_wbs_node(
                node,
                serializer.validated_data.get('new_parent_id'),
                serializer.validated_data['position'],
            )
        except WBSValidationError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(WBSTreeSerializer(moved, context={'children_map': {str(moved.id): []}}).data)
