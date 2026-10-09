# Research: Central Data Model

**Feature**: `003-central-data-model`  
**Date**: 2026-10-07

## R1 — CBS storage pattern

**Decision**: Implement `CostBreakdownNode` (CBS) as a project-scoped tree using django-treebeard `MP_Node` (same pattern as WBS), with `cbs_code`, `cbs_name`, `cost_type`, soft-delete/audit fields aligned with 002.

**Rationale**: Spec requires hierarchy distinct from WBS; treebeard already proven in-repo.

**Alternatives considered**: Flat `CostCategory` enum only (already exists) — insufficient for FR-DATA parent/child centers. Adjacency-list custom — reinventing treebeard.

## R2 — Commitment vs ActualCost vs Payment

**Decision**:
- `Commitment`: pledged future obligation (PO/contract commitment slice) with amount, currency, counterparty, WBS/CBS, status (`draft|approved|closed|cancelled`).
- `ActualCost`: remains incurred cost ledger (existing).
- `Payment`: cash/bank outflow rows linked optionally to `commitment` and/or `actual_cost`; append-only relative to source docs.
- IPC side uses `IPCCollection` for inflows (receipts), not Payment.

**Rationale**: FR-DATA-007 and glossary separation of تعهد / هزینه واقعی / پرداخت.

**Alternatives considered**: Overloaded ActualCost with a `kind` flag — conflates reporting. Reuse only CashTransaction — loses commitment remaining semantics.

## R3 — Partial IPC collections

**Decision**: New `IPCCollection` model: FK to IPC, `amount`, `collected_at`, `currency`, optional `fx_rate`, `reference`, `created_by`, soft-delete. IPC `submitted`/`approved`/`net` amounts stay immutable from collection writes. `actual_payment_date` on IPC may remain as denormalized “last collection” for backward compatibility but must not be the sole store.

**Rationale**: SC-DATA-002; current single `actual_payment_date` fails partial receipts.

**Alternatives considered**: Mutate IPC.net on each receipt — forbidden by FR-DATA-005. Only CashTransaction without IPC FK — weak certificate traceability.

## R4 — Portfolio aggregation

**Decision**: `GET /api/v1/portfolio/summary/` (or `/api/v1/projects/portfolio/`) returning per-project and totals for budget, actual, commitment, physical progress KPIs for projects the user can `view_dashboard`/`view_project`. No cross-tenant leakage.

**Rationale**: US1 / SC-005.

**Alternatives considered**: Client-only sum of project list — fails authorization consistency and SC evidence.

## R5 — Managed references

**Decision**:
- Keep `master_data.Unit`.
- Add `ContractType` (code, name_fa, name_en, is_active) org-wide; migrate `Project.contract_type` / `Contract` type toward FK with temporary CharField dual-read.
- Add `CostCode` org-wide optional synonym pointing at CBS templates OR keep cost type on CBS nodes and seed catalog; prefer CBS `cost_type` + optional global `CostCode` table for non-tree codes.
- Status enums remain TextChoices where finite; expose via schema/options endpoint rather than free text.

**Rationale**: FR-DATA-003 / SC-004 without big-bang rewrite of every status field.

**Alternatives considered**: Force all statuses into DB tables — high churn, low value for closed enums.

## R6 — OrganizationUnit & Stakeholder

**Decision**:
- `OrganizationUnit`: org-wide, self-FK parent, name, code, status; `Project.owning_unit` nullable FK.
- `Stakeholder`: project-scoped; name, organization_name, role, email/phone, influence (1–5), interest (1–5), communication_need, status; soft-delete.

**Rationale**: Entity table + foundation for spec 15.

**Alternatives considered**: Only free-text employer on Project — already exists and fails SC-001 for Stakeholder/OBS.

## R7 — Navigation ≤3 steps

**Decision**: Ensure serializers embed `project_id`, `wbs_id`/`wbs_code`, `activity_id` on daily report activity rows and progress rows; optional `GET .../daily-reports/{id}/navigation/` returning `{report, activity, wbs, project}` for one-call drill-up (counts as one logical step plus two UI clicks max).

**Rationale**: SC-DATA-003 / FR-012.

**Alternatives considered**: UI-only breadcrumbs without API — weaker automated proof.

## R8 — Dependency on 002

**Decision**: Require 002 money helpers and soft-delete conventions for new financial/CBS entities. If 002 not merged in a branch, cherry-pick `common.money` / AuditSoftDelete usage patterns.

**Rationale**: Spec 02 depends on 01.

**Alternatives considered**: Duplicate currency logic — rejected (constitution V).
