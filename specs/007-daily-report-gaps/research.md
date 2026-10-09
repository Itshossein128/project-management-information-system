# Research: Daily Site Report Gap Closure (FR-DR)

**Feature**: `007-daily-report-gaps`  
**Date**: 2026-10-08

## Current state (codebase)

| Area | Status | Notes |
|------|--------|-------|
| DailyReport header | Partial | project, date, shift, weather, preparer; **no** work_front / site location |
| Activity rows | Partial | activity_ref, qty, unit, zone/block/floor, photo, `quantity_measured`; no explicit responsible person |
| Labor rows | Partial | job-title headcount + work/OT hours; **no** absence |
| Equipment rows | Done | productive/idle/repair + idle_reason |
| Material rows | Partial | receipt / issue / waste; **no** return; no consumption location field |
| Incidents | Partial | type + description + corrective_action; **no** owner / due_date; limited types |
| Workflow | Partial | draft→submit→review→approve/reject; approved edits blocked |
| Correction / version | Missing | No amend path; SC-DR-003 incomplete |
| Unset vs zero | Partial | activity `quantity_measured` only |
| Offline sync | Done | conflict on approved; must keep not overwriting locked |
| Material vs inventory | Partial | material_ref link exists; no reconciliation hint API |
| Permissions | Done | `view_reports` / `edit_reports` / `approve_reports` |

## Decisions

### D1 — Approved equals locked

**Decision**: Keep terminal status `approved`. Product copy (fa/en) presents it as **locked** / «قفل‌شده». No new `locked` enum value. Direct PATCH/child writes remain denied for `approved`.

**Rationale**: Spec assumption; minimal change; existing progress events already fire on approve.

**Alternatives considered**: Separate `locked` status after approve (extra transition, migration of all clients); rename status to `locked` (breaking API).

### D2 — Correction request as new report version lineage

**Decision**: Introduce `DailyReportCorrectionRequest` (reason, status, requester, decision) and version lineage on `DailyReport`:

- `lineage_id` (UUID shared across versions; default = own id on create)
- `version_number` (int, starting at 1)
- `supersedes` FK → prior DailyReport (null for v1)
- `is_current` bool (exactly one current per lineage among non-deleted)

On correction open (from approved current): clone header + child rows into a **new** DailyReport with status `draft`, same project/date/shift uniqueness **waived for non-current versions** OR uniqueness scoped to `(project, report_date, shift)` where `is_current=True` only. Prior approved report stays `approved`, `is_current=False`.

**Rationale**: Retains full prior content for SC-DR-003; reuses existing edit/submit/approve path for the new draft.

**Alternatives considered**: In-place edit with JSON snapshot only (weaker row-level history); unlock-in-place (fails “retain previous version” clarity).

### D3 — Uniqueness for date/shift with versions

**Decision**: Replace/adjust unique constraint to: unique active **current** report per `(project, report_date, shift)` where `is_current=True` and `is_deleted=False`. Historical non-current versions may share the same date/shift.

**Rationale**: Spec keeps one operational report per date/shift; versions are history.

**Alternatives considered**: Change uniqueness to include work_front (out of scope v1); force date bump on correction (breaks “same shift amend”).

### D4 — Header work_front / site location

**Decision**: Add nullable/blank `work_front` CharField (max 120) on `DailyReport` (and optionally `location_notes`). Activity zone/block/floor remain for row-level detail.

**Rationale**: FR-DR-001 header requirement without inventing a WorkFront master entity in this feature.

**Alternatives considered**: FK to new WorkFront catalog (deferred); only activity-level location (fails header AC).

### D5 — Activity responsible

**Decision**: Add optional `responsible_name` CharField and optional `responsible_user` FK → User (SET_NULL). At least one of name or user SHOULD be present on submit when activities exist (warn if both empty; soft-require in v1 with clear validation message).

**Rationale**: Spec “مسئول”; User FK when known, free text for subcontractors/site names.

**Alternatives considered**: Only subcontractor_name (already exists, not the same as responsible); require ProjectMember only (too rigid for site).

### D6 — Labor absence + material return + consumption location

**Decision**:

- Labor: `absence_count` PositiveIntegerField default 0 is **wrong** for unset-vs-zero — use nullable PositiveIntegerField `absence_count` null=not recorded, 0=zero absences.
- Materials: add `RETURN = 'return'` to `MaterialTransactionType`; add optional `consumption_location` CharField.
- Keep `quantity` required for material rows when row exists; distinguish unset by not creating the row / rejecting blank quantity without coercing.

**Rationale**: FR-DR-003 / FR-DR-005 / FR-DR-010.

**Alternatives considered**: Encode return as negative issue (ambiguous); absence as computed from camp (wrong domain).

### D7 — Site events (extend incidents)

**Decision**: Extend `DailyReportIncident` (or rename presentation to “site events”):

- Expand `IncidentType` with `SITE_INSTRUCTION`, `BARRIER` (keep SAFETY/QUALITY/ENVIRONMENTAL/STOPPAGE/VISITOR).
- Add `follow_up_owner` (Char or User FK + name), `due_date` (Date, null).

**Rationale**: FR-DR-006 without a second parallel child entity; UI tab can be labeled site events / incidents.

**Alternatives considered**: Separate Barrier child model only (barriers already exist project-wide); full HSE module (14 — out of scope).

### D8 — Unset vs zero validation on submit

**Decision**: Centralize in submit validation:

- Activity: if row present and `quantity_measured=False`, quantity may be null; if `quantity_measured=True`, quantity required (0 allowed as real zero).
- Material: quantity required when row saved; never coerce null→0.
- Labor absence: null means not recorded (do not default to 0 on create unless UI explicitly sets 0).

**Rationale**: FR-DR-010; extends existing `quantity_measured`.

### D9 — Material reconciliation hint (advisory)

**Decision**: `GET .../daily-reports/{id}/materials/reconciliation/` (or include on detail) returns per linked `material_ref` row: `{ material_id, consumed_qty, available_balance, status: match|mismatch|insufficient_data }`. Uses existing material balance service read-only. Never blocks save/submit.

**Rationale**: SC-DR-002 light interpretation; constitution V (no warehouse redesign).

**Alternatives considered**: Hard stock block on submit (out of scope); ignore SC-DR-002 (fails success criteria).

### D10 — Offline sync interaction

**Decision**: Sync-batch continues to return `conflict` for approved/current locked reports. Correction must be started online (or explicit correction endpoint); offline clients must not merge into non-current historical versions as if current.

**Rationale**: Preserve Sprint 5 conflict UX; avoid silent overwrite of locked content.

### D11 — Permissions

**Decision**: Reuse `edit_reports` to create correction request; `approve_reports` to approve correction versions (same as normal approve). No new permission codes unless product later splits “request correction” from edit.

**Rationale**: Minimal coherent change; same roles already own the workflow.

### D12 — UI surfaces

**Decision**: Header field on daily report form; responsible on Activity tab; absence on Labor tab; return type + location on Materials tab; owner/due on Incidents tab; status bar shows Locked; “Show history / versions” + “Request correction” on view page for approved current reports.

**Rationale**: SC-001 / SC-003 / SC-006 without new apps.

## Resolved clarifications

All Technical Context items resolved via D1–D12; no remaining NEEDS CLARIFICATION.
