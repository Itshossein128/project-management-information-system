# A6-P4 traceability

Technical readiness only. Not customer acceptance or a release. Closed packages 1–3 on 2026-11-06.

| Requirement | Result | What changed | Evidence |
|-------------|--------|--------------|----------|
| A6-R30 | اصلاح شد | Observation read vs write separation on `IsProjectMember` / `HasProjectPermission`; project detail isolation | `permissions/project.py`; `projects/tests/test_module_access_project_scope.py`; package-1.md |
| A6-R33 | اضافه شد | `assert_same_project`; documents related_* + ProjectScopedViewSet membership | `permissions/project.py`; `documents/serializers.py`; `common/viewsets.py` |
| A6-R34 | اصلاح شد | UI `usePermission` observation assistive views without sensitive/write | `apps/web/src/app/contexts/project-context.tsx` |
| A6-R35 | اصلاح شد (جزئی) | Account-switch clears project queries; revoke retry refuses submit | `auth-context.tsx`; `permissions/tests/test_revocation_retry.py` |
| A6-R38 | اصلاح شد | Visitor legacy items write probe; alternate path parity | `permissions/tests/test_alternate_path_parity.py` |
| A6-R39 | اصلاح شد | Nested wage/contact redaction on report run + export | `permissions/redaction.py`; `report_export_service.py`; `report_views.py`; `test_redaction.py` |
| A6-R40 | حفظ شد | Stakeholder contacts remain on `view_sensitive_contacts` | `projects/tests/test_stakeholder_contacts_acl.py` |
| A6-R41 | اضافه شد | `view_person_contacts`; lookup/roster server redaction | `member_views.py`; `projects/tests/test_person_directory_acl.py` |
| A6-R42 | اصلاح شد | Nested redaction walks dict/list | `permissions/redaction.py` |
| A6-R43 | اصلاح شد | Stored file access requires active membership (no observation bypass) | `storage/permissions.py`; `storage/tests/test_stored_file_access.py` — MinIO live N/A |
| A6-R44 | اصلاح شد | Commitment/budget/IPC/actual SoD; creator cannot self-approve | `cbs_services.py`; budget/ipc/actual services; package-2.md |
| A6-R45 | اصلاح شد (جزئی) | Workflow final stage uses shared SoD; activate/retire require membership | `workflow/services/instance_service.py`; `workflow/views.py`; `test_sod_final_approve.py` |
| A6-R46 | اصلاح شد | Null creator blocked; superuser break-glass needs reason + `RoleAccessChange` | `permissions/sod.py`; `permissions/tests/test_sod.py`; `test_commitment_sod.py` |
| A6-R10 | حفظ شد | Observation ≠ org management | `test_observation_exception.py` |
| A6-R31 | اصلاح شد | Three package matrices closed with pytest evidence | `matrix/package-{1,2,3}.md` |
| A6-R32 | حفظ شد | Visitor item write refuse | `test_alternate_path_parity.py` |
| A6-R36 | اصلاح شد | Package-2/3 consumers: portfolio, procurement step RBAC, documents scope | package-2.md; package-3.md |
| A6-R37 | اصلاح شد | Observation no longer implies write via `HasProjectPermission` | `permissions/project.py` |

## Package gates

| Package | Status |
|---------|--------|
| 1 | `closed` — 46 passed; Phase 13 revalidated |
| 2 | `closed` — 65 passed; Phase 13 revalidated (inventory nested routes corrected) |
| 3 | `closed` — 16 passed; Phase 13 revalidated (file source ACL); MinIO live skipped |

## Phase 13 convergence

2026-11-06: T061–T078 closed. Focused revalidation **47 passed** (`test_sod`, alternate-path, creator repair, module-access scope, person directory, nested export, stored file, commitment SoD, workflow SoD, person dossier).

Notable honesty corrections: package-2 M20 now lists **9** project-nested inventory routes under `inventory.project_urls` (prior “0 urls” claim was wrong). Interactive Persian browser UAT remains P6; server/UI parity fixtures remain the technical spot-check evidence.

## Persian UI spot check (T059)

API/dev servers were available; spot check recorded against seeded project via existing UI-server parity fixtures + person-directory ACL (lookup omits contacts without `view_person_contacts`; observation read-without-write covered in `test_observation_exception` / `test_module_access_project_scope`). Full interactive Persian browser walkthrough of forbidden-control hide remains customer UAT (P6); server parity fixtures: `permissions/tests/test_ui_server_parity_fixtures.py`. Frontend T022 checklist: `apps/web/src/app/contexts/T022-permission-guard-checklist.md`.

## P5 / P6 handoff (T060)

- P5: `RoleAccessChange` records `sod_break_glass` / `sod_creator_repaired` and related sensitive-action hooks from T076; no claim that access-history UI is finished.
- P6: Customer acceptance scenarios in A6-P6 remain unexecuted.
