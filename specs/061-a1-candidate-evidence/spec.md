# Feature Specification for A.1.02 and A.1.04 — Reference-Day Reconciliation and Candidate Evidence

**Created** 2026-11-22  
**Updated** 2026-11-24

**Status** Draft for Supervisor review  
**Input** [Stage 2 prompt 01](../../output/speckit-prompts/a-1/01-candidate-evidence.md)  
**Sequence** 1 of 3. Hands off to [Deployment Verification](../062-a1-deployment-verification/spec.md).

## User Scenarios & Testing

### User Story 1 — Identify the exact report and files (P1)

A release owner freezes the delivery candidate so an auditor and the employer can identify and reproduce the same review bundle.

**Independent test** — Compare a sample manifest with the deployed candidate, the selected report version, the original downloads and the recalculated workbook.

1. **Given** a complete reference day and a named candidate, **when** the auditor compares the deployment identity, report identity and version, and artifact checksums with the manifest, **then** each matches the frozen record.
2. **Given** a different build, report version, or modified file, **when** the same checks are repeated, **then** the mismatch is recorded and the bundle remains blocked until the exact candidate is verified.
3. **Given** that recalculation changes the workbook bytes, **when** the auditor verifies both workbook files, **then** each checksum resolves to the correct file and the recalculated workbook and official PDF agree with the independently expected figures.

### User Story 2 — Resolve the evidence needed for release (P1)

An independent verifier traces each B05 finding to evidence applicable to the candidate so the release owner can decide whether verification may proceed.

**Independent test** — Inspect five finding records with evidence of different vintages, including one unresolved blocker, and verify the candidate's disposition.

1. **Given** the current A.1.02 timeout, its earlier export-parity pass, and the current direct A.1.03 pass, **when** the verifier reconciles these with the A.1.04 dependency finding, **then** the register limits A.1.02 reuse to proven export parity, records the lifecycle checks still due, and links the direct A.1.03 result and its candidate applicability to the manifest.
2. **Given** a fresh workbook that recalculates correctly but lacks cached formula results, **when** the verifier checks the governing export contract, **then** standalone recalculation and cache behavior receive separate results, and cache availability is a release requirement only if the contract requires it.
3. **Given** an unresolved blocking finding or evidence from a different candidate, **when** the release owner reviews the register, **then** the handoff records the blocker and employer review remains blocked.
4. **Given** earlier evidence showing six executed activities in one environment and five in another for the same report ID, **when** the verifier compares those records with the deployed report version and controlled inputs, **then** the verifier records the candidate's count and any supported explanation, and leaves applicability open where the difference cannot be explained.

### User Story 3 — Reconcile every section through approval and correction (P1)

An auditor can trace the report values on the controlled day to their sources across versions. A report preparer can correct the report while preserving the source data and the earlier approved version.

**Independent test** — Follow the controlled day in the browser and inspect the corresponding API evidence from the initial Draft through approval and a correction. Compare the latest and historical records to the fixture and versioned contract.

1. **Given** the labeled SIM-A1-001 fixture, its applicable contract revision, and a Draft report, **when** the auditor compares the sections in the browser and the corresponding API evidence, **then** each section has expected and observed values, units where applicable, and traceable references to the underlying sources and selected report version.
2. **Given** a report that was approved, **when** an authorized user opens a correction and the corrected version proceeds from Draft to Approved, **then** the auditor can follow the parent and corrected version in both evidence channels, verify the source links and retained original source data, and read the earlier approved snapshot with its original values and provenance.
3. **Given** a discrepancy, an unexpected empty section, or missing observations in either channel, **when** the auditor reviews the reconciliation record, **then** the gap is recorded against the affected section and version and that section cannot pass. Expected empty or inapplicable sections have an explicit result and source rule.

### Edge Cases

- A release label can identify several builds. The exact source SHA and deployed candidate ID must both match.
- A file can keep its filename while its content changes. A checksum mismatch invalidates the corresponding evidence.
- Persian and English views can yield different export bytes. Match each download to the manifest entry for its format and effective export language.
- An unrecorded fixture, build, or verification scope leaves applicability unverified. An unknown machinery-hour value is distinct from an explicit zero.

## Requirements

### Functional Requirements

