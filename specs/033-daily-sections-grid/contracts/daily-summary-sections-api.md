# Contract: Daily Summary Sections API (feature 033)

Base URL (established earlier): `/api/v1/projects/{project_pk}/daily-reports/…` — the read-only, auto-maintained project daily summary per date (`/by-date/{date}/`). All derived content in this contract is produced by the aggregation service; product users never create or edit it (032 rule, retained).

## 1. Summary retrieval shape extensions

`GET /daily-reports/by-date/{date}/` (and `retrieve`) extends the existing detail with, per section:

### 1.1 Executed activities
Rows with all FR-001 columns: `activity` (id+label), `activity_description`, `shift`, `contractor` (label), `crew_name` (separate field), `headcount`, `parcel`, `block`, `floor`, `location`, `quantity`, `unit`, `notes`, plus `provenance` (source version/unit/row, see §4). Empty vs zero vs unknown remain distinct fields (`null` = unknown/not provided; numbers are actual; empty list = no contributions).

### 1.2 Labor totals
- `labor.indirect_summary` / `labor.direct_summary` / `labor.overall_summary`: per resolved title aggregated `present_count`, `leave_count`, `overtime_hours`, computed `man_hours` (per effective rule), `title_code`, `display_order` (from the effective catalog), and per-unit breakdown when multiple sources exist.
- `labor.totals`: `{ indirect_man_hours, direct_man_hours, overall_man_hours, indirect_total_count, direct_total_count, overall_total_count }` — every total exposes `source_count > 1` markers and the drill-down must list every contributor (FR-012).

### 1.3 Machinery table
`machinery.rows[]`: `equipment_type`, `equipment_ref` (nullable, item-level), `status_total`, `status_active`, `status_ready`, `status_inactive`, `status_under_repair`, `operating_hours`, `stoppage_hours`, `repair_hours`, `stoppage_reason` (code + label), `provenance`. Type-level presentation rows sum item rows; a stable identity can appear exactly once (server dedupe); item rows without identity are counted per row. Response includes `vocabulary_revision_marker` of the effective snapshot.

### 1.4 Materials (main table = receipts only)
- `materials.main_table[]`: resolved receipts only — `material_description`/`material_ref`, `quantity`, `unit`, `warehouse_document_reference`, `supplier`, `receipt_evidence` (`resolved` / `unresolved_reference`), `provenance`. Generic/unclassified rows are never emitted here.
- `materials.details[]` (same retrieve payload or dedicated sub-endpoint `…/daily-reports/{pk}/materials/details/`): consumption rows and unresolved generic rows — `transaction_type`, `consumption_location`, `quantity`, `unit`, `provenance` — always included, never hidden behind the main table (FR-022).

### 1.5 Concrete
Rows with the full column set including `batching_plant`, `truck_delivery_note_number`, `lab_sample_code`, `sampling_state`, `test_sheet_count`, `qc_link` (id + href when sampling declared; `null` otherwise).

### 1.6 Structured narrative sections
- `general_activities[]`: structured rows (description, location/building, quantity/volume, unit, notes) in deterministic display order — no persisted formatted text.
- `issues[]`: structured (source unit, date, kind, text, owner, due date, order); `hse_incidents[]` (severity, immediate action, notification linkage); `visits[]` (structured, ordered). Other-type general notes appear only in a bounded `notes[]` narrative section and never as issues (FR-032).
- `attachment_counts`: per related section `{ row_kind_or_section, count, first_links[] }`; links resolve only for authorized project members (server-side re-check at fetch; no URL leaks).

### 1.7 Derived-row immutability
Every section payload is read-only through every endpoint; no `POST/PATCH/DELETE` exists on derived rows. Correction paths point to the source unit report (see UI contract §3).

## 2. Reconciliation (specific-warehouse-document anchor)

`GET …/daily-reports/{pk}/materials/reconciliation/` (endpoint retained; service reworked):

```json
{
  "items": [
    {
      "material_entry_id": "…",
      "transaction_type": "receipt" | "consumption",
      "material_ref": "… | null",
      "warehouse_document_reference": "… | null",
      "recorded_qty": "5.000",
      "document_qty": "5.000 | null",
      "status": "match" | "mismatch" | "insufficient_data",
      "evidence": { "resolved_document_id": "… | null", "basis": "specific_document" }
    }
  ]
}
```

Semantics: comparison is against the specific referenced warehouse document's recorded quantity (same project) — never the total historical inventory balance (FR-023). `insufficient_data` when the reference is missing, unresolvable, or the document lacks usable quantities (never a fabricated match). Evidence carries the resolved document id so the result is traceable (FR-024). The legacy global-balance value may appear only as an explicit `cross_check` advisory field, clearly labeled.

## 3. Rebuild behavior (unchanged guarantees, extended scope)

- Any section/data/attachment-affecting change to a contributing unit report (submit/approve/reject/correct/replace/delete) triggers or flags a rebuild; `ensure/rebuild` endpoints from 032 are retained.
- Rebuild remains atomic (`transaction.atomic`, existing lock order), idempotent (three consecutive rebuilds → identical payloads; fingerprint equality short-circuits), and deterministic. Extended fingerprint covers machinery, receipts/consumption, structured narrative, catalog rule + snapshot revision marker, vocabulary revision, attachment counts/checksums.
- Project-level overrides (weather/site-status) and management opinion are preserved untouched (FR-042).
- Mid-process failure leaves the previously valid summary intact (FR-038).

## 4. Provenance drill-down

Every derived row exposes `provenance: { source_report, source_report_version, source_unit, source_row_kind, source_row_id, contribution_value? }`; totals expose `provenance.rows[]` (multi-source, complete set — no last-source-wins). `GET …/daily-reports/{pk}/provenance/{derived_kind}/{derived_row}/` returns the full source map; resolving a source navigates to the unit page with unit-report view permission enforced (unauthorized users receive the standard denial without content disclosure, per Constitution I).

## 5. Permission summary

Read: 032 daily-report/project view permissions (server-side). Drill-down: adds the corresponding unit-report view permission per source; section-level attachment URLs additionally require project membership. No write surface exists for derived content.
