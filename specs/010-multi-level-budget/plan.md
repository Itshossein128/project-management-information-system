# Implementation Plan: Multi-Level Budget Gap Closure

**Branch**: `010-multi-level-budget` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-multi-level-budget/spec.md`

## Summary

Close FR-BUD gaps on the existing Sprint cost-control budget stack (`Budget`, bulk upsert, `BudgetGrid`, cost summary): add **BudgetVersion** (initial / approved / revised / final_forecast) with draft→submit→approve; extend lines for project / phase / contract / WBS / CBS / period; lock approved baselines behind **BudgetChangeRequest**; expose **remaining allocatable**; support **intra-budget transfers** under ceiling; hard-block over-project-ceiling allocation. Extend `apps/api/core/cost_control/` and costs UI; do not replace CBS/commitments/actuals or invent a ledger.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, existing `cost_control` models/services/views, `contracts.Contract`, `projects.WBS`, React + TanStack Query, i18next

**Storage**: PostgreSQL — new `BudgetVersion`, `BudgetChangeRequest`, `BudgetTransfer` tables; additive FKs/fields on `Budget` (version, level, contract, period); data migration for legacy rows

**Testing**: pytest + pytest-django (TDD); frontend typecheck for touched types

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/budgets/…` and related version/CR endpoints

**Project Type**: Monorepo web application

**Performance Goals**: Version list/compare and remaining snapshot within normal latency for &lt;500 lines

**Constraints**: Django 4.2 pin; project tenancy + `view_costs` / `edit_costs` / `approve_costs`; soft-delete / audit; bilingual; minimal coherent extension of `cost_control` (no parallel budget app)

**Scale/Scope**: Gap-close on multi-level versioned budget + change control + remaining/transfer; not GL, not full EVM

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | Version submit/approve, CR, transfer, line edits behind membership + permissions |
| II. Data integrity end-to-end | PASS | Version + lines + CR + remaining through model→API→UI→tests; migrate legacy rows |
| III. Bilingual / locale-correct | PASS | Status/kind labels, remaining, CR messages localized |
| IV. Explicit safe mutations | PASS | Approved baseline immutable; CR approve applies atomically; ceiling hard-block |
| V. Minimal coherent changes | PASS | Extend `cost_control` + BudgetGrid/costs route; reuse Commitment/ActualCost |
| VI. Evidence-based verification | PASS | pytest per story (versions, CR lock, remaining, transfer, ceiling) |
| VII. Accessible practical UX | PASS | Version picker, remaining columns, CR panel on costs budget tab |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/010-multi-level-budget/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── budget-versions.md
│   ├── budget-change-requests.md
│   ├── remaining-and-transfers.md
│   └── budget-lines.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/api/core/cost_control/
├── models.py                    # BudgetVersion, BudgetChangeRequest, BudgetTransfer; Budget extensions
├── services/
│   ├── budget_service.py        # extend: version-aware upsert, ceiling
│   ├── budget_version_service.py
│   ├── budget_change_service.py
│   └── remaining_service.py
├── views.py / budget_version_views.py / urls.py / serializers.py
└── tests/test_budget_versions.py, test_budget_change_requests.py, test_remaining_transfer.py

apps/web/src/
├── app/lib/api/costs.ts         # version/CR/remaining/transfer clients
├── components/costs/
│   ├── BudgetGrid.tsx           # version-aware; lock when approved
│   ├── BudgetVersionsPanel.tsx
│   ├── BudgetChangeRequestPanel.tsx
│   └── RemainingAllocatablePanel.tsx
└── app/routes/project-costs.tsx # wire panels / tabs
└── app/locales/{en,fa}.json
```

## Complexity Tracking

N/A — no constitution violations.
