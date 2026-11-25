---
description: "Dependency-ordered tasks for A.1.02 and A.1.04 Candidate Evidence"
---

# Tasks for A.1.02 and A.1.04 Candidate Evidence

**Input** [Specification](spec.md) · [Approved plan](plan.md) · [Research](research.md) · [Data model](data-model.md) · [Contract](contracts/candidate-evidence.md) · [Quickstart](quickstart.md)

**Scope** Feature 061 produces the reference-day lifecycle reconciliation, frozen candidate manifest and B05 evidence register. The downstream verification and acceptance requirements govern the handoff to [062](../062-a1-deployment-verification/spec.md) and [063](../063-a1-employer-acceptance/spec.md). The candidate work uses earlier A.1.01–A.1.03 results within their verified scope.

**Paths** Paths beginning with `specs/`, `apps/`, `output/`, or `.github/` are repository-relative. Paths beginning with `archive/` are relative to the controlled evidence workspace agreed with the release owner. Set up that workspace in T001. Keep access scoped to authorized participants and exclude credentials and session tokens.

**Task markers** Task IDs are stable references. Execute the phases in the order shown. A task marked `[P]` may run alongside another ready task with separate outputs, subject to the dependencies below. The checked tooling task is backed by the existing [local inventory](archive/tools.md).

## Phase 1 — Setup

- [X] T001 Confirm feature 061 in `.specify/feature.json`, record the intended deployment and evidence owners, and prepare the controlled evidence workspace and evidence index at `archive/README.md` using `specs/061-a1-candidate-evidence/contracts/candidate-evidence.md`.
- [X] T002 Record the browser, openpyxl, LibreOffice Calc, Poppler and SHA-256 tooling available to the verifier and the isolated fixture environment in `archive/tools.md`. Use `specs/061-a1-candidate-evidence/quickstart.md` for the validation commands and keep local regression evidence separate from deployment evidence.

## Phase 2 — Shared prerequisites

Pin the candidate, identify the starting version and independently derive the baseline expectations.

