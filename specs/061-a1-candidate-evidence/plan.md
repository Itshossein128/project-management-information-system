# Implementation Plan for A.1.04 Candidate Evidence

**Spec Kit feature** `061-a1-candidate-evidence` · **Date** 2026-11-23 · **Reviewed** 2026-11-24 · **Status** Ready for Supervisor review  
**Input** [Approved specification](spec.md)

## Summary

Freeze evidence for one deployed release and one version of the synthetic reference day. Trace each of the five B05 findings to candidate-specific evidence or an explicit gap. The manifest, raw downloads, and finding register go to [deployment verification](../062-a1-deployment-verification/spec.md). Its verification joins that same bundle for [initial employer acceptance](../063-a1-employer-acceptance/spec.md).

## Technical Context

- **Language and dependencies** — Use Python 3.12 for evidence collection and validation, the existing Django 4.2/DRF and React Router application, openpyxl for workbook inspection, LibreOffice Calc for independent recalculation, and Poppler for page captures. Record tool versions during evidence collection.
- **Storage** — Versioned files in a controlled evidence archive. Read report identity through the deployed product. Use the existing fixture workflow in an isolated environment when reproducing evidence. No schema migration is planned.
- **Testing** — Use focused pytest regressions for affected product behavior and browser downloads against the authorized deployment. Preserve bench conditions, inputs, raw outputs, and review evidence. The [quickstart](quickstart.md) describes the checks.
- **Performance** — Apply the existing SC-002 threshold of under 3.0 seconds per completed Excel FILE 4 or PDF download under standard broadband conditions for the stated typical workload.
- **Scope** — Active implementation planning covers `061` only. The authorization matrix, 72 browser section observations, decision-tree comparison, and employer minute are downstream interfaces and approval prerequisites. Earlier A.1.01–A.1.03 QA is evidence within its demonstrated scope.

## Constitution Check

- **I and IV** — Use controlled accounts and the existing authorized report routes. Keep the manifest, artifacts, and review evidence in access-controlled storage. Keep release verification and employer approval attributable to the actors who made them.
- **II** — Bind the exact deployed API/web release and source SHA, project and report IDs, selected version, controlled inputs, and raw file checksums. Compare values against independent calculations and preserve unknown versus zero.
- **III and VII** — Carry locale-specific file checksums and the existing 18-section scope into Persian RTL and English LTR browser verification on desktop and mobile. Record readability, version selection, and the download journey.
- **V and VI** — Start with evidence collection and existing regressions. Any demonstrated behavioral gap gets a targeted regression and the smallest applicable correction through the normal route. Source checks, test results, live downloads, and employer disposition have separate evidence fields.

Pre-design gate passed. Post-design review found the same controls in the handoff contract and validation scenarios. Every runtime result remains a future evidence item.

## Project Structure

### Documentation and design

- [Research decisions](research.md)
- [Data model](data-model.md)
- [Candidate evidence and handoff contract](contracts/candidate-evidence.md)
- [Validation quickstart](quickstart.md)

### Existing source surfaces

- [Deployment workflow](../../.github/workflows/deploy.yml)
- [Daily report detail actions](../../apps/api/core/field_reports/daily_report_views.py) and [documented routes](../../apps/api/core/field_reports/ENDPOINTS.md)
- [FILE 4 builder](../../apps/api/core/field_reports/shiraz_file4_excel.py) and [PDF builder](../../apps/api/core/field_reports/pdf.py)
- [Browser version view](../../apps/web/src/app/routes/daily-report-view.tsx) and [download helper](../../apps/web/src/app/lib/api/daily-reports.ts)
- [B01 reference fixture](../../apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json), [data contract](../../apps/api/core/field_reports/contracts/daily_report_contract_v1.json), and [fixture command](../../apps/api/core/field_reports/management/commands/seed_a1_reference_fixture.py)

## Implementation Sequence

1. Capture running build provenance and the resolved reference report identity. Compare repeated raw downloads early, by format and effective export locale. If bytes differ for the same manifest slot, record the cause and block that slot until a verified correction or an authorized frozen-artifact path preserves the same report/version and normal access controls.
2. Gather controlled inputs and independently derive and review expectations. Capture raw downloads, work on copies for recalculation and print evidence, and measure both downloads using the representative benchmark workload. Assemble and verify the manifest and its detached checksum.
3. Reconcile historical QA against the candidate and record five dispositions, including the B02–B04 prerequisite mapping. Record the deployed version's executed-activity count and input snapshot, then assess the applicability of the historical five- and six-row results. Output the verified manifest plus the finding register. A blocked record retains evidence and identifies the gaps for follow-up.
4. Pass the manifest reference and digest and finding register to `062`. Record blocked or unverified status when required inputs are missing. `062` returns its authorization, browser and decision-tree evidence tied to the same digest. Send the bundle to `063` for employer review only when the candidate and deployment evidence is complete and all blockers are resolved. A.1.04 closes only after the authorized representative's explicit approval is recorded for that digest.
