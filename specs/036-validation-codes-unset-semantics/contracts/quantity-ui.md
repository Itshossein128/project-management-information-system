# Contract: Activity Quantity Cells

## Scoped surfaces

- `EditableGrid.tsx`: read-only quantity column for daily-report activities, reached through ActivityTab. Existing editable input/badge behavior remains functional.
- `summary/DailyReportSummaryView.tsx`: report.activities quantity column and general_activities quantity column.
- Existing daily-report form/view submit/reject feedback consumes workflow-api.md.

Other numeric fields, specialty-unit authoring redesign, equipment, materials, labor, concrete, totals and export formatting are outside scope. No new product route or standalone report creation flow.

## Quantity rendering

Use the existing shared UnsetQuantityBadge predicate: null/undefined quantity OR quantityMeasured === false means unset. Do not use `!quantity`, `quantity || ...`, or coerce null into zero.

- measured true + null → badge.
- measured false + null → badge.
- measured false + any numeric legacy value → badge, without data mutation.
- measured true + numeric/string zero → numeric zero, no badge.
- measured true + positive quantity → numeric quantity, no badge.
- General activities have no measured flag: null → badge; zero/non-null → numeric value.

The exact label is `ثبت‌نشده` in Persian and `Unset` in English via dailyReports.unsetQuantity. Decimal zero formatting may retain precision; it must remain recognizably numeric zero. Rows/cells, not an unrelated zero elsewhere in a row, are the assertion scope.

## Visual/accessibility requirements

Keep the existing compact badge text and muted neutral background; add an explicit caution-colored border or ring locally to UnsetQuantityBadge using existing warning tokens and light/dark support. Do not change the shared neutral Badge variant. The label supplies semantic meaning without reliance on color. Check outline visibility and readable contrast in both themes and locales; retain RTL/LTR layout and keyboard input behavior. Preserve data-testid=unset-quantity-badge and existing activity-quantity-readonly/editable hooks where applicable.

## Evidence requirements

Browser checks must assert exact text separately in FA/EN, distinguish null/false/legacy false-numeric/zero/positive and general-activity null/zero, switch locale, and inspect the actual border/background in both themes. Validate read-only grid plus summary; do not rely solely on the helper's predicate. Existing broad `ثبت‌نشده|Not recorded` regex assertions must be tightened rather than discarded. A controlled browser fixture may present legacy combinations that supported write APIs normalize, but must be labeled rendering evidence and cannot replace real API workflow tests.
