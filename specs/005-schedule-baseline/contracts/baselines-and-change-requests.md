# Contract: Baselines & schedule change requests

**Base**: `/api/v1/projects/{project_id}/`

## Permissions

- Read: `view_activities`
- Write / submit / decide: `edit_activities`

---

## Baselines

### List

`GET .../baselines/`

Returns versions with: `id`, `version_name`, `is_current`, `is_locked`, `approved_at`, `approved_by`, `locked_at`, `source_change_request_id`.

### Create snapshot (optional explicit path)

`POST .../baselines/`

```json
{ "version_name": "BL-1 draft" }
```

Snapshots current live activities into `BaselineActivity`. Created **unlocked**, `is_current=false` unless query/body `make_current` is explicitly allowed before first lock (implementer chooses; prefer unlock + separate approve-lock).

### Approve & lock

`POST .../baselines/{baseline_id}/approve-lock/`

Effects:

- Sets `approved_at`, `approved_by`, `is_locked=true`, `locked_at`, `locked_by`
- Sets `is_current=true` (clears other currents)
- Does **not** delete prior baselines

**409** `baseline_already_locked` if already locked.

### Mutate snapshot

`PATCH/DELETE` on baseline activities — **403/409** `baseline_locked` when parent is locked.

Live `PATCH .../activities/{id}/` never modifies locked snapshot rows (regression).

Import (MSP/P6) may still create baselines; after this feature, imported current baselines SHOULD be approved-locked via the same action (or import leaves unlocked until approve — document choice in ENDPOINTS.md at implement time; prefer unlock-then-approve for consistency).

---

## Schedule change requests

### List / create

`GET|POST .../schedule-change-requests/`

Create (draft):

```json
{
  "reason": "",
  "milestone_impact": "",
  "cost_impact": "",
  "contract_impact": "",
  "items": [
    {
      "activity_id": "<uuid>",
      "proposed_planned_start": "2026-05-01",
      "proposed_planned_finish": "2026-05-20",
      "proposed_duration_days": 15,
      "proposed_forecast_finish": "2026-05-22",
      "notes": ""
    }
  ]
}
```

`base_baseline` defaults to current locked baseline when present.

### Detail / update draft

`GET|PATCH .../schedule-change-requests/{id}/` — PATCH only while `draft`.

### Submit

`POST .../schedule-change-requests/{id}/submit/`

Requires non-empty `reason`, `milestone_impact`, `cost_impact`, `contract_impact`.

**409** `schedule_change_in_flight` if another request is already `submitted`.

### Approve

`POST .../schedule-change-requests/{id}/approve/`

```json
{ "decision_notes": "Approved by PM" }
```

Transactional effects:

1. Apply `items` to live activities (with same date/calendar validation as activity update)
2. Create new locked current `BaselineSchedule` (+ `BaselineActivity` snapshot)
3. Set request `status=approved`, `resulting_baseline_id`
4. Prior current: `is_current=false`, remains `is_locked=true`

### Reject

`POST .../schedule-change-requests/{id}/reject/`

```json
{ "decision_notes": "Insufficient cost analysis" }
```

No new baseline version.
