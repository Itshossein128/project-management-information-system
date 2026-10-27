# Verification report — feature 033 remaining stories

Date: 2026-10-25

## What was implemented

- Concrete pour validation (`volume_must_be_positive`, sampling test information, foreign batching-plant reference) and idempotent linkage to `risk.Inspection`.
- Structured narrative validation and aggregation for issues, barriers, visits, HSE incidents, and general activities, including markup stripping and HSE notifications.
- Activity image attachment checks (hostile ZIP/EXE signatures, 10 MB limit, version and project scope) with a local storage key when MinIO is not configured.
- Aggregation fingerprint coverage for the new section families, ordered derived rows, and `GET …/provenance/{derived_kind}/{derived_row}/`.
- Unit-panel editors for concrete, general activities, issues, visits, and HSE, plus summary provenance and attachment-count components. Persian and English strings were added together.
- The daily-summary serializer now returns complete concrete fields (including sampling/test/QC-link information), ordered structured general/issue/visit/HSE rows, and per-section attachment counts. Attachment links are emitted only for an authorized project member and point to the permission-checked source attachment collection; storage keys are never exposed.
- The activity editor now provides JPEG/PNG attachment upload feedback and client-side type/size prechecks. It deliberately presents no attachment gallery or object-store URL.

## Evidence (2026-10-25)

All backend commands used the isolated `ipcas_h033` PostgreSQL database on port 5433 (`DATABASE_URL` was rewritten only for the command); the shared `test_ipcas` database was not used.

| Check | Result | What it proves |
|---|---:|---|
| `pnpm typecheck` | PASS | `react-router typegen && tsc` completed with no TypeScript errors. |
| `manage.py makemigrations --check --dry-run` | PASS | No model migration drift. Django emitted only the known `django_ratelimit.W001` Redis-cache support warning. |
| Concrete/narrative/attachment + summary-contract pytest selection | PASS — 56 passed in 3.68s | Concrete, structured narrative, attachment validation/authorization, serializer payload, and summary attachment-count behavior on PostgreSQL. |
| Aggregation pytest selection | PASS — 44 passed in 5.74s | Eligibility, provenance, completeness, idempotency, machinery dedupe, receipt-only rules, structured transfer, and attachment-count aggregation. |

The new serializer regression assertions specifically prove that a serialized summary has ordered general activities, issues/barriers, visits, HSE severity/notification data, and a count-only attachment payload when no request user is supplied.

## Boundaries

- This run does not prove browser behavior. Neither API (`:8000`) nor web (`:5173`) was running, so the required bilingual Playwright `daily-sections` path was not created or executed in this pass.
- MinIO and RabbitMQ are not part of this local run. Attachment tests prove refusal, metadata persistence, counts, and permission gating—not object-store retrieval, preview delivery, or a successful MinIO upload.
- The broad cross-domain suite requested by T061 (`sub_reports field_reports project_templates inventory risk -x`) was not run; the two focused feature selections above are the actual backend evidence.
- Usability criteria that need a person using the product are not claimed.

## Evidence update (2026-10-26)

| Check | Result | Notes |
|---|---|---|
| Section contract pytest (quickstart §1) | PASS — 91 passed | Includes `test_section_contracts`, labor/machinery/materials/concrete/narrative, plus aggregation eligibility, machinery derivation, receipts-only, structured transfer (`--reuse-db`). |
| US8 idempotency pytest | PASS — 8 passed | `test_unit_report_rebuild_idempotency.py` including mid-rebuild atomicity and machinery-only rejection slice (`--reuse-db`). |
| Playwright `daily-sections` | Added | `apps/web/e2e/tests/daily-sections-aggregation.spec.ts` (six tagged scenarios). Run via quickstart §5 with API + web `webServer` config. |
| T061 full cross-domain `-x` sweep | Deferred | Run locally when `test_ipcas` is not contended by parallel sessions. |

## Evidence update — Phase 13 Convergence (2026-10-27)

### Phase 13 Tasks Completed:
- **T070 (CRITICAL)**: Normalized TanStack Query cache key `["project-contractors", projectId]` handling across `ContractorSelect.tsx`, `section-activities.tsx`, and `section-labor.tsx` using `asList()`, eliminating cache-collision crashes. Executed Playwright E2E suite `daily-sections-aggregation.spec.ts` with all 6 mandated scenarios passing in bilingual modes (`6 passed in 48.2s`).
- **T071 (HIGH)**: Implemented machinery type-level presentation rows with per-declared-identity hour and status summing in aggregation (`daily_report_aggregation.py`) and serializer summary (`DailyReportDetailSerializer.get_machinery`).
- **T072 (HIGH)**: Created migration `0005_seed_default_labor_catalogs.py` and seed helper `labor_catalog_seeds.py` establishing standard (0002) and Shiraz (0010) labor catalogs with legacy alias resolution, ensuring fresh projects resolve labor titles seamlessly.
- **T073 (HIGH)**: Enforced per-source unit-report view permission in provenance drill-down (`daily_report_views.py:provenance`), masking confidential source metadata when `view_reports` is absent.
- **T074 (MEDIUM)**: Added `catalog_rule_code` and `machinery_vocabulary_revision` to aggregation fingerprint, and implemented `@property def snapshot_revision_marker` on `ProjectReportingConfiguration`.

| Check | Result | Details |
|---|---|---|
| Frontend TypeScript Typecheck (`pnpm typecheck`) | PASS | `react-router typegen && tsc` completed with zero errors (code 0). |
| Playwright E2E Suite (`daily-sections-aggregation.spec.ts`) | PASS — 6/6 passed in 48.2s | All 6 scenarios verified green against live API (:8000) and Web (:5173):<br>1. Executed activity appears in summary with provenance<br>2. Cross-project activity reference is rejected<br>3. Invalid quantity shows localized validation<br>4. Summary structured sections render after rebuild<br>5. Bilingual labels on unit section tabs (`fa` & `en`)<br>6. Correction removes unit contribution until resubmit |
| Feature Backend Pytest Suite (quickstart §1 & §2) | PASS — 113/113 passed in 97.88s | 13 test modules covering section contracts, labor catalogs, machinery contracts & derivation, materials receipts & details, concrete QC links, structured narratives, eligibility, completeness, rebuild idempotency, and provenance drill-down permissions. |
| Django Model Migrations (`makemigrations --check --dry-run`) | PASS | Clean migration tree, no unapplied model drift. |
