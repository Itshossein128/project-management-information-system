# Implementation Plan: Warehouse Department Reports

**Branch**: `043-warehouse-department-reports` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/043-warehouse-department-reports/spec.md`

## Summary

Implement comprehensive warehouse reporting and inventory balance management for the construction site warehouse department (`department="warehouse"`). This includes:
1. Validating that at least one of `quantity_in` or `quantity_out` is strictly positive, returning the structured error code `at_least_one_quantity_must_be_positive` with the Persian message «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد».
2. Upgrading the 8th worksheet in the weekly activity report to a native "Cumulative Material Balance Sheet" («بالانس تجمعی مصالح») aggregated by `(material_type, unit)` with dynamic opening balance computation before `week_start`, total inbound, total outbound, and native Excel formulas `=D{row}+E{row}-F{row}`.
3. Enhancing the daily warehouse report to Shiraz site standards with official Persian banners and a two-tiered footer including a native Net Daily Balance formula (`=Total_In - Total_Out`).
4. Creating a real-time HTTP GET endpoint `/api/v1/projects/{project_pk}/department-activity-records/warehouse-balance/` with `as_of_date` and `search` filters protected by `view_reports`.
5. Enhancing the web UI with standard number formatting (thousands separators), explicit warehouse export action labels, and capturing server validation error codes.
6. Synchronizing the state machine in `docs/decision-tree/`.

## Technical Context

**Language/Version**: Python 3.12 (Django 4.2.11 + DRF 3.14), TypeScript 5.8+ (React Router 7, Vite)  
**Primary Dependencies**: `openpyxl>=3.1.2`, `django-rest-framework`, `lucide-react`, `tailwindcss`  
**Storage**: PostgreSQL (blueprint schema, UUID project PKs), Redis (cache & session rate limiting)  
**Testing**: `pytest`, `pytest-django`, `pytest-cov` for backend; `react-router typegen && tsc` for frontend  
**Target Platform**: Web application (Linux container / cloud VM / modern browsers)  
**Project Type**: Monorepo with Django REST API (`apps/api`) and React SPA (`apps/web`)  
**Performance Goals**: Warehouse balance queries for projects with 5,000+ movement records resolve in < 500ms; Excel reports generate in < 1.5s  
**Constraints**: Pinned Django 4.2.11 boundary; native Excel formula syntax; Persian RTL spreadsheet alignment; no Celery/RabbitMQ dependencies for core reporting  
**Scale/Scope**: Multi-tenant projects, warehouse department records, hundreds of material types per project  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Server-Enforced Authorization and Tenant/Project Isolation**  
  *PASS*: All endpoints (`warehouse-balance`, daily report, weekly report) verify project membership (`IsProjectMember`) and check `view_reports` permission (`HasProjectPermission`, `CanViewBusinessAssignments`). Project scoping is strictly enforced via `project_id=project_pk`.
- **Principle II: Data Integrity and End-to-End Domain Consistency**  
  *PASS*: Material movements use standard 8-fields; dynamic opening balances account for all prior movements without caching stale aggregates. Grouping is strictly by `(material_type, unit)`.
- **Principle III: Bilingual and Locale-Correct Experience**  
  *PASS*: Excel reports use official Persian titles, Jalali dates, and RTL formatting. Validation errors provide the approved Persian text alongside stable machine-readable codes.
- **Principle IV: Explicit, Safe Business Mutations**  
  *PASS*: Mutations validate positive quantities; Excel batch imports validate rows atomically or report exact line errors with structured codes.
- **Principle V: Minimal Coherent Changes**  
  *PASS*: Builds upon existing `DepartmentActivityRecord` model, serializers, and `department_activity_io.py` Excel engine without creating duplicate models or parallel report generators.
- **Principle VI: Evidence-Based Verification**  
  *PASS*: Verified via `pytest` backend tests and `pnpm --filter web build`.
- **Principle VII: Accessible, Practical Construction-Management UX**  
  *PASS*: Thousands separators for large inventory figures, clear action buttons disambiguating daily Shiraz format and weekly 8-sheet balance workbooks.

## Project Structure

### Documentation (this feature)

```text
specs/043-warehouse-department-reports/
├── plan.md              # Implementation plan
├── research.md          # Technology decisions & formula specifications
├── data-model.md        # Entities, queries, and calculation models
├── quickstart.md        # Verification and testing guide
├── contracts/           # OpenAPI specs for balance & report endpoints
│   ├── warehouse-balance.openapi.yaml
│   └── warehouse-reports.openapi.yaml
└── tasks.md             # Task breakdown (speckit-tasks)
```

### Source Code Locations

```text
apps/api/core/
├── inventory/
│   ├── department_activity_data_views.py  # Report views + WarehouseBalanceView
│   ├── department_activity_io.py          # Daily & Weekly Excel report generation
│   ├── project_urls.py                    # Project URL routes (warehouse-balance/)
│   ├── serializers.py                     # CodedValidationError for positive quantities
│   └── tests.py                           # Tests for validation, reports & balance
apps/web/src/
├── app/
│   ├── hooks/queries.ts                   # React Query hooks for warehouse balance
│   └── lib/api-client.ts                  # API client
├── components/
│   └── department/
│       ├── department-page.tsx            # Formats, buttons & table display
│       └── department-activity-record-modal.tsx # Validation error display
docs/decision-tree/
└── login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/
    ├── README.md
    ├── download-daily-activity-report/README.md
    ├── download-weekly-activity-report/README.md
    ├── [create-activity-record]/README.md
    └── [query-warehouse-balance]/README.md
