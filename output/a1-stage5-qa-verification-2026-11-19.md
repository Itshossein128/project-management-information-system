# Stage 5 End-to-End QA Verification Report: Phase A.1 (B01–B06)

**Evaluation Date:** 2026-11-19T17:56:00+03:30  
**Target Environments:** Velora Web (`http://localhost:5173`) & Velora API (`http://localhost:8000`)  
**Assigned Phase:** Phase A.1 (Packages B01–B06: Data Contract, Version Integrity, Reference-Form Parity, Filters & Totals, Formula Reconciliation, Delivery Bundle)  
**Evaluator:** Per-Requirement End-User QA Agent  

---

## 1. Executive Summary & Verdict

- **Overall QA Status:** `qa_failed`
- **Root Cause & Operational Summary:**
  1. **Runtime Offline:** Live services (`localhost:5173` Vite web frontend and `localhost:8000` Django REST API) are offline and refusing connections. PostgreSQL (port 5433) and Redis (port 6379) are not running on the local host.
  2. **Upstream Implementation Pipeline Blocked:** Spec-Driven Development for Phase A.1 was halted prior to implementation. While `specs/057-a1-b01-data-contract/spec.md` exists in draft form, planning (`plan.md`) and task breakdown (`tasks.md`) were blocked awaiting employer scope ratification for decisions `C03`–`C08` (`C04` and `C06` deferred to Round 2). No implementation tasks were dispatched or executed for Phase A.1.
  3. **Episodic & Prior Defect History:** Audits of Stage 1 across packages B01 through B06 reveal critical unaddressed functional, integrity, and security defects across all end-user personas.

---

## 2. Multi-Persona End-User Evaluation

### Persona 1: Field Engineer / Site Technician (ثبت و تنظیم گزارش روزانه کارگاه)
- **Workflow:** Attempts to record daily shift operations, manpower breakdown, equipment logs, and weather details.
- **Failures Encountered:**
  - Cannot access the web application at `http://localhost:5173` (Connection Refused).
  - Data model lacks `report_number`, `project_day_number`, and shift actual duration fields (`DEF-B01-01`, `DEF-B01-02`).
  - Shift duration defaults to hardcoded placeholder `"ساعات کاری شیفت: ثبت نشده"` in exports.
  - Headcount sums treat raw attendance counts as "نفرروز" without verified individual worker presence (`DEF-B01-03`).

### Persona 2: Supervising Engineer / Technical Reviewer (بررسی، تأیید و نسخه‌گذاری گزارش)
- **Workflow:** Audits daily submission, creates revision/correction versions, and verifies provenance.
- **Failures Encountered:**
  - In correction workflows, `is_auto_summary` flag drops to `False` on the target copy (`DEF-B02-01`), allowing direct manual modification of derived rows (`DEF-B02-02`).
  - Derived source lineage links (`DailyReportDerivedSource`) fail to re-map during clone operations (`DEF-B02-03`).
  - Reviewer notes (`management_opinion`) and `weather_override` are wiped during version cloning (`DEF-B02-04`).

### Persona 3: Client Representative / Employer (پذیرش و تحویل‌گیری رسمی خروجی اکسل/PDF)
- **Workflow:** Downloads and validates official Excel/PDF exports against the reference standard.
- **Failures Encountered:**
  - Excel exports lack pre-evaluated formula results/cached values, displaying `None`/empty cells unless manually opened in MS Excel (`DEF-B05-01`).
  - Visual layout discrepancies, truncated notes, missing wind/ground condition integrations (`DEF-B01-05`, `DEF-B03-01`).
  - No frozen release package with verified SHA-256 digests or client acceptance protocol exists for Phase A.1 (`DEF-B06-01`, `DEF-B06-03`).

---

## 3. Comprehensive Defect Register (Stage 5 End-User Verification)

| Defect ID | Severity | Category | Component | Summary |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-SYS-01** | CRITICAL | Infrastructure | Web/API Server | Live endpoints (`http://localhost:5173` and `http://localhost:8000`) connection refused; PostgreSQL and Redis services not active. |
| **DEF-SYS-02** | CRITICAL | Specification/Workflow | Speckit Pipeline | Implementation pipeline blocked before code execution: B01 lacks `plan.md` and `tasks.md` due to unratified decisions C03–C08. |
| **DEF-B01-01** | HIGH | Data Contract | DailyReport Model | Missing `report_number` and `project_day_number` fields. |
| **DEF-B01-02** | HIGH | Functional / Export | Shift Hours | Work shift actual duration missing; outputs placeholder text. |
| **DEF-B01-03** | MEDIUM | Calculation | Man-Hours / Headcount | Headcount sum treated as man-days without deduplicated identity attendance tracking. |
| **DEF-B02-01** | CRITICAL | Version Integrity | Correction Service | `is_auto_summary` drops on correction version creation. |
| **DEF-B02-02** | CRITICAL | RBAC / Lock Gate | DailyReport Views | Direct child row mutations permitted on derived rows in revision reports (lock bypass). |
| **DEF-B02-03** | HIGH | Lineage / Provenance | Correction Service | `DailyReportDerivedSource` records are not remapped on cloning. |
| **DEF-B03-01** | HIGH | Parity / Export | Excel/PDF Templates | Template styling, 34/32 occupation mapping, and weather ground conditions fail standard form parity. |
| **DEF-B04-01** | HIGH | Query / Filters | DailyReport FilterSet | Queryset aggregation discrepancies between filtered pagination views and summary totals. |
| **DEF-B05-01** | HIGH | Formula / Calculation | Export Engine | Lack of formula cache evaluation in generated `.xlsx` exports. |
| **DEF-B06-01** | CRITICAL | Release & Packaging | Release Bundle | Absence of Phase A.1 frozen release package, SHA-256 digest manifest, and client sign-off protocol. |

---

## 4. Conclusion & Next Steps

Phase A.1 fails end-user QA verification. Implementation of A.1 packages B01–B06 cannot pass acceptance until:
1. Employer decisions `C03`–`C08` are formally answered and ratified.
2. `spec.md`, `plan.md`, and `tasks.md` are completed and approved under SpecKit.
3. Code implementation is carried out to resolve critical defect history (`DEF-B01` through `DEF-B06`).
4. Live environments (`localhost:8000`, `localhost:5173`) are operational for dynamic end-to-end user testing.
