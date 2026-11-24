/speckit-specify

Specify the release candidate and dependency evidence for A.1.04 (B06) — same-version daily report downloads and initial employer acceptance.

Stage 1 sources: ../../phase-a1-discovery/discovery.json, ../../phase-a1/a1-04-qa-findings.json, ../../phase-a1/a1-02-verification.json and ../../phase-a1/a1-03-qa-findings.json. A.1.01–A.1.03 have direct QA passes with zero defects. Carry these results forward as evidence. Scope specification and any candidate checks to A.1.04.

DEF-A104-01 — Define a frozen candidate and reference report version. Require a manifest tying the deployed candidate ID and exact source SHA to the reference report ID/version, controlled inputs, independent expected values with provenance and review status, final downloadable Excel and PDF samples, and the employer guide. Require verified SHA-256 for the distributed artifacts. Give the auditor an acceptance scenario that detects mismatched builds, report versions or files.

DEF-A104-02 — Define an evidence disposition for each referenced B05 finding DEF-B05-01 through DEF-B05-05. Reconcile the A.1.04 report's blocker assertion with the direct A.1.02/A.1.03 passes by build, fixture and verified scope. Reuse the recorded 88-formula recalculation and unknown-hours regression where their scope applies. Establish which residual candidate evidence is needed for workbook cache behavior and standalone recalculation, independent expected values, download latency against B05 SC-002, print/page comparisons and evidence logs, and B02–B04 prerequisite dispositions. Use the B05 evidence referenced by Discovery for the applicable criteria. Treat a workbook cache requirement as conditional on the export contract. State which findings are satisfied by traceable evidence, still open, or require an explicit scope decision. A candidate with an unresolved blocking finding remains blocked for employer handoff.

Write testable stakeholder outcomes and acceptance scenarios for A.1.04 only. The handoff to 02 is the identified candidate, manifest and dependency disposition. Final delivery evidence and employer disposition are supplied by subsequent sub-stages.
