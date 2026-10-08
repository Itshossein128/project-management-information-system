"""Baseline list/create, approve-lock, and locked snapshot mutation guards."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.project import HasProjectPermission, IsProjectMember
from schedule.models import BaselineActivity, BaselineSchedule
from schedule.serializers import (
    BaselineActivitySerializer,
    BaselineCreateSerializer,
    BaselineScheduleSerializer,
)
from schedule.services import baseline_service


class BaselineListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    @extend_schema(summary='List baseline schedules', tags=['Schedule Baselines'])
    def get(self, request, project_pk=None):
        baselines = baseline_service.list_baselines(project_pk)
        return Response(BaselineScheduleSerializer(baselines, many=True).data)

    @extend_schema(summary='Create baseline snapshot from live activities', tags=['Schedule Baselines'])
    def post(self, request, project_pk=None):
        ser = BaselineCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        baseline = baseline_service.create_baseline_snapshot(
            project_id=project_pk,
            version_name=ser.validated_data.get('version_name') or '',
            user=request.user,
            make_current=bool(ser.validated_data.get('make_current')),
        )
        return Response(BaselineScheduleSerializer(baseline).data, status=status.HTTP_201_CREATED)


class BaselineApproveLockView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_activities'

    @extend_schema(summary='Approve and lock baseline', tags=['Schedule Baselines'])
    def post(self, request, project_pk=None, baseline_id=None):
        baseline = get_object_or_404(BaselineSchedule, pk=baseline_id, project_id=project_pk)
        baseline = baseline_service.approve_lock_baseline(baseline, request.user)
        return Response(BaselineScheduleSerializer(baseline).data)


class BaselineActivityDetailView(APIView):
    """Mutate a baseline activity row — rejected when parent is locked."""

    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_activities'

    def _get(self, project_pk, baseline_id, ba_id):
        return get_object_or_404(
            BaselineActivity,
            pk=ba_id,
            baseline_id=baseline_id,
            baseline__project_id=project_pk,
        )

    @extend_schema(summary='Update baseline activity snapshot', tags=['Schedule Baselines'])
    def patch(self, request, project_pk=None, baseline_id=None, ba_id=None):
        ba = self._get(project_pk, baseline_id, ba_id)
        ser = BaselineActivitySerializer(ba, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ba = baseline_service.update_baseline_activity(ba, **ser.validated_data)
        return Response(BaselineActivitySerializer(ba).data)

    @extend_schema(summary='Delete baseline activity snapshot', tags=['Schedule Baselines'])
    def delete(self, request, project_pk=None, baseline_id=None, ba_id=None):
        ba = self._get(project_pk, baseline_id, ba_id)
        baseline_service.delete_baseline_activity(ba)
        return Response(status=status.HTTP_204_NO_CONTENT)
