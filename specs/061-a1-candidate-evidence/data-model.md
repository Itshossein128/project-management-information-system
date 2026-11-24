# Data Model for A.1.04 Candidate Evidence

The records below are archived evidence. They reference existing report and deployment identities.

## Candidate manifest

- **Identity** — Schema revision, deployed candidate ID, full source SHA, environment, observed API/web build IDs, evidence references and capture time.
- **Reference version** — Project UUID, report version UUID, report lineage ID when exposed, version number, report number, local report date and project day. Record which UUID and version the browser selected.
- **Controlled inputs** — Identifiers and SHA-256 digests for the synthetic fixture and applicable form/data-contract revisions. Record the deployed input snapshot or evidence tying the inputs to the selected report version.
- **Expected values** — Reference to the independent data and method, their source input hashes, review status, reviewer and date. Each expectation records the section, source reference, unit, normalization or rounding rule, value, and Excel cell and PDF page mapping where applicable. Distinguish null, zero and inapplicable values.
- **Distributed artifacts** — Role, archive-relative path, SHA-256, byte count and applicable format, effective locale and revision. Include both official file formats, the controlled inputs and expectations, and the versioned walkthrough guide. Use a detached digest for the manifest itself. Capture changes in a new frozen manifest and retain the original evidence.

## B05 finding disposition

- **Key** — Candidate manifest digest and one of DEF-B05-01 through DEF-B05-05. The register contains one record per finding.
- **Evidence** — Candidate, fixture and version where relevant, covered scope, prior versus candidate proof, applicability result, criterion, references and outcome. Each evidence reference identifies its own subject. A separate benchmark workload includes its identity and measured counts.
- **Disposition** — Satisfied by traceable evidence, open, or explicit scope decision required. Carry blocking impact and rationale. Open items carry follow-up owner or role and action. A recorded scope decision includes decision maker, authority, date and source.
- **Supporting records** — Formula cache and recalculation log, per-format timing, reviewed independent expectations, print comparison, and B02–B04 prerequisite records. A prerequisite record identifies the requirement tested, its release applicability and any remaining gap.
- **Activity-count reconciliation** — Both historical counts and evidence references, candidate count, deployed report version, input snapshot reference and digest, supported explanation if available, and applicability for each affected prior result.

## Downstream verification and acceptance references

- **Deployment verification** — Manifest digest, candidate ID/source SHA, report UUID/version, authorization matrix, browser matrix, decision-tree route comparisons and unresolved findings. Successful downloads reference their format/locale slot and raw checksum.
- **Employer review minute** — Same manifest digest and candidate/report identities, authority and identity of reviewer, date, guide revision, artifact paths and SHA-256, figures and pages reviewed, discrepancies, follow-up owners and decision. The minute and reviewed artifacts remain retrievable together.

## Transitions and validation

1. Collect evidence as draft. Confirm identity, independently reviewed expectations, and file checksums before freezing a manifest. A checksum or identity mismatch makes the affected submission unverified.
2. Bind each disposition to the frozen digest. Evaluate release readiness from required evidence and recorded blocking impact. A missing material decision or unresolved blocker prevents employer handoff.
3. Bind deployment and walkthrough evidence to the same digest. A candidate, report version, or reviewed file change requires a new matching evidence set and review disposition. The old bundle remains attributable to its recorded decision.
4. A.1.04 remains open for missing evidence, pending employer input, corrections, rejection or conditional response. Explicit approval from the authorized representative is recorded for the exact reviewed bundle before closure.
