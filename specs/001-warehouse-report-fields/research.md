# Research: Warehouse Report Fields

**Feature**: `001-warehouse-report-fields`  
**Date**: 2026-10-01

## 1. Schema strategy: extend shared record vs new model

**Decision**: Extend `inventory.DepartmentActivityRecord` with warehouse-specific columns and department-conditional validation. Do **not** introduce a separate warehouse activity model.

**Rationale**:
- Create/list/export/import/report already share one model, queryset helper, and URL set under `department-activity-records/`.
- Constitution Principle V favors the smallest coherent change.
- A second model would duplicate tenancy, permissions, pagination, and IO paths.

**Alternatives considered**:
- **Separate `WarehouseActivityRecord` model**: Cleaner domain purity; rejected due to duplicated endpoints/UI and migration of warehouse rows out of the shared table.
- **Reuse generic columns with remapping** (`activity_description` → material type, `contractor` → supplier, `location` → consumption location): Minimal migration; rejected because semantics diverge (contractor ≠ supplier) and inbound/outbound quantities still need new numeric columns—partial remap creates long-term confusion in admin/search/analytics.

## 2. Field storage and nullability

**Decision**:
- Add: `material_type` (string), `quantity_in` / `quantity_out` (`Decimal`, default `0`), `consumption_location` (string), `supplier` (string).
- Make existing generic fields `location`, `activity_description`, `contractor` **blank-allowed** at the DB level so warehouse rows need not invent placeholder values.
- Keep `unit` and `description` shared; warehouse always requires `unit` (warehouse uses unit today via `department_uses_unit`).

**Rationale**: Matches existing `SpaceMaterialRequest` decimal pattern (`max_digits=14`, `decimal_places=3`). Blank generic fields for warehouse avoid fake data. Default `0` for quantities simplifies “at least one positive” validation.

**Alternatives considered**:
- Nullable decimals (`NULL` meaning unset): Slightly clearer empty state; rejected in favor of `0` defaults consistent with other inventory quantities and simpler Excel round-trip.
- JSON blob for warehouse extras: Flexible; rejected—hurts filtering, sorting, OpenAPI clarity, and admin search.

## 3. Validation ownership

**Decision**: Enforce department-aware rules primarily in `DepartmentActivityRecordSerializer.validate` (and mirror the same rules in Excel import). Add helpers such as `is_warehouse_department(department)` beside `department_uses_unit`.

**Warehouse rules**:
- Required: `date`, `material_type`, `unit`, `consumption_location`, `supplier`
- Optional: `description`
- `quantity_in` / `quantity_out` ≥ 0; at least one > 0
- Clear generic fields to empty on warehouse create/update; clear warehouse fields to empty/zero on non-warehouse create/update

**Rationale**: Server-side enforcement (Constitution I/II). Client validation is UX-only. Import must not bypass API rules.

**Alternatives considered**:
- Model.`clean()` only: Easy to miss from `objects.create` in import; serializer + shared validation function called from both serializer and import is safer.
- Database CHECK constraints only: Good complement later; not sufficient alone for bilingual error messages.

## 4. API shape

**Decision**: Keep the same REST resources. Expand the serializer field list to include warehouse columns. Clients send the field set appropriate to `department`; responses may include both sets (unused side empty/zero).

**Rationale**: Avoids breaking URL contracts and React Query keys. Frontend already posts `department` on create.

**Alternatives considered**:
- Separate warehouse endpoints: Clearer contracts; rejected as unnecessary surface area for one department variant.
- Discriminated union response with `schema: "warehouse" | "generic"`: Nice for clients; can be a later additive enhancement—v1 uses empty unused fields.

## 5. Frontend department-aware UI

**Decision**: Branch inside existing `DepartmentActivityRecordModal` and `department-page` columns/filters when `department === "warehouse"`. Extend `api-types.ts` with warehouse fields and a helper (e.g. `isWarehouseDepartment`).

**Rationale**: Matches current “security hides unit” pattern (`departmentUsesUnit`). Sticky-field scope already keys by department.

**Alternatives considered**:
- Separate warehouse modal component file: Cleaner file size if form grows; optional refactor during implementation if the modal becomes unwieldy—default is inline branch for minimal churn.

## 6. Excel / PDF

**Decision**: `export_headers_for_department` and import required-column sets become warehouse-aware. Warehouse headers: `date`, `material_type`, `quantity_in`, `unit`, `quantity_out`, `consumption_location`, `supplier`, `description` with Persian/English aliases. PDF daily/weekly tables use the same warehouse columns when `department=warehouse`.

**Rationale**: Spec FR-008/FR-009; existing IO already branches on `department_uses_unit`.

## 7. Legacy data migration

**Decision**: Schema migration only (add columns with defaults/blank; alter generic fields to `blank=True`). Do **not** auto-map old warehouse `location`/`contractor`/`activity_description` into new fields. Legacy warehouse rows remain listable with empty new fields until edited; removed fields are no longer required for warehouse writes.

**Rationale**: Spec FR-011 and Assumptions—avoid incorrect semantic remapping. Operators can re-enter material data if needed.

**Alternatives considered**:
- Heuristic copy (`location` → `consumption_location`, etc.): Faster continuity; rejected as silent wrong data risk for material type/supplier/quantities.

## 8. TDD approach

**Decision**: Add failing pytest cases first for:
1. Warehouse create validation (happy path + both quantities zero + negatives + missing required)
2. Non-warehouse create still requires generic fields and rejects dependence on warehouse-only fields
3. Warehouse list filters/search on new fields
4. Warehouse Excel export headers + import create + invalid row errors
5. Warehouse PDF report column content (smoke)

Then implement model/serializer/services/IO/UI until green. Frontend type updates accompany API contract; browser verify form after API green.

**Rationale**: Spec FR-014 / SC-006; AGENTS.md mandates pytest for Django tests.

## 9. Resolved clarifications

| Topic | Resolution |
|-------|------------|
| Warehouse-only vs all departments | Warehouse-only (spec assumption) |
| Quantity types | Decimal quantities, shared unit |
| Master data for material/supplier | Free text v1 |
| Consumption location linkage | Free text v1 |
| Legacy remapping | No automatic remap |
| API versioning | Additive fields on existing endpoints |
