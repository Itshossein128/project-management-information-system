# Feature Specification: Physical Progress Measurement, Strict Financial Governance, and Technical Approval Workflow

**Feature Branch**: `040-physical-progress-measurement`  
**Created**: 2026-10-28  
**Status**: Draft  
**Input**: User description: "یک feature منسجم برای «سیستم جامع پیکربندی روشهای سهگانه اندازهگیری پیشرفت فیزیکی (مقدارمحور، نقاط عطف وزنی، و مستندمحور)، اعتبارسنجی بلادرنگ احجام و ممانعت از عبور از سقف ۱۰۰٪ (No Clamping)، تفکیک و محاسبه شاخصهای ۴ گانه پیشرفت، استناد قطعی صورتوضعیتهای مالی (IPC) صرفاً به پیشرفت تأییدشده ناظر، و ایجاد جریان کاربری تأیید فنی مهندسی ناظر»"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configuration and Synchronous Validation of Physical Measurement Methods (Priority: P1)

As a project controls engineer or planning manager (Planner), I want to configure, validate, and officially approve one of the three physical measurement methods (`quantity_based`, `weighted_milestones`, `evidence_based`) for every work package and activity in the WBS before any progress can be entered, so that site progress reporting is governed by standardized engineering formulas and no activity can register progress arbitrarily.

**Why this priority**: Core governance gate (G02, G05, G06). Allowing progress entry on unapproved measurement methods causes silent calculation drops in background tasks, corrupts physical progress metrics, and introduces arbitrary non-standard progress figures into executive reports.

**Independent Test**: Can be tested by creating a WBS activity without an approved measurement method and attempting to submit manual or daily report progress (verifying immediate synchronous rejection with `400 measurement_not_approved`), then configuring a quantity method with unit, configuring a milestone method with exactly 100% weights, approving the method, and verifying successful progress logging.

**Acceptance Scenarios**:

1. **Given** an activity configured with the quantity-based method (`quantity_based`),  
   **When** the user enters a valid total estimated quantity (`total_estimated_quantity > 0`) and selects a measurement unit (`unit_id`),  
   **Then** the measurement basis is approved, and subsequent progress is calculated strictly as `(quantity_actual / total_estimated_quantity) * 100`.
2. **Given** an activity configured with the weighted milestones method (`weighted_milestones`),  
   **When** the user defines milestone steps whose weight percentages sum to an amount other than exactly 100% (e.g., 90% or 110%),  
   **Then** the system rejects the definition with error code `incomplete_measurement_basis`, and visually highlights the imbalance until the total equals 100%.
3. **Given** an activity configured with the evidence-based method (`evidence_based`),  
   **When** the user attempts to approve the measurement method without defining the required technical documentation rules or checklist specifications (`evidence_rules`),  
   **Then** the system rejects the approval with error code `incomplete_measurement_basis`.
4. **Given** an activity that lacks a currently approved measurement version (`ActivityMeasurementVersion`),  
   **When** any user attempts to submit manual progress (`POST progress/manual/`) or records an execution row referencing this activity in a daily report or discipline sub-report,  
   **Then** the system immediately and synchronously rejects the request with HTTP 400 Bad Request, returning error code `measurement_not_approved` and the Persian message: «روش اندازه‌گیری این فعالیت هنوز تأیید نشده است».
5. **Given** a project planner creating or editing an activity in the WBS activity drawer (`activity-drawer.tsx`),  
   **When** the drawer opens,  
   **Then** the planner has direct access to the comprehensive Measurement Method Editor (`MeasurementEditor.tsx`), enabling the selection and configuration of all three methods with unit selection, dynamic milestone table, and evidence rules.

---

### User Story 2 - Strict Financial Governance in Interim Payment Certificates (IPC) via Approved Progress (Priority: P1)

As a contracts manager, financial officer, or supervising engineer, I want the automatic generation of Interim Payment Certificates (IPC) to calculate billable quantities and financial values exclusively based on supervisor-approved progress (`approved_progress_pct`), so that unverified contractor claims are never monetized or paid out before official engineering sign-off.

