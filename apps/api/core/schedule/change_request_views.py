"""Schedule change request API views."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.project import HasProjectPermission, IsProjectMember
from schedule.models import ScheduleChangeRequest
from schedule.serializers import (
    ScheduleChangeDecisionSerializer,
    ScheduleChangeRequestSerializer,
)
from schedule.services import change_request_service


class ScheduleChangeRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    @extend_schema(summary='List schedule change requests', tags=['Schedule Change Requests'])
    def get(self, request, project_pk=None):
        qs = change_request_service.list_change_requests(project_pk)
        return Response(ScheduleChangeRequestSerializer(qs, many=True).data)

    @extend_schema(summary='Create draft schedule change request', tags=['Schedule Change Requests'])
    def post(self, request, project_pk=None):
        payload = {
            'reason': request.data.get('reason', ''),
            'milestone_impact': request.data.get('milestone_impact', ''),
            'cost_impact': request.data.get('cost_impact', ''),
            'contract_impact': request.data.get('contract_impact', ''),
        }
        items = request.data.get('items') or []
        if not isinstance(items, list):
            items = []
        scr = change_request_service.create_change_request(
            project_id=project_pk,
            user=request.user,
            items=items,
            **payload,
        )
        scr = ScheduleChangeRequest.objects.prefetch_related('items').get(pk=scr.pk)
        return Response(ScheduleChangeRequestSerializer(scr).data, status=status.HTTP_201_CREATED)


class ScheduleChangeRequestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    def _get(self, project_pk, scr_id):
        return get_object_or_404(
            ScheduleChangeRequest.objects.prefetch_related('items'),
            pk=scr_id,
            project_id=project_pk,
            is_deleted=False,
        )

    @extend_schema(summary='Get schedule change request', tags=['Schedule Change Requests'])
    def get(self, request, project_pk=None, scr_id=None):
        return Response(ScheduleChangeRequestSerializer(self._get(project_pk, scr_id)).data)

    @extend_schema(summary='Update draft schedule change request', tags=['Schedule Change Requests'])
    def patch(self, request, project_pk=None, scr_id=None):
        scr = self._get(project_pk, scr_id)
        ser = ScheduleChangeRequestSerializer(scr, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        items = data.pop('items', None)
        if items is None and 'items' in request.data:
            items = request.data.get('items')
        scr = change_request_service.update_change_request(
            scr,
            request.user,
            items=items,
            **{k: v for k, v in data.items() if k != 'items'},
        )
        scr = ScheduleChangeRequest.objects.prefetch_related('items').get(pk=scr.pk)
        return Response(ScheduleChangeRequestSerializer(scr).data)


class ScheduleChangeRequestSubmitView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_activities'

    @extend_schema(summary='Submit schedule change request', tags=['Schedule Change Requests'])
    def post(self, request, project_pk=None, scr_id=None):
        scr = get_object_or_404(
            ScheduleChangeRequest,
            pk=scr_id,
            project_id=project_pk,
            is_deleted=False,
        )
        scr = change_request_service.submit_change_request(scr, request.user)
        scr = ScheduleChangeRequest.objects.prefetch_related('items').get(pk=scr.pk)
        return Response(ScheduleChangeRequestSerializer(scr).data)


class ScheduleChangeRequestApproveView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_activities'

    @extend_schema(summary='Approve schedule change request', tags=['Schedule Change Requests'])
    def post(self, request, project_pk=None, scr_id=None):
        scr = get_object_or_404(
            ScheduleChangeRequest,
            pk=scr_id,
            project_id=project_pk,
            is_deleted=False,
        )
        ser = ScheduleChangeDecisionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        scr = change_request_service.approve_change_request(
            scr,
            request.user,
            decision_notes=ser.validated_data.get('decision_notes', ''),
        )
        scr = ScheduleChangeRequest.objects.prefetch_related('items').get(pk=scr.pk)
        return Response(ScheduleChangeRequestSerializer(scr).data)


class ScheduleChangeRequestRejectView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_activities'

    @extend_schema(summary='Reject schedule change request', tags=['Schedule Change Requests'])
    def post(self, request, project_pk=None, scr_id=None):
        scr = get_object_or_404(
            ScheduleChangeRequest,
            pk=scr_id,
            project_id=project_pk,
            is_deleted=False,
        )
        ser = ScheduleChangeDecisionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        scr = change_request_service.reject_change_request(
            scr,
            request.user,
            decision_notes=ser.validated_data.get('decision_notes', ''),
        )
        scr = ScheduleChangeRequest.objects.prefetch_related('items').get(pk=scr.pk)
        return Response(ScheduleChangeRequestSerializer(scr).data)
