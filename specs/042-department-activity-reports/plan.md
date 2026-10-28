# Implementation Plan: Department Activity Reports & Excel Workbooks

**Branch**: `042-department-activity-reports` | **Date**: 2026-10-28 | **Spec**: [specs/042-department-activity-reports/spec.md](file:///home/hossein/Desktop/projects/building-management/specs/042-department-activity-reports/spec.md)

**Input**: Feature specification from `specs/042-department-activity-reports/spec.md` and `reports_gaps/09/GAP-SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md`.

## Summary

This feature resolves all critical architectural gaps in the 5 workshop department activity records (Civil/Buildings, Electrical, Mechanical, Machinery, Warehouse) by:
1. Adding the missing `executed_quantity` decimal field to `DepartmentActivityRecord` for non-warehouse departments.
2. Supporting `civil` and `buildings` department slugs interchangeably across views, serializers, and queries.
3. Replacing PDF generation with official Office Open XML (`.xlsx`) workbooks for single-day reports with project title headers, Persian RTL layout, and dynamic `=SUM(...)` formulas for total executed quantities.
4. Providing 8-sheet weekly `.xlsx` reports (7 daily sheets Saturday through Friday + 1 Summary sheet) with native `=SUM(...)` formula rollups.
5. Upgrading the filtered export to RTL format with standardized Persian column headers and executed quantities.
6. Rewriting batch import to execute inside `@transaction.atomic` for all-or-nothing rollback, validating numeric `executed_quantity`, contractor bindings, and returning structured Persian error diagnostics (`خطا در سطر ۴...`).
7. Elevating batch import permission to require `edit_reports`.
8. Updating frontend modals, date selectors, and import error alerts.

## Technical Context

**Language/Version**: Python 3.12 (Django 4.2.11 backend) & TypeScript / React Router 7 + Vite frontend  
**Primary Dependencies**: `openpyxl==3.1.5`, `djangorestframework`, `react`, `lucide-react`, `tailwindcss`  
**Storage**: PostgreSQL 16 (port 5433) + Redis  
**Testing**: `pytest`, `pytest-django`, `pnpm --filter web build`  
**Target Platform**: Web application (Linux server, modern desktop browser)  
**Project Type**: Monorepo (`apps/api` Django backend + `apps/web` React frontend)  
**Performance Goals**: Generate and stream 1,000-record Excel reports in < 3 seconds; validate batch imports in < 5 seconds  
**Constraints**: All generated Excel files must be valid Office Open XML (.xlsx) with RTL alignment and Persian font typography; strict all-or-nothing atomic import rollback; permission isolation  
**Scale/Scope**: 5 workshop departments across all active projects  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Server-Enforced Authorization & Isolation**: All endpoints verify project membership and specific permission (`view_reports` for reads/exports, `edit_reports` for batch imports).
- [x] **II. Data Integrity & Domain Consistency**: `executed_quantity` added with safe default and backward compatibility. Atomic transaction guarantees zero partial writes on batch upload failures.
- [x] **III. Bilingual & Locale-Correct Experience**: All Excel workbooks configured with RTL sheet direction, Persian headers, and Persian error diagnostics.
- [x] **IV. Explicit, Safe Business Mutations**: Batch import strictly rolls back entire transaction if any single row contains validation errors.
- [x] **V. Minimal Coherent Changes**: Builds directly upon existing `DepartmentActivityRecord` infrastructure without creating parallel models or dead code.
- [x] **VI. Evidence-Based Verification**: Validated with pytest unit/integration tests and `pnpm --filter web build`.
- [x] **VII. Accessible Construction UX**: Accessible date selectors and clear row-level Persian diagnostics.

## Project Structure

### Documentation (this feature)

```text
specs/042-department-activity-reports/
├── plan.md              # This file
├── research.md          # Technical analysis, openpyxl, RTL, formulas
├── data-model.md        # Model additions, schema, aliases, import rules
├── quickstart.md        # Developer setup, commands, curl verification
├── contracts/           # OpenAPI contracts
│   ├── daily-report.contract.yaml
│   ├── weekly-report.contract.yaml
│   ├── export.contract.yaml
│   └── import.contract.yaml
└── tasks.md             # Implementation tasks
```

### Source Code

```text
apps/api/core/
├── inventory/
│   ├── models.py                     # DepartmentActivityRecord + executed_quantity + alias
│   ├── serializers.py                # DepartmentActivityRecordSerializer + executed_quantity
│   ├── department_activity_services.py # Slug normalization, date calculations
│   ├── department_activity_io.py     # openpyxl daily/weekly report, RTL export, atomic import
│   ├── department_activity_data_views.py # Daily/weekly report views, export/import views
│   ├── views.py                      # ViewSet slug normalization & filtering
│   └── tests.py                      # Pytest automated test coverage
└── sub_reports/
    └── models.py                     # Re-export / alias DepartmentActivityRecord if needed

apps/web/src/
├── app/
│   └── lib/
│       └── api-types.ts              # DepartmentSlug ('civil'), executed_quantity
├── components/
│   └── department/
│       ├── department-page.tsx       # Date pickers for reports, XLSX downloads, atomic import
│       └── department-activity-record-modal.tsx # executed_quantity input field
```

## Test Strategy

1. **Model & Migration Tests**: Verify `executed_quantity` field exists, defaults to 0.000, and persists decimals correctly.
2. **Slug Normalization Tests**: Verify `department=civil` and `department=buildings` return identical results with HTTP 200.
3. **Daily Excel Report Tests**: Request `.../reports/daily/?department=civil&date=2026-10-17`, load generated `.xlsx` with openpyxl, verify RTL is True, header block matches project name, and total cell contains `=SUM(...)`.
4. **Weekly Multi-Sheet Excel Tests**: Request `.../reports/weekly/?department=mechanical&week_start=2026-10-17`, verify exactly 8 worksheets, Persian weekday titles, and active `=SUM(...)` formulas.
5. **RTL Filtered Export Tests**: Verify generated export `.xlsx` has RTL enabled and Persian headers.
6. **Atomic Batch Import Tests**:
   - Upload file with valid rows: all rows committed, HTTP 200 returned.
   - Upload file with error on row 4: 0 rows committed (rollback verified), HTTP 400 returned with `خطا در سطر ۴...`.
7. **Permission Elevation Tests**: User with only `view_reports` gets HTTP 403 on import endpoint. User with `edit_reports` succeeds.
8. **Frontend Build**: Verify `pnpm --filter web build` passes with zero errors.
