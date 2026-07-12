from django.urls import path

from .department_activity_data_views import (
    DepartmentActivityDailyReportView,
    DepartmentActivityExportView,
    DepartmentActivityImportView,
    DepartmentActivityWeeklyReportView,
)
from .views import SpaceMaterialRequestViewSet, DepartmentActivityRecordViewSet

# Viewset action routing for space_material_request_list.
space_material_request_list = SpaceMaterialRequestViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# Viewset action routing for space_material_request_detail.
space_material_request_detail = SpaceMaterialRequestViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Viewset action routing for department_activity_record_list.
department_activity_record_list = DepartmentActivityRecordViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# Viewset action routing for department_activity_record_detail.
department_activity_record_detail = DepartmentActivityRecordViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path(
        'space-material-requests/',
        space_material_request_list,
        name='project-space-material-request-list',
    ),
    path(
        'space-material-requests/<int:pk>/',
        space_material_request_detail,
        name='project-space-material-request-detail',
    ),
    path(
        'department-activity-records/',
        department_activity_record_list,
        name='project-department-activity-record-list',
    ),
    path(
        'department-activity-records/<int:pk>/',
        department_activity_record_detail,
        name='project-department-activity-record-detail',
    ),
    path(
        'department-activity-records/export/',
        DepartmentActivityExportView.as_view(),
        name='project-department-activity-record-export',
    ),
    path(
        'department-activity-records/import/',
        DepartmentActivityImportView.as_view(),
        name='project-department-activity-record-import',
    ),
    path(
        'department-activity-records/reports/daily/',
        DepartmentActivityDailyReportView.as_view(),
        name='project-department-activity-record-daily-report',
    ),
    path(
        'department-activity-records/reports/weekly/',
        DepartmentActivityWeeklyReportView.as_view(),
        name='project-department-activity-record-weekly-report',
    ),
]

