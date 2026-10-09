# Contract: Project EVM Report

## API

`GET /api/v1/projects/{project_id}/progress/kpis/`

**Compatibility**: Existing endpoint; response **extended** with validity/status fields. Legacy numeric fields (`ev`, `pv`, `ac`, `spi`, `cpi`, …) remain for current UI; new structured fields are authoritative for not-computable semantics.

Query: `as_of` (Jalali or Gregorian), `force_refresh` (`1`\|`true`).

Permission: `view_dashboard` (existing progress base).

### Response (extended)

```json
{
  "as_of_date": "2026-10-09",
  "scope_type": "project",
  "validity": "partial",
  "warnings": ["baseline_not_locked"],
  "schedule_baseline": {"locked": false},
  "budget_baseline": {"approved": true, "is_control": true, "version_id": "<uuid>", "currency": "IRR"},
  "bac": 1000000,
  "pv": {"amount": 400000, "status": "registered"},
  "ev": {"amount": null, "status": "unregistered"},
  "ac": {"amount": 250000, "status": "registered"},
  "sv": {"value": null, "status": "not_computable", "reason": "ev_unregistered"},
  "cv": {"value": null, "status": "not_computable", "reason": "ev_unregistered"},
  "spi": {"value": null, "status": "not_computable", "reason": "ev_unregistered"},
  "cpi": {"value": null, "status": "not_computable", "reason": "ev_unregistered"},
  "eac": {"value": null, "status": "not_computable", "reason": "cpi_not_computable"},
  "etc": {"value": null, "status": "not_computable", "reason": "cpi_not_computable"},
  "vac": {"value": null, "status": "not_computable", "reason": "cpi_not_computable"},
  "ev_legacy": 0,
  "pv_legacy": 400000,
  "ac_legacy": 250000,
  "spi_legacy": null,
  "cpi_legacy": null,
  "meta": {
    "eac_method": "bac_over_cpi",
    "ev_basis": "approved_progress",
    "bac_source": "control_budget_version"
  }
}
```

### Rules

- When `ev.status=unregistered`, clients MUST show unregistered/not-computable UX—not “EV = 0”.
- `warnings` MUST include `baseline_not_locked` if schedule baseline unlocked; `budget_baseline_not_approved` if no control/approved budget version.
- `cpi` / `spi` MUST NOT be numeric when status is `not_computable`.
- EV MUST NOT equal AC solely because AC exists (contract test).

## UI

Project Progress KPI grid:

- Banner when `validity != valid` (baseline / budget messages, fa/en).
- Cards for PV/EV/AC with status labels.
- SPI/CPI/EAC/ETC/VAC show localized “not computable” when status says so.

## Test anchor

No approved progress + locked baselines + AC > 0 → `ev.status=unregistered`, `cpi.status=not_computable`, warning list empty for baseline if locked.
