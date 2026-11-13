# Data Model: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Feature Directory**: `specs/056-a7-p6-delivery-acceptance`  
**Direct Audit IDs**: `D03`, `D04`  
**Storage Type**: Versioned Markdown and JSON evidence artifacts under `specs/056-a7-p6-delivery-acceptance/` (no new Django database models or migrations).

---

## 1. `AuditDispositionRecord` (`رکورد وضعیت ممیزی ۵۶گانه`)

Stored in `specs/056-a7-p6-delivery-acceptance/traceability.md` and `specs/056-a7-p6-delivery-acceptance/evidence/audit-disposition.json`. Represents one of the 56 audit items from `output/a7-requirements-2026-11-10/requirements.json`.

| Field | Constraint |
| --- | --- |
| `audit_id` | Required string matching `^(P0[1-9]|P1[01]|W0[1-7]|M0[1-4]|S0[1-8]|I0[1-9]|I1[0-9]|I2[0-2]|D0[1-4])$` (56 unique IDs total). |
| `owning_phase` | Required enum: `A.7-P1`, `A.7-P2`, `A.7-P3`, `A.7-P4`, `A.7-P5`, or `A.7-P6`. |
| `source_requirement` | Required non-empty string citing the originating spec/contract requirement. |
| `disposition` | Required enum: `تأیید فنی`, `ناقص`, `اجرانشده`, or `نیازمند پاسخ کارفرما`. |
| `employer_bucket` | Required enum: `قبلاً موجود و تأییدشده روی نسخه حاضر`, `در A.7 اصلاح/تکمیل شد`, `هنوز باز/اجرانشده`, or `قابل تست توسط کارفرما`. |
| `evidence_refs` | Required non-empty list of repository-relative artifact or test paths verified on the candidate `version_id`. |
| `version_id` | Required string recording `git rev-parse HEAD` plus dirty/schedule-tree digest identity. |

**Validation Rules**:
- All 56 `audit_id` values from `output/a7-requirements-2026-11-10/requirements.json` MUST be present with zero duplicates and zero omissions.
- A record with `disposition = "تأیید فنی"` MUST reference at least one executed test or runtime evidence path on the current `version_id` (task checkboxes or historical 2026-11-10 probe notes are invalid).

---

## 2. `AcceptanceScenarioRecord` (`رکورد اجرای سناریوی پذیرش`)

Stored in `specs/056-a7-p6-delivery-acceptance/evidence/scenarios.md` and `specs/056-a7-p6-delivery-acceptance/evidence/scenarios.json`. Captures each end-to-end positive (`POS-01`–`POS-10`), negative/adverse/concurrency/access-boundary (`NEG-01`–`NEG-14`), and bilingual/responsive/keyboard/operational (`OPS-01`–`OPS-04`) acceptance scenario (`D03`).

| Field | Constraint |
| --- | --- |
| `scenario_id` | Required unique string matching `^(POS-(0[1-9]|10)|NEG-(0[1-9]|1[0-4])|OPS-0[1-4])$` (28 scenarios minimum). |
| `category` | Required enum: `positive`, `negative`, `concurrency`, `access_boundary`, `bilingual_ux`, or `operational`. |
| `audit_ids` | Required non-empty list of covered `audit_id` values. |
| `role_persona` | Required enum: `creator_planner`, `independent_approver`, `viewer`, `system_admin`, `org_reference_steward`, or `multi_role`. |
| `channel` | Required enum: `api_db`, `real_worker`, `browser_e2e`, or `combined`. |
| `input_ref` | Required non-empty string naming the fixture/project code or SHA-256 digest without secrets or raw proprietary text. |
| `expected_outcome` | Required non-empty string describing expected UI/API/DB state and error/warning codes. |
| `observed_outcome` | Required non-empty string recording actual observed state on `version_id`. |
| `technical_result` | Required enum: `pass`, `fail`, or `not_run`. |
| `employer_result` | Required enum: `pending`, `accepted`, or `rejected` (MUST remain `pending` in engineering handoff). |
| `defect_id` | Nullable string (`null` when `technical_result = "pass"`; required non-empty ID when `technical_result = "fail"`). |
| `evidence_ref` | Required non-empty repository-relative path to test log, JUnit XML, JSON manifest, or screenshot. |