**Why this priority**: Critical financial integrity and claim prevention (G01). Currently, the system uses claimed progress (`actual_progress`) to generate IPC line items, enabling contractors to trigger payouts on disputed or unapproved quantities even if rejected by the site supervising engineer.

**Independent Test**: Can be tested by recording an activity with 50% claimed cumulative progress but only 40% supervisor-approved progress (or 0% approved), running the IPC auto-population routine (`auto_populate_ipc_items`), and asserting that the billable period volume and monetary amount reflect strictly the 40% approved progress (or 0 if unapproved), with an audit warning flagging any unapproved claimed progress.

**Acceptance Scenarios**:

1. **Given** an activity with claimed cumulative progress of 50% and supervisor-approved progress of 40% for the billing period,  
   **When** the system auto-populates IPC items for that contract period,  
   **Then** the payable quantity and financial amount are computed strictly using the 40% approved progress delta, completely ignoring the unapproved 10% claimed progress.
2. **Given** an activity with recorded daily/manual progress but without any supervisor technical approval (`approved_progress` is null or 0),  
   **When** the IPC auto-population runs,  
   **Then** the system sets the billable quantity (`qty_current`) and amount to zero (0), and issues a structured warning: «پیشرفت این فعالیت فاقد تأیید فنی مهندس ناظر است».
3. **Given** an approved IPC document,  
   **When** an auditor inspects the line item provenance,  
   **Then** the system presents the exact approved progress percentage, the supervising engineer's electronic signature timestamp, and the referenced technical approval record.

---

### User Story 3 - Synchronous Rejection of Progress Exceeding 100% (No Clamping) (Priority: P1)

As a supervising engineer and system administrator, I want the system to synchronously reject any progress entry (manual or daily report) that would cause cumulative physical progress to exceed 100% of the approved total estimated quantity, without automatically capping/clamping to 100%, so that physical quantity inflation is stopped at entry and contractors are required to submit formal quantity change orders.

**Why this priority**: Physical and contract scope compliance (G03). Silently clamping values to 100% masks over-execution and measurement errors, while deferring validation to background Celery tasks allows invalid daily reports to be approved without immediate user feedback.

**Independent Test**: Can be tested by taking an activity with 95% cumulative progress and submitting a daily report row or manual progress entry with 10% incremental volume (totaling 105%), verifying that HTTP 400 Bad Request with code `progress_exceeds_100` and the exact standardized Persian message is synchronously returned, and that the database records remain unchanged.

**Acceptance Scenarios**:

1. **Given** an activity with 95% cumulative physical progress and total estimated volume of 100 m³,  
   **When** a user submits a manual progress entry or daily report execution row claiming 10 m³ (bringing cumulative volume to 105 m³ / 105%),  
   **Then** the system synchronously rejects the request with HTTP 400 Bad Request, returning error code `progress_exceeds_100` and the exact message:  
   «مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند».
2. **Given** a rejected over-100% progress submission,  
   **When** inspecting the activity records,  
   **Then** the system has NOT clamped the cumulative progress to 100%, and the cumulative progress remains at its previous valid value (95%).
3. **Given** an activity that legitimately requires physical quantities beyond the original estimate,  
   **When** an authorized user submits and approves an official Quantity Change Order (`ActivityQuantityChange`) with a new total quantity,  
   **Then** subsequent progress entries up to the newly approved quantity ceiling (100% of the new total) are accepted.

---

### User Story 4 - Supervising Engineer Technical Approval Workflow in UI (Priority: P1)

As a supervising engineer (Resident Engineer / Supervising Consultant) with `approve_reports` permission, I want a dedicated, accessible UI action and modal dialog in the activity progress table to review claimed progress, specify the technically approved percentage, and attach engineering evidence references, while ensuring that site photos alone never substitute for official technical approval.

