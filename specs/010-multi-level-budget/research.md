# Research: Multi-Level Budget Gap Closure

**Feature**: 010-multi-level-budget  
**Date**: 2026-10-09

## R1 — Version model vs mutable rows only

**Decision**: Introduce `BudgetVersion` as the unit of approval; every `Budget` line belongs to exactly one version.

**Rationale**: FR-BUD-002 requires comparable kinds (initial/approved/revised/final_forecast). Mutating a single live table cannot preserve history or “approved vs forecast” semantics.

**Alternatives considered**: Soft-history triggers on `Budget` — rejected (harder to compare, no submit state). Separate snapshot JSON — rejected (breaks relational WBS/CBS FKs and remaining joins).

## R2 — Control baseline for ceiling

**Decision**: Project budget ceiling for FR-BUD-006 = sum of line amounts on the current **control version** (status=`approved`, kind in `approved`|`revised`, latest by `version_number`). Final forecast never controls ceiling until approved/promoted.

**Rationale**: Spec edge case: forecast visible but not ceiling. Aligns with project registration’s `budget_approved_*` without replacing `contract_amount`.

**Alternatives considered**: Use only `Project.contract_amount` — rejected (line-item budget can differ from registration ceiling; FR-BUD is line-level). Dual independent ceilings — deferred (document that registration gate remains separate).

## R3 — Phase level without Phase table

**Decision**: `level=phase` lines reference `wbs` where the WBS node is a phase (existing WBS structure / package meta). Validation: wbs required; prefer nodes with phase semantics when metadata exists, otherwise allow any WBS for v1 with level tag.

**Rationale**: Spec 04 already models phases in WBS; no Phase master in codebase.

## R4 — Change request vs transfer

**Decision**: **BudgetChangeRequest** required when net project total changes or approved baseline structure/amounts change beyond net-zero reallocation. **BudgetTransfer** allowed when source and target are on the same approved control version, net sum unchanged, both headings allowed, and project ceiling not exceeded.

**Rationale**: FR-BUD-003 vs FR-BUD-005 distinction in the implementation spec.

## R5 — Remaining formula

**Decision**: `remaining = approved_amount − committed − consumed` per heading key (prefer CBS if set, else WBS+category, else project+category). Committed = approved `Commitment` amounts (+ active contract amounts attributed to heading when linked). Consumed = `ActualCost` amounts. Display floor 0 with `overrun=true` when negative.

**Rationale**: FR-BUD-004; matches existing commitment/actual models.

## R6 — Legacy migration

**Decision**: Data migration creates one `BudgetVersion` per project that has orphan `Budget` rows: kind=`approved` if `project.budget_approved_at` set else `initial`/`draft`; attach all orphan lines; set `is_control=True` when approved.

**Rationale**: Keep BudgetGrid and cost summary working without manual re-entry.

## R7 — Permissions

**Decision**: Reuse `view_costs`, `edit_costs`, `approve_costs`. No new permission codes in v1.

**Rationale**: Constitution V; `approve_costs` already exists for cost domain.
