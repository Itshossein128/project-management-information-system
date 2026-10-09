from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.viewsets import ProjectScopedViewSet
from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from workflow.models import ManagementDecision, WorkflowDefinition, WorkflowInstance, WorkflowInstanceStatus
from workflow.serializers import (
    ManagementDecisionSerializer,
    WorkflowActionLogSerializer,
    WorkflowCommentSerializer,
    WorkflowDefinitionSerializer,
    WorkflowInstanceSerializer,
    WorkflowInstanceStartSerializer,
)
from workflow.services import definition_service, instance_service
from workflow.services.overdue_notify import notify_overdue_instances


class WorkflowReadMixin:
    """GET allowed with view_documents or view_project."""

    view_permission = 'view_documents'
    edit_permission = 'edit_project'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.request.method in SAFE_METHODS:
            project_id = str(self.kwargs.get('project_pk', ''))
            if member_has_codename(self.request.user, project_id, 'view_documents'):
                return 'view_documents'
            return 'view_project'
        return self.edit_permission


class ManagementDecisionViewSet(WorkflowReadMixin, ProjectScopedViewSet):
    queryset = ManagementDecision.objects.all()
    serializer_class = ManagementDecisionSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_id'] = self.get_project_id()
        return ctx

    @extend_schema(summary='List management decisions', tags=['Workflow'])
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return Response({'results': ManagementDecisionSerializer(qs, many=True).data})

    @extend_schema(summary='Create management decision', tags=['Workflow'])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary='Update management decision', tags=['Workflow'])
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class WorkflowDefinitionViewSet(WorkflowReadMixin, ProjectScopedViewSet):
    queryset = WorkflowDefinition.objects.prefetch_related('stages')
    serializer_class = WorkflowDefinitionSerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return Response({'results': WorkflowDefinitionSerializer(qs, many=True).data})

    def create(self, request, *args, **kwargs):
        stages = request.data.get('stages') or []
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stages_validated = serializer.validated_data.pop('stages', [])
        definition = WorkflowDefinition.objects.create(
            project_id=self.get_project_id(),
            created_by=request.user,
            updated_by=request.user,
            **serializer.validated_data,
        )
        if stages_validated or stages:
            definition_service.replace_stages(
                definition,
                stages_validated or stages,
            )
        definition.refresh_from_db()
        return Response(WorkflowDefinitionSerializer(definition).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        stages = serializer.validated_data.pop('stages', None)
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.updated_by = request.user
        instance.save()
        if stages is not None:
            definition_service.replace_stages(instance, stages)
        instance.refresh_from_db()
        return Response(WorkflowDefinitionSerializer(instance).data)


class WorkflowDefinitionActivateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    edit_permission = 'edit_project'

    @property
    def required_permission(self):
        return self.edit_permission

    @extend_schema(summary='Activate workflow definition', tags=['Workflow'])
    def post(self, request, project_pk=None, pk=None):
        definition = get_object_or_404(
            WorkflowDefinition,
            pk=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        definition = definition_service.activate_definition(definition, request.user)
        return Response(WorkflowDefinitionSerializer(definition).data)


class WorkflowDefinitionRetireView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    edit_permission = 'edit_project'

    @property
    def required_permission(self):
        return self.edit_permission

    @extend_schema(summary='Retire workflow definition', tags=['Workflow'])
    def post(self, request, project_pk=None, pk=None):
        definition = get_object_or_404(
            WorkflowDefinition,
            pk=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        definition = definition_service.retire_definition(definition, request.user)
        return Response(WorkflowDefinitionSerializer(definition).data)


class WorkflowInstanceViewSet(WorkflowReadMixin, ProjectScopedViewSet):
    queryset = WorkflowInstance.objects.select_related('definition')
    serializer_class = WorkflowInstanceSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        if params.get('workflow_type'):
            qs = qs.filter(definition__workflow_type=params['workflow_type'])
        if params.get('subject_type'):
            qs = qs.filter(subject_type=params['subject_type'])
        if params.get('subject_id'):
            qs = qs.filter(subject_id=params['subject_id'])
        if params.get('overdue') == 'true':
            qs = qs.filter(
                current_due_at__lt=timezone.now(),
            ).exclude(
                status__in=[
                    WorkflowInstanceStatus.APPROVED,
                    WorkflowInstanceStatus.REJECTED,
                    WorkflowInstanceStatus.CANCELLED,
                ],
            )
        return qs

    def list(self, request, *args, **kwargs):
        if request.query_params.get('overdue') == 'true':
            notify_overdue_instances(self.get_project_id())
        qs = self.get_queryset()
        return Response({'results': WorkflowInstanceSerializer(qs, many=True).data})

    def create(self, request, *args, **kwargs):
        serializer = WorkflowInstanceStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        definition = serializer.validated_data['definition']
        if str(definition.project_id) != str(self.get_project_id()):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = instance_service.start_instance(
            definition=definition,
            project_id=self.get_project_id(),
            subject_type=serializer.validated_data['subject_type'],
            subject_id=serializer.validated_data['subject_id'],
            user=request.user,
            comment=serializer.validated_data.get('comment', ''),
        )
        return Response(WorkflowInstanceSerializer(instance).data, status=status.HTTP_201_CREATED)


class WorkflowInstanceActionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember]

    def post(self, request, project_pk=None, pk=None, action_name=None):
        instance = get_object_or_404(
            WorkflowInstance,
            pk=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        may_edit = member_has_codename(request.user, str(project_pk), 'edit_project')
        may_act = instance_service.user_can_act_on_stage(
            instance, request.user, instance.current_stage_order,
        )
        if action_name in ('approve', 'reject') and not (may_edit or may_act):
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if action_name == 'cancel' and not may_edit:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        body = WorkflowCommentSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        comment = body.validated_data.get('comment', '')
        if action_name == 'approve':
            instance = instance_service.approve_instance(instance, request.user, comment=comment)
        elif action_name == 'reject':
            instance = instance_service.reject_instance(instance, request.user, comment=comment)
        elif action_name == 'cancel':
            instance = instance_service.cancel_instance(instance, request.user, comment=comment)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(WorkflowInstanceSerializer(instance).data)


class WorkflowInstanceLogView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    view_permission = 'view_documents'

    @property
    def required_permission(self):
        project_id = str(self.kwargs.get('project_pk', ''))
        if member_has_codename(self.request.user, project_id, 'view_documents'):
            return 'view_documents'
        return 'view_project'

    @extend_schema(summary='Workflow instance action log', tags=['Workflow'])
    def get(self, request, project_pk=None, pk=None):
        instance = get_object_or_404(
            WorkflowInstance,
            pk=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        logs = instance.action_logs.order_by('acted_at', 'id')
        return Response({'results': WorkflowActionLogSerializer(logs, many=True).data})