**Why this priority**: Operational completeness and separation of roles (G04). The backend technical approval endpoint currently exists but is orphaned with zero frontend UI trigger, preventing supervisors from executing technical approvals and leaving the "Approved %" column permanently blank or zero.

**Independent Test**: Can be tested by logging in as a user with `approve_reports` permission, navigating to `/projects/:projectId/progress`, clicking the "تأیید فنی پیشرفت" (Technical Approve) action button on an activity with pending progress, entering the verified percentage with test certificate references, and verifying that `approved_progress_pct` updates immediately. Conversely, submitting photo-only verification must be rejected with `photo_not_technical_approval`.

**Acceptance Scenarios**:

1. **Given** an authorized supervising engineer viewing the Activity Progress Table (`ActivityProgressTable.tsx`),  
   **When** they inspect an activity with recorded claimed progress,  
   **Then** a prominent action button labeled «تأیید فنی پیشرفت» (Technical Approve) is available in the row action menu.
2. **Given** a user without `approve_reports` permission (e.g., contractor field worker or read-only guest),  
   **When** viewing the Activity Progress Table,  
   **Then** the technical approval button is hidden or disabled with an explanatory tooltip.
3. **Given** a supervising engineer opening the Technical Approval dialog,  
   **When** they enter the verified progress percentage, attach technical references (e.g., concrete break test results, topographic survey sign-offs), and confirm approval,  
   **Then** the system calls the technical approval endpoint, records the supervisor's user ID and timestamp, updates `approved_progress_pct`, and updates the progress view in real time.
4. **Given** an approval submission where the basis is specified solely as photographic documentation (`basis: "photo"`),  
   **When** the request is submitted,  
   **Then** the system rejects the operation with HTTP 400 Bad Request, returning error code `photo_not_technical_approval` and message: «بارگذاری عکس به‌تنهایی معادل تأیید فنی نیست؛ تأیید صریح ناظر الزامی است».

---

### User Story 5 - Four-Way Progress Calculation and Period Physical Quantity Reporting (Priority: P2)

As an executive project manager or project controls engineer, I want the system to compute and display the complete 4-way progress breakdown—including period progress percentage (`period_progress_pct`), period physical quantity (`period_quantity`), cumulative progress percentage (`cumulative_progress_pct`), planned baseline percentage (`planned_progress_pct`), and approved percentage (`approved_progress_pct`) along with variance—so that executive reporting provides absolute physical transparency.

**Why this priority**: Reporting precision and milestone tracking (G06, G07). Currently, the breakdown API and UI omit the physical volume executed in the period (`period_quantity`), showing only percentages. Furthermore, activities measured via weighted milestones must be able to report progress across periodic cycles.

**Independent Test**: Can be tested by querying `GET progress/activities/?period_start=...&period_end=...` and verifying that the response contains `period_quantity` in the activity's unit of measurement, and verifying that `ActivityProgressTable.tsx` displays a dedicated "حجم دوره" column alongside the four progress percentages.

**Acceptance Scenarios**:

1. **Given** an activity with an approved quantity-based measurement method and unit (e.g., "متر مکعب"),  
   **When** three approved daily reports in the active week record 2 m³, 3 m³, and 5 m³ respectively,  
   **Then** the activity breakdown reports `period_quantity = 10` with unit "متر مکعب", and `period_progress_pct = 10%` (for a 100 m³ total).
2. **Given** the Activity Progress Table in the web frontend,  
   **When** the user views the table for any selected period,  
   **Then** the table displays distinct columns for:
     - حجم کل مصوب (Total Quantity)
     - حجم دوره (Period Quantity with Unit)
     - پیشرفت دوره٪ (Period Progress %)
     - پیشرفت تجمعی٪ (Cumulative / Claimed Progress %)
     - پیشرفت برنامه‌ای٪ (Planned Baseline %)
     - پیشرفت تأییدشده٪ (Approved Progress %)
     - انحراف از زمان‌بندی (Variance % with red/green status indicator)
