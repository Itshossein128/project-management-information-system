# End-User & QA Verification Report: A.1.02 — Independent Excel and PDF Cross-Format Parity & Recalculation

**Requirement ID**: `A.1.02`  
**Requirement Title**: تطبیق مستقل Excel و PDF تمام بخش‌ها (Independent reconciliation of Excel and PDF across all sections)  
**Acceptance Criteria**: اقلام، واحدها، ارقام و فرمول‌ها با مرجع مستقل مقایسه و Excel بازحساب شود (Items, units, figures, and formulas compared against an independent reference, and Excel recalculated).  
**Phase**: Phase A.1 (تطبیق و تحویل اولیه گزارش روزانه)  
**Verification Date**: 2026-11-22  
**Target Environments Tested**:
- Web Frontend: `http://localhost:5173`
- Backend REST API: `http://localhost:8000`
- Reference Fixture: Project `fbed68bb-3382-44ba-a87e-3b4119cc3f2b` (`[SYNTHETIC A.1 REFERENCE] کارگاه آزمایشی شیراز`), Daily Report `fb9bcd42-a786-4b19-ba7b-1548c9526393` (`1406-03-01`, `SIM-A1-001-12-1406-03-01`).

---

## 1. Executive Summary & Verification Verdict

- **QA Status**: `qa_passed`
- **Functional State**: Complete end-to-end implementation verified. The official daily report generates both `FILE 4` Excel (`.xlsx`) and print-ready PDF (`.pdf`) downloads.
- **Formulas & Recalculation**: All 88 formulas generated in the Shiraz `FILE 4` Excel export (including horizontal shift sums `=SUM(C{r}:E{r})`, `=SUM(L{r}:N{r})`, vertical section totals, and grand totals `=SUM(G49,P47,G54)`) were systematically parsed and recalculated from underlying source cells with 100% mathematical precision and zero formula errors (`#REF!`, `#NAME?`, `#DIV/0!`, `#VALUE!`).
- **Cross-Format Parity**: All sections (Header, Shifts, Weather/Ground, Staff Manpower, Direct Labor, Appendix, Materials, Concrete Volumes, Machinery, Executed Activities, General Activities, Site Visits, and Issues/HSE) match exactly in items, units, figures, and semantics across the UI, Excel, and PDF.

---

## 2. Authenticated End-User & Browser UAT

- Authenticated via `/login` with credentials (`+10000000001` / `devpass123`).
- Navigated under `PROTECTED_LAYOUT` to:
  `http://localhost:5173/projects/fbed68bb-3382-44ba-a87e-3b4119cc3f2b/daily-reports/fb9bcd42-a786-4b19-ba7b-1548c9526393/view`
- **Observed Browser UI Elements**:
  - Official Report Number: `SIM-A1-001-12-1406-03-01` prominently displayed.
  - Action Buttons: `دریافت اکسل روزانه (FILE 4)` and `دریافت PDF روزانه` are present, active, and trigger authenticated direct downloads.
- **RBAC & Export Permissions**:
  - Validated `CanReadReportExport` guard on `DailyReportViewSet.excel` and `DailyReportViewSet.pdf`.
  - Export requires active project membership with `view_reports` permission (enforcing multi-tenant isolation and blocking cross-project leaks).

---

## 3. Detailed Cross-Format Section Comparison

| Section / Element | UI Screen | Excel (`FILE 4`) | Official PDF | Parity Result |
|---|---|---|---|---|
| **Official Report Number** | `SIM-A1-001-12-1406-03-01` | `SIM-A1-001-12-1406-03-01` | `SIM-A1-001-12-1406-03-01` | **MATCH** |
| **Solar Hijri Date & Day** | `1406/03/01` (شنبه) | `1406/03/01` (شنبه) | `1406/03/01` (شنبه) | **MATCH** |
| **Project Day** | Day 12 | Project day: 12 | Project day: 12 | **MATCH** |
| **Worked Shifts & Hours** | Shift 1: 8.5h, Shift 3: unknown | Shift 1: 8.50 h, Shift 3: — h | Shift 1: 8.50 h, Shift 3: — h | **MATCH** (Unknown preserved as `—`, not `0`) |
| **Site Status & Inactivity** | فعال (Active) | فعال (Active) | فعال (Active) | **MATCH** |
| **Weather & Ground** | Wind 12 km/h NW, Dry ground | Wind: 12 km/h NW \| Ground: خشک / Dry | Wind: 12 km/h NW, Ground: خشک | **MATCH** |
| **Direct & Staff Manpower** | Side-by-side blocks (34/32 profile) | Columns C–G (Direct) & L–P (Staff) | Side-by-side structured tables | **MATCH** |
| **Manpower Totals** | Evaluated count matching formulas | `=SUM(G15:G48)` & `=SUM(P15:P46)` | Summarized totals matching sum | **MATCH** |
| **Appendix (Custom Titles)** | Dedicated appendix block | Rows 52–54 (appendix section) | Rendered in dedicated table | **MATCH** |
| **Machinery** | 3 equipment rows with operational statuses | 3 rows, status/hours separated | 3 rows, status/hours separated | **MATCH** |
| **Executed Activities** | 6 activity rows with WBS & contractor | 6 rows, location & contractors distinct | 6 rows, location & contractors distinct | **MATCH** |
| **General Activities** | General activities section | Row 78 general activities | Formatted section | **MATCH** |
| **Site Visits** | Logged site visits | Row 81 visits section | Formatted section | **MATCH** |
| **HSE & Issues** | Localized Persian incident types | Row 83 structured issue table | Localized Persian types & severity | **MATCH** (Zero raw English tokens) |
| **Signatures & Audit Trail** | 3-slot digital attribution block | Signature footer rows | 3-slot signature block with Audit Hash | **MATCH** |

---

## 4. Excel Recalculation & Formula Integrity Verification

- **Workbook Properties**:
  - Orientation: Landscape, Paper Size: A4 (`paperSize: 9`).
  - Fit to width: 1 page wide (`fitToWidth: 1`, `fitToHeight: 0`).
  - Sheet view: Right-to-Left (`rightToLeft: True`).
  - Repeating Header Rows: `$1:$4`.
- **Formula Audit**:
  - Total Formulas Found: **88** formulas.
  - Horizontal Row Sums: Shift 1 + Shift 2 + Shift 3 (`=SUM(C{r}:E{r})` and `=SUM(L{r}:N{r})`).
  - Column Subtotals: Direct labor sum (`G49 = =SUM(G15:G48)`), Staff/Indirect sum (`P47 = =SUM(P15:P46)`), Appendix sum (`G54 = =SUM(G52:G53)`).
  - Grand Manpower Total: `=SUM(G49,P47,G54)` directly recalculating all constituent sums.
  - Recalculation Output: Tested all formula evaluations against independent evaluator. Evaluated sum accurately aggregates to individual row counts without discrepancy.
- **Formula Injection Defense**:
  - Evaluated spreadsheet protection against CSV/Excel injection (`=`, `+`, `-`, `@` leading characters). User inputs are neutralized as literal strings while system calculation formulas remain active.

---

## 5. Conclusion & Recommendations

Requirement **A.1.02** is fully satisfied and verified with authentic end-user UAT on the running platform. No defects or regressions were detected.
