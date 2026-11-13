# Research: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Feature Directory**: `specs/056-a7-p6-delivery-acceptance`  
**Direct Audit IDs**: `D03`, `D04`  
**Integrated Scope**: `P01`–`P11`, `W01`–`W07`, `M01`–`M04`, `S01`–`S08`, `I01`–`I22`, `D01`–`D04` (56 total items)  
**Date**: 2026-11-13

## R1 — Keep Acceptance Records as Versioned Files in `specs/056-a7-p6-delivery-acceptance/`

- **Decision**: Store the 56-item master disposition matrix (`traceability.md`), scenario execution records (`evidence/scenarios.md`), reference schedule reconciliation ledger (`evidence/reconciliation.md`), role accounts guide (`evidence/accounts.md`), defect log (`evidence/defects.md`), Persian Employer Test Guide (`guide.md`), and unsigned acceptance minutes (`evidence/minutes.md`) as versioned markdown/JSON files under `specs/056-a7-p6-delivery-acceptance/`, validated by a deterministic script (`evidence/validate_package.py`).
- **Rationale**: A.7-P6 proves and packages behavior already implemented across A.7-P1 through A.7-P5 (`051`–`055`). Adding new database tables or a custom acceptance UI would violate Constitution Principle V (Minimal coherent changes) and would not test the actual screens and APIs that the employer uses.
- **Alternatives considered**:
  - Creating Django models for acceptance test tracking — rejected as an unnecessary parallel product surface.
  - Mutating `output/a7-requirements-2026-11-10/requirements.json` in place — rejected because the 2026-11-10 audit snapshot is a historical baseline artifact and must remain immutable.

## R2 — Verify Predecessor Handoffs (`051`–`055`) via Live Execution and Backfill Missing Standalone Traceability Files

- **Decision**:
  1. Treat `specs/051-a7-p1-project-reference` through `specs/055-a7-p5-import-operations` handoffs as the entry gate, now including the completed independent second-operator reproduction of P5 `T049` (`specs/055-a7-p5-import-operations/evidence/reproduction.md`, `## Fifth clean run`).
  2. Backfill standalone `traceability.md` files in `specs/052-a7-p2-import-safety/traceability.md` and `specs/053-a7-p3-import-fidelity/traceability.md` (distilled directly from their existing `handoff.md` and `evidence/verification.md`) so all 6 phases (`051`–`056`) have uniform `spec.md`, `handoff.md`, `evidence/verification.md`, and `traceability.md` artifacts.
  3. Re-execute the integrated P1–P5 backend regression suite and P6 end-to-end acceptance suite on the exact candidate tree so no predecessor claim rests on stale runs.
- **Rationale**: `06-delivery-acceptance.md` requires inspecting `spec.md`, `handoff.md`, `evidence/verification.md`, and `traceability.md` across P1–P5 and ensuring all 56 items are backed by current-version evidence.
- **Alternatives considered**:
  - Relying on P1–P5 task checkboxes without re-running integrated checks — rejected per Constitution Principle VI and prompt instructions.

## R3 — Separate Evidence Channels (API/DB Integration, Real Worker Runtime, Real Browser E2E, and Employer Sign-Off)

- **Decision**: Maintain explicit separation across four evidence channels in `specs/056-a7-p6-delivery-acceptance/evidence/`:
  1. **Integrated API & Database Channel**: `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py` plus the full P1–P5 pytest suite on an isolated PostgreSQL test database, exercising the complete 10-step positive journey (`US2`) and the full negative/adverse/concurrency/role-boundary catalog (`US3`).
  2. **Real Broker, Worker & Containment Channel**: The isolated `a7p5-import` Compose stack (`ops/a7-p5/compose.yml`, image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`, schedule-tree SHA-256 `52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`) processing unchanged `real-data/plan.mpp` and XML/XER fixtures with `CELERY_TASK_ALWAYS_EAGER=False` and `IMPORT_PREPARE_INLINE=False`.
  3. **Real Browser E2E Channel**: Playwright suite `e2e/tests/a7-p6-delivery-acceptance.spec.ts` running against the live backend and frontend without mocked API responses, covering the positive reference journey, P1 carry-over lifecycle buttons (`complete` / `undo-complete` and `archive` / `restore`), P4 carry-over account/project-switch observation, negative/adverse UX, keyboard navigation, and bilingual (`fa` RTL / `en` LTR) desktop (`1280x800`) and mobile (`390x844`) viewports.
  4. **Employer Confirmation Channel**: Unfabricated sign-off fields in `evidence/minutes.md` (`decision: pending`, blank `signer_role`, blank `signed_at`), strictly separated from technical verification (`technical_status: ready_for_acceptance`).
- **Rationale**: Prevents conflating eager pytest runs with real worker execution, or automated browser runs with human employer sign-off.
- **Alternatives considered**:
  - Using mocked API responses in Playwright — rejected because P6 (`D03`) requires end-to-end verification with real backend and database state.

## R4 — Reference Schedule Reconciliation Contract (`real-data/plan.mpp` and XML/XER Fixtures)

- **Decision**: Reconcile `real-data/plan.mpp` (SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`, 777,216 bytes) and the authored MSP XML (`apps/api/core/schedule/tests/fixtures/a7_p1_valid_schedule.xml`) and Primavera P6 XER (`apps/api/core/schedule/tests/fixtures/a7_p1_valid_schedule.xer`) fixtures across four stages: (1) source file totals, (2) preview response, (3) import job summary, and (4) stored PostgreSQL rows.
  - For `real-data/plan.mpp`, stored counts must equal **6 WBS nodes, 72 activities, and 72 relationships**, with `rows_read = 80`, `rows_omitted = 13`, `warned_count = 13` (parentless `شروع` and `پایان` omitted with `activity_without_parent`; summary predecessors `8055`, `8084`, `8102`, `8120` skipped with `predecessor_is_summary`; source calendar noted with `calendar_not_applied`).
  - Repeat `append` of the same file must yield `nothing_changed = true`, `0` duplicates, and `0` redundant baseline versions.
- **Rationale**: Directly fulfills `D03`, `D04`, `I03`–`I05`, `I08`, and the stakeholder decision recorded in P3 (`2026-11-12`).
- **Alternatives considered**:
  - Inventing synthetic counts or ignoring warning codes — rejected per `06-delivery-acceptance.md`.

## R5 — Defect Triage and Predecessor Convergence Protocol

- **Decision**: Log every failure discovered during P6 verification in `specs/056-a7-p6-delivery-acceptance/evidence/defects.md` with `defect_id`, `audit_ids`, `owning_phase`, `severity`, `status`, `before_evidence`, and `after_evidence`. If a product defect belongs to P1–P5 (`051`–`055`), fix it in the owning code module, record convergence in the owning feature directory, and re-run both P5 operational checks (if `apps/api/core/schedule/` runtime files changed) and P6 integrated verification on the updated candidate tree.
- **Rationale**: Preserves phase ownership and guarantees that all evidence artifacts reference the same final candidate tree identity.
- **Alternatives considered**:
  - Patching P1–P5 bugs silently without logging or updating predecessor evidence — rejected per `FR-010`.
