# Feature Specification for A.1.04 — Candidate Evidence

**Created** 2026-11-22  
**Status** Draft for Supervisor review  
**Input** [Stage 2 prompt 01](../../output/speckit-prompts/a-1/01-candidate-evidence.md)  
**Sequence** 1 of 3. Hands off to [Deployment Verification](../062-a1-deployment-verification/spec.md).

## User Scenarios & Testing

### User Story 1 — Identify the exact report and files (P1)

A release owner freezes the delivery candidate so an auditor and the employer can identify and reproduce the same review bundle.

**Independent test** — Inspect a sample manifest and compare it with the deployed candidate, the selected report version, and both downloaded files.

1. **Given** a complete reference day and a named candidate, **when** the auditor compares the deployment identity, report identity and version, and artifact checksums with the manifest, **then** each matches the frozen record.
2. **Given** a different build, report version, or modified file, **when** the same checks are repeated, **then** the mismatch is recorded and the bundle remains blocked until the exact candidate is verified.

### User Story 2 — Resolve the evidence needed for release (P1)

An independent verifier traces each B05 finding to evidence applicable to the candidate so the release owner can decide whether verification may proceed.

**Independent test** — Inspect five finding records with evidence of different vintages, including one unresolved blocker, and verify the candidate's disposition.

1. **Given** the direct A.1.02 and A.1.03 QA passes and the later A.1.04 blocker assertion, **when** the verifier compares their build, fixture, and verified scope with the frozen candidate, **then** the applicable results are reused, any missing identity or coverage is recorded, and residual checks are assigned to the candidate.
2. **Given** a fresh workbook that recalculates correctly but lacks cached formula results, **when** the verifier checks the governing export contract, **then** standalone recalculation and cache behavior receive separate results, and cache availability is a release requirement only if the contract requires it.
3. **Given** an unresolved blocking finding or evidence from a different candidate, **when** the release owner reviews the register, **then** the handoff records the blocker and employer review remains blocked.
4. **Given** earlier evidence showing six executed activities in one environment and five in another for the same report ID, **when** the verifier compares those records with the deployed report version and controlled inputs, **then** the verifier records the candidate's count and any supported explanation, and leaves applicability open where the difference cannot be explained.

### Edge Cases

- A release label can identify several builds. The exact source SHA and deployed candidate ID must both match.
- A file can keep its filename while its content changes. A checksum mismatch invalidates the corresponding evidence.
- Persian and English views can yield different export bytes. Match each download to the manifest entry for its format and effective export language.
- An unrecorded fixture, build, or verification scope leaves applicability unverified. An unknown machinery-hour value is distinct from an explicit zero.

## Requirements

### Functional Requirements

- **FR-001** — The release owner MUST freeze a manifest linking the deployed candidate ID and exact source SHA to the reference report ID and version, controlled inputs, independently derived expected values with provenance and review status, downloadable master daily report Excel (FILE 4) and PDF, and the versioned employer walkthrough guide. The manifest MUST identify the artifact for each applicable format and effective export language. The verifier MUST record verified SHA-256 checksums for the distributed artifacts.
- **FR-002** — The verifier MUST maintain one disposition per referenced B05 finding, with candidate, fixture, verified scope, evidence reference, blocking impact, and any required follow-up. Allowed dispositions are satisfied by traceable evidence, open, or explicit scope decision required. Compare the A.1.04 QA assertion with the direct A.1.02 and A.1.03 passes. Reuse the 88-formula recalculation and the unknown-hours regression only within their demonstrated scope. A missing material scope decision remains open for release purposes until recorded by the authorized decision maker.
- **FR-003** — For **DEF-B05-01**, the verifier MUST record the original workbook's cached-value behavior, then independently recalculate the standalone downloaded copy and compare formulas and values with expectations. The applicable export contract governs whether cached values are mandatory. Record an unresolved contract question as a scope decision if it affects release.
- **FR-004** — For **DEF-B05-02**, the verifier MUST record the elapsed time from starting the export to receiving the full file for both Excel FILE 4 and official PDF on the candidate. Apply the B05 SC-002 threshold of under 3.0 seconds per format over standard broadband for a typical day with 15–30 activities and 20 materials or equipment rows. Record workload, conditions and result.
- **FR-005** — For **DEF-B05-03**, independent expected values MUST be derived from controlled source inputs and reference-form rules, including units and rounding. Their derivation MUST be independent of the product's calculations. Record the origin, reviewer, result, and discrepancies.
- **FR-006** — For **DEF-B05-04**, the verifier MUST compare PDF pages and workbook print pages against the applicable reference form, retain a cell and page mapping, readable comparison captures, recalculation evidence, file checksums and discrepancies, and apply the referenced B05 coverage to standard and long reports where applicable. The employer bundle stays tied to one reference day.
- **FR-007** — For **DEF-B05-05**, the verifier MUST record candidate applicability and dispositions for B02, B03 and B04 prerequisites, including the distinction between status labels on the delivery plan and the direct A.1.02 and A.1.03 QA results. The handoff MUST carry the manifest and finding register together. Unresolved blocking evidence MUST prevent employer handoff.

### Key Entities

- **Candidate manifest** — The release identity, reference report ID and version, controlled inputs, review status, versioned guide, files and checksums that define the bundle.
- **Finding disposition** — A B05 finding linked to the evidence assessed, its applicability, blocking impact and follow-up.

## Success Criteria

### Measurable Outcomes

- **SC-001** — An auditor can trace both download formats in every applicable export language, and every distributed artifact, to one manifest, with zero build, report-version or checksum mismatches in a passing bundle.
- **SC-002** — All five B05 findings have explicit dispositions with candidate-linked evidence or a recorded gap. Zero unresolved blockers advance to employer handoff.
- **SC-003** — A passing latency result includes two complete downloads, each under the adopted 3.0-second threshold at the stated workload.

## Assumptions and Sources

- Scope covers A.1.04 for one reference day. A.1.01–A.1.03 contribute prior QA evidence. Any dependency work is limited to evidence gaps relevant to the candidate handoff. The ratified synthetic day is SIM-A1-001, Solar Hijri 1406-03-01, project day 12. Record the actual deployed report ID and version when the candidate is frozen. [B01 data contract](../057-a1-b01-data-contract/spec.md)
- The saved Stage 1 discovery and QA reports establish the input scope. The standalone Stage 1 snapshot was unavailable. [Discovery](../../output/phase-a1-discovery/discovery.json) · [A.1.04 findings](../../output/phase-a1/a1-04-qa-findings.json) · [A.1.02 verification](../../output/phase-a1/a1-02-verification.json) · [A.1.03 findings](../../output/phase-a1/a1-03-qa-findings.json)
- The activity-count comparison comes from two historical verification records. [A.1.02 parity evidence](../../output/phase-a1/a1-02-excel-pdf-parity-verification.json.md) · [B03 reference parity evidence](../059-a1-b03-reference-parity/implementation-evidence.md)
- FR-001 covers DEF-A104-01. FR-002–FR-007 cover DEF-A104-02. The B05 sources define the referenced evidence checks. [Discovery-cited B05 prompt](../../output/a1-requirements-2026-11-18/speckit-prompts/05-b05-independent-reconciliation.md) · [November 22 B05 findings](../../output/a1-requirements-2026-11-22-stage1-b05-qa-findings.md) · [SC-002 source](../044-shiraz-excel-parity-pdf/spec.md)
