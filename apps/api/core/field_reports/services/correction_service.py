"""Daily report correction requests and version lineage."""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ErrorDetail, ValidationError

from field_reports.services.lifecycle_errors import get_lifecycle_msg, lifecycle_error_detail

from field_reports.models import (
    CorrectionRequestStatus,
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportCorrectionRequest,
    DailyReportEquipment,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportLaborCamp,
    DailyReportMachineryRow,
    DailyReportMaterial,
    DailyReportGeneralActivity,
    DailyReportVisit,
    ReportStatus,
)

OPEN_CORRECTION_STATUSES = {
    CorrectionRequestStatus.DRAFT,
    CorrectionRequestStatus.SUBMITTED,
}

CHILD_CLONE_SPECS = (
    (DailyReportActivity, 'activities', {
        'activity_ref_id', 'activity_description', 'shift', 'subcontractor_name',
        'subcontractor_ref_id', 'headcount', 'zone', 'block', 'floor', 'location_detail',
        'quantity', 'quantity_measured', 'unit', 'execution_percentage', 'achieved_milestones',
        'responsible_user_id', 'responsible_name', 'notes', 'photo_file_id',
        'contractor_ref_id', 'crew_name', 'foreman_count', 'worker_count', 'parcel',
        'source_sub_report_id', 'source_discipline', 'is_derived',
    }),
    (DailyReportLabor, 'labor_entries', {
        'project_id', 'report_date', 'labor_category', 'job_title', 'custom_title',
        'contractor_ref_id', 'contractor_name',
        'shift_1_count', 'shift_2_count', 'shift_3_count', 'total_count',
        'work_hours', 'overtime_hours', 'daily_rate', 'absence_count',
        'source_set_complete', 'source_sub_report_id', 'source_discipline', 'is_derived',
    }),
    (DailyReportEquipment, 'equipment_entries', {
        'equipment_id', 'equipment_name', 'equipment_ref', 'shift', 'status',
        'ownership_type', 'work_start', 'work_end', 'repair_hours', 'idle_hours',
        'idle_reason', 'productive_hours', 'hourly_rate', 'fuel_cost',
        'activity_ref_id', 'notes',
    }),
    (DailyReportMaterial, 'material_entries', {
        'material_ref_id', 'material_description', 'quantity', 'unit_cost', 'unit',
        'transaction_type', 'consumption_location', 'supplier',
        'warehouse_document_reference', 'receipt_resolved', 'reconciliation_status',
        'reconciliation_document_id', 'reconciliation_checked_at',
        'activity_ref_id', 'notes', 'source_sub_report_id', 'source_discipline', 'is_derived',
    }),
    (DailyReportConcreteLog, 'concrete_logs', {
        'concrete_description', 'volume_m3', 'activity_ref_id', 'zone', 'block',
        'floor', 'notes', 'structural_element', 'parcel', 'batching_plant',
        'truck_delivery_note_number', 'lab_sample_code', 'sampling_state',
        'test_sheet_count', 'qc_inspection_id', 'source_sub_report_id',
        'source_discipline', 'is_derived',
    }),
    (DailyReportLaborCamp, 'labor_camp_entries', {
        'connex_number', 'subcontractor_name', 'contractor_ref_id', 'total_residents',
        'present_count', 'on_leave_count', 'capacity',
    }),
    (DailyReportIncident, 'incidents', {
        'incident_type', 'description', 'corrective_action',
        'follow_up_owner_user_id', 'follow_up_owner_name', 'due_date',
        'severity', 'notification_id', 'row_number', 'source_report_id', 'source_row_id',
    }),
    (DailyReportMachineryRow, 'machinery_rows', {
        'equipment_type', 'equipment_ref_id', 'status_total', 'status_active',
        'status_ready', 'status_inactive', 'status_under_repair', 'operating_hours',
        'stoppage_hours', 'repair_hours', 'stoppage_reason_code',
        'source_sub_report_id', 'source_discipline', 'is_derived',
    }),
    (DailyReportGeneralActivity, 'general_activities', {
        'row_number', 'activity_description', 'location', 'quantity', 'unit', 'notes',
        'source_sub_report_id', 'source_discipline', 'is_derived',
    }),
    (DailyReportVisit, 'visits', {
        'row_number', 'text', 'source_sub_report_id', 'source_discipline', 'is_derived',
    }),
)


def _clone_children(source: DailyReport, target: DailyReport) -> None:
    for model, related_name, fields in CHILD_CLONE_SPECS:
        manager = getattr(source, related_name)
        for row in manager.filter(is_deleted=False):
            data = {field: getattr(row, field) for field in fields}
            model.objects.create(report=target, **data)


