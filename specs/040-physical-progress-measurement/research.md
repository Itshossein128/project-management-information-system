# Research & Technical Decisions: Physical Progress Measurement, Financial Governance & Technical Approval

## Feature: `specs/040-physical-progress-measurement`

### Research Topic 1: Unified Enum Alignment (`quantity_based`, `weighted_milestones`, `evidence_based`)

- **Context**: The existing database model in `schedule.models.MeasurementMethod` had choices: `QUANTITY = 'quantity'`, `WEIGHTED_MILESTONES = 'weighted_milestones'`, `EVIDENCE_PERCENT = 'evidence_percent'`. The specification requires standardized enums: `quantity_based`, `weighted_milestones`, `evidence_based`.
- **Decision**: Update `schedule.models.MeasurementMethod` to define:
  ```python
  class MeasurementMethod(models.TextChoices):
      QUANTITY_BASED = 'quantity_based', 'Quantity based'
      WEIGHTED_MILESTONES = 'weighted_milestones', 'Weighted milestones'
      EVIDENCE_BASED = 'evidence_based', 'Evidence based'
      # Backwards compatibility alias support:
      QUANTITY = 'quantity', 'Quantity (legacy)'
      EVIDENCE_PERCENT = 'evidence_percent', 'Evidence percent (legacy)'
  ```
  Provide normalizers in `measurement_service.py` and frontend `progress.ts` so that incoming `'quantity'` maps to `'quantity_based'`, and `'evidence_percent'` maps to `'evidence_based'`.
- **Alternatives Considered**:
  - Hard migration replacing all existing rows with no backward compatibility: Risk of breaking existing client code or API consumers that send `quantity` or `evidence_percent`.
  - Keeping only the old names: Violates FR-001 and constitution consistency requirements.

---

### Research Topic 2: Strict Financial Governance in Interim Payment Certificates (IPC)

- **Context**: `apps/api/core/contracts/services/ipc_service.py` previously calculated `qty_current` using `actual_progress` (contractor claimed progress):
  ```python
  progress_start = float(earliest_before.actual_progress) if earliest_before else 0
  progress_end = float(latest.actual_progress)
  progress_delta = max(progress_end - progress_start, 0)
  qty_current = Decimal(str(progress_delta * float(item.activity.total_quantity or 0)))
  ```
  This allowed unapproved or disputed quantities to trigger financial payouts.
- **Decision**:
  - `auto_populate_ipc` must query `approved_progress` instead of `actual_progress`.
  - For `progress_start`, look for latest `approved_progress` before `ipc.period_start`.
  - For `progress_end`, look for latest `approved_progress` on or before `ipc.period_end`.
  - If `latest` has `approved_progress is None` or `0`, or no approved progress exists, `progress_delta = 0`, `qty_current = Decimal('0')`, and `amount_current = Decimal('0')`.
  - If an activity has recorded progress (`actual_progress > 0`) during the period but `approved_progress` is null/0, append or record a structured warning:
    `«پیشرفت این فعالیت فاقد تأیید فنی مهندس ناظر است»`.
- **Alternatives Considered**:
  - Allow a configuration flag to bill unapproved progress: Rejected per core principle G01 and constitution financial isolation. Contractor claims must NEVER be monetized prior to official supervisor sign-off.

---

### Research Topic 3: Synchronous Validation of Approved Measurement Method

- **Context**: Previously, background Celery tasks skipped activities without approved measurement versions silently, logging a warning. If manual progress was submitted, `require_approved_version` raised `ProgressValidationError('روش اندازه‌گیری این فعالیت هنوز تأیید نشده است.', 'measurement_not_approved')`. However, daily report activities and sub-report activities lacked synchronous validation at serializer/API submission time.
- **Decision**:
  - Add synchronous validation in `DailyReportActivitySerializer.validate()`:
    When an `activity_ref` is provided, synchronously check if an active approved `ActivityMeasurementVersion` exists via `get_current_approved_version(activity_ref)`.
    If not, raise `serializers.ValidationError`:
    `{'error': {'code': 'measurement_not_approved', 'message': 'روش اندازه‌گیری این فعالیت هنوز تأیید نشده است.'}}` (or standard DRF validation error formatted with code `'measurement_not_approved'`).
  - Do the same in `DisciplineSubReportActivity` serialization / save (`UnitReportActivitySectionSerializer` and `SubReportActivitySerializer`).
