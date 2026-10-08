"""Working calendar and exception API views."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.project import HasProjectPermission, IsProjectMember
from schedule.models import CalendarException, WorkingCalendar
from schedule.serializers import CalendarExceptionSerializer, WorkingCalendarSerializer
from schedule.services import calendar_service


class WorkingCalendarListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    @extend_schema(summary='List working calendars', tags=['Schedule Calendars'])
    def get(self, request, project_pk=None):
        calendars = calendar_service.list_calendars(project_pk)
        return Response(WorkingCalendarSerializer(calendars, many=True).data)

    @extend_schema(summary='Create working calendar', tags=['Schedule Calendars'])
    def post(self, request, project_pk=None):
        ser = WorkingCalendarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        calendar = calendar_service.create_calendar(
            project_id=project_pk,
            user=request.user,
            **ser.validated_data,
        )
        return Response(WorkingCalendarSerializer(calendar).data, status=status.HTTP_201_CREATED)


class WorkingCalendarDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    def _get(self, project_pk, calendar_id):
        return get_object_or_404(
            WorkingCalendar,
            pk=calendar_id,
            project_id=project_pk,
            is_deleted=False,
        )

    @extend_schema(summary='Get working calendar', tags=['Schedule Calendars'])
    def get(self, request, project_pk=None, calendar_id=None):
        return Response(WorkingCalendarSerializer(self._get(project_pk, calendar_id)).data)

    @extend_schema(summary='Update working calendar', tags=['Schedule Calendars'])
    def patch(self, request, project_pk=None, calendar_id=None):
        calendar = self._get(project_pk, calendar_id)
        ser = WorkingCalendarSerializer(calendar, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        calendar = calendar_service.update_calendar(calendar, request.user, **ser.validated_data)
        return Response(WorkingCalendarSerializer(calendar).data)

    @extend_schema(summary='Soft-delete working calendar', tags=['Schedule Calendars'])
    def delete(self, request, project_pk=None, calendar_id=None):
        calendar = self._get(project_pk, calendar_id)
        calendar_service.soft_delete_calendar(calendar, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CalendarExceptionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    def _calendar(self, project_pk, calendar_id):
        return get_object_or_404(
            WorkingCalendar,
            pk=calendar_id,
            project_id=project_pk,
            is_deleted=False,
        )

    @extend_schema(summary='List calendar exceptions', tags=['Schedule Calendars'])
    def get(self, request, project_pk=None, calendar_id=None):
        calendar = self._calendar(project_pk, calendar_id)
        qs = CalendarException.objects.filter(calendar=calendar, is_deleted=False)
        return Response(CalendarExceptionSerializer(qs, many=True).data)

    @extend_schema(summary='Create calendar exception', tags=['Schedule Calendars'])
    def post(self, request, project_pk=None, calendar_id=None):
        calendar = self._calendar(project_pk, calendar_id)
        ser = CalendarExceptionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        exc = calendar_service.create_exception(
            calendar=calendar,
            user=request.user,
            **ser.validated_data,
        )
        return Response(CalendarExceptionSerializer(exc).data, status=status.HTTP_201_CREATED)


class CalendarExceptionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_activities' if self.request.method == 'GET' else 'edit_activities'

    def _get(self, project_pk, calendar_id, exception_id):
        return get_object_or_404(
            CalendarException,
            pk=exception_id,
            calendar_id=calendar_id,
            calendar__project_id=project_pk,
            is_deleted=False,
        )

    @extend_schema(summary='Update calendar exception', tags=['Schedule Calendars'])
    def patch(self, request, project_pk=None, calendar_id=None, exception_id=None):
        exc = self._get(project_pk, calendar_id, exception_id)
        ser = CalendarExceptionSerializer(exc, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        exc = calendar_service.update_exception(exc, request.user, **ser.validated_data)
        return Response(CalendarExceptionSerializer(exc).data)

    @extend_schema(summary='Soft-delete calendar exception', tags=['Schedule Calendars'])
    def delete(self, request, project_pk=None, calendar_id=None, exception_id=None):
        exc = self._get(project_pk, calendar_id, exception_id)
        calendar_service.soft_delete_exception(exc, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
