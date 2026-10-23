from django.urls import path

# Canonical unit daily report API (feature 032).
from sub_reports.unit_report_views import (
    UnitReportActivitySectionViewSet,
    UnitReportViewSet,
)

unit_current_view = UnitReportViewSet.as_view({'get': 'current'})
unit_open_view = UnitReportViewSet.as_view({'post': 'open'})
unit_detail_view = UnitReportViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
unit_history_view = UnitReportViewSet.as_view({'get': 'history'})
unit_submit_view = UnitReportViewSet.as_view({'post': 'submit'})
unit_approve_view = UnitReportViewSet.as_view({'post': 'approve'})
unit_reject_view = UnitReportViewSet.as_view({'post': 'reject'})
unit_correct_view = UnitReportViewSet.as_view({'post': 'correct'})

# §1 executed-activity section rows (feature 033, T017).
activity_section_list = UnitReportActivitySectionViewSet.as_view(
    {'get': 'list', 'post': 'create'},
)
activity_section_row = UnitReportActivitySectionViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)

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
]