- **FR-001** — The release owner MUST freeze an archive for one complete controlled day. The manifest MUST link the fixture and contract revisions, day identifier and local date, deployment identity and full source commit SHA, report ID and version, independently derived expected values, section reconciliation evidence, and the versioned walkthrough guide. For each applicable export language, it MUST identify the original master Excel (FILE 4) download, the recalculated Excel used for acceptance, and the readable official PDF. If recalculation changes the bytes, preserve both Excel files, give each its own SHA-256 checksum, and link the recalculated file to the original and its recalculation evidence. If the bytes are identical, one file may serve both roles. Record reproducible SHA-256 checksums for all distributed files and pass the frozen manifest and its digest to 062.
- **FR-002** — The verifier MUST resolve the current DEF-A104-02 assertion by recording the A.1.02 timeout, the previous A.1.02 export-parity coverage and the outstanding lifecycle observations, and the direct zero-defect A.1.03 pass. Link the A.1.03 report from the manifest as prerequisite evidence and record its build, fixture, verified scope and applicability to the frozen candidate. Keep missing candidate evidence open. Retain the existing B05 dispositions with their own evidence references, candidate applicability, blocking impact and follow-up. Record unresolved material scope decisions with their status and authorized decision maker.
- **FR-003** — For **DEF-B05-01**, the verifier MUST record the original workbook's cached-value behavior, then independently recalculate the standalone downloaded copy and compare formulas and values with expectations. The applicable export contract governs whether cached values are mandatory. Record an unresolved contract question as a scope decision if it affects release.
- **FR-004** — For **DEF-B05-02**, the verifier MUST record the elapsed time from starting the export to receiving the full file for both Excel FILE 4 and official PDF on the candidate. Apply the B05 SC-002 threshold of under 3.0 seconds per format over standard broadband for a typical day with 15–30 activities and 20 materials or equipment rows. Record workload, conditions and result.
- **FR-005** — For **DEF-B05-03**, independent expected values MUST be derived from controlled source inputs and reference-form rules, including units and rounding. Their derivation MUST be independent of the product's calculations. Record the origin, reviewer, result, and discrepancies.
- **FR-006** — For **DEF-B05-04**, the verifier MUST compare PDF pages and workbook print pages against the applicable reference form, retain a cell and page mapping, readable comparison captures, recalculation evidence, file checksums and discrepancies, and apply the referenced B05 coverage to standard and long reports where applicable. The employer bundle stays tied to one reference day.
- **FR-007** — For **DEF-B05-05**, the verifier MUST record candidate applicability and dispositions for B02, B03 and B04. The handoff MUST carry the manifest, section reconciliation record and finding register together. Unresolved blocking evidence MUST prevent employer handoff.
- **FR-008** — QA MUST inventory every section under the applicable daily report contract and record at least one reconciliation row per section, covering operations, activity and WBS, manpower, machinery, materials, weather, obstacles and incidents, photos, and approval. For each section record the independent expected values or expected state, observed values or state, source references and applicable units, report and version identity, browser and API evidence, and disposition. Capture source lineage in Draft, Approved and correction, including the link to the earlier version and retention of original source data. A section with missing evidence or an unresolved discrepancy MUST remain unverified.

### Key Entities

- **Candidate manifest** — The release identity, reference report ID and version, controlled inputs, review status, versioned guide, files and checksums that define the bundle.
- **Finding disposition** — A B05 finding linked to the evidence assessed, its applicability, blocking impact and follow-up.
- **Section reconciliation record** — The inventory and per-section comparisons linking expected and observed values or states, version history, underlying sources and evidence.

## Success Criteria

### Measurable Outcomes

- **SC-001** — An auditor can trace both formats in every applicable export language and reproduce 100% of the distributed-file checksums from one manifest. The recalculated Excel and readable official PDF match 100% of applicable controlled figures under the documented units and rounding rules, with zero unresolved build, report-version or checksum mismatches.
- **SC-002** — All five B05 findings have explicit dispositions with candidate-linked evidence or a recorded gap. Zero unresolved blockers advance to employer handoff.
- **SC-003** — A passing latency result includes two complete downloads, each under the adopted 3.0-second threshold at the stated workload.
- **SC-004** — A passing A.1.02 record covers 100% of inventoried sections with documented source and lineage in the browser and API across Draft, Approved and correction, with zero unresolved discrepancies, missing required observations or unexpected changes to retained source data.

## Assumptions and Sources

- Scope covers A.1.02 and the candidate portion of A.1.04 for one reference day. The Stage 2 coverage records A.1.01 and A.1.03 as passed prerequisites. The ratified synthetic day is SIM-A1-001, Solar Hijri 1406-03-01, project day 12. Record the actual deployed report ID and version when the candidate is frozen. [Stage 2 coverage](../../output/speckit-prompts/a-1/coverage.json) · [B01 data contract](../057-a1-b01-data-contract/spec.md) · [B02 version integrity](../058-a1-b02-version-integrity/spec.md)
- The saved Stage 1 discovery and current QA reports establish the input scope. The standalone Stage 1 snapshot was unavailable. The prior A.1.02 export report supports only the comparisons it covers. [Stage 1 discovery](../../output/phase-a1-discovery/stage1-discovery.json) · [Current A.1.04 QA](../../output/phase-a1-qa/A.1.04-verification.json) · [A.1.02 export verification](../../output/phase-a1/a1-02-verification.json) · [Current A.1.03 QA](../../output/phase-a1-qa/A.1.03-verification.json)
- The activity-count comparison comes from two historical verification records. [A.1.02 parity evidence](../../output/phase-a1/a1-02-excel-pdf-parity-verification.json.md) · [B03 reference parity evidence](../059-a1-b03-reference-parity/implementation-evidence.md)
- FR-001 and SC-001 cover current DEF-A104-01. FR-002 and FR-008 cover current DEF-A104-02. FR-008 and SC-004 cover A.1.02 directly. FR-003–FR-007 retain the previously specified B05 checks and their original DEF-B05 identifiers. [B05 prompt](../../output/a1-requirements-2026-11-18/speckit-prompts/05-b05-independent-reconciliation.md) · [November 22 B05 findings](../../output/a1-requirements-2026-11-22-stage1-b05-qa-findings.md) · [Export success criteria](../044-shiraz-excel-parity-pdf/spec.md)

## Owner decisions of 2026-11-24

The existing Per-Requirement End-User QA agent independently validates T008. Preserve the starting snapshot and create a controlled synthetic scenario with WBS and unit-source links for lifecycle testing. Pin its snapshot and independently review affected expected values. Unknown actual shift duration remains unknown under C03.

For B05-01, check and document the original workbook’s formula caches. Use the independently recalculated Excel and the official PDF for review. Validate cached results without recalculation when that preview is part of the employer’s workflow. The employer test deployment and the agent’s authority to set delivery status are governed by [063](../063-a1-employer-acceptance/spec.md).
