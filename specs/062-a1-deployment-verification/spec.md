# Feature Specification for A.1.04 — Deployment Verification

**Created** 2026-11-22  
**Status** Draft for Supervisor review  
**Input** [Stage 2 prompt 02](../../output/speckit-prompts/a-1/02-deployment-verification.md)  
**Sequence** 2 of 3. Uses [Candidate Evidence](../061-a1-candidate-evidence/spec.md) and hands off to [Employer Acceptance](../063-a1-employer-acceptance/spec.md).

## User Scenarios & Testing

### User Story 1 — Verify who can download the reference version (P1)

A QA verifier confirms that the intended project user can download the selected version and that the release enforces download permissions.

**Independent test** — Use controlled accounts and projects against the frozen candidate and record expected and actual outcomes for both formats.

1. **Given** an active member authorized to view and export the reference report, **when** the user downloads its Excel and PDF through the report screen and by its direct version-specific download routes, **then** the files match the frozen report version and manifest checksums.
2. **Given** a signed-out visitor, an active project member without required export permission, or a user authorized for a different project without access to the reference project, **when** each attempts access to either format through the report journey or a direct report/version download route, **then** access is denied and the report and its artifacts are withheld.

### User Story 2 — Verify both languages on desktop and mobile (P1)

A field engineer can read all 18 daily report sections, identify the selected version, and download both files in the required language and viewport.

**Independent test** — Follow the report journey for Persian and English on desktop and on a 390 × 844 mobile viewport using the same candidate.

1. **Given** each of the four language and viewport combinations, **when** the engineer opens all 18 sections and selects the reference report version, **then** text direction is correct, content and controls are readable and usable, and both downloads match the selected version and manifest.
2. **Given** an unreadable or clipped section, an incomplete download, a different version, or missing evidence for a combination, **when** a verifier reviews the matrix, **then** that combination cannot receive a passing result and the gap is carried forward.

### User Story 3 — Verify documented access and export paths (P2)

A decision-tree maintainer can trace each relevant documented export route and decision to observed candidate behavior.

**Independent test** — Compare the candidate's observed routes and allow or deny results with the intended access rules and the decision tree.

1. **Given** the relevant report journey and version-specific download routes, **when** the maintainer checks each path and authorization decision, **then** the record links the documentation, intended result and observed result, with a disposition for every discrepancy.

### Edge Cases

- A deployment change during verification invalidates affected observations until they are repeated on the manifest candidate.
- If a report has several versions, a successful download of the current version does not satisfy the check for a different selected version.
- Evidence may cite controlled test data and account roles. Credentials and session tokens are excluded.

## Requirements

### Functional Requirements

- **FR-001** — QA MUST verify the deployed candidate ID and exact source SHA against the frozen manifest and bind each result to the reference report ID and version. Missing identity or a mismatch MUST be marked unverified and carried into handoff.
- **FR-002** — QA MUST record an authorization matrix covering an authorized project member, a signed-out visitor, a project member lacking the required role or export permission, and an otherwise authorized user from another project without access to the reference project. Check both Excel and PDF, including direct report/version downloads. Each row MUST capture the candidate, role and project context, route or action, expected and actual result, and evidence reference. For allowed downloads, record file identity against the frozen manifest. Denials MUST withhold the report and its artifacts.
- **FR-003** — QA MUST record all 18 sections in Persian RTL and English LTR, each on desktop and on mobile at 390 × 844. Record interface language, actual viewport, report journey, section readability and layout, correct version selection, both downloads and their version and file identity, observed outcomes and evidence references for every combination. Match each download to the manifest entry for its format and effective export language.
- **FR-004** — The decision-tree maintainer MUST verify the relevant deployed export routes and authorization decisions against the intended access rules and project decision tree. Record each reviewed route, documentation reference, intended result, observed result and discrepancy disposition.
- **FR-005** — QA MUST hand off the candidate-linked authorization and browser matrices, decision-tree references, and all unresolved findings. Required evidence gaps, candidate drift, access mismatches or incomplete verification MUST remain visible in the handoff and block employer acceptance readiness.

### Key Entities

- **Authorization matrix** — Expected and observed permission outcomes for the controlled account, project, report version, route and file format.
- **Browser verification record** — The report journey, section and download observations for one language and viewport combination.
- **Decision-tree verification record** — A documented route and access decision linked to the intended rule, candidate observation and discrepancy disposition.

## Success Criteria

### Measurable Outcomes

- **SC-001** — The candidate evidence covers four access contexts for both formats and the direct version-specific routes. Every passing authorized download matches the manifest and every passing denial withholds protected content.
- **SC-002** — All 72 section observations across the four language and viewport combinations have recorded outcomes. Each passing combination includes two matching downloads and the correct selected version.
- **SC-003** — Every reviewed export route has a decision-tree reference and an observed authorization result. Every discrepancy has an explicit disposition.

## Assumptions and Sources

- The candidate manifest and B05 disposition are upstream inputs. The application’s existing project permission rules govern access. Use the actual measured desktop viewport in the QA record. [Constitution, Principle I](../../.specify/memory/constitution.md#i-server-enforced-authorization-and-tenantproject-isolation)
- FR-001 and FR-005 bind the evidence to the candidate. FR-002 covers DEF-A104-04 (E09), FR-003 covers DEF-A104-05 (Q03), and FR-004 covers DEF-A104-06 (Q04). [A.1.04 findings](../../output/phase-a1/a1-04-qa-findings.json) · [Decision tree](../../docs/decision-tree/README.md)
