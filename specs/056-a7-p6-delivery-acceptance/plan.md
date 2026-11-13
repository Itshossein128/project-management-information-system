# Implementation Plan: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Branch**: `develop` (feature directory `056-a7-p6-delivery-acceptance`; no git branch switch performed) | **Date**: 2026-11-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/056-a7-p6-delivery-acceptance/spec.md`

## Summary

Verify the integrated Module A.7 commitment (`P01`–`P11`, `W01`–`W07`, `M01`–`M04`, `S01`–`S08`, `I01`–`I22`, `D01`–`D04`) on a single candidate codebase and assemble the self-contained Employer Delivery Package (`D04`). Re-verify predecessor handoffs (`051`–`055`, including the completed independent second-operator reproduction of P5 `T049`), backfill missing standalone traceability files for P2 (`052`) and P3 (`053`), execute the 10-step positive reference project journey (`POS-01`–`POS-10`) and 14 independent negative/adverse/concurrency/role-boundary scenarios (`NEG-01`–`NEG-14`) across API/DB, real worker runtime, and real browser Playwright E2E (`OPS-01`–`OPS-04`), reconcile `real-data/plan.mpp` (`6` WBS, `72` activities, `72` relationships) and XML/XER fixtures, and publish the Persian Employer Test Guide (`guide.md`) and unsigned acceptance minutes (`evidence/minutes.md`).

## Technical Context

**Language/Version**: Python 3.12 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7 and Vite.

**Primary Dependencies**: Existing `projects`, `project_templates`, `schedule`, and `permissions` domain services; MPXJ 16.10.0 / JPype 1.7.1 / OpenJDK 21 in the isolated `a7p5-import` runtime; Playwright E2E and pytest-django.

**Storage**: PostgreSQL (`:5433` host test DB and `:55432` isolated `a7p5-import` DB) and Redis (`:6379` / `:56379`). Acceptance package records are versioned Markdown and JSON files under `specs/056-a7-p6-delivery-acceptance/`—no new database tables or migrations are added.

**Testing**: `pytest` on an isolated PostgreSQL test database (`apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py` + P1–P5 suites); real non-eager worker/containment evidence from `ops/a7-p5` bound to the exact schedule-tree SHA-256 (`52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`); Playwright real-stack browser suite (`e2e/tests/a7-p6-delivery-acceptance.spec.ts`); deterministic package validator (`specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py`).

**Target Platform**: Linux server and desktop/mobile browser viewports (`1280x800` and `390x844`) in Persian (`fa`, RTL) and English (`en`, LTR).

**Project Type**: Monorepo web application (`apps/api` and `apps/web`) plus versioned acceptance delivery package in `specs/056-a7-p6-delivery-acceptance/`.

**Performance Goals**: All integrated acceptance and browser journeys complete within interactive and bounded worker deadlines; `real-data/plan.mpp` reconciles with 0 duplicates on repeat append.

**Constraints**: Constitution v1.1.0; Django pinned to `4.2.11`; do not install `requirements-dev.txt` wholesale; do not mutate `output/a7-requirements-2026-11-10/` historical snapshot; do not expose secrets, tokens, or proprietary schedule text in evidence; keep `employer_decision = "pending"` and signer fields blank for human employer completion.

**Scale/Scope**: 56 total A.7 audit items (`P01`–`D04`), 28 structured acceptance scenarios (`POS-01`–`POS-10`, `NEG-01`–`NEG-14`, `OPS-01`–`OPS-04`), 5 role personas, and 4 schedule reference fixtures (`real-data/plan.mpp` + XML/XER).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Research Gate | Post-Design Gate |
| --- | --- | --- |
| I. Server-Enforced Access & Isolation | **PASS** — Cross-project isolation, SoD, `view_only`, archived read-only, and non-member System Admin observation are verified against server endpoints as well as UI. | **PASS** — `POS-02`, `NEG-10`–`NEG-14` test server-side enforcement directly and in browser. |
| II. Data Integrity & Safe Migrations | **PASS** — No schema migration planned; atomic rollback, soft-delete replacement guards, and archive/restore preservation are explicitly verified. | **PASS** — `data-model.md` adds only file-based acceptance records and forbids destructive history edits. |
| III. Bilingual, RTL/LTR & Accessible UX | **PASS** — Persian (`fa`, RTL) and English (`en`, LTR) and keyboard/responsive checks are mandatory (`OPS-01`–`OPS-03`). | **PASS** — `guide.md` is authored in clear Persian and Playwright verifies both `fa` and `en` at `1280x800` and `390x844`. |
| IV. Safe Mutations & Environment Isolation | **PASS** — All tests run on isolated test projects/databases; shared and production data remain untouched. | **PASS** — `quickstart.md` and `guide.md` include deterministic isolated setup and reset steps. |
| V. Minimal, Coherent Changes | **PASS** — No parallel acceptance app or redundant endpoints introduced. | **PASS** — Any in-scope defect fix is routed to its owning module (`projects`, `project_templates`, `schedule`). |
| VI. Evidence-Based Verification | **PASS** — API/DB, real worker (`ops/a7-p5`), browser E2E, and human employer sign-off channels remain strictly separated. | **PASS** — `validate_package.py` enforces evidence binding, 56-item coverage, and blank employer sign-off fields. |

