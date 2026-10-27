# Contract: Unit Report Submission & Approval API

## Submission Endpoint

`POST /api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/submit/`

### Successful Submission (200 OK)
- Pre-conditions: Report is in `draft` or `rejected` status; contains at least one active row across operational sections (`activities`, `labor_entries`, `material_entries`, `concrete_entries`, `machinery_rows`, `general_activities`).
- Side-effects:
  - Transitions `status` to `submitted`.
  - Stamps `submitted_by` and `submitted_at`.
  - Automatically creates/links `risk.Inspection` records for any activity row with `is_hydrostatic_tested=True` and `test_outcome='PASSED'`.
  - Triggers daily master rollup rebuild.

### Empty Sub-Report Submission Rejection (400 Bad Request)
When report contains 0 active operational rows:
- **HTTP Status**: 400 Bad Request
- **Response**:
```json
{
  "detail": "امکان ارسال گزارش خالی وجود ندارد؛ حداقل یک ردیف فعالیت یا کارکرد وارد نمایید",
  "code": "cannot_submit_empty_sub_report"
}
```
- **State Effect**: Report status remains strictly `draft`, no submission timestamp is saved, and no daily summary rollup is executed.

---

## Approval Endpoint

`POST /api/v1/projects/{project_id}/units/{unit}/daily-reports/{report_id}/approve/`

### Successful Approval (200 OK)
- Pre-conditions: Report is in `submitted` status; caller is not the preparer or submitter (Segregation of Duties).
- Side-effects:
  - Transitions `status` to `approved`.
  - Stamps `approved_by` and `approved_at`.
  - For every activity row with an associated `contractor_ref`, automatically generates or updates a `SubcontractorLaborLedgerEntry` record:
    `total_person_hours = (foreman_count + worker_count) * shift_hours`.
  - Triggers daily master rollup rebuild.