3. **Given** an activity configured with weighted milestones (`weighted_milestones`),  
   **When** daily or periodic reports mark milestone steps as achieved,  
   **Then** the system increments period and cumulative progress by the exact sum of weights of the achieved milestones.

---

### Edge Cases

- **Zero Total Quantity in Draft Activity**: If an activity has `total_quantity = 0` or null, selecting the quantity-based method must prevent approval until a strictly positive quantity is specified.
- **Precision and Floating-Point Tolerances**: In the weighted milestone editor, floating-point sums between 99.99% and 100.01% are tolerated within `±0.01%` (or weights represented in basis points `0.0001` / decimal percentages `0-100`), but any sum outside this range must trigger `incomplete_measurement_basis`.
- **Approved Method Modification Locked**: Once a measurement method version is approved, direct inline modification of the active version is locked (`400 measurement_locked`). Any modification must be initiated via the formal method change workflow (`activities/{id}/measurement/change/`) requiring a documented justification (`reason`).
- **Retroactive Daily Report Approvals**: When an older daily report is approved out of chronological sequence, cumulative quantities must be recomputed across all subsequent reports to verify that cumulative totals at no point exceeded 100% of the approved volume.
- **Technical Approval Greater Than Claimed**: If a supervisor attempts to approve a progress percentage greater than the claimed cumulative progress without a recorded measurement basis, the system must require an explicit reason code or reject the submission.
- **Multiple Disciplinary Sub-Reports on the Same Activity in One Day**: When two sub-reports (e.g., Day Shift and Night Shift) log quantities for the same activity on the same day, the synchronous 100% ceiling check must evaluate the running cumulative sum of all approved and in-flight draft entries for that day.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Physical Measurement Methods & Configuration (US-PR-01, G05, G06)
- **FR-001**: The system MUST support exactly three mutually exclusive measurement methods for any WBS activity, identified by standardized string enums:
  1. `quantity_based`: Units complete based on ratio of executed volume to total estimated volume.
  2. `weighted_milestones`: Discrete milestone steps with assigned weight percentages summing to 100%.
  3. `evidence_based`: Qualitative or document-based progression governed by engineering rules and supervisor verification.
- **FR-002**: For `quantity_based` activities, the system MUST require both a strictly positive total estimated quantity (`total_quantity > 0`) and a valid measurement unit reference (`unit_id`) before the measurement method can be approved.
- **FR-003**: For `weighted_milestones` activities, the system MUST require at least one milestone step and enforce that the sum of milestone weights equals exactly 100% (within a tolerance of ±0.01%). If the sum differs, the system MUST reject approval with error code `incomplete_measurement_basis`.
- **FR-004**: For `evidence_based` activities, the system MUST require a non-empty technical rules specification (`evidence_rules`) before approval.
- **FR-005**: The system MUST maintain version history for measurement methods (`ActivityMeasurementVersion`). Once a version is approved, direct modification MUST be rejected with error code `measurement_locked`, requiring the user to submit a method change request with a mandatory documented justification (`reason`).
- **FR-006**: The WBS Activity Drawer (`activity-drawer.tsx`) and the standalone Measurement Editor (`MeasurementEditor.tsx`) MUST provide a unified, bilingual interface to configure, review, and approve measurement definitions, including dynamic addition/removal of milestones with real-time weight summation indicators.

#### Synchronous Progress Validation Gate (US-PR-01, US-PR-03, G02, G03)
- **FR-007**: The system MUST synchronously validate the existence of an active, approved measurement version (`ActivityMeasurementVersion`) at the API boundary whenever a progress record or daily report execution row referencing an activity is created or updated.
- **FR-008**: If a progress record or daily report row references an activity without an approved measurement method version, the server MUST synchronously reject the request with HTTP 400 Bad Request, error code `measurement_not_approved`, and the Persian message:  
  «روش اندازه‌گیری این فعالیت هنوز تأیید نشده است».