@transaction.atomic
def open_correction(*, source_report: DailyReport, user, reason: str, request=None) -> DailyReportCorrectionRequest:
    reason = (reason or '').strip()
    if len(reason) < 10:
        raise ValidationError({
            'reason': lifecycle_error_detail('reason_required', request=request),
            'code': 'reason_required',
        })

    # Lock the authoritative source row before checking for another open request
    # or replacing the current version.  The view instance may be stale when two
    # users click the correction action at nearly the same time.
    source_report = DailyReport.objects.select_for_update().get(
        pk=source_report.pk,
        project_id=source_report.project_id,
        is_deleted=False,
    )

    lineage_id = source_report.lineage_id or source_report.id
    open_exists = DailyReportCorrectionRequest.objects.filter(
        project_id=source_report.project_id,
        source_report__lineage_id=lineage_id,
        status__in=OPEN_CORRECTION_STATUSES,
        is_deleted=False,
    ).exists()
    if open_exists:
        raise ValidationError({
            'detail': lifecycle_error_detail('correction_already_open', request=request),
        })

    if source_report.status != ReportStatus.APPROVED or not source_report.is_current:
        raise ValidationError({'detail': lifecycle_error_detail(
            'report_not_locked', request=request,
        )})

    result = DailyReport(
        project_id=source_report.project_id,
        report_date=source_report.report_date,
        shift=source_report.shift,
        work_front=source_report.work_front,
        location_notes=source_report.location_notes,
        weather_condition=source_report.weather_condition,
        temp_max=source_report.temp_max,
        temp_min=source_report.temp_min,
        site_status=source_report.site_status,
        inactivity_reason=source_report.inactivity_reason,
        weather_impact_notes=source_report.weather_impact_notes,
        general_notes=source_report.general_notes,
        prepared_by=user,
        status=ReportStatus.DRAFT,
        lineage_id=lineage_id,
        version_number=source_report.version_number + 1,
        supersedes=source_report,
        is_current=True,
        created_by=user,
        updated_by=user,
    )
    source_report.is_current = False
    source_report.updated_by = user
    source_report.save(update_fields=['is_current', 'updated_by', 'updated_at'])
    result.save()
    _clone_children(source_report, result)

    correction = DailyReportCorrectionRequest.objects.create(
        project_id=source_report.project_id,
        source_report=source_report,
        result_report=result,
        reason=reason,
        status=CorrectionRequestStatus.SUBMITTED,
        requested_by=user,
        requested_at=timezone.now(),
        created_by=user,
        updated_by=user,
    )
    return correction


@transaction.atomic
def cancel_correction(*, correction: DailyReportCorrectionRequest, user, request=None) -> DailyReportCorrectionRequest:
    correction = DailyReportCorrectionRequest.objects.select_for_update().get(
        pk=correction.pk,
        is_deleted=False,
    )
    if correction.status not in OPEN_CORRECTION_STATUSES:
        raise ValidationError({
            'detail': lifecycle_error_detail('correction_not_open', request=request),
        })

    result = (
        DailyReport.objects.select_for_update().filter(pk=correction.result_report_id).first()
        if correction.result_report_id else None
    )
    source = DailyReport.objects.select_for_update().get(pk=correction.source_report_id)
    if (
        result is None
        or result.status != ReportStatus.DRAFT
        or not result.is_current
        or result.version_number <= 1
        or result.project_id != source.project_id
        or (source.lineage_id and result.lineage_id != source.lineage_id)
        or result.supersedes_id != source.id
        or result.version_number != source.version_number + 1
    ):
        raise ValidationError({
            'detail': lifecycle_error_detail('result_not_cancellable', request=request),
        })
    if source.status != ReportStatus.APPROVED or source.is_current:
        raise ValidationError({
            'detail': lifecycle_error_detail('source_not_restorable', request=request),
        })

    if result is not None:
        result.is_current = False
        result.updated_by = user
        result.save(update_fields=['is_current', 'updated_by', 'updated_at'])
        result.soft_delete(user=user)

    source.is_current = True
    source.updated_by = user
    source.save(update_fields=['is_current', 'updated_by', 'updated_at'])

    correction.status = CorrectionRequestStatus.CANCELLED
    correction.decided_by = user
    correction.decided_at = timezone.now()
    correction.updated_by = user
    correction.save(
        update_fields=['status', 'decided_by', 'decided_at', 'updated_by', 'updated_at'],
    )
    return correction


def mark_correction_approved_for_report(report: DailyReport, user) -> None:
    """When a correction result report is approved, close its correction request."""
    qs = DailyReportCorrectionRequest.objects.filter(
        result_report=report,
        status__in=OPEN_CORRECTION_STATUSES,
        is_deleted=False,
    )
    now = timezone.now()
    for correction in qs:
        correction.status = CorrectionRequestStatus.APPROVED
        correction.decided_by = user
        correction.decided_at = now
        correction.updated_by = user
        correction.save(
            update_fields=['status', 'decided_by', 'decided_at', 'updated_by', 'updated_at'],
        )


def list_versions(report: DailyReport):
    lineage_id = report.lineage_id or report.id
    return DailyReport.objects.filter(
        project_id=report.project_id,
        lineage_id=lineage_id,
        is_deleted=False,
    ).select_related('created_by', 'updated_by').prefetch_related(
        'correction_requests_as_result',
    ).order_by('version_number')
