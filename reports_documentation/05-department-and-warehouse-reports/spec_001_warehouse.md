# Feature Specification: Warehouse Report Fields

**Feature Branch**: `001-warehouse-report-fields`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Warehouse reports form needs fields: تاریخ، نوع مصالح، ورودی، واحد، خروجی، محل مصرف، تامین‌کننده، and توضیحات. Remove the rest of fields. Use TDD. Update related parts across the application (API, DB, validations, tables, etc.)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record warehouse material movement (Priority: P1)

As a warehouse operator, I open the warehouse activity/report create form and enter only the warehouse-relevant fields (date, material type, inbound quantity, unit, outbound quantity, consumption location, supplier, and notes). I can save a valid record without seeing or filling the old generic activity fields (location, contractor, activity description).

**Why this priority**: This is the core operational change. Warehouse staff currently see the wrong form shape and cannot capture material in/out data correctly.

**Independent Test**: Open the warehouse create form, fill the eight warehouse fields with valid values, submit, and confirm the new record appears with those values.

**Acceptance Scenarios**:

1. **Given** a user with access to a project's warehouse department, **When** they open the create form, **Then** they see exactly: تاریخ، نوع مصالح، ورودی، واحد، خروجی، محل مصرف، تامین‌کننده، توضیحات — and no generic activity fields (موقعیت، پیمانکار، شرح فعالیت).
2. **Given** the create form with required warehouse fields completed (date, material type, unit, and at least one of inbound or outbound greater than zero), **When** the user submits, **Then** the record is saved and listed with the entered warehouse values.
3. **Given** the create form with both inbound and outbound left empty or zero, **When** the user submits, **Then** the system rejects the save and shows a clear validation message.

---

### User Story 2 - Browse and find warehouse records with the new columns (Priority: P1)

As a warehouse operator or project manager, I view the warehouse activity table and see columns that match the warehouse field set so I can scan material movements without irrelevant columns.

**Why this priority**: Creating records is useless if the list still shows the old schema and hides inbound/outbound and material type.

**Independent Test**: With at least one warehouse record present, open the warehouse department list and verify column headers and cell values match the warehouse field set.

**Acceptance Scenarios**:

1. **Given** existing warehouse records with the new fields, **When** the user opens the warehouse department page, **Then** the table columns are: تاریخ، نوع مصالح، ورودی، واحد، خروجی، محل مصرف، تامین‌کننده، توضیحات (or a clearly equivalent localized set without legacy columns).
2. **Given** a warehouse list, **When** the user searches or filters by material type, consumption location, or supplier, **Then** matching records are returned.

---

### User Story 3 - Non-warehouse departments stay unchanged (Priority: P2)

As a buildings, mechanical, electrical, machinery, or security operator, I continue to use the existing activity-log fields (date, unit where applicable, location, contractor, activity description, description) without warehouse-only fields appearing.

**Why this priority**: The warehouse field change must not break other department workflows that still use the generic activity schema.

**Independent Test**: Open any non-warehouse department create form and list; confirm the legacy field set remains and warehouse-only fields are absent.

**Acceptance Scenarios**:

1. **Given** a non-warehouse department, **When** the user opens the create form, **Then** they still see the existing generic activity fields and do not see نوع مصالح، ورودی، خروجی، محل مصرف، or تامین‌کننده.
2. **Given** existing non-warehouse activity records, **When** the user views the department table, **Then** columns and values remain consistent with the previous generic schema.

---

### User Story 4 - Import, export, and reports use warehouse fields (Priority: P2)

As a warehouse operator, I can import and export warehouse activity data, and view daily/weekly warehouse summaries, using the new warehouse columns so Excel and report workflows stay aligned with the form.

**Why this priority**: Import/export and summary reports are daily warehouse operations; mismatched columns cause data loss and rework.

**Independent Test**: Export warehouse data, confirm headers match warehouse fields; import a valid warehouse file; open daily/weekly views and confirm warehouse-relevant values appear.

**Acceptance Scenarios**:

1. **Given** warehouse records, **When** the user exports, **Then** the file columns match the warehouse field set (not the removed generic fields).
2. **Given** a valid warehouse import file with the new columns, **When** the user imports, **Then** records are created/updated with those values and invalid rows are rejected with clear errors.
3. **Given** warehouse records spanning days, **When** the user opens daily or weekly warehouse reports, **Then** summaries reflect the warehouse field data (material movements) rather than removed generic activity attributes.

---

### Edge Cases

