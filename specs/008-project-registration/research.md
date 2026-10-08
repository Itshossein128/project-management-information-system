# Research: Project Registration & Kickoff Gap Closure (FR-PRJ)

**Feature**: `008-project-registration`  
**Date**: 2026-10-08

## Current state (codebase)

| Area | Status | Notes |
|------|--------|-------|
| Project create / list / patch | Present | `ProjectViewSet`; create via `create_project_with_creator`; default **status=active** |
| Status enum | Partial | `active`, `suspended`, `completed`, `handed_over` — no draft / pending_approval / archived |
| Identity fields | Partial | code (unique), name, employer, PM, dates, contract_type/amount, currency, location, owning_unit; missing purpose, scope, deliverables, contract_number, budget approval metadata |
| Kickoff charter | Missing | No model or UI |
| Project change request | Missing | Schedule change request exists under `schedule` (different domain) |
| Activation gates | Missing | PATCH can set status freely with `edit_project` |
| Baseline before approval | Ungated | `baseline_service.approve_lock_baseline` does not check project status |
| Permissions | Partial | `view_project` / `edit_project`; no `approve_project` |
| UI | Partial | Create wizard + settings edit protected fields directly |

## Decisions

### D1 — Expand `ProjectStatus` on existing `Project`

**Decision**: Replace/extend choices to: `draft`, `pending_approval`, `active`, `suspended`, `completed`, `archived`. Migrate `handed_over` → `completed`. New creates default to `draft`. Existing rows remain `active` / mapped status.

**Rationale**: Spec FR-PRJ-002; one root entity already exists (constitution V).

**Alternatives considered**: Separate `ProjectLifecycle` table (unnecessary indirection); keep `handed_over` as distinct forever (spec maps to closed/completed).

### D2 — Additive identity fields; budget approval flag

**Decision**: Add `purpose`, `scope_description`, `main_deliverables` (Text), `contract_number` (Char). Treat existing `contract_amount` as **initial budget ceiling**. Add `budget_approved_at` (DateTime null) + `budget_approved_by` (FK User null). Activation requires `project_manager`, non-blank `scope_description`, and `budget_approved_at` set (set during approve-to-active or explicit budget-approve step in the same transition).

**Rationale**: Spec FR-PRJ-001/003; avoid renaming `contract_amount` (wide UI/API use).

**Alternatives considered**: New `initial_budget` column duplicate of amount (confusion); require separate Budget module approval (out of scope 09).

### D3 — Lifecycle transitions in a dedicated service

**Decision**: `projects/services/lifecycle_service.py` with explicit actions: `submit_for_approval`, `approve` (→ active if gates pass; sets `budget_approved_at` if still null when amount present), `reject` (→ draft with reason optional), `suspend`, `resume` (→ active), `complete`, `archive`. Disallow free-form PATCH of `status` to illegal targets; `ProjectUpdateSerializer` either removes `status` from general PATCH or validates against allowed transitions.

**Rationale**: FR-PRJ-003; mirrors daily-report / schedule CR action endpoints.

**Alternatives considered**: Client-only status buttons calling PATCH (fails server enforcement); generic workflow engine (15 — out of scope).

### D4 — Kickoff charter OneToOne

**Decision**: `ProjectKickoffCharter` (`AuditSoftDeleteModel` if pattern fits, else TimeStamped): OneToOne → Project; fields justification, success_criteria, constraints, assumptions, key_stakeholders_summary, pm_authority (all Text). GET/PUT under `/api/v1/projects/{id}/kickoff-charter/`. Editable when project not archived (or system admin).

**Rationale**: FR-PRJ-005; one charter per project for v1.

**Alternatives considered**: JSONField on Project (harder validation/permissions); versioned charter history (not required by SC-004).

### D5 — Project change request for protected fields

**Decision**: `ProjectChangeRequest` with status `draft|submitted|approved|rejected|cancelled`; fields: project, reason (min 10), proposed payload JSON for keys in `{start_date, planned_finish_date, contract_amount, employer, scope_description}`, requester, decided_by, decided_at, decision_notes. On approve, apply payload to Project and stamp decision. While project is `active` (and optionally `suspended`), direct PATCH of those keys → **400/403** `protected_field_requires_change_request`. At most one open (`draft`/`submitted`) CR per project (or per field group) → **409** `change_request_already_open`.

**Rationale**: FR-PRJ-006 / SC-003; distinct from `ScheduleChangeRequest`.

**Alternatives considered**: Reuse schedule CR (wrong domain); allow direct edit with audit only (fails SC-003).

### D6 — Permission `approve_project`

**Decision**: Add `approve_project` to `PERMISSIONS` and seed default roles (project_manager + admin-equivalent). Use for lifecycle approve/reject and CR approve/reject. Create project: authenticated (existing). Edit draft/charter/CR create: `edit_project`. Archive mutate exceptions: Django superuser or global `admin` group (system admin).

**Rationale**: Constitution I; separates edit from approve.

**Alternatives considered**: Only `edit_project` for approve (weaker SoD); new capability catalog key (unnecessary for core lifecycle).

### D7 — FR-PRJ-004 / suspended gates

**Decision**: Shared helper `assert_project_allows_definitive_baseline(project)` — allow only when `status == active`. Call from `approve_lock_baseline` (and create baseline with `is_locked=True`). Shared helper `assert_project_allows_binding_commitment(project)` — same rule; call from the primary binding commitment entry point identified at implement time (prefer `contracts` Contract create if used as commitment; otherwise cost-control commitment create). Draft/pending_approval/suspended/archived → **400** `project_not_active_for_commitment` (or specific codes).

**Rationale**: FR-PRJ-004 and suspended edge; minimal hook points.

**Alternatives considered**: Soft warn only (fails SC); block all cost rows (too broad for line budgets 09).

### D8 — UI surfaces

**Decision**: Create wizard saves as draft; status bar with Submit / Approve / Suspend / Archive actions by permission; settings: unprotected fields editable; protected fields show “Request change”; charter tab/panel on overview or settings; list filter by status.

**Rationale**: SC-001–004 need end-to-end UX without redesigning portfolio.

### D9 — Migration strategy

**Decision**: Data migration: `handed_over` → `completed`; leave `active`/`suspended`/`completed` as-is; backfill empty new text fields to `''`; `budget_approved_at` = `created_at` for existing `active` projects that have `contract_amount` (treat legacy actives as budget-approved) so gates do not break production data; new projects start draft with null budget approval.

**Rationale**: Constitution II preserve valid existing data.

**Alternatives considered**: Force all projects to draft (disruptive); leave handed_over forever (spec closed set).