```

## Architecture Decisions & Component Diagrams

```
                       User Action (UI / API)
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
[Record Mutation]       [Download Reports]         [Warehouse Balance]
(POST / PUT / Import)   (Daily / Weekly XLSX)      (GET warehouse-balance/)
     │                           │                           │
     ▼                           ▼                           ▼
CodedValidationError    department_activity_io     WarehouseBalanceView
- code: at_least_one_   - Daily: Shiraz Banner &   - Filters: date__lte,
  quantity_must_be_       Net Daily Balance          search icontains
  positive              - Weekly Sheet 8:          - Aggregates by
- Persian Message         * Group by (mat, unit)     (material_type, unit)
                          * Dynamic Opening Stock  - Returns: total_in,
                          * Formula: =D+E-F          total_out, current_bal
```

## Test Strategy

1. **Unit Tests (Serializers & Validation)**:
   - Submit record with `quantity_in=0, quantity_out=0` $\rightarrow$ Expect HTTP 400, `error.code == 'at_least_one_quantity_must_be_positive'`, Persian message.
   - Submit record with negative quantities $\rightarrow$ Expect HTTP 400.
   - Submit valid records $\rightarrow$ Expect HTTP 201.
2. **Integration Tests (Excel Generation)**:
   - Generate daily report $\rightarrow$ Verify sheet title, headers, Tier 1 sum formulas, and Tier 2 net balance formula `=D{tot}-F{tot}`.
   - Generate weekly report with prior history $\rightarrow$ Verify Sheet 8 exists with title «بالانس تجمعی مصالح», correct opening balances, closing formula `=D{r}+E{r}-F{r}`, and column `=SUM(...)` totals.
   - Verify material with prior balance but no current week records appears in Sheet 8.
3. **API Endpoint Tests (Warehouse Balance)**:
   - Verify `GET /api/v1/projects/{project_pk}/department-activity-records/warehouse-balance/` returns 200 with correct balances.
   - Verify `as_of_date` and `search` query parameter filtering.
   - Verify 403 Forbidden for non-members or lack of `view_reports`.
4. **Frontend Verification**:
   - `pnpm --filter web build` compiles cleanly with zero TypeScript errors.

## Complexity Tracking

No constitution violations detected. Standard DRF and React architecture followed.