**Validation Rules**:
- `not_run` MUST NEVER be rolled up as `pass`.
- `employer_result` MUST remain `pending` until a human employer representative records a decision.

---

## 3. `ReferenceScheduleReconciliationRecord` (`جدول تطبیق فایل مرجع زمان‌بندی`)

Stored in `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.md` and `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.json`. Reconciles source file figures, preview figures, import job summary figures, and stored PostgreSQL figures (`D03`, `D04`, `I03`–`I05`, `I08`).

| Field | Constraint |
| --- | --- |
| `fixture_id` | Required unique string (`real_data_plan_mpp`, `valid_msp_xml`, `valid_p6_xer`, `valid_p6_xml`). |
| `file_path` | Required repository-relative path to the schedule file. |
| `sha256` | Required 64-character lowercase hex SHA-256 digest (`3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553` for `real-data/plan.mpp`). |
| `size_bytes` | Required positive integer (`777216` for `real-data/plan.mpp`). |
| `source_counts` | Required object with integer keys `rows_total`, `wbs_candidates`, `activity_candidates`, `relation_candidates`. |
| `preview_counts` | Required object with integer keys `wbs_count`, `activity_count`, `relation_count`, `warning_count`. |
| `stored_counts` | Required object with integer keys `wbs_count`, `activity_count`, `relation_count` (`{"wbs_count": 6, "activity_count": 72, "relation_count": 72}` for `real-data/plan.mpp`). |
| `repeat_append_result` | Required object with `nothing_changed: true`, `duplicate_wbs: 0`, `duplicate_activities: 0`, `duplicate_relations: 0`, `extra_baselines: 0`. |
| `expected_warning_codes` | Required list of strings (`["activity_without_parent", "predecessor_is_summary", "calendar_not_applied"]` for `real-data/plan.mpp`). |

---

## 4. `EmployerDeliveryPackage` & `DefectRecord` (`بسته تحویل کارفرما و رکورد نقص`)

Stored across `specs/056-a7-p6-delivery-acceptance/guide.md`, `specs/056-a7-p6-delivery-acceptance/evidence/package.json`, `specs/056-a7-p6-delivery-acceptance/evidence/accounts.md`, `specs/056-a7-p6-delivery-acceptance/evidence/defects.md`, and `specs/056-a7-p6-delivery-acceptance/evidence/minutes.md` (`D04`).

| Field | Constraint |
| --- | --- |
| `version_id` | Required string with `git_head` (`40`-char hex), `tree_dirty` (boolean), `schedule_tree_sha256` (`64`-char hex), and `acceptance_image_digest` (`sha256:...`). |
| `environment_id` | Required non-empty string identifying the isolated acceptance environment (`local-isolated-postgres-5433` + `a7p5-import-compose-18000`). |
| `role_personas` | Required list of 5 secret-free role descriptors: `creator_planner`, `independent_approver`, `viewer`, `system_admin`, `org_reference_steward`. |
| `summary_buckets` | Required object with 4 keys (`already_verified`, `fixed_in_a7`, `still_open_or_unrun`, `testable_by_employer`) partitioning the 56 audit items. |
| `technical_readiness` | Required enum: `ready_for_acceptance` or `blocked`. |
| `employer_decision` | Required enum: `pending`, `accepted`, or `rejected` (authored value MUST be `pending`). |
| `employer_signer_role` | Required empty string `""` in authored package (filled only by employer representative role title upon decision; no personal names required). |
| `employer_signed_at` | Required empty string `""` in authored package (filled only upon human employer decision). |

### State Transitions

```text
draft_specification
  -> predecessor_gates_verified   (when P1–P5 handoffs and P5 T049 second-operator reproduction are verified)
  -> technical_verification_run   (when POS-01..10, NEG-01..14, OPS-01..04, and 56-item reconciliation complete)
  -> ready_for_acceptance         (when 0 open in-scope blocking defects remain and validate_package.py exits 0)
  -> employer_accepted / rejected (ONLY when human employer representative records decision; never set by agent)
```
