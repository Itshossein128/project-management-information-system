# Research: Physical Progress & Periodic Reports Gap Closure (FR-PRG)

**Feature**: `009-progress-periodic-reports`  
**Date**: 2026-10-09

## Current state (codebase)

| Area | Status | Notes |
|------|--------|-------|
| Quantity → progress | Present | Approved daily `quantity_measured` / `total_quantity` recalc in `field_reports/tasks.py` |
| ActivityProgress | Present | `planned_progress`, `actual_progress`, `cumulative_quantity`, `source` daily_report\|manual; unique (activity, report_date) |
| Progress dashboard / S-curve / KPIs | Present | `progress_views.py`, `progress_service.py`, web `project-progress.tsx` |
| Manual progress | Present | POST `progress/manual/`; clamps values >100% to 100% |
| Measurement method | Missing | No enum/model; always implicit quantity |
| Basis approval gate | Missing | `total_quantity` / `weight` / `unit` exist on Activity without “approved for reporting” |
| Period vs approved | Partial | Actual ≈ cumulative snapshot; no period delta; no separate approved % |
| Photo ≠ technical approval | Missing | Photo on daily row; no rule separating evidence from approved progress |
| Project weekly/monthly report | Missing | Schedule-status + domain KPIs exist separately; inventory “weekly” PDF is unrelated |
| Figure provenance on period reports | Missing | Progress history links to daily report only |
| Method versioning | Missing | — |

## Decisions

### D1 — Measurement definition as versioned entity on Activity

**Decision**: Introduce `ActivityMeasurementDefinition` (1:current per activity) with `method` ∈ {`quantity`, `weighted_milestones`, `evidence_percent`}, basis payload (total qty/unit or milestone weights or evidence rules), `status` ∈ {`draft`, `approved`}, and append-only `ActivityMeasurementVersion` rows on each approved change. Progress records store `measurement_version_id` (FK).

**Rationale**: FR-PRG-001 / 011 require selectable method + versioned change without rewriting history.

**Alternatives considered**: Enum only on Activity without versions (fails FR-011); package-only method without activity (breaks daily-feed mapping).

### D2 — Default method for existing activities

**Decision**: On migrate/read, activities with `total_quantity` set default to `quantity` in **draft** until explicitly approved for reporting; reporting/manual entry blocked until basis approved (FR-002). Activities without total stay without an approved quantity method (quantity method unavailable).

**Rationale**: Avoids mass auto-approval of incomplete data; matches edge case “no total → method disabled.”

**Alternatives considered**: Auto-approve all existing (unsafe); require method before any progress read (too breaking for dashboard).

### D3 — Four-way progress semantics

**Decision**: API/UI expose for each activity (and rollups where applicable):

| Field | Meaning |
|-------|---------|
| `period_progress` | Incremental actual for selected interval (week/month/custom), from approved sources only when showing “approved period”; recorded-but-unapproved shown separately if needed |
| `cumulative_progress` | Latest cumulative actual (today’s semantics of `actual_progress` snapshot) |
| `planned_progress` | Planned % on as-of date (existing planned curve) |
| `approved_progress` | Last technically approved cumulative % (only advances on technical approval of progress / approved daily-report path) |

Recorded/manual drafts MUST NOT silently equal `approved_progress`.

**Rationale**: FR-PRG-004 / SC-005; maps cleanly onto extending `ActivityProgress` + snapshot DTOs without replacing S-curve.

**Alternatives considered**: Three fields only (fails approved distinction); rename `actual` only in UI (ambiguous).

### D4 — Reject >100% (replace clamp-as-success)

**Decision**: Manual entry and daily-report recalc MUST return validation error `progress_exceeds_100` when computed % > 1.0 unless an **approved quantity/basis change** is linked (reuse schedule change request item or a lightweight `ActivityQuantityChange` approved flag). Do not treat clamp as successful save.

**Rationale**: FR-PRG-003 / SC-003; current clamp hides overstatement.

**Alternatives considered**: Keep clamp + warning (fails MUST reject); hard-cap forever with no change-order path (fails exception clause).

### D5 — Technical approval vs photo evidence

**Decision**: Approved progress advances only when: (a) daily report is **approved/locked**, or (b) an explicit technical-approval action on a progress entry. Photos remain attachments/evidence and never alone set `approved_progress`. Manual entry creates `source=manual` recorded progress that stays unapproved until an authorized approve action (or project setting that treats manual as auto-approved — **default: require approve**).

**Rationale**: FR-PRG-005; aligns with 007 “approved = locked” for dailies.

**Alternatives considered**: Auto-approve any manual with photo (forbidden by spec).

### D6 — Incomplete weighted milestones

**Decision**: If method is `weighted_milestones` and milestone weights missing/sum ≠ 1 (±ε), block progress reporting with `incomplete_measurement_basis` (warn in UI; hard block on write).

**Rationale**: Spec edge case; avoid invented 100%.

### D7 — Weekly / monthly project reports as generated snapshots

**Decision**: New `ProjectPeriodReport` with `kind` ∈ {`weekly`, `monthly`}, period start/end, `generated_at`, `generated_by`, status `generated` \| `superseded`. Child `PeriodReportFigure` rows: `section`, `label_key`, `value` (nullable), `value_status` ∈ {`recorded`, `not_recorded`}, `source_type`, `source_id`, `source_url` (or resolvable path), `source_approved`, `last_updated_at`. Generation is idempotent per (project, kind, period) → supersede prior snapshot.

Weekly sections (minimum): critical activities, next-week plan, barriers/obstacles, decisions required — composed from schedule-status, approved dailies, barriers/alerts.

Monthly sections (minimum): progress summary, baseline variance, cost, commitments, IPC, key risks, next-month forecast — pull from existing modules; missing → `not_recorded` (never misleading zero).

**Rationale**: FR-PRG-007–009; SC-002 / SC-004; “not recorded” from edge cases.

**Alternatives considered**: Live-only views without snapshot (no audit of “what was reported”); PDF-only without structured figures (fails one-step provenance).

### D8 — Overrides of final figures

**Decision**: Direct PATCH of figure `value` denied by default. Optional `PeriodReportFigureOverride` with reason, old/new value, actor, timestamp; list in report history. Prefer regenerate from sources over override.

**Rationale**: FR-PRG-010.

**Alternatives considered**: Fully immutable forever (too rigid for typo fixes); free edit without trail (forbidden).

### D9 — Permissions

**Decision**: Reuse `view_dashboard` (or `view_activities`) for progress/report read; `edit_activities` for method draft/submit and manual progress; `approve_reports` (or `edit_activities` if approve_reports unavailable for method) for measurement basis approve and technical progress approve; report generate: `view_dashboard` + membership; override: `edit_activities` + reason required.

**Rationale**: Constitution I; minimal new permission codes (V).

### D10 — Placement in codebase

**Decision**: Keep entities in `schedule` app next to `ActivityProgress`; web changes on `project-progress` + small report panel/route. Do not use `inventory` department weekly endpoints.

**Rationale**: Principle V; avoids domain confusion called out in the spec.

## Resolved clarifications

No open NEEDS CLARIFICATION remain after these decisions. Phase-1 monthly optional sections use `not_recorded` when upstream modules lack data.
