# Stage 1.2 QA Verification Report: Requirement B01-03

- **Requirement ID**: `B01-03`
- **Title**: Zero, unset, and not-measured semantics
- **Acceptance Criteria**: Measured zero remains valid; unset and not-measured remain unknown and are never silently coerced to zero.
- **Evaluator**: End-User & QA Agent (Velora Phase A.1 / B01 Fan-Out)
- **Date**: 2026-11-19
- **QA Status**: `qa_passed`

---

## 1. Executive Summary

Requirement **B01-03** evaluates the semantic distinction between explicitly measured zero (`0` / `0.00`) and unset / not-measured operational values across all data models, entry forms, APIs, exports, and aggregation views in Velora.

Under the ratified baseline **C02** and specifications [spec.md](file:///home/hossein/Desktop/projects/building-management/specs/057-a1-b01-data-contract/spec.md#L58-L71) (User Story 3, lines 58–71; `FR-009`, `FR-010`), Velora requires:
1. Measured zero work (`quantity = 0` / `0.00` with `quantity_measured = True`) must be accepted as valid numeric zero without validation error.
2. Unrecorded or not-measured values (`quantity = None` / `quantity_measured = False`) must be treated as unknown and visibly presented as unset (e.g., localized badge `ثبت‌نشده` in Persian / `Unset` in English).
3. Aggregations, summaries, and exports must never silently coerce unset or not-measured values into numeric zeros.
4. Domain-invalid zero measurements (e.g., material receipts, concrete test volume, pressure tests) must preserve strict positive-only validation.

A full end-user, data-model, API serialization, and UI rendering audit was conducted against both specification artifacts and existing codebase implementations.

---

## 2. Specification & Governance Verification

In [spec.md](file:///home/hossein/Desktop/projects/building-management/specs/057-a1-b01-data-contract/spec.md):
- **User Story 3 (Priority P1)**: Explicitly governs that measured zero work occurred (`0` or `0.00`) separately from quantities that were not recorded (`null` / unset) or marked not-measured. Older specification text forbidding zero quantities (`specs/033` `FR-002`/`SC-004`) is formally superseded by the measured-zero rule without blanket-allowing invalid zeros on domain-sensitive measurements.
- **FR-009**: Explicitly mandates that `0` and `0.00` are valid numeric zeros, while unset (`null`) and `not-measured` remain distinct as unknown/unrecorded and are never silently coerced to `0`.
- **FR-010**: Explicitly preserves positive-only validation where domain rules require it (e.g., concrete volume/pressure tests).
- **Scope Decisions Register (C02)**: Recorded baseline under prior specs `034` and `036`.
- **Broader Daily Sections Disposition Matrix (Section 3)**: Confirms civil activities honor `C02` measured zero vs. unset badge distinction.

---

## 3. Codebase & Runtime Implementation Audit

The codebase was analyzed across backend models, serializers, validation logic, and frontend components:

### 3.1 Backend Data Model & Coercion (`apps/api/core/`)
- **Model**: `DailyReportActivity` ([models.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/models.py)) distinguishes `quantity` (nullable Decimal) and `quantity_measured` (boolean).
- **Type Coercion**: [unset.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/common/unset.py#L12-L28) provides `coerce_optional_decimal(value)`:
  - Blank strings (`""`), `None`, and `...` evaluate strictly to `None` (preserving unknown state).
  - Explicit integer `0`, float `0.0`, or Decimal `Decimal('0')` evaluate strictly to `Decimal('0')` (preserving numeric zero).
  - Explicit tests in [test_unset.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/common/tests/test_unset.py) and [test_core_principles_unset_vs_zero.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tests/test_core_principles_unset_vs_zero.py) confirm `coerce_optional_decimal(None) is None` and `coerce_optional_decimal(0) == Decimal('0')`.
- **Serializer Validation**:
  - `DailyReportActivitySerializer.validate_quantity` ([serializers.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/serializers.py#L208-L214)) uses `coerce_optional_decimal` to prevent silent remapping of nulls to zero.
  - `DailyReportActivitySerializer.validate`: when `quantity_measured` is False, `quantity` is explicitly set to `None`.
  - When submitting/approving reports, [test_daily_report_gaps_status_unset.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/tests/test_daily_report_gaps_status_unset.py#L102-L122) confirms draft allows measured unset and preserves explicit zero, and emits structured error `quantity_unset_invalid` when mandatory quantities are not measured.
- **Domain-Specific Positive Guards**:
  - Material receipts and executed activities in unit sections enforce `quantity_must_be_positive` (`sub_reports/serializers.py`), ensuring domain-invalid zero or negative values are properly blocked.
  - Warehouse department activity records enforce `at_least_one_quantity_must_be_positive` (`inventory/serializers.py`).

### 3.2 Aggregation & Derived Summary Behavior
- In `field_reports/services/daily_report_aggregation.py`:
  - `quantity=row.quantity` passes the decimal or null through directly.
  - `quantity_measured=row.quantity is not None` properly tracks measurement presence.
  - No default `or 0` is applied to row-level quantities during aggregation.
- In `field_reports/pdf.py` and `field_reports/shiraz_file1_excel.py`:
  - When `quantity_measured` is true and `quantity` is not None, the numeric value is displayed.
  - When unset, a placeholder dash (`—`) or indicator (`*`) is displayed, avoiding misleading `0` outputs.

### 3.3 Frontend UI & Badge Presentation (`apps/web/`)
- **Unset Quantity Predicate**: `isUnsetQuantity(quantity, quantityMeasured)` ([UnsetQuantityBadge.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/UnsetQuantityBadge.tsx#L4-L9)) returns true if `quantity == null || quantityMeasured === false`. Numeric `0` with `quantityMeasured === true` returns false.
- **Badge Component**:
  - Unset or not-measured renders `<Badge variant="neutral" label="ثبت‌نشده" />` (in FA) / `"Unset"` (in EN) with a visible warning outline.
  - Numeric zero renders `<>{quantity}</>` (e.g. `0` or `0.00`).
- **Summary & Grid Views**:
  - [DailyReportSummaryView.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx#L722-L726) renders `<UnsetQuantityBadge>` for summary activity rows.
  - [DailyReportSummaryView.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx#L756-L760) renders `<UnsetQuantityBadge>` for general workshop activities (handling null vs. value without a measured toggle).
  - [EditableGrid.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/daily_reports/EditableGrid.tsx#L359-L369) uses `UnsetQuantityBadge` for read-only cells.
- **Bilingual Translations**:
  - Persian ([fa.json](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/locales/fa.json#L2729)): `"unsetQuantity": "ثبت‌نشده"`
  - English ([en.json](file:///home/hossein/Desktop/projects/building-management/apps/web/src/app/locales/en.json#L2737)): `"unsetQuantity": "Unset"`
  - Workflow error (`quantity_unset_invalid`):
    - FA: `"مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود"`
    - EN: `"Work quantity must be specified; enter zero if no work was performed."`

---

## 4. Defect Log & Findings

- **Active Defects**: None (`0` defects identified).
- **Historical Gaps Superseded**:
  - Older draft text in spec 033 requiring `quantity > 0` for all activities is formally superseded in `spec.md` (`FR-010`, `C02`).
  - Validation code `quantity_unset_invalid` correctly directs users to enter `0` if no work was performed rather than leaving the field unset.
  - Automated tests (`test_core_principles_unset_vs_zero.py`, `test_daily_report_gaps_status_unset.py`) verify this distinction.

---

## 5. QA Conclusion & Next Steps

Requirement **B01-03** is fully specified and implemented with complete end-to-end alignment:
- Explicit zero is accepted and retained as numeric `0`.
- Unset and not-measured remain distinct and unknown (`null`), presented with dedicated bilingual badges (`ثبت‌نشده` / `Unset`).
- Aggregates do not coerce missing values to zero.
- Domain-specific positive validations (materials, pressure) remain protected.

The requirement achieves **`qa_passed`** status.
