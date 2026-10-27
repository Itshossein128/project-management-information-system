# T002 section and writer inventory

Static inspection at `develop@89ac5db`; inventory of code paths, not evidence of functional coverage. `department-page.tsx` hosts `unit-daily-report-panel.tsx`; current/open/workflow hooks are in `apps/web/src/app/hooks/queries.ts`, network client in `apps/web/src/app/lib/api/unit-reports.ts`. That client currently declares hard-coded support below: this alone does not prove effective-dated project configuration is applied; verify that configuration separately when implementing FR-001.

| Section | Client support currently declared | Form and mutation | Server writer and validation |
|---|---|---|---|
| activities | buildings, electrical, mechanical | `section-activities.tsx`, `useCreate/Update/DeleteUnitReportActivity` | `UnitReportActivitySectionViewSet`, `validate_activity_rows`, `update_activity_row` |
| labor | buildings, electrical, mechanical | `section-labor.tsx`, labor hooks | `UnitReportLaborSectionViewSet`, `validate_labor_rows`, `update_labor_row` |
| machinery | machinery | `section-machinery.tsx`, machinery hooks | `UnitReportMachinerySectionViewSet`, `validate_machinery_rows`, `update_machinery_row` |
| materials | warehouse | `section-materials.tsx`, material hooks | `UnitReportMaterialSectionViewSet`, `validate_material_rows`, `update_material_row` |
| concrete | buildings, mechanical | `section-concrete.tsx` / `section-structured.tsx`, `createUnitSection`, `deleteUnitSection` | `UnitReportConcreteSectionViewSet`, `validate_concrete_rows`; URL has create/delete, no patch |
| general activities | all six | `section-general.tsx` / `section-structured.tsx` | `UnitReportGeneralSectionViewSet`, `validate_narrative_rows`; URL has create/delete |
| issues | buildings, electrical, mechanical, security | `section-issues.tsx` / `section-structured.tsx` | `UnitReportIssueSectionViewSet`, `validate_narrative_rows`; URL has create/delete |
| visits | buildings, security | `section-visits.tsx` / `section-structured.tsx` | `UnitReportVisitSectionViewSet`, `validate_narrative_rows`; URL has create/delete |
| HSE incidents | security | `section-hse.tsx` / `section-structured.tsx` | `UnitReportHseSectionViewSet`, `validate_narrative_rows`; URL has create/delete |
| existing attachments | relevant source activity | dedicated attachment interface | `UnitReportAttachmentSectionViewSet`; preserve references; new offline binary upload is out of scope |

All six units are `buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`. Unit report `current/open/patch/delete/submit/approve/reject/correct` are registered in `apps/api/core/sub_reports/urls.py` and handled by `UnitReportViewSet` and `unit_report_services.py`. Unit metadata is `form_code`, `revision_number`, `weather_condition`, `site_status`; nested notes/rows can use replacement on old header PATCH, so inventory this path as a writer too. Section viewsets check `IsAuthenticated`, `IsProjectMember`, `HasProjectPermission`; read needs `view_reports`, mutation `edit_reports`; workflow approve/reject uses `approve_reports`; global admin exception is in `permissions/project.py`. Verify these rules under race at actual mutation, not only pre-check.

Other relevant writers: project summary create/by-date, PATCH, child CRUD, sync batch in `field_reports/daily_report_views.py` and `field_reports/services/__init__.py`; summary regeneration in `field_reports/services/daily_report_aggregation.py`; formal project correction in `field_reports/services/correction_service.py`; unit lifecycle/correction in `sub_reports/unit_report_services.py`; section writers in `sub_reports/services/section_validation.py` and viewsets. Both direct summary PATCH nested activities and legacy batch must be guarded against derived writes. Continue searching all model write paths at T013; this preliminary inventory does not assert it exhausts unrelated administrative writers.
