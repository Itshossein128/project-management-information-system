# Verification: Contractor Stakeholder Select

**Feature**: `027-contractor-stakeholder-select`  
**Started**: 2026-10-17  
**Phase 7 complete**: 2026-10-17

## Baseline (T001 / T003)

| Item | Value |
|------|-------|
| Branch | `develop` (ahead of origin) |
| Dirty (unrelated) | `CreatableSelect.tsx`, Jalali pickers, `app.css`, date-picker tokens |
| Python / Django | 3.12.3 / 4.2.11 |
| Postgres / Redis | running / PONG |
| Feature docs | research, data-model, contracts/, quickstart, tasks |
| Intended test modules | `projects/tests/test_contractor_stakeholder_filter.py`, `projects/tests/contractor_select_helpers.py`, `inventory/tests/test_department_activity_contractor_ref.py`, `inventory/tests/test_department_activity_contractor_import.py`, `field_reports/tests/test_daily_report_contractor_ref.py`, `field_reports/tests/test_labor_camp_contractor_ref.py`, `projects/tests/test_project_contractor_ref.py` |
| Quickstart | [quickstart.md](quickstart.md) |

## Evidence log

### Final API suite (Phase 7)

```text
projects/tests/test_contractor_stakeholder_filter.py
inventory/test_department_activity_contractor_ref.py
inventory/test_department_activity_contractor_import.py
projects/tests/test_project_contractor_ref.py
field_reports/tests/test_daily_report_contractor_ref.py
field_reports/tests/test_labor_camp_contractor_ref.py
→ 19 passed (includes unbound-name rejection guards T051/T052)
```

### Foundational
- RED then GREEN: stakeholder role normalize + `?role=contractor&status=active` filter

### US1
- GREEN: department activity `contractor_ref` create/filter/history + import resolve
- UI: `ContractorSelect`, department activity modal + filter, `fetchProjectContractors`

### US2
- ذینفعان create form: role (contractor) + status; invalidate `project-contractors` query
- ذینفعان row edit: PATCH role/status via `updateStakeholder` (T048)

### US3
- Migrations: `projects.0018_contractor_stakeholder_ref`, `field_reports.0016_contractor_stakeholder_ref`
- Daily report activity/labor options from ذینفعان; project settings `ContractorSelect`
- Create wizard: free-text پیمانکار removed; deferred help points to ذینفعان (T049)
- Labor camp page + tab: `ContractorSelect` / select-only (T050–T052)
- Serializers reject unbound free-text `subcontractor_name` without resolvable `contractor_ref`

### Phase 7 polish
- e2e: `e2e/tests/contractor-stakeholder-select.spec.ts` → **2 passed** (ذینفعان role + department empty/populated)
- FA gettext: contractor validation strings in `apps/api/core/locale/fa/LC_MESSAGES/django.po` (+ compiled `.mo`)
- All `tasks.md` items marked `[X]`

### Typecheck (T055)

```text
pnpm typecheck
→ pre-existing failures unrelated to 027:
  - daily-report-view.tsx projectId prop
  - ManualProgressDrawer activityId
  - KickoffCharterPanel index
→ ContractorSelect `asList(data ?? [])` fixed in-feature
```

### Quickstart scenarios 1–6 / SC-001–SC-005

| Scenario / SC | Evidence |
|---------------|----------|
| QS1 Active contractor list | API filter tests GREEN; `fetchProjectContractors` |
| QS2 Department create with ref | US1 pytest + `ContractorSelect` modal |
| QS3 Import resolve / reject invent | import pytest GREEN |
| QS4 ذینفعان role/status | create + row edit UI (T048); filter tests |
| QS5 Daily / labor camp require ref | serializer reject tests + select UX |
| QS6 Project settings contractor | `ContractorSelect` on settings; wizard deferred |
| SC-001 No free-text invent | Wizard help; serializer guards; select-only grids |
| SC-002 Project isolation | filter isolation pytest |
| SC-003 Inactive excluded | `status=active` filter tests |
| SC-004 Name snapshot on write | activity/labor camp snapshot tests |
| SC-005 Empty list help | `contractors.emptyHelp` on `ContractorSelect` |

### Notes
- Early run failed with 403 (HR group) and `inventory/tests/` package clash; fixed via flat modules + `hr_auth_client`
- Out of scope preserved: `subcontractors` app / Contract FK left in place
