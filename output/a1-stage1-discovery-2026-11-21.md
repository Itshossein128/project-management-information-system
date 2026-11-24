# Stage 1.1 Discovery — Velora Phase A.1

Date: 2026-11-21

Original request: `continue developing this application based on A.1 gaps and check finished ones in http://localhost:5173/delivery-plan`

## Evidence boundary

The knowledge index was refreshed with `python3 scripts/knowledge/cli.py index --semantic`; the requested context query completed with a fresh hybrid index. Graphify queried the existing `graphify-out/graph.json` for A.1 daily reports/exports and identified the prior A.1 audit, the six B01–B06 work packages, and the daily-report specifications.

The shell probe to `http://localhost:5173/delivery-plan` returned `302 /login?redirectTo=%2Fdelivery-plan`. Browser automation was unavailable, so authenticated browser/UAT status is not claimed.

## Delivery-plan reconciliation

Source: `apps/web/src/app/data/delivery-plan.ts:160-199`.

- Phase `A.1` is `گزارش روزانه و خروجی‌ها`, scheduled 2026-11-20 through 2026-11-27, with planned acceptance on 2026-11-29.
- `A.1-available-1` — `خروجی Excel و PDF گزارش روزانه` — is marked `implemented`. This is implementation status only, not final acceptance.
- `A.1.01` — `نهایی‌کردن قواعد اطلاعات روزانه` — remains.
- `A.1.02` — `تطبیق تمام بخش‌های گزارش با روز مرجع` — remains.
- `A.1.03` — `رفع اختلاف ارقام و نمایش خروجی‌ها` — remains.
- `A.1.04` — `ارائه نمونه نهایی و تأیید اولیه گزارش` — remains.

The schedule source (`output/delivery-plan-2026-11-03/schedule.json:246-318`) describes the same phase as “تطبیق و تحویل اولیه گزارش روزانه”: a complete representative day, independently reconciled Excel/PDF, correction of proven output discrepancies, and download/walkthrough/initial approval. Full report-domain closure is deferred to A.10.

## Fan-out requirements

These six requirement-level work packages are the downstream Per-Requirement End-User QA inputs. The existing audit contains the linked atomic H/D/W/E/Q/X register and subordinate B01 stories.

### B01 — Data contract and reference-day fixture

Acceptance: independently map every required field and the complete reference day; resolve C01–C08 decisions affecting official output. Evidence: `output/a1-requirements-2026-11-19-stage1-b01-01-qa-findings.md` through `...-b01-06-qa-findings.md`. Open examples include the missing executable `SIM-A1-001` fixture/seed, missing versioned field-to-output contract, absent report/project-day identifiers, shift/duration mismatches, silent eight-hour substitution, mislabelled labor metrics, and hardcoded Shiraz role catalogs. B01 is not accepted.

### B02 — Version integrity, derived locks, and preservation

Acceptance: correction, cancellation, concurrency, unauthorized mutation, lineage, source preservation, and approved-current aggregation pass end-user scenarios. Evidence: `output/a1-requirements-2026-11-19-stage1-b02-qa-findings.md`. The package remains open and is a hard dependency of B05/B06.

### B03 — Reference-form parity

Acceptance: Excel/PDF values, fields, labels, roles, unknown semantics, long text, pagination, printing, timezone, and watermark match the agreed reference form. Evidence: `output/a1-requirements-2026-11-19-stage1-b03-qa-findings.md`. Reported open defects include layout/header/shift-print/zero-versus-unknown and reference-form parity gaps.

### B04 — Filters, complete result set, and totals

Acceptance: API, UI, URL, Excel, pagination, and totals represent one complete filtered queryset with correct units and unset semantics. Evidence: `output/a1-requirements-2026-11-19-stage1-b04-qa-findings.md`. QA reports no whole-queryset activity-log aggregation, page-only UI totals, and missing discipline/block/contractor filters. Status: `qa_failed`.

### B05 — Independent numeric, formula, and print reconciliation

Acceptance: independent expected values, recalculation logs, mapping, checksums, screenshots, discrepancy decisions, and measured download time prove Excel/PDF parity. Evidence: `output/a1-requirements-2026-11-19-stage1-b05-qa-findings.md`. QA reports absent formula cached values, no independent recalc/oracle, no measured typical-download benchmark, and no page-by-page visual comparison. Status: `qa_failed`; depends on B02–B04.

### B06 — Delivery and initial employer acceptance bundle

Acceptance: fixed release/SHA, guide, inputs/expected values, checksums, role/device/language/cross-project tests, and explicit employer review are recorded. Evidence: `output/a1-requirements-2026-11-19-stage1-b06-qa-findings.md`. The frozen release/checksum package and explicit employer sign-off are absent; live cross-project isolation and bilingual/mobile evidence are unverified. Status: `qa_failed`; blocked by B01–B05.

## Consolidated conclusion

The only A.1 item represented as implemented in the delivery-plan snapshot is export capability. Remaining work requires contract/fixture closure, version-safe correction and lineage, reference-form parity, complete filtered totals, independent Excel/PDF reconciliation, and a frozen delivery plus employer-review record. No requirement should be promoted to accepted from the static plan alone.

## Source index

- `apps/web/src/app/data/delivery-plan.ts:160-199`
- `output/delivery-plan-2026-11-03/schedule.json:246-318`
- `output/a1-stage1-discovery-2026-11-19.json`
- `output/a1-requirements-2026-11-18/requirements-and-delivery.md`
- `output/a1-requirements-2026-11-18/source-clauses.md`
- `output/a1-requirements-2026-11-19-stage1-b01-01-qa-findings.md` through `...-b06-qa-findings.md`
- `docs/delivery/delivery-plan-status-review-2026-11-11.md:1-6`

```json
{"phase":"A.1","requirements":[{"id":"B01","title":"Data contract and reference-day fixture","acceptance":"Independently map every required field and complete reference day; resolve C01-C08 decisions affecting official output.","status":"open"},{"id":"B02","title":"Version integrity, derived locks, and preservation","acceptance":"Correction, cancellation, concurrency, unauthorized mutation, lineage, source preservation, and approved-current aggregation pass end-user scenarios.","status":"open"},{"id":"B03","title":"Reference-form parity","acceptance":"Excel/PDF values, fields, labels, roles, unknown semantics, long text, pagination, printing, timezone, and watermark match the agreed reference form.","status":"open"},{"id":"B04","title":"Filters, complete result set, and totals","acceptance":"API, UI, URL, Excel, pagination, and totals represent one complete filtered queryset with correct units and unset semantics.","status":"qa_failed"},{"id":"B05","title":"Independent numeric, formula, and print reconciliation","acceptance":"Independent expected values, recalculation logs, mapping, checksums, screenshots, discrepancy decisions, and measured download time prove Excel/PDF parity.","status":"qa_failed"},{"id":"B06","title":"Delivery and initial employer acceptance bundle","acceptance":"Fixed release/SHA, guide, inputs/expected values, checksums, role/device/language/cross-project tests, and explicit employer review are recorded.","status":"qa_failed"}],"summary":"A.1 is the active next delivery phase. The plan marks daily Excel/PDF export implemented, while A.1.01-A.1.04 remain. Six downstream QA work packages B01-B06 cover the unresolved contract, lineage, parity, totals, independent reconciliation, and acceptance gaps; authenticated browser UAT and employer sign-off are unverified."}
```
