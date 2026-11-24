# QA Verification Report: Requirement A.1.03 (رفع اختلاف ارقام و نمایش خروجی‌ها)

## 1. Overview & Verification Context
- **Requirement ID**: `A.1.03`
- **Title**: رفع اختلاف ارقام و نمایش خروجی‌ها
- **Acceptance Criteria**: ساعت نامعلوم ماشین‌آلات صفر قطعی جلوه نکند و تست دقیق اضافه شود.
- **Verification Date**: 2026-11-24
- **Active Phase**: `A.1` (گزارش روزانه و خروجی‌ها)
- **Environments Checked**:
  - Web Frontend: `http://localhost:5173`
  - Backend API: `http://localhost:8000`

---

## 2. Authenticated End-User Browser Verification (UAT)
- **User Persona**: Admin (`+10000000001` / `devpass123`)
- **Authentication**: Successful login via `/login` and redirect to `/projects`.
- **Target Route**: `/delivery-plan`
- **Findings**:
  - Route `/delivery-plan` confirmed protected behind authentication layout.
  - Phase `A.1` and requirement `A.1.03` («رفع اختلاف ارقام و نمایش خروجی‌ها») are rendered under the active delivery plan.
  - Delivery plan item status in data definition: `remaining`, baseline window 2026-11-24 to 2026-11-25.

---

## 3. Backend & Parity Verification (Code & Tests)
- **Domain Coverage**: Daily Report machinery / equipment operating hours export and representation across Excel (`FILE 4`) and PDF.
- **Key Historical Issue & Gap Fix**:
  - Linked to `DEF-B03-05` (resolving historical strict XFAIL) and FR-012 under `specs/059-a1-b03-reference-parity/spec.md`.
  - Machine rows with unknown (`None` / `null`) operating hours must be displayed as unknown (blank or `—`), NEVER coerced or fabricated as `0`.
  - Explicit `0` or `0.00` operating hours must remain numeric `0`.
- **Automated Test Results**:
  - Executed: `field_reports/tests/test_pdf_summary_parity.py::test_b03_legacy_equipment_zero_and_unknown_across_exports`
  - Result: **PASSED** (asserts `{'Unknown machine': None, 'Measured machine': 0}` in Excel and `{'Unknown machine': '—', 'Measured machine': 0}` in PDF).
  - All 16 field report parity & aggregation test cases passed.

---

## 4. Assessment Summary
- **Implementation Status**: Fully implemented in backend generators (`ShirazFile4ExcelBuilder` and `pdf.generate_daily_report_pdf`) with rigorous regression test coverage (`test_b03_legacy_equipment_zero_and_unknown_across_exports`).
- **Defects / Gaps Identified**: None. The acceptance criteria («ساعت نامعلوم ماشین‌آلات صفر قطعی جلوه نکند و تست دقیق اضافه شود») are completely satisfied.
