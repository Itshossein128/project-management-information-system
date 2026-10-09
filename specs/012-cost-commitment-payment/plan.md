# Implementation Plan: Cost Commitment & Payment Gap Closure

**Branch**: `012-cost-commitment-payment` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-cost-commitment-payment/spec.md` (FR-CST gap closure)

**Tasking constraint (user)**: Implementation tasks (`/speckit-tasks` and implement) **MUST** follow **TDD** — write a failing test first, then the minimal production change that makes it pass, then refactor. See [TDD Approach](#tdd-approach).

## Summary

Extend existing `cost_control` (Commitment / ActualCost / Payment / remaining) and join approved procurement requisitions so FR-CST gaps close: payment terms + optional contract/requisition origin on commitments; actual-cost occurrence/register dates and approval status; duplicate-safe payments with authorized exception; contract/order remaining; non-double-counting remaining math; and a document-traceable cost–commitment–payment view. Employer IPC receivables stay in `011-contracts-ipc`.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query; apps `cost_control`, `procurement`, `contracts`  
**Storage**: PostgreSQL (UUID PKs, soft-delete audit models)  
**Testing**: **TDD with pytest + pytest-django** for all backend gaps; Playwright/e2e only for UI smoke after API green; no claiming done from typecheck alone  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Remaining and ledger report O(commitments + costs + payments in project) with aggregates; no N+1 on list/report  
**Constraints**: Extend existing spine — no parallel ledger; preserve 010 remaining/ceiling gates; do not redesign GRN/warehouse; bilingual UI (fa/en)  
**Scale/Scope**: Additive model fields + services + a few endpoints + costs UI payments/report panel; P2 requisition→commitment handoff

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — all mutations under `/api/v1/projects/{uuid}/` with `view_costs` / `edit_costs` / existing procurement perms |
| II. Data integrity end-to-end | Pass — model → migration → serializer → service → API → UI → pytest (+ e2e smoke for UI) |
| III. Bilingual UX | Pass — new labels/errors in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — approve/void/exception paths with codes and localized messages; no silent history rewrite |
| V. Minimal coherent changes | Pass — extend Commitment/ActualCost/Payment + remaining_service; thin convert service from procurement |
| VI. Evidence-based verification | Pass — TDD pytest first; report which suites ran |
| VII. Accessible practical UX | Pass — costs page payments + report; clear validation |

**Post-Phase 1 re-check**: Still pass — design adds fields/services only; remaining formula change is documented and covered by failing-first tests.

## TDD Approach

Every implementable backlog item produced later by `/speckit-tasks` MUST be ordered and executed as:

1. **Red** — Add or extend a pytest (API or service) that asserts the FR/SC behavior and **fails** on current `develop`.
2. **Green** — Minimal model/service/serializer/view/UI change to pass that test.
3. **Refactor** — Keep tests green; no drive-by refactors outside the gap.

Rules:

- Prefer one vertical slice per story (e.g. duplicate payment guard) over big-bang migrations.
- Backend gaps get pytest before UI; UI follows with a thin client against the already-green API (optional Playwright smoke last).
- Regression locks for already-correct behavior (e.g. commitment approve requires WBS/CBS) stay as tests that start green.
- Do not mark a task done without the new/updated test file named in the verification evidence.

## Project Structure

### Documentation (this feature)

```text
specs/012-cost-commitment-payment/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1 (TDD validation commands)
├── contracts/           # Phase 1 API/UI contracts
│   ├── commitment-payment-terms.md
│   ├── actual-cost-lifecycle.md
│   ├── payment-duplicate-guard.md
│   ├── remaining-and-report.md
│   └── requisition-to-commitment.md
├── checklists/requirements.md
└── tasks.md             # Phase 2 (/speckit-tasks — TDD-ordered; NOT created here)
```

### Source Code (touched)

```text
apps/api/core/cost_control/
  models.py                 # payment_terms, contract/requisition FKs; actual dates/status; payment exception fields
  migrations/000X_*.py
  serializers.py
  cbs_services.py           # create_payment duplicate guard; remaining helpers
  services/remaining_service.py   # non-double-count formula
  services/ledger_report_service.py  # NEW optional: cost–commitment–payment lines
  services/commitment_origin_service.py  # NEW: from requisition/contract
  cbs_views.py / views.py / urls.py
  tests/test_commitment_payment_terms.py      # TDD
  tests/test_actual_cost_lifecycle.py         # TDD
  tests/test_payment_duplicate_guard.py       # TDD
  tests/test_remaining_no_double_count.py     # TDD
  tests/test_contract_order_remaining.py      # TDD
  tests/test_ledger_report.py                 # TDD
  tests/test_requisition_create_commitment.py # TDD (may live under procurement/tests)
  ENDPOINTS.md

apps/api/core/procurement/
  services/...              # financial-review gate for convert; create-commitment action
  views / urls              # POST convert/create-commitment

apps/web/src/
  app/lib/api/central-data.ts (or costs API module)
  components/costs/*          # payment terms; payments panel; ledger report
  app/routes/project-costs.tsx
  locales en.json / fa.json
```

**Structure Decision**: Stay in the existing monorepo apps; no new package. Tests live next to domain apps (`cost_control/tests`, `procurement/tests`) following current pytest layout.

## Complexity Tracking

None — additive extensions + one formula clarification. No new top-level apps.

## Implementation Phases (TDD-shaped)

1. **P1 Remaining non-double-count** — Red: remaining with linked actual+commitment; Green: formula in `remaining_service`.
2. **P1 Commitment fields** — Red: payment_terms + optional contract FK round-trip; Green: model/API/UI.
3. **P1 Actual cost lifecycle** — Red: occurrence/register dates + approve status + classification/document gates; Green: model/service.
4. **P1 Payment duplicate guard** — Red: second payment same `document_ref` blocked; Green: guard + exception ack path.
5. **P1 Contract/order remaining + ledger report** — Red: remaining & report endpoints; Green: services + costs UI.
6. **P2 Requisition → commitment** — Red: convert only after financial review / approved; Green: origin service + action.

Each phase starts with the named test file failing, then implementation.
