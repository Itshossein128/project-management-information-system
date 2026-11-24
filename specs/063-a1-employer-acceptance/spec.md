# Feature Specification for A.1.04 — Initial Employer Acceptance

**Created** 2026-11-22  
**Status** Draft for Supervisor review  
**Input** [Stage 2 prompt 03](../../output/speckit-prompts/a-1/03-employer-acceptance.md)  
**Sequence** 3 of 3. Uses [Candidate Evidence](../061-a1-candidate-evidence/spec.md) and [Deployment Verification](../062-a1-deployment-verification/spec.md).

## User Scenarios & Testing

### User Story 1 — Walk through and approve one reference day (P1)

An authorized employer representative uses the versioned guide to download the exact Excel and PDF reviewed by QA, then checks figures and pagination against the independent reference.

**Independent test** — Give the representative a complete, verified candidate bundle and inspect the resulting review minute and archived files.

1. **Given** a named and authorized representative, complete deployment evidence, and a candidate with no unresolved blockers, **when** the representative follows the guide, downloads both files, reviews the figures and pages, and expressly approves the reviewed version, **then** the minute records the decision and the bundle is retrievable with its exact files and checksums.
2. **Given** the correct report version but a different file checksum, **when** the representative downloads the file, **then** the mismatch is recorded and approval remains pending for the bundle until the reviewed files and evidence match.

### User Story 2 — Preserve corrections requests and pending reviews (P1)

The delivery owner can see which issues remain open and which version a representative actually reviewed.

**Independent test** — Exercise correction, conditional or rejected, pending and changed-candidate cases against a known bundle.

1. **Given** an authorized representative who requests corrections, rejects the candidate, or attaches conditions to the decision, **when** the delivery owner archives the minute, **then** the exact disposition, feedback and follow-up owners are recorded and A.1.04 remains open pending explicit approval.
2. **Given** missing employer input or an internal QA pass alone, **when** progress is recorded, **then** employer disposition remains pending and A.1.04 remains open.
3. **Given** an earlier review and a changed candidate identity, report version, or reviewed file, **when** the revised bundle is offered for review, **then** the prior minute remains linked to its original version and the revised bundle requires applicable evidence and its own employer disposition.

### Edge Cases

- An unidentified or unauthorized participant may provide feedback. Their feedback cannot establish employer approval.
- An undated or incomplete minute cannot support closure until the required fields and explicit decision are recorded.
- The acceptance applies to the reviewed reference day. It does not establish full reporting-scope acceptance.

## Requirements

### Functional Requirements

- **FR-001** — Before the walkthrough, the delivery owner MUST verify the frozen manifest, candidate-specific dependency dispositions, and deployment verification handoff. The review MUST identify the authorized employer representative and review date and use the versioned employer guide. Unresolved blocking evidence MUST prevent employer handoff.
- **FR-002** — The authorized representative MUST follow the same-version Excel and PDF download journey. The review MUST record that the downloaded files match the manifest and capture which reference figures and pages were compared with the independently reviewed expected values and reference layout, along with any discrepancies.
- **FR-003** — The delivery owner MUST preserve a retrievable review minute with the reviewed artifacts, guide and evidence references. The minute MUST record participants, review date, the representative's authority and identity, exact candidate and source SHA, report ID and version, file identifiers and SHA-256 checksums, figures and pages reviewed, discrepancies, follow-up owners, and the representative's explicit decision when available. Record pending status where employer input is absent.
- **FR-004** — Only the authorized employer representative may issue employer acceptance. Internal QA and agents may assemble and verify evidence. A.1.04 MUST remain open until the required evidence and explicit employer approval are recorded for that same version. A change in candidate identity, report version, or reviewed files requires applicable evidence and a fresh disposition for the changed bundle.

### Key Entities

- **Walkthrough guide** — Versioned instructions for selecting the reference version, downloading both files, and reviewing figures and pagination.
- **Review minute** — Evidence of attendance, review scope, artifact identity, observations, follow-up and the employer disposition for the exact candidate.

## Success Criteria

### Measurable Outcomes

- **SC-001** — Every recorded approval has a retrievable minute with all required fields and two reviewed files whose checksums and report version match the frozen manifest.
- **SC-002** — All correction, conditional, rejection and pending scenarios leave A.1.04 open. Every changed bundle has its own evidence and disposition before closure.
- **SC-003** — One authorized employer decision is recorded for the accepted reference day. Internal verification cannot satisfy that condition.

## Assumptions and Sources

- The employer representative's identity and the review date are B06 handoff fields under GOV-01 and are recorded during delivery. Their absence keeps employer disposition pending. [B01 data contract](../057-a1-b01-data-contract/spec.md)
- All functional requirements address DEF-A104-03 (Q05). Acceptance is limited to initial review of the one reference day and does not close A.10. [A.1.04 findings](../../output/phase-a1/a1-04-qa-findings.json) · [Stage 1 discovery](../../output/phase-a1-discovery/discovery.json)
