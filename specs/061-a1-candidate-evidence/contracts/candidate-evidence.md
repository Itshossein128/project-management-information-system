# Candidate Evidence and Handoff Contract

**Producer** — Release owner and independent verifier for 061  
**Consumers** — Deployment QA in [062](../../062-a1-deployment-verification/spec.md) and delivery owner in [063](../../063-a1-employer-acceptance/spec.md)  
**Record definitions** — [Data model](../data-model.md)

## Existing application interface

Use the browser report details for the selected version and the project-scoped detail GETs under `/api/v1/projects/{projectId}/daily-reports/{versionUuid}/`, with `excel/` and `pdf/` for the two formats. The version UUID identifies the selected report record. Respect the deployed server-side authorization for each action. The existing per-version helpers send the project and report IDs and display the resulting attachment. [Server route documentation](../../../apps/api/core/field_reports/ENDPOINTS.md) · [Browser download helper](../../../apps/web/src/app/lib/api/daily-reports.ts)

## Archive interface

- Store the manifest as UTF-8 JSON with the fields in the data model. Publish the SHA-256 of the exact saved manifest bytes separately. Use a checksum list in SHA-256 command format for the distributed files, with paths relative to the archive and values matching the manifest. Capture original downloads before independent processing. Use separate paths for recalculated copies and printable derivatives.
- Maintain a manifest slot for each relevant format and effective export locale. Every slot maps to a complete artifact and its SHA-256. Repeated authorized downloads for the slot must match that artifact. Layout, approved figures and embedded audit fingerprints are additional evidence.
- Pass the frozen manifest reference and digest, finding register and candidate status to deployment QA. If the manifest is still a draft or evidence remains incomplete, pass the blocked or unverified status and gap list. Reject evidence for a different digest, source SHA, deployment or report version at each handoff.
- Include only controlled reference data and evidence needed for review. Keep archive access scoped to authorized participants. Exclude credentials and session tokens.

## B05 evidence expected at the 061 handoff

- **DEF-B05-01** — Original cache observations, governing export contract assessment, standalone recalculation log, formula/value/error comparison. Record cache availability separately from recalc success.
- **DEF-B05-02** — Candidate, benchmark workload and network conditions, elapsed time to complete Excel and PDF downloads and each format's threshold result. Record incomplete runs as such.
- **DEF-B05-03** — Independent expected values, input and rule provenance, units, rounding, review record and discrepancies.
- **DEF-B05-04** — Standard and applicable long-report cell/page mappings, Excel print and PDF comparisons with the reference form, captures, checksums, logs and discrepancy decisions.
- **DEF-B05-05** — B02–B04 candidate applicability and prerequisite dispositions. Explain the relationship between direct technical QA and delivery-plan statuses. Include the five-versus-six activity comparison, candidate count, input provenance, and the applicability of the affected prior evidence.

## Downstream evidence returned for closure

- **062** — For each controlled authorization context, format and relevant route, return expected/observed outcomes and references. Confirm direct download policy and that each allowed file matches the relevant manifest slot. Denials withhold report and file data. Preserve the applicable owning-unit observation rule during the decision-tree comparison. Record Persian RTL and English LTR results for desktop and 390 × 844 mobile, with all 18 sections, journey, viewport, readability, correct selected version and both downloads in every combination. Include decision-tree comparisons and unresolved findings.
- **063** — Begin employer review after the 061 candidate and 062 deployment evidence are complete and all blockers are resolved. Use the versioned guide and same verified bundle. Record the manifest digest, participants, named authorized employer representative, date, reviewed figures and pages, exact artifacts and checksums, discrepancies, follow-up and explicit disposition. Preserve the minute and artifacts together. Internal QA contributes evidence. Explicit employer approval for the same digest and complete required evidence are required to close A.1.04.
