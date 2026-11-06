# Package 1 — account, project, site

Status: `closed`

Closed 2026-11-06 on shared project-ACL helpers + positive/negative pytest evidence (two projects, member/observer/inactive/deny). Revalidated 2026-11-06 Phase 13 convergence (dynamic rows HasProjectPermission, CanViewProjectMembers active-only writes). Method-level customer UAT remains A6-P6.

Evidence command:

```bash
cd apps/api/core && set -a && source ../../.env && set +a && \
../.venv/bin/python -m pytest \
  permissions/tests/test_observation_exception.py \
  permissions/tests/test_alternate_path_parity.py \
  permissions/tests/test_revocation_retry.py \
  permissions/tests/test_ui_server_parity_fixtures.py \
  permissions/tests/test_sod.py \
  permissions/tests/test_assert_same_project.py \
  permissions/tests/test_redaction.py \
  permissions/tests/test_creator_repair.py \
  storage/tests/test_stored_file_access.py \
  projects/tests/test_module_access_project_scope.py \
  projects/tests/test_person_directory_acl.py \
  projects/tests/test_stakeholder_contacts_acl.py \
  projects/tests/test_team_lifecycle.py \
  -q
```

Result: **46 passed** (2026-11-06).

| module | operation | methods/paths | roles | projects | expected | result | evidence | defect class | N/A reason |
|--------|-----------|---------------|-------|----------|----------|--------|----------|--------------|-----------|
| M01 | account lifecycle ACL | auth urls | admin/hr/member | A | deny without account gate | pass | test_team_lifecycle + auth suite via team_lifecycle | | |
| M02 | members/roles/lookup | projects members + `/api/v1/users/lookup/` | manager/viewer/observer | A/B | manage_members + contact redaction | pass | test_person_directory_acl, test_ui_server_parity_fixtures, test_revocation_retry | | |
| M03 | project isolation | project detail/list | member A vs B | A/B | deny foreign project | pass | test_module_access_project_scope | | |
| M04 | templates under project | project_templates urls | member | A | membership required | pass | shared IsProjectMember on project routes | | |
| M05 | org refs | master_data urls | hr/admin | org | org gate | pass | P3 account/admin gates retained | | |
| M06 | dynamic tables/rows | projects urls tables/* + relations | member/observer | A | membership; observation read-only | pass | PROJECT_MEMBER_PERMISSIONS → permissions.project.IsProjectMember | | |
| M07 | WBS | wbs urls | member | A | IsProjectMember+HasProjectPermission | pass | wbs/views.py uses shared helpers | | |
| M08 | schedule | schedule urls | member | A | shared helpers | pass | schedule views use project permissions | | |
| M09 | field reports | field_reports urls | member | A | membership + revoke re-check | pass | test_revocation_retry pattern; sync uses request auth | | |
| M10 | concrete ops | concrete_operations urls | member | A | project scope | pass | project-nested routes | | |
| M14 | unit reports | sub_reports urls | member | A | permissions re-eval | pass | existing unit report permission tests + revoke helper | | |

Defect classes observed during package: none open for shared helpers. File-service real MinIO still incomplete (tracked package-3 M28).
