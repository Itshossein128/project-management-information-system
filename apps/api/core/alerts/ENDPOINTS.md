# Alerts Endpoints

Configurable alert rules, fired-event log, and acknowledgement. Rules are evaluated by `alerts/services/alert_engine.py` on a schedule (Celery) and on domain signals (daily reports, costs, inventory, subcontractor scores, correspondence).

All routes are nested under a project: `/api/v1/projects/{project_pk}/`.

## Permissions

| Action | Permission |
|--------|------------|
| List / acknowledge alerts, active counts | `view_project` + `IsProjectMember` |
| Create / update / delete rules | `edit_project` |

## Endpoints

### 1. Alert Rules

*   **URL:** `/alert-rules/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: Returns project-specific rules plus system-wide rules (`project` is null). System rules are read-only for delete.
    *   `POST`: Creates a project-scoped rule. Body fields: `alert_type`, `name`, `threshold_value`, `notify_roles` (comma-separated role names), `recipient_ids` (optional user UUID list), `cooldown_hours`, `is_active`.
*   **Tags:** Alerts

*   **URL:** `/alert-rules/{rid}/`
*   **Methods:** `PATCH`, `DELETE`
*   **Description:**
    *   `PATCH`: Partial update. Project rules and matching system rules can be updated.
    *   `DELETE`: Soft-deletes **project-owned** rules only. System rules return `400 Cannot delete system rules`.

### 2. Alert Log

*   **URL:** `/alerts/`
*   **Method:** `GET`
*   **Description:** Lists up to 200 log entries, newest first.
*   **Query params:**
    *   `acknowledged=false` — unacknowledged only
    *   `alert_type` — filter by rule type (e.g. `budget_overrun`)
    *   `date_from`, `date_to` — ISO date filters on `fired_at`

*   **URL:** `/alerts/active/`
*   **Method:** `GET`
*   **Description:** Unacknowledged alert counts grouped by `alert_type`. Cached 5 minutes.

*   **URL:** `/alerts/{lid}/acknowledge/`
*   **Method:** `POST`
*   **Description:** Sets `acknowledged_at` and `acknowledged_by` on a log entry.

## Supported `alert_type` values

| Type | Threshold meaning | Trigger source |
|------|-------------------|----------------|
| `ipc_payment_overdue` | Days past planned payment | Approved IPCs with no actual payment date |
| `guarantee_expiring` | Days until expiry (default 30) | Active contract guarantee dates |
| `budget_overrun` | Budget consumption % (default 100) | WBS budget vs actual variance |
| `cash_gap_detected` | — | Cumulative negative cash-flow month |
| `low_stock` | — | Material below minimum level |
| `activity_behind_schedule` | Lag % (default 10) | Planned vs actual activity progress |
| `missing_daily_report` | Days ago (default 1) | No report for target date |
| `daily_report_not_approved` | Hours pending (default 24) | Submitted but not approved reports |
| `baseline_not_set` | — | No current baseline schedule |
| `subcontractor_at_risk` | — | `compute_risk_flag()` true |
| `subcontractor_score_low` | Score floor (default 6) | Latest overall score below threshold |
| `correspondence_response_due` | Days ahead (default 3) | Correspondence with upcoming due date |
| `sync_conflict_unresolved` | — | Reserved for offline sync conflicts |

When a rule fires, in-app `Notification` records are created for `recipient_ids` or members matching `notify_roles`. `AlertLog` records the event; `cooldown_hours` prevents duplicate fires for the same `trigger_reference`.

## Background tasks

```bash
# Celery beat (production)
alerts.tasks.run_daily_alert_checks      # all active projects
alerts.tasks.monitor_cash_gaps             # cash-flow forecast gaps
alerts.tasks.check_and_fire_for_project_task  # per-project evaluation
```

## Signals (real-time re-check)

Post-save hooks on: `DailyReport` (approved), `ActualCost`, `InventoryTransaction`, `SubcontractorPerformanceScore`, `Correspondence` — each queues `check_and_fire_for_project_task`.
