# Research for A.1.04 Candidate Evidence

## R1 — Pin the running release and selected version (FR-001)

**Decision** — Use deployment provenance with the exact source SHA and observed running API/web build identifiers. Record the environment, project UUID, report version UUID, human-readable report number and version number. Confirm identity around collection and before handoff.

**Rationale** — The deployment workflow tags API and web images with the selected SHA. A known commit or successful pipeline does not establish what a given environment serves. The existing browser and server use the selected version UUID for the detail download. The date-range workbook covers a different selection. [Deployment workflow](../../.github/workflows/deploy.yml) · [Endpoint reference](../../apps/api/core/field_reports/ENDPOINTS.md)

**Alternative considered** — Use the branch name, date, report number, or status row as identity. Each can recur across builds or versions.

## R2 — Verify the downloaded bytes per locale (FR-001)

**Decision** — Capture original downloads, assign a manifest slot by format and effective locale, and compare repeat downloads for each slot. Desktop and mobile use the same slot when they receive the same effective export locale. If both locale slots contain identical bytes, they may reference the same file. Archive the actual files and verify SHA-256 on those bytes.

**Rationale** — Both actions generate output on request and pass the request language to the exporter. Filenames and visible values do not guarantee byte identity. Same-locale instability is a hypothesis to test. If confirmed, first isolate its cause. Any correction must preserve the authorized version-specific route and re-verify the resulting release. [Export actions](../../apps/api/core/field_reports/daily_report_views.py) · [Excel builder](../../apps/api/core/field_reports/shiraz_file4_excel.py) · [PDF builder](../../apps/api/core/field_reports/pdf.py)

**Alternative considered** — Normalize metadata for hashing or compare figures alone. Neither proves the distributed raw file matches the reviewed artifact.

## R3 — Reuse historical findings within their verified scope (FR-002, FR-007)

**Decision** — Record the evidence source, build, fixture, report/version and exact scope for each prior result. A.1.02 supports 88 formula comparisons with zero reported discrepancies and the listed cross-format comparisons. Its detailed report describes a formula parser. A.1.03 supports the unknown-versus-zero regression. The saved summaries do not establish exact deployed source SHA, selected report version, or matching raw file hashes for the proposed bundle. Reconfirm missing applicability on the candidate. Use B02/B03/B04 evidence for version integrity, export parity and filter/totals prerequisites only where applicable.

**Rationale** — The detailed A.1.02 evidence lists six executed activity rows. Earlier B03 evidence lists five for the same reference report UUID. Record the candidate count and its input provenance, along with any explanation supported by the compared records. Keep applicability open for evidence that depends on the count if the discrepancy remains unexplained. [A.1.02 verification](../../output/phase-a1/a1-02-verification.json) · [Detailed reconciliation](../../output/phase-a1/a1-02-excel-pdf-parity-verification.json.md) · [B03 implementation evidence](../059-a1-b03-reference-parity/implementation-evidence.md) · [A.1.03 verification](../../output/phase-a1/a1-03-qa-findings.json) · [A.1.04 findings](../../output/phase-a1/a1-04-qa-findings.json)

**Alternative considered** — Mark B05 closed from prior pass labels or repeat all earlier work. Use exact candidate evidence for each unmet scope and reuse applicable prior proof.

## R4 — Recalculate a copy and use a separate independent reference (FR-003, FR-005, FR-006)

**Decision** — Inspect formula cells and cached values on the original workbook. Recalculate a copy using LibreOffice Calc with an isolated profile. Record formula mappings, calculated values, errors and tool version. Build expected values from the controlled inputs and reference-form rules using explicit units, conversions and rounding. Review the expected values independently of the application exporters and aggregators. Compare workbook print pages and official PDF pages with the reference using cell/page mapping and readable captures for the applicable standard and long cases.

**Rationale** — Earlier B03 evidence demonstrates a workable toolchain and covers selected outputs. The prior parser or a saved grand-total calculation provides partial evidence. The B05 prompt makes the cache requirement conditional on the export contract. The reviewed FILE 4 sources establish formula behavior and rendering, with no unconditional cached-value requirement located in those sources. Record the governing contract and result at execution. Any material conflict over applicability remains open pending an explicit scope decision. [Discovery-cited B05 prompt](../../output/a1-requirements-2026-11-18/speckit-prompts/05-b05-independent-reconciliation.md) · [B03 implementation evidence](../059-a1-b03-reference-parity/implementation-evidence.md) · [B03 export contract](../059-a1-b03-reference-parity/contracts/exports.md) · [FILE 4 requirements](../044-shiraz-excel-parity-pdf/spec.md)

**Alternative considered** — Use product calculations as the expected data or recalculate the archived original. Both weaken independence or artifact identity.

## R5 — Time completed downloads on the real journey (FR-004)

**Decision** — Capture export initiation through completed file receipt for both formats on the pinned deployment, using 15–30 activities and 20 materials/equipment rows under standard broadband. If the frozen reference day falls outside these counts, use a separate controlled benchmark workload bound to the same deployed candidate and record its own identity. Keep the reference bundle unchanged.

**Rationale** — A header response or server execution time omits transfer time. The exact workload is needed to interpret the under-3.0-second criterion. [SC-002](../044-shiraz-excel-parity-pdf/spec.md#measurable-outcomes) · [B05 findings](../../output/a1-requirements-2026-11-22-stage1-b05-qa-findings.md)

**Alternative considered** — Measure the synthetic employer fixture regardless of size. Treat those timings as descriptive if the fixture falls outside the specified range.
