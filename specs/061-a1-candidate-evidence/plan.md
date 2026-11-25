# Implementation Plan for A.1.02 and A.1.04 Candidate Evidence

**Spec Kit feature** `061-a1-candidate-evidence` · **Updated** 2026-11-24 · **Status** Ready for Supervisor review

**Input** [Approved specification](spec.md)

## Summary

Reconcile every section of SIM-A1-001 across Draft, Approved and correction in the browser and API. Freeze the candidate and one approved report version with the reconciliation record, original downloads, recalculated workbook and reviewed expectations. Trace all five B05 findings to applicable evidence or an explicit gap. [Deployment verification](../062-a1-deployment-verification/spec.md) and [delivery status and employer review](../063-a1-employer-acceptance/spec.md) consume the same frozen manifest digest.

## Technical Context

- **Language and dependencies** — Use Python 3.12 for evidence collection and validation, the existing Django 4.2/DRF and React Router application, openpyxl for workbook inspection, LibreOffice Calc for independent recalculation, and Poppler for page captures. Record tool versions during evidence collection.
- **Storage** — Versioned files in a controlled evidence archive. Read report identity through the deployed product and use the existing fixture workflow for isolated reproduction. The evidence model uses files and existing report records.
- **Testing** — Use focused pytest regressions for affected product behavior and browser/API observations on the authorized candidate. Preserve fixture and source snapshots, lifecycle evidence, download bytes, bench conditions and review records. The [quickstart](quickstart.md) describes the checks.
- **Target and project type** — Velora web and API on the selected deployment, with an isolated fixture environment for supplementary regressions. Capture candidate identity for every observation.
- **Performance** — Apply the existing SC-002 threshold of under 3.0 seconds per completed Excel FILE 4 or PDF download under standard broadband conditions for the stated typical workload.
- **Scope** — Plan 061 for A.1.02 and the candidate portion of A.1.04. The authorization matrix, 72 browser section observations, decision-tree comparison and agent delivery disposition are downstream interfaces. A.1.01 and A.1.03 are prerequisites with prior evidence reusable within its demonstrated scope.

## Constitution Check

- **I and IV** — Use controlled accounts, distinct preparer and approver, and the existing authorized report routes. Run lifecycle writes only in an authorized synthetic test scope. Keep the manifest, artifacts and review evidence in access-controlled storage and attribute each approval to its actor.
- **II** — Bind the exact deployed API/web release and source SHA, project and report IDs, selected version, controlled inputs, original and recalculated file checksums. Compare independent expected values and retain source rows and the earlier approved snapshot through correction.
- **III and VII** — Carry locale-specific file checksums and the existing 18-section scope into Persian RTL and English LTR browser verification on desktop and mobile. Record readability, version selection, and the download journey.
- **V and VI** — Start with evidence collection and existing regressions. Any demonstrated behavioral gap gets a targeted regression and the smallest applicable correction through the normal route. Source checks, test results, live downloads, and optional employer feedback have separate evidence fields.

Pre-design gate passed. Post-design review found the same controls in the handoff contract and validation scenarios. Every runtime result remains a future evidence item.

## Project Structure

### Documentation and design

- [Research decisions](research.md)
- [Data model](data-model.md)
- [Candidate evidence and handoff contract](contracts/candidate-evidence.md)
- [Validation quickstart](quickstart.md)
- [Existing execution tasks](tasks.md)

### Existing source surfaces

- [Deployment workflow](../../.github/workflows/deploy.yml)
- [Daily report detail actions](../../apps/api/core/field_reports/daily_report_views.py) and [documented routes](../../apps/api/core/field_reports/ENDPOINTS.md)
- [Correction service](../../apps/api/core/field_reports/services/correction_service.py) and [B02 version-integrity regressions](../../apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py)
- [FILE 4 builder](../../apps/api/core/field_reports/shiraz_file4_excel.py) and [PDF builder](../../apps/api/core/field_reports/pdf.py)
- [Browser version view](../../apps/web/src/app/routes/daily-report-view.tsx) and [download helper](../../apps/web/src/app/lib/api/daily-reports.ts)
- [B01 reference fixture](../../apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json), [data contract](../../apps/api/core/field_reports/contracts/daily_report_contract_v1.json), and [fixture command](../../apps/api/core/field_reports/management/commands/seed_a1_reference_fixture.py)

## Implementation Sequence

1. Verify running build provenance, resolve the controlled reference day and inventory the sections from the pinned contract. Independently derive and review expected values. Capture browser and API evidence across Draft, Approved and correction. Check parent/result links and compare original source data and the earlier approved snapshot before and after correction. Record the approved UUID/version selected for delivery and its snapshot (FR-008, SC-004).
2. Capture and compare repeated original downloads by format and effective export locale for that selected version. Investigate byte drift and reverify after a candidate change. Recalculate from each applicable original Excel, verify both file identities and compare the recalculated figures and official PDF to the independent expectations. Link the lifecycle reconciliation and applicable A.1.03 prerequisite evidence before freezing the archive (FR-001, FR-002, FR-003, FR-005, SC-001).
3. Finish the five B05 dispositions, including complete-download timing (FR-004, SC-003), print comparison (FR-006) and B02–B04 applicability (FR-007). Record the source and verified scope for the earlier A.1.02 parity result and the direct A.1.03 pass (FR-002). Compare the historical five and six activity counts with the selected candidate's snapshot. Bind the resulting register to the frozen manifest digest (SC-002).
4. Pass the frozen manifest, reconciliation record and finding register to 062, or issue a receipt with explicit gaps when blocked. QA matches allowed downloads to their original manifest slots and verifies the archived recalculated Excel checksum. 063 receives verified 061 and 062 evidence for the same digest after blockers are resolved. A.1.04 closes when the authorized representative explicitly approves that bundle. Previews acceptance and the human-escalation decision have their own recorded scope.
