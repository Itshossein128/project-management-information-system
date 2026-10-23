# Contract: Unit-Report Section API (feature 033)

Base URL (as established by feature 032): `/api/v1/projects/{project_pk}/unit-reports/…` — section endpoints are nested under the unit-report version the unit page already resolves (`open`/`current` returns the report + existing child sections). No standalone `/sub-reports` route exists or returns.

All section mutations are permitted only while the parent report version is `draft` or `rejected` (032's edit rule); submitted/approved content is immutable except via the 032 correction flow, which must re-run every validation below.

## 1. Executed activities (Buildings / Electrical / Mechanical)

- `GET …/unit-reports/{version}/activities/` — list (ordered by `row_number`), each row: `row_number`, `activity_ref` (id + label + code), `activity_description`, `shift`, `contractor_ref` (id + display name), `crew_name`, `headcount` (derived: foreman+worker), `foreman_count`, `worker_count`, `parcel`, `block`, `floor`, `zone` (location), `quantity`, `unit`, `notes`.
- `POST/PATCH/DELETE …/activities/{id}/` — child-row CRUD bound to the version.

Validation (422 JSON, fielded, localized fa/en):

| Code | Condition |
|---|---|
| `quantity_must_be_positive` | provided `quantity` ≤ 0 |
| `invalid_shift` | `shift` outside recognized vocabulary |
| `activity_not_in_project_scope` | WBS activity from another project, or inactive/unapproved |
| `contractor_not_in_project_scope` | contractor stakeholder from another project |
| `contractor_required` | missing contractor |

`crew_name` and `contractor` are always returned as separate fields; no serializer merges them.

## 2. Labor (all units' applicable sections)

- `GET/POST/PATCH/DELETE …/labor/` — rows: `labor_category` (indirect/direct), `job_title` (catalog-resolved), `custom_title` (only accepted from the effective catalog's project-specific titles), `present_count`, `leave_count`, `overtime_hours`, `contractor_ref` (optional), resolved `title_code`, `display_order`.

Validation: `headcount_must_be_non_negative` (present/leave), `unknown_job_title` (title not resolvable in the effective catalog snapshot for the report date), `invalid_labor_category` (must match the catalog title's category). Man-hours are NOT stored here; the summary computes them per the configuration rule.

## 3. Machinery (Machinery unit)

- `GET/POST/PATCH/DELETE …/machinery/` — rows: `row_number`, `equipment_type`, `equipment_ref` (optional stable identity), `status_total`, `status_active`, `status_ready`, `status_inactive`, `status_under_repair`, `operating_hours`, `stoppage_hours`, `repair_hours`, `stoppage_reason_code` + label.

Validation: `stoppage_reason_required_when_stoppage_gt_zero`; `hours_exceed_day_limit` (sum > 24 for the declared item or row); `stoppage_reason_not_in_vocabulary`; `machinery_status_sums_inconsistent` (mixed type/item rows whose type sums disagree); `status_count_must_be_non_negative`. The response lists the effective reason vocabulary (code + localized label) so editors present controlled choices.

## 4. Materials (Warehouse unit)

- `GET/POST/PATCH/DELETE …/materials/` — rows: `transaction_type` (`receipt`/`consumption`), `material_description`, `material_ref` (optional), `quantity`, `unit`, `consumption_location`, `supplier`, `warehouse_document_reference`, `notes`.

Validation: `transaction_type_required`; `receipt_requires_document_reference`; `consumption_location_required_for_consumption`; `quantity_must_be_positive`. Receiptness (resolved vs unresolved) is computed read-only, never stored client-side.

## 5. Concrete (Buildings / Mechanical as configured)

- `GET/POST/PATCH/DELETE …/concrete/` — rows: `concrete_description`/grade, `volume_m3`, `structural_element`, `location` (`zone`), `parcel`, `block`, `floor`, `batching_plant`, `truck_delivery_note_number`, `lab_sample_code`, `sampling_state` (`not_sampled`/`sampling_declared`), `test_sheet_count`, `qc_inspection` (read-only link info once created).
- Sampling linkage: on submit (or correction-resubmit) of a version containing declared sampling, the backend creates/links a project `risk.Inspection` record and returns its id via `qc_inspection` on the row. Missing test information blocks submit with `sampling_requires_test_information`.

Validation: `volume_must_be_positive`; `sampling_requires_test_information`; `reference_not_in_project_scope` (batching plant/document/project refs from other projects).

## 6. Structured narrative (issues/barriers, visits, HSE, general notes)

- `GET/POST/PATCH/DELETE …/issues/` — rows: `row_number`, `kind` (`issue`/`barrier`), `text`, `owner_user` (+ display name), `due_date`. Barrier validation: `barrier_owner_and_due_date_required`.
- `…/visits/` — rows: `row_number`, `text`.
- `…/hse-incidents/` — rows: `row_number`, `text`, `severity` (`minor`/`moderate`/`major`), `immediate_action` (required: `hse_immediate_action_required`). On submit, the incident emits the required `notifications.Notification` (+ follow-up task where supported); the response confirms `notification_id`.
- `…/general-activities/` — structured rows: `row_number`, `activity_description`, `location` (building), `quantity`, `unit`, `notes`. No text-encoding; free text never becomes an issue row (general notes stay `other` type notes; `POST …/notes/` remains for explicitly typed notes only).

## 7. Attachments (activity images)

- `POST …/attachments/` — multipart upload: file (JPEG/PNG, ≤ 10 MB, content-validated: `unsupported_file_format`, `file_too_large`), `capture_date`, `work_front`, optional `row_kind`+`row_id` (must belong to this version: `attachment_row_not_in_version`), cross-project targets refused (`reference_not_in_project_scope`).
- `GET …/attachments/`, `DELETE …/attachments/{id}/` — list/delete per 032 edit rules.

## 8. Permissions

Section view requires the 032 unit-report view permission for the project; section create/edit/submit follows the 032 permission matrix (unit members for create/edit, reviewers for transitions). All lookups resolve through the authorized project scope; knowing a row or attachment id grants nothing cross-project (server-side check on every route, per Constitution I). Catalog/vocabulary reads (needed by editors) use project-scoped reporting-configuration endpoints — see [reporting-configuration-catalog-api.md](./reporting-configuration-catalog-api.md).

## 9. Submission integrity

On submit/correction/replace, section validation runs as one atomic check suite; a version with any section-level contract violation is refused with fielded localized errors and stays in its previous state. Legacy rows archived before 033 that violate new contracts surface as `submission_blocked_by_section_contract` on theVersion (never silently dropped or coerced).

Related contracts: [daily-summary-sections-api.md](./daily-summary-sections-api.md) for the derived/aggregation surface; [unit-report-and-summary-ui.md](./unit-report-and-summary-ui.md) for the UI contract.
