# Quickstart: Contractor Stakeholder Select

Validation guide after implementation. Design refs: [data-model.md](data-model.md), [contracts/contractor-select-api.md](contracts/contractor-select-api.md), [contracts/contractor-select-ui.md](contracts/contractor-select-ui.md).

## Prerequisites

- Postgres + Redis up; API and web as in `AGENTS.md`
- Seeded project with a user who has `view_project` + `edit_project`

## 1. Register a contractor

1. Open project **ذینفعان**.
2. Add stakeholder with role **پیمانکار** / contractor, status active.
3. Confirm it appears in the stakeholder list with role contractor.

**Expect**: `GET /api/v1/projects/{id}/stakeholders/?role=contractor&status=active` returns that row.

## 2. Department activity (P1)

1. Open a non-warehouse department activity log → create.
2. پیمانکار control is a select of contractors only (no free text / no Add).
3. Save with a selected contractor.
4. Row shows the same name; API payload has `contractor_ref` and matching `contractor` snapshot.

**Negative**: With zero contractors, save without selection fails with clear message. Typing a novel name is impossible.

## 3. Isolation

1. Create contractor only on project A.
2. On project B activity form, options must not include A’s contractor.
3. API reject: POST activity on B with A’s stakeholder UUID → 400.

## 4. Inactive

1. Set contractor status inactive on ذینفعان.
2. New activity form no longer lists them.
3. Previously saved row still displays the snapshot name.

## 5. P2 smoke (when implemented)

- Daily report activity پیمانکار options match ذینفعان contractors (not contracts list).
- Labor camp پیمانکار same source.
- Project settings پیمانکار select syncs project display name.

## 6. Import

- Import sheet with پیمانکار = exact active contractor name → succeeds.
- Unknown name → row error; no new stakeholder created.

## Suggested automated checks

```bash
# From apps/api/core with .env sourced
../.venv/bin/python -m pytest projects/tests/test_central_data_stakeholders.py inventory/tests.py -q
# Add focused tests for contractor_ref validation / filter once written
```

Frontend: `pnpm typecheck` for touched web files; browser check fa + en on department modal empty and populated states.