- **FR-009**: The system MUST synchronously validate at the API boundary that any new progress or execution quantity does not cause cumulative progress to exceed 100% of the approved total estimated quantity (or the total revised quantity under an approved `ActivityQuantityChange`).
- **FR-010**: If cumulative progress exceeds 100%, the system MUST NOT clamp or truncate the value to 100%. The system MUST reject the request with HTTP 400 Bad Request, error code `progress_exceeds_100`, and the exact standardized Persian message:  
  «مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند».
- **FR-011**: Approved quantity change orders (`ActivityQuantityChange`) MUST serve as the sole legitimate mechanism to increase the total approved physical volume ceiling for an activity.

#### Financial Governance & Interim Payment Certificates (US-PR-02, G01)
- **FR-012**: In the contracts and billing domain (`contracts/services/ipc_service.py`), the automatic generation of IPC line items (`auto_populate_ipc_items`) MUST derive payable period quantities (`qty_current`) and financial amounts strictly and exclusively from supervisor-approved progress (`approved_progress_pct`).
- **FR-013**: If an activity has claimed progress (`actual_progress`) but no supervisor-approved progress (`approved_progress` is null or zero), the IPC auto-population MUST set the payable quantity and monetary amount for that period to zero (0).
- **FR-014**: When generating an IPC for activities with zero approved progress, the system MUST issue a structured audit warning indicating unapproved claimed progress:  
  «پیشرفت این فعالیت فاقد تأیید فنی مهندس ناظر است».

#### Supervisor Technical Approval Workflow (US-PR-03, G04)
- **FR-015**: The system MUST provide an interactive UI action button and modal dialog for "تأیید فنی پیشرفت" (Technical Approve) in the Activity Progress Table (`ActivityProgressTable.tsx`) and project progress views.
- **FR-016**: The technical approval action MUST be restricted to users possessing the `approve_reports` permission (Supervising Engineers, Project Managers, and System Admins).
- **FR-017**: The technical approval dialog MUST enable the supervisor to review claimed progress, specify or confirm the verified progress percentage or quantity, and optionally record technical document references (`evidence_refs`).
- **FR-018**: Photographic evidence alone MUST NEVER constitute technical engineering approval. Any approval request specifying photographic documentation as the primary approval basis (`basis: "photo"`) MUST be rejected with HTTP 400 Bad Request, error code `photo_not_technical_approval`, and Persian message:  
  «بارگذاری عکس به‌تنهایی معادل تأیید فنی نیست؛ تأیید صریح ناظر الزامی است».
- **FR-019**: Each technical approval MUST record the approving supervisor's user ID, an immutable timestamp, the approved percentage, and audit comments in the activity progress history.

#### Four-Way Progress & Physical Reporting (US-PR-02, G06, G07)
- **FR-020**: The activity progress breakdown endpoint (`GET progress/activities/`) and dataset MUST compute and return all four progress indicators:
  1. `period_progress_pct`: Percentage of physical progress achieved within the selected period window.
  2. `period_quantity`: Actual physical quantity executed during the period, formatted in the activity's unit of measurement.
  3. `cumulative_progress_pct`: Total claimed cumulative progress to date.
  4. `planned_progress_pct`: Planned baseline progress as of the period date according to the approved schedule baseline.
  5. `approved_progress_pct`: Officially certified progress approved by the supervising engineer.
- **FR-021**: The system MUST compute schedule variance as `variance = cumulative_progress_pct - planned_progress_pct` (or against approved progress) and render visual indicators (red badge for delay, green badge for ahead-of-schedule) in the UI.
- **FR-022**: The Activity Progress Table (`ActivityProgressTable.tsx`) MUST include a dedicated visible column for "حجم دوره" (Period Quantity) displaying the numeric value alongside the activity's measurement unit symbol.
- **FR-023**: For activities using the weighted milestones method, completing milestones via sub-reports or progress dialogs MUST advance period and cumulative progress according to the pre-defined milestone weight percentages.

---

### Key Entities *(mandatory)*

