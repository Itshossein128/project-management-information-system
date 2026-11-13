# Phase Handoff: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Phase**: `A.7-P6` (`specs/056-a7-p6-delivery-acceptance`)  
**Title**: پذیرش یکپارچه و بسته تحویل کارفرما (Integrated Acceptance and Employer Delivery Package)  
**Direct Audit IDs**: `D03`, `D04`  
**Integrated Audit Scope**: All 56 items (`P01`–`P11`, `W01`–`W07`, `M01`–`M04`, `S01`–`S08`, `I01`–`I22`, `D01`–`D04`) from `output/a7-requirements-2026-11-10/requirements.json`  
**Status**: Technical Acceptance Complete (`technical_readiness = "ready_for_acceptance"`); Employer Sign-Off Pending (`employer_decision = "pending"`)  
**Date**: 2026-11-13

---

## 1. Candidate Version & Environment Identity

- **Base Git Commit**: `b0a894d23c9798aa44e06e1df7356e2b7eb38a66`
- **Django Version Pin**: `4.2.11` (verified in `apps/api/.venv` and container runtime)
- **Isolated Runtime Container Image**: `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`
- **Product Schedule Source SHA-256**: `eb2a29edcb92f01711d8a3594c41c26e05b078601258a9ce45ebd4ebe635abb1`
- **Reference Schedule File (`real-data/plan.mpp`)**:
  - SHA-256: `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`
  - Size: `777216` bytes
  - Stored Reconciliation Counts: **6 WBS nodes, 72 activities, 72 relationships, 1 initial baseline**
  - Expected Structured Warnings: `activity_without_parent` (`شروع`, `پایان`), `predecessor_is_summary` (`8055`, `8084`, `8102`, `8120`), `calendar_not_applied`

---

## 2. Predecessor & Integrated Verification Summary

1. **A.7-P5 `T049` Independent Second-Operator Reproduction Closed**:
   - Independent second-operator subagent (`conversationId: de389ce3-d1d2-4991-b379-f9c719ecfb7d`) executed the full clean `quickstart.md` / `ops/a7-p5/README.md` sequence on image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5`: 13/13 runtime matrix groups, `check-broker-outage.py`, `check-concurrent-delivery.py`, 4/4 Playwright browser retry tests, `maintain_import_jobs`, `makemigrations --check`, 110/110 `check-host.sh`, and `pnpm typecheck`. Recorded in `specs/055-a7-p5-import-operations/evidence/reproduction.md` and `specs/055-a7-p5-import-operations/handoff.md`.
2. **Combined P1–P5 Backend Non-Regression Suite (`T008`)**:
   - `168 passed, 0 failed, 0 skipped` (`specs/056-a7-p6-delivery-acceptance/evidence/p1-p5-regression-junit.xml`).
3. **P6 Integrated Positive (`POS-01`–`POS-10`) & Negative (`NEG-01`–`NEG-14`) Backend Acceptance Suite (`T011`, `T013`, `T014`)**:
   - `2 passed` in `apps/api/core/schedule/tests/test_a7_p6_delivery_acceptance.py` (`specs/056-a7-p6-delivery-acceptance/evidence/p6-pytest-junit.xml`).
4. **P6 Real-Stack Playwright Browser E2E Suite (`T015`, `T016`)**:
   - `6 passed` in `e2e/tests/a7-p6-delivery-acceptance.spec.ts` against the isolated `a7p5-import` API (`127.0.0.1:18000`) and Vite (`127.0.0.1:15173`), covering:
     - Live browser clicks for `Complete` → `Undo completion` (`P07`) and `Archive` → `Restore from archive` (`P09`) on `/projects/:projectId/overview`
     - Schedule import wizard preview, invalid file rejection/recovery, and append import across `fa` (`RTL`) and `en` (`LTR`) at `1280x800` and `390x844` viewports (`OPS-01`, `OPS-02`)
     - Keyboard-only navigation (`Tab`, `Enter`, `Escape`) (`OPS-03`)
     - Live project-switch and Viewer account-switch isolation (`I10`, `NEG-11`, `NEG-12`)
   - Screenshots saved in `specs/056-a7-p6-delivery-acceptance/evidence/screenshots/`.
5. **Frontend Typecheck**:
   - `pnpm typecheck` exited with code `0`.
6. **Deterministic Delivery Package Validator (`T019`)**:
   - `python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py` exited with code `0` (`56` audit items verified, `28` scenarios verified, `4` reconciliation fixtures verified, `secret_scan: "clean"`, `output/a7-requirements-2026-11-10/` untouched, and all 6 phases preserved in `output/a7-implementation/phase-map.json`).

---

## 3. Employer Delivery Package Index (`D03`, `D04`)

| Deliverable | Path | Purpose |
| --- | --- | --- |
| Persian Employer Test Guide | `specs/056-a7-p6-delivery-acceptance/guide.md` | Self-contained step-by-step employer acceptance guide with startup/reset commands, 5-persona setup, control figures, and 4-category status summary |
| Unsigned Acceptance Minutes | `specs/056-a7-p6-delivery-acceptance/evidence/minutes.md` | Employer sign-off template with `decision: pending` and blank signature fields |
| Package Metadata | `specs/056-a7-p6-delivery-acceptance/evidence/package.json` | Machine-readable `EmployerDeliveryPackage` manifest |
| 56-Item Audit Disposition | `specs/056-a7-p6-delivery-acceptance/evidence/audit-disposition.json` & `traceability.md` | Full traceability and disposition for `P01`–`D04` |
| 28-Scenario Execution Matrix | `specs/056-a7-p6-delivery-acceptance/evidence/scenarios.json` & `scenarios.md` | Technical pass/fail and pending employer decision for `POS-01`–`POS-10`, `NEG-01`–`NEG-14`, `OPS-01`–`OPS-04` |
| Schedule Reconciliation Ledger | `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.json` & `reconciliation.md` | Source vs. preview vs. stored vs. repeat-append figures for `real-data/plan.mpp` and XML/XER fixtures |
| 5-Persona Account Provisioning | `specs/056-a7-p6-delivery-acceptance/evidence/accounts.md` | Secret-free provisioning & reset commands for the 5 acceptance personas |
| Defect & Convergence Log | `specs/056-a7-p6-delivery-acceptance/evidence/defects.md` | Predecessor convergence and defect log (`0` open blocking defects) |
| Package Validator | `specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py` | Automated verifier for all package invariants and secret scanning |

---

## 4. Residual Boundaries

1. **Human Employer Acceptance Pending**: All technical checks (`technical_readiness = "ready_for_acceptance"`) are complete, but `employer_decision` remains `"pending"` until the employer representative executes `guide.md` and signs `evidence/minutes.md`.
2. **Native OS File Chooser Dialog**: Automated Playwright tests attach files to the `<input type="file" data-testid="msp-import-file">` element directly; clicking the native OS file-picker window remains part of the human employer interactive walkthrough in `guide.md`.
