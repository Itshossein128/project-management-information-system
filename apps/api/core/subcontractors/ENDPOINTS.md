# Subcontractors Endpoints

Subcontractor registry linked to contracts, performance scorecards, warning timeline, and automated risk flags. Financial summaries derive from linked contract IPCs and deductions.

Base URL: `/api/v1/projects/{project_pk}/subcontractors/`

## Permissions

| Action | Permission |
|--------|------------|
| List, retrieve, scores (GET), warnings (GET), risk-summary | `view_contracts` + `IsProjectMember` |
| Create, update, delete, POST scores/warnings | `edit_contracts` |

## Endpoints

### 1. Subcontractor Registry

*   **URL:** `/subcontractors/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: List with computed `risk_flag`, `risk_reasons`, `latest_score`, `financial_summary` (outstanding, retention).
    *   **Query filters:** `status`, `discipline` (icontains), `risk_only=true`
    *   `POST`: Create. Fields: `company_name`, `contract` (UUID, optional), `discipline`, `responsible_person`, `phone`, `status`.

*   **URL:** `/subcontractors/{pk}/`
*   **Methods:** `GET`, `PATCH`, `DELETE`
*   **Description:**
    *   `GET`: Detail with `contract_summary`, full `financial_status`, score history metadata.
    *   `PATCH`: Partial update.
    *   `DELETE`: Soft-delete (`is_deleted=true`).

### 2. Risk Summary

*   **URL:** `/subcontractors/risk-summary/`
*   **Method:** `GET`
*   **Description:** All at-risk subcontractors with `risk_reasons`. Cached 1 hour.

### 3. Performance Scores

*   **URL:** `/subcontractors/{pk}/scores/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: Score history plus `average_overall` and `trend` (`improving` | `declining` | `stable`).
    *   `POST`: Create score. Required: `score_date`, `progress_score`, `hse_score`, `evaluator`. Optional dimension scores (0–10): `quality_score`, `payment_compliance_score`, `cooperation_score`, `notes`. `overall_score` is computed automatically (weighted average).

*   **URL:** `/subcontractors/{pk}/scores/{scid}/`
*   **Methods:** `PATCH`, `DELETE`
*   **Description:** Update or soft-delete a score.

**Overall score weights:** progress 30%, quality 25%, HSE 25%, payment compliance 10%, cooperation 10%.

### 4. Warnings

*   **URL:** `/subcontractors/{pk}/warnings/`
*   **Methods:** `GET`, `POST`
*   **Description:**
    *   `GET`: Warning timeline (newest first).
    *   `POST`: Create warning (`warning_type`, `warning_date`, `description`, etc.).

*   **URL:** `/subcontractors/{pk}/warnings/{wid}/`
*   **Method:** `PATCH`
*   **Description:** Update warning; setting `resolved=true` auto-fills `resolved_date` if empty.

## Risk flag logic (`compute_risk_flag`)

A subcontractor is flagged when any of:

1. Latest `overall_score` &lt; 6
2. Unresolved warning of type written, final, or contract suspension
3. Status is `suspended`
4. Linked contract activity progress lags plan by &gt;15%

Risk evaluation also feeds the `subcontractor_at_risk` and `subcontractor_score_low` alert types.

## Financial summary (linked contract)

When `contract_id` is set, `financial_summary` includes:

- `total_billed` — approved/paid IPC gross amounts
- `total_paid` — paid IPC net amounts
- `outstanding`, `retention_held`, `advance_paid`, `advance_recovered`, `advance_remaining`

## Cache invalidation

Create/update/delete on subcontractors, scores, or warnings invalidates project caches (`subcontractor_risk`, etc.).