- [X] T003 Obtain release-owner provenance and verify the running API and web build identities against the selected deployment using `.github/workflows/deploy.yml` as reference. Record the deployed candidate ID, full source SHA, environment, observed API/web build IDs, evidence references and capture time in `archive/deployment.json`. Leave provenance unverified if any required identity is absent or mismatched.
- [X] T004 Resolve SIM-A1-001-12-1406-03-01 (Solar Hijri 1406-03-01, project day 12) in the pinned deployment and identify the starting report UUID and version for lifecycle verification. In `archive/inputs/reference-version.json`, record project UUID, report version UUID, report lineage ID when exposed, version number, report number, local report date and project day. Link the starting input snapshot to that version and record identifiers and SHA-256 digests of that snapshot, the synthetic fixture, and applicable form/data-contract revisions. Use `apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json` and `apps/api/core/field_reports/contracts/daily_report_contract_v1.json` as the baseline.
- [X] T008 After T004, derive expected figures independently from the controlled input snapshot and reference-form rules in `archive/expectations/expected-values.json`. For each expectation record the section, source reference, unit, normalization or rounding rule, value, and Excel cell and PDF page mapping where applicable. Distinguish null, zero and inapplicable values. Record the method, source input hashes, review status, reviewer and date in `archive/expectations/review.md`. These shared inputs support US1, US3 and FR-005. Keep the derivation independent of product calculations. Independent QA passed revision 2 at SHA-256 `aef5d6efed8b2ca56aaa9e77b17b8282c3207748b3a9d70a301245428632064d`. [Evidence receipt](archive/README.md#t008-independent-qa).

## Phase 3 — US3 · Reconcile every section through approval and correction (P1)

**Goal** Reconcile the controlled day and identify the approved delivery version.

**Independent test** Compare the fixture and contract to the report in both the browser and API through Draft, Approved, correction Draft and corrected Approved. A passing result covers every inventoried section and preserves the original source data and earlier approved snapshot.

- [X] T023 [US3] After T004 and T008, record the contract inventory and per-section expected and observed values or states in `archive/reconciliation/sections.json`, referencing the Draft, Approved, correction Draft and corrected Approved observations in the browser and API. Capture the version and parent/result IDs, source references, before/after source and historical snapshot comparisons, and evidence for any expected empty section. Use distinct authorized preparer and approver accounts in a synthetic test scope. Mark missing or discrepant sections unverified. Tie each expected result to the observed lifecycle version. If a controlled correction changes a report value, document the change and independently review the expected value for the selected version in the T008 records. Select the approved report for delivery and link its UUID, version and input snapshot in `archive/inputs/reference-version.json` for T005 and T009. Apply the lifecycle check in `specs/061-a1-candidate-evidence/quickstart.md` for FR-008 and SC-004.

## Phase 4 — US1 · Capture original exports (P1)

**Goal** Identify repeatable original Excel and PDF downloads for the selected version and prepare the walkthrough.

Verify that each applicable format and effective locale produces a complete download and matching checksums on repeat. Complete the US1 independent check in Phase 6.

- [X] T005 [US1] After T023 identifies the approved delivery version, download untouched Excel FILE 4 and official PDF from that version through the authorized report journey in Persian and English. Capture the actual effective export locale, version, complete byte count and raw SHA-256 in `archive/downloads/observations.json`. Repeat each format/locale slot on the same candidate and compare both observations. Use the per-version actions in `apps/api/core/field_reports/ENDPOINTS.md`.
- [X] T006 [US1] Resolve the T005 repeatability gate in `archive/downloads/repeatability.md`. Record matches for each slot. If bytes vary, reproduce the mismatch and isolate the cause. For a product correction within approved scope, first capture a failing regression on the normal version-specific route using the existing coverage in `apps/api/core/field_reports/tests/test_shiraz_file4_excel.py` and `apps/api/core/field_reports/tests/test_pdf_summary_parity.py` as references, then verify the narrow fix preserves authorization and version selection. Capture a new deployment and rerun identity and download checks after a candidate change. Keep any unresolved slot unverified.
- [X] T007 [P] [US1] Prepare the versioned walkthrough guide in `archive/walkthrough/guide.md` with the exact version selection and Excel/PDF download steps, effective locale, original download verification, and the frozen recalculated Excel and PDF figures and pages to review. Use the review protocol in `specs/063-a1-employer-acceptance/spec.md`. Draft the figure and page references against T008 for verification in T009.

## Phase 5 — US2 · Collect evidence for the five B05 findings (P1)

**Goal** Collect candidate-specific proof or record a gap for each finding.

Complete the standalone workbook recalculation, independent figures comparison and prior-evidence applicability review before freezing the bundle. Complete the US2 independent check in Phase 6.

- [X] T011 [P] [US2] Build the prior-evidence comparison in `archive/b05/prior-evidence.md`. Compare candidate build, input snapshot, report version and verified scope with the A.1.02 timeout in `output/speckit-prompts/a-1/coverage.json`, limited prior export-parity report in `output/phase-a1/a1-02-verification.json`, direct A.1.03 pass in `output/phase-a1-qa/A.1.03-verification.json` and the blocker assertion in `output/phase-a1-qa/A.1.04-verification.json`. Record the A.1.03 prerequisite reference and scope for T009. Reconcile six executed activity rows in `output/phase-a1/a1-02-excel-pdf-parity-verification.json.md` versus five for the same UUID in `specs/059-a1-b03-reference-parity/implementation-evidence.md`. Record the candidate count, deployed version, input snapshot reference and digest, supported explanation if available, and applicability of each affected result. Keep applicability open when the discrepancy is unexplained. Reuse the reported 88 formula checks and unknown-hours regression only within their demonstrated scope.
- [X] T012 [P] [US2] For DEF-B05-01 (FR-003), record original formula and cache observations and the governing export contract in `archive/b05/01-recalculation.md`. Perform standalone Calc recalculation on a separate copy for each applicable workbook slot. Record tool version, formula/value/error comparisons, original and recalculated SHA-256 and their linkage for T009. Judge cache availability separately using the contract. Record any material uncertainty as an explicit scope decision required.
- [X] T014 [P] [US2] For DEF-B05-03 (FR-005), compare the T012 recalculated workbook and official PDF, for each applicable locale, with the independently reviewed expectations from T008. Record the input and rule provenance, review reference, values, units, rounding, null/zero results and discrepancies by cell/page in `archive/b05/03-expected-values.md`.
- [X] T015 [P] [US2] Collect and complete DEF-B05-04 (FR-006) print evidence in `archive/b05/04-print.md` and `archive/b05/print-captures/`. Use the T012 workbook to compare print pages and official PDF pages against the reference form for the standard and applicable long cases. Record cell/page mappings, page sizes and counts, readable captures, checksums and discrepancy decisions. Link the completed T012 recalculation log when assembling the register.
- [X] T016 [US2] For DEF-B05-05 (FR-007), use T011 to record B02 version integrity, B03 export parity and B04 filter/totals prerequisite results in `archive/b05/05-prerequisites.md`. Record the requirements tested, exact candidate applicability, supporting evidence and follow-up for gaps. Explain which delivery-plan status labels differ from direct QA and why the underlying evidence applies or remains unverified. Use the focused regression references in `specs/061-a1-candidate-evidence/quickstart.md` where necessary.
- [X] T013 [US2] For DEF-B05-02 (FR-004 and SC-003), time both complete downloads from export initiation through file receipt on the pinned deployment. Record the workload identifier, 15–30 activities, 20 materials/equipment rows, standard broadband conditions, elapsed time and result per format in `archive/b05/02-latency.md`. Use a separate candidate-linked workload if the frozen reference day falls outside those counts. Measure in a window free of overlapping checks that could affect timing. The criterion passes when both completed downloads are under 3.0 seconds. Record incomplete attempts.

## Phase 6 — Freeze and validate the bundle

### US1 · Identify the exact report and files (P1)

**Independent test** Verify the known deployment, selected version, each original download and the recalculated workbook against the manifest. Substitute each identity or checksum in turn. Expect each mismatch to stay unverified.

- [X] T009 [US1] Assemble and freeze UTF-8 `archive/manifest.json` with schema revision, verified deployment and reference identities, controlled inputs, reviewed expectations, guide, T023 reconciliation and the T011 A.1.03 prerequisite link and applicability. Before freeze, confirm the T007 guide against the T012 recalculated workbook and T014 comparison. Require verified parity for every applicable slot and resolved section discrepancies in T023. Keep evidence files included in the manifest keyed to candidate, fixture and version so their checksums can be computed before the manifest digest. For each distributed item record role, archive-relative path, SHA-256, byte count and applicable format, effective locale and revision. Link original Excel/PDF by effective locale and each recalculated Excel to its original slot and recalculation log. Preserve separate files and checksums when bytes differ. Write the detached manifest digest to `archive/manifest.sha256` and the distributed-file checksums to `archive/artifacts.sha256`. Preserve the old manifest if the candidate, report version or reviewed files change. When required content is missing, retain a draft and record the blocking gap.
- [X] T010 [US1] Run the independent US1 check and checksum verification from `specs/061-a1-candidate-evidence/quickstart.md`. Verify the stored archive after transfer and confirm the recorded 100% parity of applicable controlled figures in the recalculated workbook and official PDF. Record results and the build, version, original-file and recalculated-file mismatch cases in `archive/manifest-validation.md` for FR-001 and SC-001.

### US2 · Verify the release evidence (P1)

**Independent test** Verify a register with one record per B05 finding, including the historical activity-count discrepancy, cache and recalculation observations, and an unresolved blocker. Expect the blocker to prevent employer handoff.

- [X] T017 [US2] Assemble `archive/b05/dispositions.json` from T011–T016, attaching T012 to the print evidence and recording one row each for DEF-B05-01, DEF-B05-02, DEF-B05-03, DEF-B05-04 and DEF-B05-05. Bind every row to the frozen manifest digest where available. Record candidate, fixture and version where relevant, covered scope, prior versus candidate proof, applicability, criterion, references and outcome. Use the dispositions “Satisfied by traceable evidence”, “open”, or “explicit scope decision required”. Include blocking impact and rationale, follow-up owner or role and action for open items, and decision maker, authority, date and source for any recorded scope decision. If the manifest cannot freeze, keep the register as draft and record the missing binding.
- [X] T018 [US2] Run the independent US2 check and confirm exactly five unique dispositions and zero unresolved blockers for a passing result. Test that stale identity, missing evidence or an unresolved blocking scope decision keeps the bundle blocked. Record results in `archive/b05/register-validation.md` for FR-002 and SC-002.

## Phase 7 — Cross-cutting handoff

Send 062 the candidate receipt or its explicit blockers. Employer review in 063 requires verified 061 and 062 evidence for the same manifest digest.

- [X] T019 Recheck running release identity and both archive checksum lists before writing the handoff receipt in `archive/handoffs/061-candidate.md`. Include the manifest reference and digest, section reconciliation, five-finding register, candidate status and explicit gaps. Preserve a blocked or unverified receipt if the manifest, checks or dispositions are incomplete. When an upstream task blocks collection, update the receipt with the gap and leave T019 open.
- [X] T020 Record what 062 must return in `archive/handoffs/062-verification-requirements.md` against `specs/062-a1-deployment-verification/spec.md` (DEF-A104-04). Carry the same candidate ID, source SHA, report UUID/version and manifest digest into the authorization matrix for all controlled access contexts in 062, including the authenticated Visitor, and both formats, including direct version-specific routes. Include expected/observed outcomes and protected-content withholding. For each allowed download, match the raw checksum to the original manifest entry for its format and effective export language. Verify the archived recalculated workbook digest and linkage, and scope reuse of prior 403/404 to matching candidate and request evidence. Require 72 section observations across Persian RTL and English LTR on desktop and 390 × 844 mobile, with actual viewport, text direction, readability, selected version, the report journey and both matching downloads for each combination. Retain decision-tree route, policy and outcome comparisons, including the applicable owning-unit observation rule, and unresolved findings.
- [X] T021 Record what 063 must return in `archive/handoffs/063-acceptance-requirements.md` against `specs/063-a1-employer-acceptance/spec.md` (DEF-A104-03). Require a verified 061 and 062 bundle before the delivery agent records completion. Bind the disposition and retrievable artifacts to the same digest, guide revision and file checksums. Record evidence, discrepancies and follow-up. Keep A.1.04 open for incomplete evidence or blocking findings. Reverify affected evidence after a bundle change.
- [X] T022 Validate the 061 handoff against `specs/061-a1-candidate-evidence/contracts/candidate-evidence.md` and the mismatch cases in `specs/061-a1-candidate-evidence/quickstart.md`. Verify on copies that candidate drift, a missing lifecycle observation, the wrong original or recalculated artifact checksum, and a different downstream digest leave the affected evidence unverified. Verify that incomplete QA or a confirmed blocker keeps A.1.04 open. Verify that outstanding employer feedback does not prevent an evidence-backed disposition. Link artifact checks, isolated regressions, deployed evidence and outstanding downstream records from `archive/README.md`.

## Dependencies and execution order

- T001 → T002 → T003 → T004 → T008 → T023 → T005 → T006. T023 also uses the T004 starting version and records the approved delivery version before the first download.
- After T006, T007, T011 and T012 can proceed in parallel. T014 requires T008 and T012. T015 finalizes the print comparison after T012. T016 follows T011. Run T013 after T006 in its own measurement window, outside other deployment checks.
- T009 requires T006, T007, T008, T011, T012, T014 and T023. T010 verifies the frozen archive. T017 requires the T009 digest and T011–T016 evidence. T018 verifies the completed register.
- T019 follows T010 and T018, then T020 → T021 → T022. Recheck the candidate and repeat affected collection after identity drift. A blocked receipt or draft disposition can record diagnostic evidence while checks remain open.

## Requirement coverage

- FR-001 / SC-001 and DEF-A104-01 — T003–T010, T012, T014 and T023 pin the build and report version, reconcile the day, compare files and validate the archive.
- FR-002 / SC-002 and DEF-A104-02 — T011, T017, T018 and T023 reconcile prior QA and candidate-specific evidence. T009 links the applicable A.1.03 prerequisite.
- FR-003, FR-004 / SC-003, FR-005 and FR-006 — T012, T013, T008/T014 and T015 provide recalculation, timing, independent figures and print evidence, respectively.
- FR-007 — T016–T022 verify prerequisite applicability and document the handoffs.
- FR-008 / SC-004 — T023 checks every inventoried section, lifecycle lineage and retained source data in the browser and API. T022 checks the effect of a missing observation on the handoff.

## Parallel execution

- **US1** — After T006, draft the walkthrough while US2 collects historical evidence and recalculates the workbook. Confirm references before T009.
- **US2** — Run T011 and T012 in separate working files. After T012, T014 and T015 can compare figures and print layouts in separate files. T016 can proceed when T011 is complete. Reserve the deployment measurement window for T013.
- **US3** — Within T023, compile the browser and API evidence in parallel for an observed version. Capture both observations before mutating that version through the next lifecycle transition.

## Implementation strategy

- **First verifiable increment** Complete setup and shared prerequisites, then run US3 against the controlled day. Validate all sections and select the approved report version.
- **Candidate bundle** Capture the originals, collect the B05 evidence, and independently verify the frozen manifest and disposition register.
- **Handoff** Publish the 061 receipt for 062. Route verified evidence for the same manifest digest to 063. A.1.04 stays open until candidate-specific QA and the agent’s evidence-based disposition are recorded.
