# Stage 1.2 QA Verification: Requirement B01-05 (Job-Title Catalog and Shiraz Profile)

- **Requirement ID**: `B01-05`
- **Title**: Job-title catalog and Shiraz profile
- **Phase**: Phase A.1 (`specs/057-a1-b01-data-contract`)
- **Evaluation Date**: 2026-11-19
- **Assigned Acceptance Criteria**:
  > Separate the configurable project catalog from the 34/32 Shiraz profile and preserve extra, custom, and historical titles in an appendix.
- **Audited Specifications & Standards**:
  - [spec.md](file:///home/hossein/Desktop/projects/building-management/specs/057-a1-b01-data-contract/spec.md) (User Story 5, FR-014, FR-015, SC-004, SC-005, C04, D08, DEF-B01-04)
  - [requirements.md](file:///home/hossein/Desktop/projects/building-management/specs/057-a1-b01-data-contract/checklists/requirements.md)
- **Audited Codebase & Endpoints**:
  - Backend models & services: `apps/api/core/project_templates/models.py` (`LaborTitleCatalog`, `ProjectReportingConfigurationLaborTitle`), `apps/api/core/field_reports/models.py` (`DailyReportLabor`), `apps/api/core/project_templates/labor_catalog_seeds.py`
  - Excel export engines: [shiraz_file4_excel.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/shiraz_file4_excel.py#L22-L75) (`SHIRAZ_INDIRECT_ROLES`, `SHIRAZ_DIRECT_ROLES`, `_write_labor`), `apps/api/core/field_reports/shiraz_file1_excel.py`
  - Frontend UI components: `apps/web/src/components/daily_reports/LaborTab.tsx`, `apps/web/src/components/department/section-labor.tsx`, `apps/web/src/app/routes/project-labor-productivity.tsx`
  - Runtime services: `http://localhost:5173` and `http://localhost:8000` (offline/unreachable; verified via checked-in code, migrations, and AST analysis)

---

## 1. End-User Persona & Workflow Evaluation

### 1.1 Project Administrator Persona
- **Configurable Catalog vs. Form Presentation Profiles (FR-014, C04)**:
  - *Expectation*: A project administrator maintains a versioned, project-specific catalog of labor titles. When configuring the project, they can choose standard catalogs or custom roles without being forced into a hardcoded 34-indirect / 32-direct Shiraz form layout. Updating catalog templates for future days must never alter or delete historical daily report labor entries or counts.
  - *Observed Reality*:
    - While `project_templates` provides `LaborTitleCatalog` and `ProjectReportingConfigurationLaborTitle`, the official daily report exporter ([shiraz_file4_excel.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/shiraz_file4_excel.py#L22-L75)) bypasses the active project's catalog and hardcodes global static lists `SHIRAZ_INDIRECT_ROLES` (34 items) and `SHIRAZ_DIRECT_ROLES` (32 items) directly into module code.
    - There is no selectable "Presentation Profile" mechanism in the daily report generator or export endpoints; the Shiraz 34/32 form layout is treated as universal truth.

### 1.2 Resident Supervisor & Technical Office Persona
- **Deterministic Placement & Dedicated Appendix for Extra/Custom/Historical Titles (FR-015, C04, DEF-B01-04)**:
  - *Expectation*: Under ratified `C04`, the selectable Shiraz 34/32 profile must place standard titles in their designated form rows. Any additional, custom, or historical job titles outside the 34/32 positions MUST NOT be merged, dropped, or silently appended to the middle/end of the primary standard tables; they MUST be formatted in an explicit, distinct **Appendix** section with proper headers and subtotaling.
  - *Observed Reality*:
    - In [shiraz_file4_excel.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/field_reports/shiraz_file4_excel.py#L280-L345):
      ```python
      for idx, role in enumerate(SHIRAZ_INDIRECT_ROLES + sorted(set(indirect_entries) - set(SHIRAZ_INDIRECT_ROLES)), start=1):
      ...
      for idx, role in enumerate(SHIRAZ_DIRECT_ROLES + sorted(set(direct_entries) - set(SHIRAZ_DIRECT_ROLES)), start=1):
      ```
    - Unmatched titles are simply concatenated onto the bottom of the 34-row and 32-row standard tables, altering the fixed row count of the standard sections instead of rendering an isolated Appendix table.
    - No Appendix table, sheet, or section exists in `shiraz_file4_excel.py` or any PDF exporter.

### 1.3 QA Auditor Persona
- **Historical Integrity & Immutability**:
  - *Expectation*: Changing or deprecating a catalog entry preserves historical records with their original snapshot titles and counts.
  - *Observed Reality*:
    - While `DailyReportLabor` preserves historical string titles (`job_title`, `custom_title`), the export layout breaks reference form alignment whenever custom titles exist by pushing subsequent rows out of positional alignment, rather than delegating custom/historical rows to an appendix as required by ratified `C04`.

---

## 2. Acceptance Criteria Verification Matrix

| Acceptance Item | Specification Rule | Code / Implementation Status | Verdict |
|:---|:---|:---|:---|
| **Separation of Project Catalog from Form Profile** | FR-014, C04: Keep versioned, configurable project job-title catalog separate from selectable form profiles. | Exporter `shiraz_file4_excel.py` hardcodes `SHIRAZ_INDIRECT_ROLES` (34) and `SHIRAZ_DIRECT_ROLES` (32); no profile selector exists in export flow. | **Failed** |
| **Preservation of Historical Titles on Template Edit** | FR-014, US5 AC1: Modifying catalog templates must not delete or retroactively alter historical report records. | `DailyReportLabor` stores raw titles; however, export layout shifts dynamically when unmapped titles appear. | **Partially Implemented** |
| **Dedicated Appendix for Extra/Custom/Historical Titles** | FR-015, C04: Extra, custom, and historical job titles outside the 34/32 Shiraz profile must be listed in an appendix without dropping or relabeling. | Exporter concatenates extra titles directly to the bottom of standard sections (`SHIRAZ_INDIRECT_ROLES + sorted(...)`); no appendix section exists. | **Failed** |
| **Bilingual Labeling & Alignment** | SC-005, spec §4: Persian and English presentation support without hardcoded unmapped layout distortion. | Table headers and roles are hardcoded Persian only; no presentation profile abstraction exists. | **Failed** |

---

## 3. Discovered Defects Register

1. **DEF-B01-05-GAP-01 (Hardcoded 34/32 Shiraz Catalog in Export Pipeline)**:
   - *Description*: `apps/api/core/field_reports/shiraz_file4_excel.py` lines 22–75 hardcode static 34 staff and 32 worker roles. It does not load the versioned project catalog or allow selecting an alternate presentation profile, violating FR-014 and C04.
   - *Component*: `apps/api/core/field_reports/shiraz_file4_excel.py`
   - *Severity*: High

2. **DEF-B01-05-GAP-02 (Missing Dedicated Appendix for Non-Profile Titles)**:
   - *Description*: Extra, custom, or historical titles outside the 34/32 profile are appended directly to the end of the main indirect/direct tables (`SHIRAZ_INDIRECT_ROLES + sorted(...)`) rather than being formatted in a dedicated, clearly labeled Appendix table or section as mandated by ratified `C04` and FR-015 (`DEF-B01-04`).
   - *Component*: `apps/api/core/field_reports/shiraz_file4_excel.py` (L280, L345)
   - *Severity*: High

3. **DEF-B01-05-GAP-03 (Lack of Form Presentation Profile Model / Contract Abstraction)**:
   - *Description*: The software lacks an explicit data contract or configuration entity representing a "Form Presentation Profile" (such as the Shiraz 34/32 Profile) that maps project-level catalog IDs to positional reference form rows.
   - *Component*: `apps/api/core/project_templates/models.py`, `apps/api/core/field_reports/`
   - *Severity*: Medium

---

## 4. Final QA Verdict & Status

Requirement `B01-05` has been successfully ratified in `specs/057-a1-b01-data-contract/spec.md` (User Story 5, FR-014, FR-015, C04), but the implementation in the codebase fails acceptance criteria: the 34/32 roles are statically hardcoded in export scripts rather than driven by a selectable form profile, and custom/extra titles are appended directly into the main table rather than isolated in an appendix.

```json
{
  "requirementId": "B01-05",
  "title": "Job-title catalog and Shiraz profile",
  "acceptanceCriteria": "Separate the configurable project catalog from the 34/32 Shiraz profile and preserve extra, custom, and historical titles in an appendix.",
  "qaStatus": "qa_failed",
  "defects": [
    "DEF-B01-05-GAP-01: Exporter hardcodes 34 indirect and 32 direct Shiraz roles globally instead of separating project catalog from a selectable presentation profile (FR-014, C04)",
    "DEF-B01-05-GAP-02: Non-standard, custom, and historical job titles are concatenated onto main tables instead of being isolated in a dedicated appendix (FR-015, C04, DEF-B01-04)",
    "DEF-B01-05-GAP-03: No Form Presentation Profile data contract abstraction exists in backend or frontend to bind project catalog items to reference form slots"
  ],
  "verificationDetails": {
    "specStatus": "Ratified in specs/057-a1-b01-data-contract/spec.md under C04, US5, FR-014, FR-015",
    "excelExporter": "shiraz_file4_excel.py L22-75 hardcodes SHIRAZ_INDIRECT_ROLES / SHIRAZ_DIRECT_ROLES and L280/L345 concatenates extra roles without an appendix",
    "catalogModel": "project_templates/models.py has LaborTitleCatalog but it is uncoupled from daily report export presentation",
    "appendixImplementation": "Absent across Excel and PDF outputs"
  },
  "summary": "Requirement B01-05 failed QA verification: while C04 is ratified in the specification, the current implementation hardcodes 34/32 Shiraz roles in the export logic and fails to provide a dedicated appendix for extra, custom, and historical job titles."
}
```
