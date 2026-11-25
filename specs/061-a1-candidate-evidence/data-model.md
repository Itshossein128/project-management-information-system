# Data Model for A.1.02 and A.1.04 Candidate Evidence

The records below are archived evidence. They reference existing report and deployment identities.

## Candidate manifest

- **Identity** — Schema revision, deployed candidate ID, full source SHA, environment, observed API/web build IDs, evidence references and capture time.
- **Reference version** — Project UUID, report version UUID, report lineage ID when exposed, version number, report number, local report date and project day. Record which UUID and version the browser selected.
- **Controlled inputs** — Identifiers and SHA-256 digests for the synthetic fixture and applicable form/data-contract revisions. Record the deployed input snapshot or evidence tying the inputs to the selected report version.
- **Expected values** — Reference to the independent data and method, their source input hashes, review status, reviewer and date. Each expectation records the section, source reference, unit, normalization or rounding rule, value, and Excel cell and PDF page mapping where applicable. Distinguish null, zero and inapplicable values.
- **Evidence references** — Section reconciliation and its contract inventory, applicable A.1.03 prerequisite evidence and versioned walkthrough guide. References to included files carry their SHA-256.
- **Distributed artifacts** — Role, archive-relative path, SHA-256, byte count and applicable format, effective locale and revision. Per locale, identify the original Excel and PDF downloads and the recalculated workbook. The recalculated entry identifies the source slot and recalculation evidence. Both workbook roles may share a file when hashes match. Use a detached digest for the manifest itself.

## Section reconciliation

- **Scope** — Candidate and source SHA, fixture ID and digest, contract revision and digest, project, date and report lineage. Reference both lifecycle versions and identify the approved UUID/version selected for delivery.
- **Inventory and observations** — One or more rows per contract section. Each row records underlying source references, expected values or expected state, observed values or state, applicable unit and comparison rule, version UUID/number and status, browser and API evidence, and disposition. Expected empty and inapplicable results include their source rule.
- **Lifecycle comparison** — Record the initial Draft, Approved, correction Draft and corrected Approved observations. Record parent/result identifiers, selected version, source snapshots and comparison references for retention of the original source values and earlier approved snapshot. An incomplete observation or unresolved discrepancy makes the relevant section unverified.

## B05 finding disposition

- **Key** — Candidate manifest digest and one of DEF-B05-01 through DEF-B05-05. The register contains one record per finding.
- **Evidence** — Candidate, fixture and version where relevant, covered scope, prior versus candidate proof, applicability result, criterion, references and outcome. Each evidence reference identifies its own subject. A separate benchmark workload includes its identity and measured counts.
- **Disposition** — Satisfied by traceable evidence, open, or explicit scope decision required. Carry blocking impact and rationale. Open items carry follow-up owner or role and action. A recorded scope decision includes decision maker, authority, date and source.
- **Supporting records** — Formula cache and recalculation log, per-format timing, reviewed independent expectations, print comparison, and B02–B04 prerequisite records. A prerequisite record identifies the requirement tested, its release applicability and any remaining gap.
- **Activity-count reconciliation** — Both historical counts and evidence references, candidate count, deployed report version, input snapshot reference and digest, supported explanation if available, and applicability for each affected prior result.

## Downstream verification and acceptance references

- **Deployment verification** — Manifest digest, candidate ID/source SHA, report UUID/version, authorization matrix, browser matrix, decision-tree route comparisons and unresolved findings. Successful downloads reference their original format/locale slot and checksum. Record archived recalculated Excel checksum and original linkage verification.
- **Delivery disposition** — Same manifest digest, candidate and report identities, QA date, agent reviewer, guide revision, artifact hashes, checked figures and pages, blockers and follow-up. Employer feedback, when relayed by the project owner, is recorded separately for the affected version.

## Transitions and validation

1. Collect evidence as draft and key it by candidate, fixture and report/version. Confirm identity, section reconciliation, prerequisite reference, independently reviewed expectations, file checksums and recalculation linkage before freezing a manifest. Evidence hashed by the manifest refers to the candidate identity. The detached digest is used in later records so the manifest and included files have no circular checksum references. A checksum or identity mismatch makes the affected submission unverified.
2. Bind each disposition to the frozen digest. Evaluate release readiness from required evidence and recorded blocking impact. A missing material decision or unresolved blocker prevents employer handoff.
3. Bind deployment and walkthrough evidence to the same digest. A candidate, report version, or reviewed file change requires a new matching evidence set and review disposition. The old bundle remains attributable to its recorded decision.
4. A.1.04 remains open for missing technical evidence or blocking defects. The agent records the exact verified bundle before closure.
