# Implementation Plan: Contracts & IPC Gap Closure

**Branch**: `011-contracts-ipc` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-contracts-ipc/spec.md` (FR-CON gap closure)

## Summary

Extend the existing Django `contracts` app and web Contracts UI so FR-CON is fully covered: free-text **payment terms** on contracts; distinct **submitted** vs **approved** IPC amounts with variance notes; hard regression that **collections never mutate approval status or amounts**; and a **receivables report** (overdue + near-due) with UI on the contracts page.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query, existing `contracts` + `cash_flow`  
**Storage**: PostgreSQL (UUID PKs)  
**Testing**: pytest + pytest-django; UI manual / existing e2e patterns  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Receivables report O(IPCs in project) with annotate for remaining  
**Constraints**: Do not redesign cash-flow; do not break existing IPCCollection APIs from 003  
**Scale/Scope**: Additive fields + one report endpoint + UI polish

## Constitution Check

| Principle | Status |
|-----------|--------|
| Spec-first / gap-driven | Pass — builds on existing module |
| Thin views / services | Pass — extend `collection_service`; add `receivables_service` |
| Project tenancy | Pass — all routes under `/projects/{uuid}/` |
| Permissions | Pass — reuse `view_contracts` / `edit_contracts` / `approve_contracts` |
| No secrets in repo | Pass |

## Project Structure

### Documentation (this feature)

```text
specs/011-contracts-ipc/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── payment-terms.md
│   ├── ipc-amounts.md
│   └── receivables-report.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (touched)

```text
apps/api/core/contracts/
  models.py                          # payment_terms; submitted_amount; approved_amount; approval_note
  migrations/000X_*.py
  serializers.py
  services/collection_service.py     # assert status unchanged; optional guard
  services/receivables_service.py    # NEW report builder
  views.py / urls.py                 # report endpoint
  tests/test_payment_terms.py        # NEW
  tests/test_ipc_amounts.py          # NEW
  tests/test_collection_status_invariant.py  # NEW
  tests/test_receivables_report.py   # NEW
  ENDPOINTS.md

apps/web/src/
  app/lib/api/contracts.ts
  components/contracts/*             # form payment terms; IPC amount fields; ReceivablesPanel
  app/routes/project-contracts.tsx
  locales en.json / fa.json
```

## Complexity Tracking

None — additive extensions only.

## Implementation Phases

1. **Models + migration** — Contract.payment_terms; IPC.submitted_amount / approved_amount / approval_variance_note; backfill from gross_amount.
2. **Services + API** — submit snapshots submitted; approve sets approved (+ optional note); receivables report; collection invariant.
3. **Frontend** — payment terms field; show submitted/approved; receivables panel.
4. **Tests + docs** — pytest coverage for FR-CON gaps; ENDPOINTS.md.
