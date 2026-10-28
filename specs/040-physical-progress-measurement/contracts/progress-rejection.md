# API Contract: Progress Rejection and Boundary Enforcement

## Progress Entry Points
1. `POST /api/v1/projects/{project_pk}/progress/manual/`
2. `POST /api/v1/projects/{project_pk}/daily-reports/{report_pk}/activities/`
3. `POST /api/v1/projects/{project_pk}/units/{unit}/daily-reports/{report_pk}/activities/`

---

### Case 1: Progress without Approved Measurement Method

#### Request Condition
Submitting progress or daily report row referencing an activity where `get_current_approved_version(activity)` is `None`.

#### Response: 400 Bad Request
```json
{
  "error": {
    "code": "measurement_not_approved",
    "message": "روش اندازه‌گیری این فعالیت هنوز تأیید نشده است."
  }
}
```

---

### Case 2: Cumulative Progress > 100% (No Clamping)

#### Request Condition
Submitting progress or execution volume where cumulative progress exceeds 100% (`pct > 1.0` or `cumulative_quantity > effective_total_quantity`) and no approved `ActivityQuantityChange` covers the excess.

#### Response: 400 Bad Request
```json
{
  "error": {
    "code": "progress_exceeds_100",
    "message": "مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند"
  }
}
```

#### Behavior Invariant
- The database state remains unchanged.
- The system MUST NOT clamp or truncate the cumulative progress to 100%.
- Cumulative progress remains at its previously recorded valid percentage.
