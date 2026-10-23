# Contract: Canonical Unit Aggregation and Provenance

**Feature**: `032-unit-report-source-truth`  
**Existing base**: `/api/v1/projects/{project_id}/daily-reports/`

The existing materialized DailyReport shell and by-date open/ensure contract remain. This contract replaces legacy discipline metadata with canonical unit completeness and complete source-row provenance.

## Eligible inputs

A source report contributes only when it is current, non-deleted, non-quarantined, submitted or approved, and matches the requested project/date. Historical, draft, rejected, deleted, wrong-project, and wrong-date versions contribute neither content nor completeness credit.

## Aggregation metadata

DailyReport detail and by-date responses include:

```json
{
  "aggregation": {
    "is_auto_summary": true,
    "aggregated_at": "2026-10-22T15:00:00Z",
    "completeness": {
      "state": "partial",
      "configuration_id": "configuration-uuid",
      "source_template": {
        "id": "template-uuid",
        "name": "Residential project"
      },
      "expected_units": ["buildings", "electrical", "mechanical"],
      "contributing_units": ["buildings"],
      "missing_units": ["electrical", "mechanical"]
    },
    "weather_source": "derived",
    "site_status_source": "override"
  }
}
```

`completeness.state` is one of:

- `configuration_incomplete`: no effective/bound project reporting configuration; never considered complete.
- `partial`: configuration exists and at least one required unit is missing.
- `complete`: configuration exists and no required unit is missing.

Eligible non-required units appear in `contributing_units` but never in `missing_units`.

## Provenance projection

Every derived row or combined value includes an ordered list:

```json
{
  "id": "derived-row-uuid",
  "is_derived": true,
  "provenance": [
    {
      "unit": "buildings",
      "report_id": "source-version-uuid",
      "report_version": 2,
      "source_row_kind": "department_activity",
      "source_row_id": "1842",
      "contribution_value": "7.0000",
      "can_view_source": true
    },
    {
      "unit": "electrical",
      "report_id": "source-version-uuid-2",
      "report_version": 1,
      "source_row_kind": "labor",
      "source_row_id": "source-row-uuid",
      "contribution_value": "3.0000",
      "can_view_source": false
    }
  ]
}
```

- Union rows normally contain one reference.
- Combined totals contain every contributing row, never just the last report.
- `can_view_source=false` suppresses navigable source detail but not the unit attribution needed to explain the summary.
- Legacy `source_discipline` and single `source_sub_report` fields may remain temporarily for compatibility, but new clients do not use them and they do not define truth.

## Rebuild behavior

- `GET/POST daily-reports/by-date/?date=...` ensures the existing full-shift summary and invokes the same serialized rebuild orchestration used by workflow transitions.
- Submit, approve, reject, delete, correction/current replacement, and relevant report-owned source changes trigger rebuild for the affected project/date.
- Rebuild acquires the documented locks and upserts deterministic derived keys.
- An unchanged source/configuration fingerprint may skip writes, but the returned metadata must remain current.
- Three consecutive rebuilds with unchanged inputs yield identical logical content, row counts, ordered provenance, completeness, and summary-owned override values.
- Rejected/deleted/superseded data is removed without retaining stale derived keys.

## Summary-owned data

Rebuild never unintentionally changes:

- management opinion;
- explicit weather override and overridden weather value;
- explicit site-status override and overridden site status/reason;
- project-summary workflow/audit fields outside aggregation ownership.

Direct mutation of unit-derived rows remains forbidden through DailyReport child endpoints.

## Source navigation authorization

Opening a provenance source re-enters the unit-report API and rechecks project membership, `view_reports`, unit scope, and historical visibility. A summary viewer cannot use a source ID to bypass those rules.