- **ActivityMeasurementDefinition**: Represents the measurement method governance shell for a WBS activity. Contains the current method (`quantity_based`, `weighted_milestones`, `evidence_based`), current status (`draft`, `approved`, `superseded`), and foreign key to the active approved version.
- **ActivityMeasurementVersion**: An immutable, versioned snapshot of the approved measurement basis for an activity. Contains version number, method enum, approved total quantity, measurement unit ID, serialized milestone steps list (with title and weight percentage), serialized evidence rules, approving user reference, and approval timestamp.
- **ActivityProgress**: Represents periodic and cumulative progress records for an activity on a specific date or reporting cycle. Contains references to activity, measurement version, source (`daily_report`, `manual`), period progress percentage, period physical quantity (`period_quantity`), cumulative actual progress percentage (`cumulative_progress_pct`), planned baseline percentage (`planned_progress_pct`), approved progress percentage (`approved_progress_pct`), and technical approval audit metadata.
- **ActivityQuantityChange**: Represents an official quantity change order (variation order) that modifies the approved total estimated quantity of an activity. Contains activity reference, previous total quantity, proposed new total quantity, justification reason, status (`draft`, `approved`, `rejected`), approving user reference, and approval date.
- **TechnicalApprovalLog**: An immutable audit log tracking every technical approval or rejection event performed by supervising engineers. Contains activity reference, progress record reference, approving supervisor user ID, approved percentage, evidence document references, and timestamp.
- **IPCItem (Interim Payment Certificate Item)**: A financial billing line item representing work performed in a contract billing period. Strictly references the activity's `approved_progress_pct` (never `actual_progress`) to calculate period payable volume (`qty_current`) and payable monetary amount.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Interim Payment Certificate (IPC) line items generated by the system calculate payable quantities and billing amounts exclusively from supervisor-approved progress (`approved_progress`), with zero financial disbursement based on unapproved claimed progress.
- **SC-002**: 100% of attempts to submit daily report execution rows or manual progress for activities lacking an approved measurement method are synchronously blocked at the API boundary with HTTP 400 and code `measurement_not_approved`.
- **SC-003**: 100% of progress entries exceeding 100% of the approved volume ceiling are synchronously rejected with HTTP 400 and code `progress_exceeds_100`, with zero instances of automatic clamping/truncation to 100%.
- **SC-004**: Supervising engineers with `approve_reports` permission can complete a technical approval action directly from the Activity Progress Table UI in under 3 clicks and less than 15 seconds.
- **SC-005**: 100% of photo-only approval attempts submitted without explicit supervising engineer sign-off are rejected with HTTP 400 and code `photo_not_technical_approval`.
- **SC-006**: The Activity Progress Table renders all four progress metrics plus the period physical quantity (`period_quantity`) with unit symbol in 100% of project progress views.
- **SC-007**: 100% of weighted milestone measurement methods approved in the system have weights summing to exactly 100% (within ±0.01% tolerance).

---

## Assumptions

- **Existing RBAC Permissions**: The user role model already includes `view_activities`, `edit_activities`, `view_dashboard`, and `approve_reports` permissions as defined in `schedule_and_progress_ENDPOINTS.md` and `constitution.md`.
- **Unit Catalog Availability**: A standard project or global measurement unit catalog (`unit_id` referencing unit definitions like m³, m², kg, etc.) is available in the system for binding to quantity-based activities.
- **Jalali and Gregorian Dual-Calendar**: All date-based progress calculations and queries accept either Jalali (`1404-01-15`) or ISO Gregorian strings, handled consistently with the rest of the Velora application.
- **EVM and Contract Decoupling**: Earned Value Management (EVM) indices (PV, EV, AC, CPI, SPI) consume approved progress as calculated by this feature, but complex cost-variance algorithms remain scoped to EVM specific modules.
- **Offline Sync Reconciliation**: In offline mobile/site scenarios, daily report activities entered offline are validated against the approved measurement version upon synchronization, rejecting over-100% entries before committing to the server state.
