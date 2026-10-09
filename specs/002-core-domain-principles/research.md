# Research: Core Domain Principles & Glossary

**Feature**: `002-core-domain-principles`  
**Date**: 2026-10-07

## R1 — Soft-delete / audit universality

**Decision**: Migrate critical project-tree models that still lack soft-delete (`Project` retention strategy, `WBS`) onto patterns compatible with `AuditSoftDeleteModel` (or equivalent soft-delete + audit fields), and add regression tests that hard-delete of approved/final rows is rejected. Do not soft-delete every legacy inventory table in this feature — scope is FR-CORE sample + project core graph.

**Rationale**: Spec SC-CORE-002 / FR-007 require zero physical deletes of approved records; current `WBS` hard-deletes and `Project` lacks soft-delete.

**Alternatives considered**:
- Global hard ban on `QuerySet.delete()` via middleware — too invasive and breaks cleanup jobs.
- Soft-delete only via API layer without DB columns — insufficient (ORM/admin can still hard-delete).

## R2 — Project currency & rial/toman

**Decision**: Add `Project.currency` with allowed values `IRR` (rial) and `IRT` (toman) for v1. Default existing projects to `IRR`. Provide server helper `assert_same_currency` / `convert_explicit(amount, from, to, rate)` that refuses mixed aggregation without `rate`. UI always renders unit label from project currency or per-amount override if present.

**Rationale**: FR-006 / SC-003; UI currently hardcodes «ریال» in places without project field.

**Alternatives considered**:
- Multi-currency with live FX feeds — out of scope (no ERP).
- Treat toman as display-only divisor of 10 — risky silent conversion without user intent.

**Conversion default**: If product later needs a fixed rial↔toman factor, require explicit `rate` parameter (document `10` as suggested default only when user confirms); never auto-apply in aggregates.

## R3 — Unset vs zero

**Decision**: Prefer nullable numeric fields (`null=True`) for quantities that may be “not recorded”; serializers use explicit `null` and OpenAPI `nullable: true`. UI empty input maps to `null`, not `0`. Where fields are already non-null with default `0`, introduce additive nullable companion only if changing default would corrupt semantics; otherwise document per-field exceptions in story tests.

**Rationale**: FR-010; progress/EVM treat missing as zero today in places.

**Alternatives considered**: Sentinel `-1` — confusing and breaks math. Separate boolean `is_recorded` on every field — too heavy for v1.

## R4 — Actionable notifications

**Decision**: Extend `notifications.Notification` with `responsible_user` (FK, nullable for broadcast) and `due_at` (nullable DateTime). Keep existing `link`. Creation helpers require `responsible_user` + `link` for actionable types; `due_at` required when `notification_type` is in an actionable allowlist.

**Rationale**: FR-011; model already has `link` but not owner/deadline.

**Alternatives considered**: Separate `Task` entity — deferred to spec 15. Overloading `message` with free text — not testable.

## R5 — Project capability toggles

**Decision**: New `ProjectCapabilitySetting` with `capability_key` (stable English code), `enabled` bool, optional `mode` (`required`|`optional`|`disabled`). Seed keys from current project nav modules (e.g. `risk`, `economic`, `procurement`, `cash_flow`, `documents`). API + project settings UI. When disabled: hide nav entry and reject create/mutate for that module with `403`/`409` capability_disabled; GET list/detail of historical rows still allowed with read permission.

**Rationale**: FR-012 + edge case “history preserved”.

**Alternatives considered**: Feature flags only in frontend — fails server enforcement. Global Django settings — not per-project.

## R6 — Fiscal period lock

**Decision**: `FiscalPeriodLock` per project with `period_start`, `period_end`, `closed_at`, `closed_by`, `reason`. Middleware/service check on mutating financial endpoints (actual costs, cash transactions, IPC pay, budget lines) when document date falls in a closed period → `409` unless `corrective=true` + `correction_reason` audited.

**Rationale**: FR-015; project-scoped v1 per Assumptions.

**Alternatives considered**: Organization-wide calendar — deferred. Soft warning only — too weak for SC.

## R7 — Duplicate document warning

**Decision**: Shared validator `warn_duplicate_document_ref(project, model, field, value)` returning warning payload; API responses include `warnings: [{code: duplicate_document_ref, ...}]` and require `acknowledge_warnings: true` to finalize when warnings present. Apply first to `ActualCost` and `CashTransaction` document refs / contract numbers where fields exist.

**Rationale**: FR-013; advisory with explicit acknowledge matches Assumptions.

**Alternatives considered**: Hard unique constraint only — may block legitimate amendments. Silent allow — fails FR.

## R8 — Glossary alignment

**Decision**: Maintain a checklist of term keys → fa/en strings in research/contracts; update `fa.json`/`en.json` and any hard-coded labels on WBS, costs, IPC surfaces. Add a lightweight pytest or scripted locale assertion for critical keys (WBS, IPC, commitment vs actual cost).

**Rationale**: US1 / SC-001.

**Alternatives considered**: Full CMS-managed glossary UI — out of scope for this feature.

## R9 — TDD workflow

**Decision**: For each user story: add failing pytest modules under the owning app’s `tests/` (and contract markdown as acceptance oracle), run to confirm fail, implement minimal code, re-run to pass. Frontend: prefer testing-library or type-level guards where present; otherwise manual bilingual checklist in quickstart after API green. No implement work in Spec Kit pass.

**Rationale**: User explicitly required TDD; constitution VI.

**Alternatives considered**: Reverse TDD (code then tests) — rejected.
