# Stage 1.1 Discovery & Inspection — Phase A.1

Date: 2026-11-22
Original request: `Go for the next step to deliver the application, based on A.1 phase in http://localhost:5173/delivery-plan`

## Evidence boundary
- `python3 scripts/knowledge/cli.py context ...` was attempted after checking freshness. The hybrid index reported stale uncommitted content; `index --semantic` then failed with embedding HTTP 400. Knowledge context is therefore historical/unavailable for this run and is not treated as proof.
- `graphify query` ran against `graphify-out/graph.json` and located A.1, B01–B06, daily-report specifications, and prior audits. `graphify explain` and `graphify path` were also attempted; ambiguous node names were not used as behavioral proof.
- Unauthenticated inspection of `http://localhost:5173/delivery-plan` redirects to `/login?redirectTo=%2Fdelivery-plan`; authenticated end-user UAT is not claimed.

## Delivery-plan reconciliation
Source: `apps/web/src/app/data/delivery-plan.ts:160-201`.
- Phase `A.1` — `گزارش روزانه و خروجی‌ها` — scheduled 2026-11-20 through 2026-11-27; planned acceptance 2026-11-29.
- `A.1-available-1` — `خروجی Excel و PDF گزارش روزانه` — marked `implemented`; this is not final acceptance.
- Remaining items: `A.1.01` rules/fixture, `A.1.02` full reference-day reconciliation, `A.1.03` proven output discrepancy fixes, and `A.1.04` final sample/walkthrough/initial approval.
- `output/delivery-plan-2026-11-03/schedule.json:246-321` defines the same scope as a complete representative day, independently reconciled Excel/PDF, correction of proven discrepancies, and download/walkthrough/initial approval. Full report-domain closure is deferred to A.10.

## Dynamic fan-out packages
The downstream Per-Requirement End-User QA Agent should run one unit for each package and execute every linked atomic story and acceptance criterion. Static source presence is not acceptance.

### B01 — Data contract and reference-day fixture
Acceptance: map every required field to source, unit, conversion, null/zero rule, output disposition, and revision/provenance; provide an executable labelled reference-day fixture and resolve C01–C08 decisions affecting official output. Gaps: missing `SIM-A1-001`, versioned contract, report/project-day identifiers, shift/duration mismatches, silent eight-hour substitution, labor metric ambiguity, and hardcoded role catalogs. Status: not accepted.

### B02 — Version integrity, derived locks, and preservation
Acceptance: correction, cancellation, concurrency, unauthorized mutation, lineage, source preservation, reviewer/weather preservation, and approved-current aggregation pass. Hard dependency of B05/B06. Status: open.

### B03 — Reference-form parity
Acceptance: Excel/PDF values, fields, labels, roles, unknown semantics, long text, pagination, printing, timezone, and watermark match the agreed reference form. Open gaps include layout/header/shift-print and zero-versus-unknown semantics.

### B04 — Filters, complete result set, and totals
Acceptance: API, UI, URL, Excel, pagination, and totals represent one complete filtered queryset with correct units and unset semantics, including date/status, discipline, contractor, block and activity dimensions. Existing QA reports page-only totals, missing whole-queryset activity-log aggregation, and missing discipline/block/contractor filters. Status: `qa_failed`.

### B05 — Independent numeric, formula, and print reconciliation
Acceptance: independent expected values, recalculation logs/oracle, mapping, checksums, screenshots, discrepancy decisions, and measured typical-download time prove Excel/PDF parity. Existing QA reports absent cached formula values, independent recalc, download benchmark, and page-by-page visual comparison. Depends on B02–B04; status: `qa_failed`.

### B06 — Delivery and initial employer acceptance bundle
Acceptance: fixed release/SHA, guide, input and expected-value fixture, checksums, role/device/language/cross-project tests, walkthrough, and explicit employer review/sign-off are recorded. Frozen package and sign-off are absent; live cross-project isolation and bilingual/mobile evidence are unverified. Depends on B01–B05; status: `qa_failed`.

## Full atomic user-story inventory
Source: `output/a1-requirements-2026-11-18/atomic-stories.json` and `requirements-and-delivery.md`.
- Daily report: `US-DR-01` weather/temperature; `US-DR-02` shifts/operations; `US-DR-03` unique current report; `US-DR-04` WBS activities; `US-DR-05` labor; `US-DR-06` equipment; `US-DR-07` materials/warehouse reconciliation; `US-DR-08` concrete logs; `US-DR-09` incidents/work orders/stoppages; `US-DR-10` field images/documents; `US-DR-11` approval/rejection; `US-DR-12` immutability; `US-DR-13` correction/version lineage; `US-DR-14` zero versus unset; `US-DR-15` offline rows/client UUID; `US-DR-16` batch sync/conflicts.
- Specialized/aggregation: `US-SR-01` civil; `US-SR-02` electrical; `US-SR-03` mechanical/plumbing/HVAC; `US-SR-04` subreport validation/workflow; `US-AG-01` `by-date` access; `US-AG-02` auto-rollup; `US-AG-03` derived-row locks; `US-AG-04` weather override; `US-AG-05` missing-disciplines banner; `US-AG-06` live `ACTIVITY` log.
- Progress/reporting: `US-PR-01` physical measurement; `US-PR-02` four-way progress; `US-PR-03` 100% ceiling/technical approval; `US-PR-04` weekly report; `US-PR-05` monthly status; `US-PR-06` figure provenance; `US-PR-07` controlled override.
- Department/warehouse: `US-DP-01` department daily Excel; `US-DP-02` department weekly Excel; `US-DP-03` department batch Excel; `US-WH-01` eight-field warehouse movement; `US-WH-02` warehouse reports/balance.
- Exports: `US-EX-01` FILE 4 parity; `US-EX-02` FILE 5/6 parity; `US-EX-03` official print/PDF/signatures; `US-EX-04` multidimensional filters.

## Employer-facing requirement register
The source register contains H01–H06 (identity/weather/operations/uniqueness), D01–D17 (daily sections and semantics), W01–W06 (workflow/version/lineage/locks), E01–E17 (Excel/PDF, permissions and filters), Q01–Q05 (reference day, speed, browser/language/device, guide and acceptance bundle), and X01–X10 (offline, specialist/progress/periodic/department/warehouse/migration/deployment handoffs). Complete wording and line-level traceability remain in `output/a1-requirements-2026-11-18/requirements-and-delivery.md:47-901` and `source-clauses.md`.

## Consolidated gap decision
A.1 is not ready for implementation completion or employer acceptance. The next safe action is requirement-level end-user QA fan-out for B01–B06 in dependency order `B01 → B02 → B03 → B04 → B05 → B06`. Do not promote `implemented` export status to accepted without live authenticated verification, independent numeric/formula reconciliation, and the frozen delivery/sign-off bundle.
