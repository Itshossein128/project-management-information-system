# Contract: Reporting Configuration Catalog API (feature 033)

Base URL (established by feature 032): `/api/v1/projects/{project_pk}/reporting-configuration/…` — the effective-dated activation surface. Catalog administration lives on project templates (`/api/v1/…/project-templates/{pk}/…`) during the draft phase; activation snapshots are read-only.

## 1. Labor-title catalog (draft template)

- `GET/POST/PUT …/project-templates/{pk}/labor-catalogs/` — list/create versions within a draft template: `version_name`, `notes`, `titles[]`.
- `…/labor-catalogs/{id}/titles/` — CRUD: `title_code` (stable, language-independent), `title_label_fa` / `title_label_en`, `category` (`indirect`/`direct`), `display_order`, `active`, `legacy_alias`, `project_specific`.

Rules: one catalog active per template draft; retitling a legacy alias records the migration (alias retained for history; FR-011); `display_order` unique within (catalog, category); no automatic title-count constants exposed anywhere.

## 2. Effective snapshot (read-only)

- `GET …/reporting-configuration/current?date=D` (and `…/by-date/{date}/`) — returns the effective `ProjectReportingConfiguration` for the date including:
  - `required_units[]` (032),
  - `labor_titles[]`: `title_code`, labels, `category`, `display_order`, `legacy_alias`, `source_catalog_version`,
  - `man_hours_rule`: `{ "rule_code": "standard_shift_plus_overtime", "parameters": { "standard_shift_hours": 8 } }`,
  - `stoppage_reasons[]`: `reason_code` + localized labels,
  - `activated_at`, `effective_from`, `supersedes` chain.
- Activation/preview endpoints from 032 (`activate`, `preview`) extended to include the new snapshot pieces; the preview shows the exact catalog/rule/vocabulary that would become effective, per 032 Constitution IV (safe mutations).

## 3. Resolution semantics shared by validators

- Title resolution order: legacy alias → exact `title_label` (locale-independent match against stored labels) → project-specific alias set. Unresolved → `unknown_job_title` (save/submit rejected).
- Vocabulary check: machinery stoppage reason codes must exist in the effective snapshot's `stoppage_reasons`.
- Man-hours: computed by aggregation from `man_hours_rule` only; identical inputs always produce identical outputs (FR-008); the registry contains only code-reviewed rule implementations.
- Historical rows: rows recorded under a superseded snapshot keep their original title evidence; current entries must use the effective snapshot (spec edge case).

## 4. Permissions

- Catalog administration: project-template-management permission (server-enforced; draft-only editability, per Constitution IV).
- Snapshot reads: any authenticated project member with unit-report view permission (editors need these to render controlled choices and totals).
- Every lookup is project-scoped; template ids from other projects resolve nothing.

Related: [unit-report-sections-api.md](./unit-report-sections-api.md), [daily-summary-sections-api.md](./daily-summary-sections-api.md).
