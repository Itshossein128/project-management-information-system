"""Serializers for the canonical unit daily report API (feature 032, US1).

Detail/history shapes per contracts/unit-report-api.md. Capabilities are
convenience projections only; every mutation re-evaluates authorization on the
server.
"""
from __future__ import annotations

from rest_framework import serializers

from common.serializers import JalaliDateField
from permissions.project import member_has_codename
from sub_reports.models import (
    DisciplineSubReport,
    SubReportStatus,
    UnitReportStatusEvent,
)


class UnitReportOpenSerializer(serializers.Serializer):
    report_date = JalaliDateField(required=True)


class UnitReportCurrentQuerySerializer(serializers.Serializer):
    date = JalaliDateField(required=True)


def _user_ref(user):
    if user is None:
        return None
    return {'id': str(user.id), 'display_name': user.get_full_name() or user.username}


class UnitReportRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default='',
    )

    def validate(self, attrs):
        reason = (attrs.get('rejection_reason') or '').strip()
        if not reason:
            raise serializers.ValidationError(
                {'rejection_reason': serializers.ErrorDetail('دلیل رد الزامی است', code='rejection_reason_required')},
                code='rejection_reason_required',
            )
        attrs['rejection_reason'] = reason
        return attrs


class UnitReportAuditSerializer(serializers.Serializer):
    prepared_by = serializers.SerializerMethodField()
    submitted_by = serializers.SerializerMethodField()
    submitted_at = serializers.DateTimeField()
    approved_by = serializers.SerializerMethodField()
    approved_at = serializers.DateTimeField()
    rejected_by = serializers.SerializerMethodField()
    rejected_at = serializers.DateTimeField()
    rejection_reason = serializers.CharField(allow_blank=True)

    def get_prepared_by(self, obj):
        return _user_ref(obj.created_by)

    def get_submitted_by(self, obj):
        return _user_ref(obj.submitted_by)

    def get_approved_by(self, obj):
        return _user_ref(obj.approved_by)

    def get_rejected_by(self, obj):
        return _user_ref(obj.rejected_by)


class UnitReportCapabilitiesSerializer(serializers.Serializer):
    can_edit = serializers.BooleanField()
    can_submit = serializers.BooleanField()
    can_approve = serializers.BooleanField()
    can_reject = serializers.BooleanField()
    can_correct = serializers.BooleanField()
    can_delete = serializers.BooleanField()
    can_view_history = serializers.BooleanField()


def compute_capabilities(report, user) -> dict:
    """Server-authoritative capability projection for the requester."""
    is_preparer_or_submitter = (
        user is not None
        and not getattr(user, 'is_superuser', False)
        and (
            report.created_by_id == getattr(user, 'id', None)
            or report.submitted_by_id == getattr(user, 'id', None)
        )
    )
    has_view = member_has_codename(user, str(report.project_id), 'view_reports')
    has_edit = member_has_codename(user, str(report.project_id), 'edit_reports')
    has_approve = member_has_codename(user, str(report.project_id), 'approve_reports')

    is_active_current = report.is_current and not report.is_deleted

    can_edit = (
        is_active_current
        and report.status in (SubReportStatus.DRAFT, SubReportStatus.REJECTED)
        and has_edit
    )
    can_submit = can_edit
    can_approve = (
        is_active_current
        and report.status == SubReportStatus.SUBMITTED
        and has_approve
        and not is_preparer_or_submitter
    )
    can_reject = (
        is_active_current
        and report.status == SubReportStatus.SUBMITTED
        and has_approve
    )
    can_correct = (
        is_active_current
        and report.status == SubReportStatus.APPROVED
        and has_edit
    )
    can_delete = can_edit
    can_view_history = has_view

    return {
        'can_edit': can_edit,
        'can_submit': can_submit,
        'can_approve': can_approve,
        'can_reject': can_reject,
        'can_correct': can_correct,
        'can_delete': can_delete,
        'can_view_history': can_view_history,
    }


class UnitReportDetailSerializer(serializers.ModelSerializer):
    project_id = serializers.SerializerMethodField()
    report_date = JalaliDateField()
    last_changed_at = serializers.DateTimeField(source='updated_at')
    audit = UnitReportAuditSerializer(source='*')
    capabilities = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineSubReport
        fields = [
            'id', 'lineage_id', 'version_number', 'is_current', 'project_id',
            'unit', 'report_date', 'status', 'last_changed_at', 'sync_revision',
            'audit', 'capabilities', 'content',
        ]
        read_only_fields = fields

    def get_project_id(self, obj):
        return str(obj.project_id)

    def get_capabilities(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        return compute_capabilities(obj, user)

    def get_content(self, obj):
        return {
            'activity_records': [],
            'legacy_contributions': [],
        }


class UnitReportVersionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    version_number = serializers.IntegerField()
    status = serializers.CharField()
    is_current = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    supersedes = serializers.UUIDField(source='supersedes_id', default=None, allow_null=True)
    superseded_by = serializers.UUIDField(default=None, allow_null=True)


class UnitReportEventSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    from_status = serializers.CharField()
    to_status = serializers.CharField()
    actor = serializers.SerializerMethodField()
    occurred_at = serializers.DateTimeField()
    reason = serializers.CharField(allow_blank=True)

    def get_actor(self, obj):
        return _user_ref(obj.actor)


class UnitReportHistorySerializer(serializers.Serializer):
    lineage_id = serializers.UUIDField()
    current_version_id = serializers.UUIDField()
    versions = UnitReportVersionSerializer(many=True)
    events = UnitReportEventSerializer(many=True)
