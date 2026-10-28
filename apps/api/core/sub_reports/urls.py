from django.urls import path

# Canonical unit daily report API (feature 032).
from sub_reports.unit_report_views import (
    UnitReportActivitySectionViewSet,
    UnitReportAttachmentSectionViewSet,
    UnitReportConcreteSectionViewSet,
    UnitReportGeneralSectionViewSet,
    UnitReportHseSectionViewSet,
    UnitReportIssueSectionViewSet,
    UnitReportLaborSectionViewSet,
    UnitReportMachinerySectionViewSet,
    UnitReportMaterialSectionViewSet,
    UnitReportViewSet,
    UnitReportVisitSectionViewSet,
    SyncOperationsV2View,
    ContractorLaborLedgerView,
)

unit_current_view = UnitReportViewSet.as_view({'get': 'current'})
unit_open_view = UnitReportViewSet.as_view({'post': 'open'})
unit_detail_view = UnitReportViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
unit_history_view = UnitReportViewSet.as_view({'get': 'history'})
unit_submit_view = UnitReportViewSet.as_view({'post': 'submit'})
unit_approve_view = UnitReportViewSet.as_view({'post': 'approve'})
unit_reject_view = UnitReportViewSet.as_view({'post': 'reject'})
unit_correct_view = UnitReportViewSet.as_view({'post': 'correct'})
unit_excel_view = UnitReportViewSet.as_view({'get': 'excel'})

# §1 executed-activity section rows (feature 033, T017).
activity_section_list = UnitReportActivitySectionViewSet.as_view(
    {'get': 'list', 'post': 'create'},
)
activity_section_row = UnitReportActivitySectionViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)

# §2 labor section rows (feature 033, T021).
labor_section_list = UnitReportLaborSectionViewSet.as_view(
    {'get': 'list', 'post': 'create'},
)
labor_section_row = UnitReportLaborSectionViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)

# §3 machinery section rows (feature 033, T028).
machinery_section_list = UnitReportMachinerySectionViewSet.as_view(
    {'get': 'list', 'post': 'create'},
)
machinery_section_row = UnitReportMachinerySectionViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)

# §4 materials section rows (feature 033, T035).
material_section_list = UnitReportMaterialSectionViewSet.as_view(
    {'get': 'list', 'post': 'create'},
)
material_section_row = UnitReportMaterialSectionViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)
concrete_section_list = UnitReportConcreteSectionViewSet.as_view({'get': 'list', 'post': 'create'})
concrete_section_row = UnitReportConcreteSectionViewSet.as_view({'delete': 'destroy'})
issue_section_list = UnitReportIssueSectionViewSet.as_view({'get': 'list', 'post': 'create'})
issue_section_row = UnitReportIssueSectionViewSet.as_view({'delete': 'destroy'})
visit_section_list = UnitReportVisitSectionViewSet.as_view({'get': 'list', 'post': 'create'})
visit_section_row = UnitReportVisitSectionViewSet.as_view({'delete': 'destroy'})
hse_section_list = UnitReportHseSectionViewSet.as_view({'get': 'list', 'post': 'create'})
hse_section_row = UnitReportHseSectionViewSet.as_view({'delete': 'destroy'})
general_section_list = UnitReportGeneralSectionViewSet.as_view({'get': 'list', 'post': 'create'})
general_section_row = UnitReportGeneralSectionViewSet.as_view({'delete': 'destroy'})
attachment_section_list = UnitReportAttachmentSectionViewSet.as_view({'get': 'list', 'post': 'create'})
attachment_section_row = UnitReportAttachmentSectionViewSet.as_view({'delete': 'destroy'})

# NOTE (FR-032 / US5 / research D2):
# Legacy client endpoints under `/api/v1/projects/{project_id}/sub-reports/`
# (list, detail, submit, approve, reject) have been unregistered from client exposure.
# Internal model and service compatibility remains until the retirement milestone
# (no later than the third feature in this series), at which point destructive schema cleanup occurs.

urlpatterns = [
    path('units/<str:unit>/daily-reports/current/', unit_current_view, name='unit-report-current'),
    path('units/<str:unit>/daily-reports/open/', unit_open_view, name='unit-report-open'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/', unit_detail_view, name='unit-report-detail'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/history/', unit_history_view, name='unit-report-history'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/submit/', unit_submit_view, name='unit-report-submit'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/approve/', unit_approve_view, name='unit-report-approve'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/reject/', unit_reject_view, name='unit-report-reject'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/correct/', unit_correct_view, name='unit-report-correct'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/excel/', unit_excel_view, name='unit-report-excel'),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/activities/',
        activity_section_list,
        name='unit-report-activities',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/activities/<uuid:row_pk>/',
        activity_section_row,
        name='unit-report-activity-row',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/labor/',
        labor_section_list,
        name='unit-report-labor',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/labor/<uuid:row_pk>/',
        labor_section_row,
        name='unit-report-labor-row',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/machinery/',
        machinery_section_list,
        name='unit-report-machinery',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/machinery/<uuid:row_pk>/',
        machinery_section_row,
        name='unit-report-machinery-row',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/materials/',
        material_section_list,
        name='unit-report-materials',
    ),
    path(
        'units/<str:unit>/daily-reports/<uuid:pk>/materials/<uuid:row_pk>/',
        material_section_row,
        name='unit-report-material-row',
    ),
    path('units/<str:unit>/daily-reports/<uuid:pk>/concrete/', concrete_section_list, name='unit-report-concrete'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/concrete/<uuid:row_pk>/', concrete_section_row, name='unit-report-concrete-row'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/issues/', issue_section_list, name='unit-report-issues'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/issues/<uuid:row_pk>/', issue_section_row, name='unit-report-issue-row'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/visits/', visit_section_list, name='unit-report-visits'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/visits/<uuid:row_pk>/', visit_section_row, name='unit-report-visit-row'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/hse-incidents/', hse_section_list, name='unit-report-hse'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/hse-incidents/<uuid:row_pk>/', hse_section_row, name='unit-report-hse-row'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/general-activities/', general_section_list, name='unit-report-general'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/general-activities/<uuid:row_pk>/', general_section_row, name='unit-report-general-row'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/attachments/', attachment_section_list, name='unit-report-attachments'),
    path('units/<str:unit>/daily-reports/<uuid:pk>/attachments/<uuid:row_pk>/', attachment_section_row, name='unit-report-attachment-row'),
    path('contractors/<uuid:contractor_pk>/labor-ledger/', ContractorLaborLedgerView.as_view(), name='contractor-labor-ledger'),
    path('daily-reports/sync-operations/v2/', SyncOperationsV2View.as_view(), name='sync-operations-v2'),
]