- **Alternatives Considered**:
  - Validating only upon report approval: Rejected because it allows bad data to accumulate in drafts and surprises users days later upon submission. Synchronous API validation gives instant feedback.

---

### Research Topic 4: Synchronous Rejection of Progress > 100% (No Clamping)

- **Context**: In construction management, cumulative progress exceeding 100% represents either an error or unapproved scope expansion. Clamping/capping values to 100% masks over-execution and creates financial and schedule discrepancies.
- **Decision**:
  - In `validate_progress_pct` and `compute_quantity_progress`:
    If cumulative progress or quantity causes the ratio to exceed `1.0` (taking into account approved `ActivityQuantityChange`), raise `ProgressValidationError` with error code `progress_exceeds_100` and exact Persian message:
    `«مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند»`.
  - In `DailyReportActivitySerializer.validate()`:
    Calculate proposed cumulative quantity for `activity_ref` = existing approved cumulative quantity + other approved reports' quantities + current row quantity. If this exceeds `effective_total_quantity`, reject with code `progress_exceeds_100`.
- **Alternatives Considered**:
  - Automatically clamp to 100% with a warning: Strictly forbidden by FR-010 and SC-003 ("No Clamping").
  - Warning only without blocking: Rejected; causes invalid reporting and downstream EVM corruption.

---

### Research Topic 5: Supervisor Technical Approval Workflow & Photo-Only Rejection

- **Context**: `ProgressTechnicalApproveView` existed at `POST /api/v1/projects/:projectId/progress/:activityId/technical-approve/`, but:
  1. The frontend had no UI trigger or modal dialog in `ActivityProgressTable.tsx`.
  2. The endpoint did not allow the supervisor to specify a verified percentage (it merely copied `actual_progress` to `approved_progress`).
  3. Photo rejection (`photo_not_technical_approval`) needed clear Persian messaging:
     `«بارگذاری عکس به‌تنهایی معادل تأیید فنی نیست؛ تأیید صریح ناظر الزامی است»`.
- **Decision**:
  - Enhance `technical_approve_progress`:
    Accept optional `approved_progress_pct` (or `approved_progress`) in payload: if provided, validate that `0 <= pct <= 1` (or 100%), and ensure `pct <= actual_progress + epsilon` (cannot approve more than claimed without explicit documented basis).
    Verify user has `approve_reports` permission.
    If `data.get('basis') == 'photo'` or `data.get('approved_by_photo')`, reject with `photo_not_technical_approval` and the exact Persian message.
  - In frontend:
    Add a Technical Approve button and modal dialog in `ActivityProgressTable.tsx`. Only display/enable for users holding `approve_reports` via `usePermission(projectId)`.
    Modal collects:
    - Activity code & name (display)
    - Claimed progress % (display)
    - Approved progress % (number input, defaulting to claimed %)
    - Evidence references (e.g. Test sheet #, Survey log #)
    - Basis selector (explicitly disallow "photo only" as valid basis)
- **Alternatives Considered**:
  - Allow any authenticated user to approve: Rejected; violates RBAC and principle I.
  - Approve entire project at once: Supervisors need granular activity-level approval capability.

---

### Research Topic 6: Four-Way Progress & `period_quantity` Calculation

- **Context**: `get_activity_progress_breakdown` in `progress_service.py` returned `period_progress_pct`, `cumulative_progress_pct`, `planned_progress_pct`, and `approved_progress_pct`, but omitted the executed physical volume in the period (`period_quantity`).
- **Decision**:
  - In `get_activity_progress_breakdown`:
    Calculate `period_quantity`:
    - For quantity-based activities: `period_progress_delta * effective_total_quantity` (or delta of `cumulative_quantity` between `period_start` and `period_end`).
    - Format or round to appropriate decimal places (e.g. 2 to 4 decimal places).
    - Return `period_quantity` in the row dictionary.
  - In `ActivityProgressTable.tsx`:
    Add column `حجم دوره` displaying `row.period_quantity ?? "—"` with `row.unit`.
- **Alternatives Considered**:
  - Show period quantity only in sub-reports: Rejected; executive progress monitoring requires seeing both percentage and physical quantity side-by-side.