**Predecessor Gate Status — VERIFIED (2026-11-13)**:
- `051` through `055` handoffs are verified; P5 `T049` (independent second-operator clean reproduction on `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`) is complete and recorded in `specs/055-a7-p5-import-operations/evidence/reproduction.md` (`## Fifth clean run`) and `handoff.md`.

## Project Structure

### Documentation (this feature)

```text
specs/056-a7-p6-delivery-acceptance/
├── spec.md                           # Feature specification (/speckit-specify)
├── plan.md                           # This file (/speckit-plan)
├── research.md                       # Phase 0 research decisions (/speckit-plan)
├── data-model.md                     # Phase 1 entity & validation rules (/speckit-plan)
├── quickstart.md                     # Phase 1 runnable validation guide (/speckit-plan)
├── contracts/
│   └── delivery-acceptance.md        # Phase 1 package & scenario contract (/speckit-plan)
├── checklists/
│   └── requirements.md               # 16/16 specification quality checklist
├── guide.md                          # Concise Persian Employer Test Guide (D04)
├── traceability.md                   # Master 56-item audit disposition matrix
├── handoff.md                        # Phase handoff & readiness summary
├── evidence/
│   ├── verification.md               # Consolidated technical verification report
│   ├── package.json                  # EmployerDeliveryPackage metadata
│   ├── audit-disposition.json        # 56 AuditDispositionRecord entries
│   ├── reconciliation.md             # Reference schedule reconciliation ledger
│   ├── reconciliation.json           # Machine-readable reconciliation data
│   ├── scenarios.md                  # 28 AcceptanceScenarioRecord entries (Markdown)
│   ├── scenarios.json                # 28 AcceptanceScenarioRecord entries (JSON)
│   ├── accounts.md                   # Secret-free 5-persona role setup guide
│   ├── defects.md                    # Defect log & remediation record
│   ├── minutes.md                    # Unsigned employer acceptance minutes
│   ├── validate_package.py           # Deterministic package & secret-scan validator
│   └── screenshots/                  # Browser E2E screenshots (fa/en, desktop/mobile)
└── tasks.md                          # Generated by /speckit-tasks
```

### Source Code (repository root)

```text
apps/api/core/
├── projects/                         # Project lifecycle, charter, change request, WBS
├── project_templates/                # WBS & schedule template library and copy service
├── schedule/                         # Activities, relations, baselines, MSP/P6 import
│   └── tests/
│       └── test_a7_p6_delivery_acceptance.py  # Integrated 10-step positive & 14-step negative API/DB acceptance suite
e2e/tests/
└── a7-p6-delivery-acceptance.spec.ts # Real-stack Playwright E2E suite (positive, lifecycle clicks, negative, fa/en, 1280/390, keyboard)
specs/052-a7-p2-import-safety/
└── traceability.md                   # Backfilled standalone P2 traceability matrix
specs/053-a7-p3-import-fidelity/
└── traceability.md                   # Backfilled standalone P3 traceability matrix
```

**Structure Decision**: Keep product logic in `apps/api/core/{projects,project_templates,schedule}` and `apps/web/src/`. Add focused integrated acceptance test suites (`apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py` and `e2e/tests/a7-p6-delivery-acceptance.spec.ts`), backfill standalone `traceability.md` files for `052` and `053`, and store the complete employer delivery package under `specs/056-a7-p6-delivery-acceptance/`.

## Complexity Tracking

No Constitution violations require justification.
