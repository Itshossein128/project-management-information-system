# Stage 1 Discovery — Phase A.1

Date: 2026-11-19  
Phase: A.1 — گزارش روزانه و خروجی‌ها (Daily Reports & Exports)

## Evidence and status boundary

- Source of truth: `apps/web/src/app/data/delivery-plan.ts:160-201`.
- Scheduled window: 2026-11-20 through 2026-11-27; acceptance date 2026-11-29.
- `A.1-available-1` (daily Excel/PDF export) is marked `implemented`.
- `A.1.01` through `A.1.04` are marked `remaining`.
- `schedule.json` was not present at the requested repository path, and `http://localhost:5173/delivery-plan` was not reachable during this pass (connection refused). The source block above is therefore the verified current plan evidence.
- Knowledge status reports a stale hybrid index (`indexed_commit=f41fc...`, current commit `63a95...`) because `docs/delivery/A1-requirements-and-delivery-audit.md` changed. The recorded embedding job is failed, not active; graphify queries were still run as locator evidence. Claims below are grounded in current files, not stale retrieval alone.

## Phase work packages for downstream QA fan-out

The existing audit defines the executable dependency order B01 → B02 → B03 → B04 → B05 → B06. Each item is a separate end-user QA handoff; a package is not considered accepted merely because focused tests pass.

### B01 — Data contract and reference-day fixture

Close the contract for the representative day: field-to-source mapping, null versus measured zero, shifts and duration, people/person-shift/person-hours, title/section ordering, one-day versus multi-sheet scope, and decisions C01–C08. Acceptance requires an independently mapped complete reference day and no material unresolved decision affecting the official output.

### B02 — Version integrity, derived locks, and preservation

Ensure correction versions retain aggregate identity, all child/source lineage, management opinion, permitted weather/site overrides, template/aggregation metadata, and history; derived rows remain read-only across UI, child, batch, and legacy paths; only the current approved version enters the official operational aggregate. Acceptance includes correction, cancellation, concurrent correction, unauthorized mutation, other-project, viewer, and historical-version scenarios.

### B03 — Reference-form parity

Reconcile real shift times, approved header fields, workforce ordering/catalogue, legacy unknown equipment hours (must not become zero), concrete/HSE fields, actor roles, timezone, Excel print layout, long Persian/English text, 50+ rows, PDF pagination, signatures, and draft watermark behavior against the agreed reference form.

### B04 — Filters, complete result set, and totals

Make discipline/contractor/block/date/status filters consistent across API, UI, URL, and Excel. Totals must use the full filtered queryset, preserve units and measured/unset semantics, and use the approved headcount meaning. Acceptance includes 51-row pagination, multiple units, unknown quantity, duplicate contractor names, shared URLs, refresh/back navigation, and stable totals across pages.

### B05 — Independent numeric, formula, and print reconciliation

Build expected values from independently controlled reference data, not the builder or aggregation engine. Recalculate Excel independently; compare Excel/PDF values, labels, formulas, layout, and print behavior; measure download time. Preserve mapping, checksums, screenshots, recalc logs, and every unresolved discrepancy.

### B06 — Delivery and initial employer acceptance bundle

Deliver one identifiable release/SHA with access path, roles, inputs/expected values, checksums, test guide, and acceptance scenarios. Test authorized/unauthorized and cross-project access, desktop/mobile, FA/EN, submitted versus approved source behavior, and fingerprint limits. Record explicit employer review and initial acceptance; automation alone is insufficient.

## Employer requirements and atomic stories

The audit’s `requirements-and-delivery.md` contains the normalized requirement register H01–H06, D01–D17, W01–W06, E01–E17, Q01–Q05, and X01–X10. `atomic-coverage.md` contains 42 atomic story headings, including US-DR-01..16, US-SR-01..04, US-AG-01..06, US-PR-01..07, US-DP-01..03, US-WH-01..02, and US-EX-01..02. The complete clause-level and story-level inventories are preserved in those files and must be used by downstream agents rather than inferred from package titles.

## Open decisions that block material acceptance

C01 raw versus derived daily input; C02 zero versus positive-only semantics; C03 shift identity and duration; C04 configurable catalogue versus 34/32 fixed form profiles; C05 one-day sheet versus historical multi-sheet workbook; C06 meaning and limits of “digital signature”; C07 independent PDF for specialty subreports; C08 real-form fields versus explicit contract list; C09 summary approval versus approval of every source; C10 communications/public reports remain owned by A.3.C/A.10. No unresolved decision should be silently replaced with a developer default.

## Delivery gaps observed

The audit records six independently reproduced defects: legacy unknown equipment hours becoming zero, historical/current approved versions being double-counted, activity totals aggregating only the current page, correction clones losing derived-source identity/locks, incomplete source preservation, and loss of management opinion/weather override. It also states that full real-day parity, independent Excel recalculation, browser UAT, production verification, and employer acceptance were not established by the audit snapshot.

## Handoff

Fan out one Per-Requirement End-User QA Agent for each B01–B06 package, using the clause/story registers linked above. Keep technical evidence, historical reproduction, missing evidence, proposed scope, and employer sign-off as distinct outcomes. Do not claim A.1 complete from the implemented export row or from automated tests alone.

## Related artifacts

- [Requirements and delivery audit](a1-requirements-2026-11-18/requirements-and-delivery.md)
- [Remaining work packages](a1-requirements-2026-11-18/remaining-work.md)
- [Atomic story coverage](a1-requirements-2026-11-18/atomic-coverage.md)
- [Scope decisions](a1-requirements-2026-11-18/scope-decisions.md)
- [Speckit prompts](a1-requirements-2026-11-18/speckit-prompts/README.md)
