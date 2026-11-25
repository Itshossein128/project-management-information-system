# Candidate Evidence and Handoff Contract

**Producer** — Release owner and independent verifier for 061  
**Consumers** — Deployment QA in [062](../../062-a1-deployment-verification/spec.md) and delivery owner in [063](../../063-a1-employer-acceptance/spec.md)  
**Record definitions** — [Data model](../data-model.md)

## Existing application interface

Use the browser report details for the selected version and the project-scoped detail GETs under `/api/v1/projects/{projectId}/daily-reports/{versionUuid}/`, with `excel/` and `pdf/` for the two formats. The version UUID identifies the selected report record. Respect the deployed server-side authorization for each action. The existing per-version helpers send the project and report IDs and display the resulting attachment. [Server route documentation](../../../apps/api/core/field_reports/ENDPOINTS.md) · [Browser download helper](../../../apps/web/src/app/lib/api/daily-reports.ts)

For the section reconciliation, use the contract inventory, selected report details, version history, correction records and applicable source provenance. Record the corresponding browser and API observations under the version UUID observed at each lifecycle point. Use authorized synthetic data and distinct preparer and approver accounts. [Lifecycle and provenance routes](../../../apps/api/core/field_reports/ENDPOINTS.md)

## Archive interface

- Store the manifest as UTF-8 JSON with the fields in the data model. Publish the SHA-256 of the exact saved manifest bytes separately. Use a checksum list in SHA-256 command format for the distributed files, with paths relative to the archive and values matching the manifest. Capture original downloads before independent processing. Use separate paths for recalculated copies and printable derivatives.
- Maintain an original-download slot for each relevant format and effective export locale. Each slot maps to the complete artifact and SHA-256 expected from repeated authorized downloads. Link each recalculated workbook to its original slot and recalculation record. When the checksums differ, retain both files and checksum entries. Include the reconciliation record and A.1.03 prerequisite reference and applicability in the manifest.
- Pass the frozen manifest reference and digest, section reconciliation, finding register and candidate status to deployment QA. If the manifest is still a draft or evidence remains incomplete, pass the blocked or unverified status and gap list. Reject evidence for a different digest, source SHA, deployment or report version at each handoff.
- Include only controlled reference data and evidence needed for review. Keep archive access scoped to authorized participants. Exclude credentials and session tokens.

## B05 evidence expected at the 061 handoff

- **DEF-B05-01** — Original cache observations, governing export contract assessment, standalone recalculation log, formula/value/error comparison. Record cache availability separately from recalc success.
- **DEF-B05-02** — Candidate, benchmark workload and network conditions, elapsed time to complete Excel and PDF downloads and each format's threshold result. Record incomplete runs as such.
- **DEF-B05-03** — Independent expected values, input and rule provenance, units, rounding, review record and discrepancies.
- **DEF-B05-04** — Standard and applicable long-report cell/page mappings, Excel print and PDF comparisons with the reference form, captures, checksums, logs and discrepancy decisions.
- **DEF-B05-05** — B02–B04 candidate applicability and prerequisite dispositions. Explain the relationship between direct technical QA and delivery-plan statuses. Include the five-versus-six activity comparison, candidate count, input provenance, and the applicability of the affected prior evidence.

## Downstream evidence returned for closure

- **062** — For each controlled authorization context in the 062 specification, including the authenticated Visitor, return expected and observed outcomes for both formats and applicable routes. Verify original-download SHA-256 by format and effective locale and verify archived recalculated Excel SHA-256 and its linkage. Denials withhold protected report and file data. Preserve the applicable owning-unit observation rule in decision-tree comparisons. Record all 72 section observations for Persian RTL and English LTR on desktop and 390 × 844 mobile, including required actions, viewport, readability, selected version and both downloads. Carry unresolved findings and reuse earlier 403 and 404 observations only where candidate and request applicability match.
- **063** — Begin employer review after 061 candidate and 062 deployment evidence are complete for the same digest and blockers are resolved. Use the versioned guide, verify the original downloads and review the archived recalculated workbook and official PDF. Preserve the delivery agent’s disposition and verified artifacts together using the [data model](../data-model.md#downstream-verification-and-acceptance-references). Record employer feedback separately when the project owner relays it. A.1.04 requires complete technical evidence for that digest.
