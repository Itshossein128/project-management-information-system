# Research: HR & Capacity Gap Closure (FR-HR)

**Feature**: `006-hr-capacity`  
**Date**: 2026-10-08

## Current state (codebase)

| Area | Status | Notes |
|------|--------|-------|
| User identity / contact / status | Partial | `full_name`, email, mobile, `UserStatus`; `organization` text only |
| Skills / qualifications / supervisor / org unit | Missing | No dossier extensions; OBS `OrganizationUnit` exists unused by User |
| ProjectMember | Present | Access + optional wage/dates/position — **not** % capacity / WBS / activity allocation |
| Wage ACL | Missing | Wage exposed on some membership serializers without field-level gate |
| ResourceAllocation | Missing | No model, capacity calc, or exception workflow |
| Leave / overtime | Present | `hr` app; reuses report permissions |
| Daily-report labor | Present | Headcount grids; `_auto_create_costs_from_report` uses `daily_rate` |
| Progress isolation | Present | Progress from measured `DailyReportActivity` only — keep |
| HR permission codes | Missing | No `view_hr` / `edit_hr` / `approve_hr` / `view_wage` |

## Decisions

### D1 — Person dossier on User (+ OBS FK)

**Decision**: Add to `authentication.User`: `skills` (JSON list of strings), `qualifications` (JSON list), `org_unit` FK → `master_data.OrganizationUnit` (null), `supervisor` FK → User (null, SET_NULL). Status continues via existing `status` / `is_active`. Position remains project-contextual via `ProjectMember.position`.

**Rationale**: Spec person is org-wide; User already holds identity/contact; OBS already exists; minimal coherent change (constitution V).

**Alternatives considered**: Separate `hr.PersonProfile` 1:1 (extra join for little gain); put skills only on ProjectMember (wrong scope for FR-HR-001).

### D2 — ResourceAllocation in `hr`, not `ProjectMember` / `resources`

**Decision**: New `hr.ResourceAllocation` (`AuditSoftDeleteModel`): `person` (User), `project`, optional `wbs`, optional `activity`, `start_date`, `end_date`, `role` (Char), `capacity_percent` (Decimal 0–N), optional `capacity_hours`, `work_location`, `supervisor` (User), `status` (`planned`/`active`/`completed`/`cancelled`), links to capacity exception when over-capacity.

**Rationale**: Spec requires allocation ≠ membership; `resources` app is materials; leave/OT already live in `hr`.

**Alternatives considered**: Overload ProjectMember with % capacity (conflates access with planning); put in `projects` (wrong domain home).

### D3 — Capacity overlap math and standard day

**Decision**: Available capacity default **100%** per person (overridable later via dossier field `default_capacity_percent` if needed; v1 hard-default 100). For a candidate allocation interval, sum `capacity_percent` of overlapping non-deleted allocations for the same person (any project). If only hours provided: `capacity_percent = capacity_hours / STANDARD_DAY_HOURS * 100` with **STANDARD_DAY_HOURS = 8**. Conflict when `existing_sum + candidate > available`.

**Rationale**: Spec assumption; unambiguous server rule for SC-001.

**Alternatives considered**: Hours-only capacity (harder cross-project compare); calendar-aware FTE (out of scope).

### D4 — Soft-block save; hard path via CapacityException

**Decision**: `POST/PATCH` allocation that would exceed capacity without an approved exception → **409** `capacity_conflict` with payload `{ available, committed, requested, overlapping_allocation_ids }`. Client then submits exception (reason) → manager `approve` → allocation create/update with `has_capacity_exception=True` and FK to exception. Draft/rejected exception does not authorize over-capacity.

**Rationale**: Matches FR-HR-004/005 (warn + exception); avoids silent overbook.

**Alternatives considered**: Soft warn always allow (fails SC-001); hard block forever (no exception path).

### D5 — Permissions and optional capability

**Decision**: Add permission codes: `view_hr`, `edit_hr`, `approve_hr`, `view_wage` (and `edit_wage` if write of wage/rates is separate). Seed via permissions migration pattern. Allocation CRUD: `view_hr`/`edit_hr`; exception approve: `approve_hr`. Wage/approved-rate fields omitted unless `view_wage`. Optional: add `'hr'` to project `CAPABILITY_CATALOG` if product wants feature toggle (default enabled for existing projects in migration). Leave/OT may keep report perms in v1 (out of scope to migrate).

**Rationale**: Aligns with `{view|edit|approve}_*` catalog; closes SC-HR-003 wage leak.

**Alternatives considered**: Reuse `view_reports` for allocations (wrong semantics); hide wage client-only (fails constitution I).

### D6 — ApprovedLaborRate + cost estimate

**Decision**: New `hr.ApprovedLaborRate` (project + person optional, amount, currency aligned with project, effective dates, `AuditSoftDeleteModel`). Estimate endpoint/service: if approved rate + approved hours exist → `rate × hours`; else return warning `missing_approved_rate` and null amount — never invent from membership wage or daily_rate without permission and without calling it “approved.” Prefer approved rate over daily-report auto cost when estimating (auto cost path can remain but must respect `view_wage` for rate display).

**Rationale**: FR-HR-008; wages stay confidential.

**Alternatives considered**: Always use ProjectMember.wage (not “approved”; ACL missing); invent mid-band rate (forbidden).

### D7 — Progress and attendance isolation (regression only)

**Decision**: No code path from ResourceAllocation → ActivityProgress. No change to `recalculate_activity_progress` inputs. Document and test that allocation create and labor headcount alone do not change progress.

**Rationale**: FR-HR-007 / SC-HR-002 already satisfied for manpower; must not regress when allocation lands.

### D8 — UI surfaces (minimal)

**Decision**: Project route/panel for allocations list + create/edit with capacity conflict UX; person dossier edit on user/settings or project people drawer; exception approve action for managers; redact wage in membership UI without `view_wage`.

**Rationale**: SC-005 needs end-to-end visibility; avoid building full HRIS.

## Resolved clarifications

All Technical Context items resolved from codebase + FR-HR assumptions — no remaining NEEDS CLARIFICATION.
