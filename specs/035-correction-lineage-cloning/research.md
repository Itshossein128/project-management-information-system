# Research: Daily Report Correction Lineage and Lossless Cloning

**Feature**: `035-correction-lineage-cloning`  
**Date**: 2026-10-27  
**Status**: Completed  

## Overview

This research document consolidates architectural decisions, data flows, and interface contracts for the daily report correction lineage, child row cloning, cancellation flow, and enriched version history.

---

## Decision 1: Lossless Child Row Cloning Specifications

### Problem
When an approved daily report opens a correction draft, the previous implementation missed newer domain fields on activities (contractor references, crew names, foreman counts, worker counts, parcel) and completely skipped several child tables (`DailyReportMachineryRow`, `DailyReportGeneralActivity`, `DailyReportVisit`, and incident severity/discipline fields), causing catastrophic silent data loss upon correction.

### Decision
Define a declarative `CHILD_CLONE_SPECS` tuple mapping each child model to its related name on `DailyReport` and its set of non-relational or foreign-key ID fields:

1. `DailyReportActivity`:
   - `activity_ref_id`, `activity_description`, `shift`, `subcontractor_name`, `subcontractor_ref_id`, `headcount`, `zone`, `block`, `floor`, `location_detail`, `quantity`, `quantity_measured`, `unit`, `execution_percentage`, `responsible_user_id`, `responsible_name`, `notes`, `photo_file_id`, `contractor_ref_id`, `crew_name`, `foreman_count`, `worker_count`, `parcel`, `source_sub_report_id`, `source_discipline`.
2. `DailyReportMachineryRow`:
   - `equipment_type`, `equipment_ref_id`, `status_total`, `status_active`, `status_ready`, `status_inactive`, `status_under_repair`, `operating_hours`, `stoppage_hours`, `repair_hours`, `stoppage_reason_code`, `source_sub_report_id`, `source_discipline`.
3. `DailyReportGeneralActivity`:
   - `row_number`, `activity_description`, `location`, `quantity`, `unit`, `notes`, `source_sub_report_id`, `source_discipline`.
4. `DailyReportVisit`:
   - `row_number`, `text`, `source_sub_report_id`, `source_discipline`.
5. `DailyReportIncident`:
   - `incident_type`, `description`, `corrective_action`, `follow_up_owner_user_id`, `follow_up_owner_name`, `due_date`, `severity`, `source_report_id`, `source_row_id`.
6. Retain existing child specs for `DailyReportLabor`, `DailyReportEquipment`, `DailyReportMaterial`, `DailyReportConcreteLog`, and `DailyReportLaborCamp`.

### Rationale
- Declarative specifications guarantee that adding new fields or models is localized in a single tuple.
- Filtering `manager.filter(is_deleted=False)` ensures soft-deleted rows in the source report are never carried over into the new correction draft.
- Direct dictionary extraction and `create(report=target, **data)` prevents circular dependency issues and ensures foreign keys (`_id`) are preserved intact.

### Alternatives Considered
- *Django ModelForms / DRF serializers for cloning*: Rejected because serializers introduce validation overhead and may mutate or fail on derived/read-only fields that must be preserved identically.
- *Shallow SQL clone (`INSERT INTO ... SELECT`)*: Rejected because child models have application-level UUID primary keys and model signals/audit metadata that should be initialized cleanly.

---

## Decision 2: Concurrency Control & HTTP Status for Duplicate Corrections

### Problem
Previously, triggering a concurrent correction returned HTTP 409 (`ConflictError`), which did not follow standard client validation conventions and lacked explicit structured error details.

### Decision
Raise `rest_framework.exceptions.ValidationError` returning HTTP 400 with a localized Persian detail and code `correction_already_open`:
```python
raise ValidationError({
    'detail': ErrorDetail(
        'درخواست اصلاح باز برای این گزارش وجود دارد',
        code='correction_already_open',
    ),
})
```
Additionally, wrap the lineage lookup in `transaction.atomic()` with `select_for_update()` on the source report to eliminate race conditions between concurrent requests.

### Rationale
- DRF standardizes validation failures as HTTP 400.
- Frontend error handlers and toast notification hooks uniformly handle `detail` strings and `code` keys.
- Atomic row locking prevents two concurrent clicks from spawning dual draft records.

### Alternatives Considered
- *HTTP 409 Conflict*: Non-standard in this codebase's REST conventions; creates inconsistent client-side exception handling.
- *Silently returning existing open draft*: Violates Principle IV (Explicit Mutations); the user must be informed that an open request is already being edited.

---

## Decision 3: Cancellation Workflow and Lifecycle Pattern

### Problem
When an editor opens a correction accidentally, they had no self-service exit. The report remained stuck in draft v2+, preventing subsequent workflows.

### Decision
Provide an atomic `cancel_correction` service and API endpoint:
1. Endpoint: `POST /api/v1/projects/{project_pk}/correction-requests/{correction_id}/cancel/` (with alias `/api/v1/projects/{project_pk}/daily-reports/correction-requests/{correction_id}/cancel/`).
2. Action:
   - Soft-delete the draft result report (`result.soft_delete(user=user)`).
   - Set `result.is_current = False`.
   - Restore the source approved report: `source.is_current = True`.
   - Mark the correction request status as `CANCELLED`, recording `decided_by` and `decided_at`.
3. UI:
   - Render "انصراف از اصلاح / Cancel Correction" in `ApprovalStatusBar.tsx` only when `report.status === 'draft'` and `report.is_current !== false` and `openCorrection` exists.
   - Require explicit two-step confirmation dialog.
   - On success, redirect the user to the restored approved version (`/projects/{projectId}/daily-reports/{source_report_id}/view`).

### Rationale
- Completely preserves audit history: the draft is soft-deleted, and the correction request transition is permanently recorded as `CANCELLED`.
- Self-service unblocking without needing database administrator intervention.
- The confirmation dialog prevents accidental clicks from discarding legitimate draft work.

### Alternatives Considered
- *Hard deletion of the draft report*: Rejected because audit compliance and soft-delete models (`ChildRowModel`, `AuditSoftDeleteModel`) mandate traceable deletion timestamps.

---

## Decision 4: Enriched Version Lineage Attribution & Localized Formatting

### Problem
`DailyReportVersionSerializer` only exposed basic version numbers and statuses. Stakeholders could not see who authored each version, what justification was entered for the correction, or when it was approved. Furthermore, version 1 displayed misleading placeholder text or erroneously inherited successor reasons.

### Decision
1. Enhance `DailyReportVersionSerializer` with:
   - `modifier_name`: Full name of the user who created or last updated the version.
   - `correction_reason`: Reason extracted from `DailyReportCorrectionRequest` where `result_report = version`. For version 1 (root), return `None`.
   - `approved_at`: ISO timestamp of approval (from `AuditLog` or approval action).
2. Enhance `ApprovalStatusBar.tsx` version list:
   - Display version number, status badge (`جاری / Current`, `قفل / Locked`, `پیش‌نویس / Draft`).
   - Display `modifier_name`.
   - Display `correction_reason` or "ثبت اولیه / Initial submission" for v1.
   - Format `approved_at` using Jalali calendar (`formatJalaliDateTime`) for Persian locale.
   - Navigation links to inspect historical versions in read-only mode.

### Rationale
- Provides clear provenance and auditability.
- Strict isolation of root version guarantees no back-propagation of correction reasons.
- Consistent Jalali formatting adheres to Constitution Principle III.
