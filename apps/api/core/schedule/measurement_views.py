"""Activity measurement, quantity-change and technical-approval API views (FR-PRG)."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from projects.models import Activity
from schedule.models import ActivityMeasurementDefinition, ActivityQuantityChange
from schedule.services import measurement_service as svc
from schedule.services.progress_service import invalidate_s_curve_cache


def serialize_definition(definition: ActivityMeasurementDefinition) -> dict:
    versions = definition.versions.order_by('version_number')
    return {
        'id': str(definition.id),
        'activity_id': str(definition.activity_id),
        'method': definition.method,
        'status': definition.status,
        'total_quantity': float(definition.total_quantity) if definition.total_quantity is not None else None,
        'unit_id': str(definition.unit_id) if definition.unit_id else None,
        'milestones': definition.milestones or [],
        'evidence_rules': definition.evidence_rules,
        'pending_change_reason': definition.pending_change_reason,
        'current_version_id': str(definition.current_version_id) if definition.current_version_id else None,
        'approved_at': definition.approved_at.isoformat() if definition.approved_at else None,
        'approved_by': str(definition.approved_by_id) if definition.approved_by_id else None,
        'versions': [
            {
                'id': str(v.id),
                'version_number': v.version_number,
                'method': v.method,
                'change_reason': v.change_reason,
                'approved_at': v.approved_at.isoformat(),
                'approved_by': str(v.approved_by_id) if v.approved_by_id else None,
            }
            for v in versions
        ],
    }


def serialize_quantity_change(change: ActivityQuantityChange) -> dict:
    return {
        'id': str(change.id),
        'activity_id': str(change.activity_id),
        'previous_total': float(change.previous_total),
        'new_total': float(change.new_total),
        'status': change.status,
        'reason': change.reason,
        'approved_at': change.approved_at.isoformat() if change.approved_at else None,
        'approved_by': str(change.approved_by_id) if change.approved_by_id else None,
    }


def error_response(exc: svc.ProgressValidationError) -> Response:
    return Response(exc.as_response(), status=exc.http_status)


class ProgressDomainView(APIView):
    """Base: project-scoped, per-method permission codes, ProgressValidationError → HTTP."""

    read_permission = 'view_dashboard'
    write_permission = 'edit_activities'
    approve_permission = 'approve_reports'
    # Subclasses may mark specific HTTP methods as approval actions.
    approve_methods: tuple[str, ...] = ()

    def get_permissions(self):
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        method = self.request.method
        if method in SAFE_METHODS:
            return self.read_permission
        if method in self.approve_methods:
            return self.approve_permission
        return self.write_permission

    def get_activity(self):
        return get_object_or_404(
            Activity, pk=self.kwargs['activity_id'], project_id=self.kwargs['project_pk'],
        )

    def handle_exception(self, exc):
        if isinstance(exc, svc.ProgressValidationError):
            return error_response(exc)
        return super().handle_exception(exc)


class ActivityMeasurementView(ProgressDomainView):
    @property
    def required_permission(self):
        """Read allowed for ``view_activities`` or ``view_dashboard`` holders."""
        if self.request.method in SAFE_METHODS and member_has_codename(
            self.request.user, str(self.kwargs['project_pk']), 'view_activities',
        ):
            return 'view_activities'
        return super().required_permission

    @extend_schema(summary='Get activity measurement definition', tags=['Progress'])
    def get(self, request, project_pk, activity_id):
        activity = self.get_activity()
        definition = svc.get_or_create_definition(activity, request.user)
        return Response(serialize_definition(definition))

    @extend_schema(summary='Update draft measurement basis', tags=['Progress'])
    def patch(self, request, project_pk, activity_id):
        activity = self.get_activity()
        definition = svc.get_or_create_definition(activity, request.user)
        svc.update_draft(definition, request.data, request.user)
        return Response(serialize_definition(definition))

    put = patch


class ActivityMeasurementApproveView(ProgressDomainView):
    approve_methods = ('POST',)

    @extend_schema(summary='Approve measurement basis (creates version)', tags=['Progress'])
    def post(self, request, project_pk, activity_id):
        activity = self.get_activity()
        definition = svc.get_or_create_definition(activity, request.user)
        svc.approve_definition(definition, request.user, request.data.get('reason', ''))
        definition.refresh_from_db()
        return Response(serialize_definition(definition), status=status.HTTP_200_OK)


class ActivityMeasurementChangeView(ProgressDomainView):
    @extend_schema(summary='Start measurement method/basis change', tags=['Progress'])
    def post(self, request, project_pk, activity_id):
        activity = self.get_activity()
        definition = svc.get_or_create_definition(activity, request.user)
        svc.start_method_change(definition, request.data, request.user, request.data.get('reason', ''))
        return Response(serialize_definition(definition), status=status.HTTP_201_CREATED)


class ActivityQuantityChangeListCreateView(ProgressDomainView):
    @extend_schema(summary='List activity quantity changes', tags=['Progress'])
    def get(self, request, project_pk, activity_id):
        activity = self.get_activity()
        changes = ActivityQuantityChange.objects.filter(activity=activity)
        return Response([serialize_quantity_change(c) for c in changes])

    @extend_schema(summary='Create draft quantity change', tags=['Progress'])
    def post(self, request, project_pk, activity_id):
        activity = self.get_activity()
        change = svc.create_quantity_change(activity, request.data, request.user)
        return Response(serialize_quantity_change(change), status=status.HTTP_201_CREATED)


class ActivityQuantityChangeApproveView(ProgressDomainView):
    approve_methods = ('POST',)

    @extend_schema(summary='Approve quantity change', tags=['Progress'])
    def post(self, request, project_pk, change_id, activity_id=None):
        filters = {'pk': change_id, 'project_id': project_pk}
        if activity_id:
            filters['activity_id'] = activity_id
        change = get_object_or_404(ActivityQuantityChange, **filters)
        svc.approve_quantity_change(change, request.user)
        invalidate_s_curve_cache(project_pk)
        return Response(serialize_quantity_change(change))


class ProgressTechnicalApproveView(ProgressDomainView):
    approve_methods = ('POST',)

    @extend_schema(summary='Technically approve latest recorded progress', tags=['Progress'])
    def post(self, request, project_pk, activity_id):
        activity = self.get_activity()
        report_date_raw = request.data.get('report_date')
        report_date = parse_jalali_or_gregorian(report_date_raw) if report_date_raw else None
        progress = svc.technical_approve_progress(
            activity, request.user, report_date=report_date, data=request.data,
        )
        invalidate_s_curve_cache(project_pk)
        return Response({
            'id': str(progress.id),
            'activity_id': str(activity.id),
            'report_date': progress.report_date.isoformat(),
            'cumulative_progress_pct': round(float(progress.actual_progress) * 100, 2),
            'approved_progress_pct': round(float(progress.approved_progress) * 100, 2),
            'technical_approved_at': progress.technical_approved_at.isoformat(),
            'measurement_version_id': (
                str(progress.measurement_version_id) if progress.measurement_version_id else None
            ),
        })