- Both inbound and outbound are zero or blank → reject with a validation message requiring at least one positive quantity.
- Negative inbound or outbound values → reject.
- Very large quantities → accept within agreed numeric limits; reject values outside those limits with a clear message.
- Material type, consumption location, or supplier longer than allowed length → reject or truncate per validation rules with a clear message (prefer reject with message).
- Optional notes (توضیحات) left blank → allow save.
- Existing warehouse records created under the old field set → after migration they remain readable; missing new fields show empty/default values; removed fields are no longer required for warehouse create/edit.
- Non-warehouse records are unaffected by warehouse field validation.
- Bilingual UI: Persian and English labels both present for every warehouse field; date entry remains locale-correct.
- Concurrent create of two warehouse records with the same date and material → both allowed (no uniqueness constraint unless already enforced elsewhere).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: For the warehouse department only, the create/edit form MUST present exactly these fields: تاریخ (date), نوع مصالح (material type), ورودی (inbound quantity), واحد (unit), خروجی (outbound quantity), محل مصرف (consumption location), تامین‌کننده (supplier), توضیحات (notes).
- **FR-002**: For the warehouse department, the system MUST NOT present or require the removed generic fields: موقعیت (location), پیمانکار (contractor), شرح فعالیت (activity description).
- **FR-003**: Non-warehouse departments MUST retain their existing activity-log field set and behavior.
- **FR-004**: Warehouse date, material type, unit, and consumption location MUST be required. Supplier MUST be required. Notes MUST be optional. At least one of inbound or outbound MUST be a positive number.
- **FR-005**: Inbound and outbound MUST be numeric quantities greater than or equal to zero (when provided); negative values MUST be rejected.
- **FR-006**: The warehouse list/table MUST display columns aligned with FR-001 and MUST NOT show the removed generic columns for warehouse.
- **FR-007**: Warehouse search/filter/sort surfaces MUST operate on the warehouse field set (including material type, consumption location, and supplier) instead of the removed generic fields.
- **FR-008**: Warehouse Excel import and export MUST use the warehouse field set and MUST validate rows with the same rules as the form.
- **FR-009**: Warehouse daily and weekly report views MUST reflect the warehouse field set so operators can review material movements without relying on removed fields.
- **FR-010**: Persisted warehouse records MUST store the warehouse field values end-to-end so create, list, detail, import, export, and reports show consistent data.
- **FR-011**: Existing warehouse records MUST be migrated or mapped so the application remains usable: new required fields may be empty for legacy rows until edited; removed fields MUST NOT block warehouse workflows going forward.
- **FR-012**: All warehouse field labels, validation messages, table headers, and import/export headers MUST be available in Persian and English.
- **FR-013**: Server-side validation MUST enforce the warehouse field rules regardless of client behavior; unauthorized users MUST NOT create or modify warehouse records outside project permissions.
- **FR-014**: Delivery MUST follow a test-driven approach: failing tests for warehouse field behavior are written first, then implementation is updated until those tests pass, covering form validation, persistence rules, list/report presentation contracts, and import/export validation for warehouse.

### Key Entities

- **Warehouse Activity Record**: A project-scoped warehouse department entry capturing a material movement on a date. Attributes: date, material type, inbound quantity, unit, outbound quantity, consumption location, supplier, optional notes. Distinct field shape from generic department activity records.
- **Generic Department Activity Record**: Unchanged activity-log entry for non-warehouse departments (date, location, activity description, contractor, unit where applicable, notes).
- **Warehouse Import/Export Row**: Tabular representation of a warehouse activity record used for bulk transfer; column set matches the warehouse fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Warehouse operators can create a valid warehouse record using only the eight specified fields in under 2 minutes in a standard project context.
- **SC-002**: 100% of newly created warehouse records persist and redisplay all entered warehouse field values correctly on list, export, and report views.
- **SC-003**: 0 non-warehouse department create or list flows regress: other departments still complete create/list with the previous field set without warehouse-only fields appearing.
- **SC-004**: Invalid warehouse submissions (missing required fields, both quantities zero, negative quantities) are rejected with a user-visible message in 100% of tested cases, including when bypassing the client form.
- **SC-005**: Warehouse Excel round-trip (export then import of valid data) preserves field values for at least 95% of rows in a representative sample (remaining differences limited to documented formatting normalizations such as date display).
- **SC-006**: Focused automated tests for warehouse field rules exist before implementation is considered complete, and those tests pass against the final behavior (TDD evidence).

## Assumptions

- Scope is **warehouse department only**; other departments keep the current generic activity-log schema.
- "تامیین کننده" in the request means **تامین‌کننده** (supplier).
- ورودی and خروجی are **numeric quantities** (not free text), in the same unit selected on the record.
- A single warehouse record may include both inbound and outbound on the same date for the same material; at least one quantity must be greater than zero.
- محل مصرف is free text (same style as the previous location field), not a forced link to another master entity in this change.
- نوع مصالح and تامین‌کننده are free-text (optionally with creatable suggestions later); no mandatory master-data picklist is required for v1.
- Existing shared create modal/list/import/export/report surfaces become **department-aware**: warehouse uses the new schema; others keep the old schema.
- Legacy warehouse rows may have empty new fields after migration; users can edit them later. Historical values in removed fields may be retained for audit/migration but are not shown or required in warehouse UI.
- Permissions, project tenancy, and sticky-field UX patterns remain as today unless they conflict with the new field set.
- TDD is a delivery constraint for this feature: tests define expected warehouse behavior first, then implementation follows across create/list screens, stored records, validation, tables, and related report/import/export paths.
