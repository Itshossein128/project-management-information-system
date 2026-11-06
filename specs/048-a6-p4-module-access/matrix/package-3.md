# Package 3 — documents, collaboration, management outputs

Status: `closed`

Closed 2026-11-06 on shared ACL helpers + package-3 consumer fixes (documents related-id `assert_same_project`, workflow activate/retire membership, nested export redaction parity, storage membership-only file ACL). Revalidated 2026-11-06 Phase 13 (source-permission file ACL, nested export/dashboard redaction, workflow stage membership). Method-level customer UAT remains A6-P6. Live MinIO still skipped.

Evidence command:

```bash
cd apps/api/core && set -a && source ../../.env && set +a && \
../.venv/bin/python -m pytest \
  documents/tests/test_correspondence_contract_link.py \
  workflow/tests/test_sod_final_approve.py \
  storage/tests/test_stored_file_access.py \
  permissions/tests/test_redaction.py \
  projects/tests/test_stakeholder_contacts_acl.py \
  permissions/tests/test_assert_same_project.py \
  -q
```

Result: **16 passed** (2026-11-06).

| module | operation | methods/paths | roles | projects | expected | result | evidence | defect class | N/A reason |
|--------|-----------|---------------|-------|----------|----------|--------|----------|--------------|-----------|
| M11 | ریسک | risk urls | member | A | IsProjectMember+HasProjectPermission | pass | risk/views.py shared helpers | | |
| M12 | تصمیم | decision-cases | member | A | IsProjectMember+HasProjectPermission | pass | decision_support/views.py shared helpers | | |
| M22 | اسناد | correspondence related_* | member | A/B | cross-project related id rejected | pass | test_correspondence_contract_link + assert_same_project in serializers | project-scope | |
| M23 | گردش‌کار SoD | workflow final approve | starter≠approver | A | sod_self_approve | pass | test_sod_final_approve; instance_service | action/SoD | |
| M24 | ذی‌نفع contacts | stakeholders | ±view_sensitive_contacts | A | redact without permission | pass | test_stakeholder_contacts_acl | sensitive-field | |
| M25 | گزارش nested | report run/export | ±view_wage/contacts | A | nested redaction | pass | test_redaction; report_views + report_export_service | sensitive-field | |
| M27 | اعلان | notifications | owner | — | user-scoped queryset only | pass | notifications/views.py filters `user=request.user` | | |
| M28 | ذخیره file ACL | download/confirm | member vs observer | A | no observation/admin bypass | pass | test_stored_file_access | file | Real MinIO presign not exercised in this environment — policy unit evidence only |
| M29 | ممیزی | RoleAccessChange + audit middleware | — | — | break-glass/`sod_*` actions persist; body redaction | pass | test_sod + audit/tests.py; history UI deferred to P5 | | |

Honest gaps: live MinIO upload/download integration not run (Docker-only). Full workflow stage matrix beyond final-approve SoD not separately re-probed.
