# Stage 1.1 Discovery — Phase A.1 / B01

Date: 2026-11-19  
Scope: `specs/057-a1-b01-data-contract` only. B02–B06 are excluded from this fan-out.

## Discovery result

The next remaining delivery phase is A.1, “گزارش روزانه و خروجی‌ها”. The checked-in delivery plan lists the available Excel/PDF capability as implemented, while A.1.01–A.1.04 remain. The supplied workflow narrows this run to B01: the versioned daily-report data contract and the synthetic reference-day fixture. The B01 specification is clarified and ready for planning; it preserves C03–C08, uses synthetic fixture `SIM-A1-001`, and permits planning/implementation/internal verification under GOV-01 while employer representative and acceptance date remain a B06 handoff concern.

## Evidence inspected

- `apps/web/src/app/data/delivery-plan.ts:160-201`: A.1 dates, acceptance date, available export item, and remaining A.1.01–A.1.04 tasks.
- `output/delivery-plan-2026-11-03/schedule.json:246-321`: A.1 work, acceptance, inputs, owner, and four formal subtasks.
- `specs/057-a1-b01-data-contract/spec.md:11-231`: clarifications, six user stories, FR-001–FR-019, success criteria, assumptions, and C01–C10/GOV-01 register.
- `specs/057-a1-b01-data-contract/spec.md:235-289`: all 18 broader daily sections and B01 traceability/QA findings.
- `specs/057-a1-b01-data-contract/checklists/requirements.md`: all quality/readiness checks are marked complete; next gate is supervisor review then `/speckit-plan`.
- `output/a1-requirements-2026-11-18/remaining-work.md`: prior dependency-ordered A.1 backlog and acceptance boundaries.
- `output/a1-requirements-2026-11-19-stage-1.1.md` and `output/a1-requirements-2026-11-19-stage1-b01-qa-findings.md`: existing Stage 1 evidence and historical QA baseline.
- `graphify-out/graph.json`: queried for A.1/B01 context; graph results are locator evidence only, not proof of runtime behavior.

## B01 requirement fan-out

Each item below is an independent end-user QA unit for the downstream dynamic fan-out. Acceptance is contract-level and must not be inferred from source presence alone.

1. **B01-01 — Versioned contract and synthetic reference day** (`US1`, `FR-001`–`FR-004`, `SC-001`–`SC-003`): publish a reviewable versioned contract and clearly labelled `SIM-A1-001`, Solar Hijri `1406-03-01`, project day 12 fixture; map every required field to source, unit, conversion, null/zero rule, print/drill-down disposition, and revision history; handoff fields remain for B06.
2. **B01-02 — Governance and anti-fabrication** (`US2`, `FR-005`–`FR-008`, `GOV-01`, `C01`–`C10`): preserve source wording and provenance for decisions; distinguish observed behavior, ratified decisions, boundaries, and unresolved items; never fabricate missing dates, durations, weather, forecasts, or employer rulings.
3. **B01-03 — Zero, unset, and not-measured semantics** (`US3`, `FR-009`–`FR-010`, `C02`): accept measured zero, preserve unset/not-measured as unknown, prevent silent zero coercion across display/export/aggregation, and retain domain-specific positive-only validation where applicable.
4. **B01-04 — Shifts, actual duration, and labor metrics** (`US4`, `FR-011`–`FR-013`, `C03`): one report per project/local date; worked shifts only; canonical IDs 1/2/3 everywhere; person-hours from actual duration only; missing duration remains unknown; labels distinguish headcount, person-shifts, person-days, and person-hours in Persian and English.
5. **B01-05 — Job-title catalog and Shiraz profile** (`US5`, `FR-014`–`FR-015`, `C04`): keep the versioned configurable project catalog separate from the selectable 34/32 Shiraz presentation profile; preserve historical catalog entries; place extra/custom/historical titles in an appendix.
6. **B01-06 — Official header, weather, outputs, and boundaries** (`US6`, `FR-016`–`FR-019`, `C05`–`C08`, `X01`–`X10`): require single-day Excel/PDF, discipline Excel/PDF, and date-range multi-sheet Excel; derive official Solar Hijri report number and project day; source observed weather/wind/ground from logs and three-day forecast from MET Norway; show unknown when unavailable; describe attribution/fingerprint without claiming PKI; route non-A.1 ownership to named phases.

## Open gaps and evidence limits

- B01 contract readiness is documented, but implementation, generated exports, independent recalc/parity, browser UAT, and employer acceptance are not proven by this discovery step.
- Historical Stage 1.2 defects `DEF-B01-01`–`DEF-B01-06` are mapped in the updated spec; downstream QA must verify that the ratified contract is actually implemented rather than treating the old findings as closed.
- The live browser check of `http://localhost:5173/delivery-plan` could not be completed because the browser access host was unavailable. The checked-in TypeScript delivery plan and archived schedule were inspected instead.
- Do not fan out B02–B06 from this request. Their existence in prior audit files is context only.

## Gate recommendation

Route B01 to Supervisor re-review. If the Supervisor confirms the updated spec/checklist and the preserved decisions are sound, route to `/speckit-plan`; do not claim implementation or acceptance from this Stage 1 report.
