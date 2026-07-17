from django.urls import path

from .department_activity_data_views import (
    DepartmentActivityDailyReportView,
    DepartmentActivityExportView,
    DepartmentActivityImportView,
    DepartmentActivityWeeklyReportView,
)
from .views import SpaceMaterialRequestViewSet, DepartmentActivityRecordViewSet

# View functions for SpaceMaterialRequest endpoints (list and create actions)
space_material_request_list = SpaceMaterialRequestViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)

# View functions for SpaceMaterialRequest endpoints (retrieve, update, and destroy actions)
space_material_request_detail = SpaceMaterialRequestViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# View functions for DepartmentActivityRecord endpoints (list and create actions)
department_activity_record_list = DepartmentActivityRecordViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)

# View functions for DepartmentActivityRecord endpoints (retrieve, update, and destroy actions)
department_activity_record_detail = DepartmentActivityRecordViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# URL routing configurations for business-scoped inventory APIs.
# Defines endpoints for space material requests, department activity records (CRUD, export, import, and reports).
urlpatterns = [
    path(
        '<int:business_pk>/space-material-requests/',
        space_material_request_list,
        name='business-space-material-request-list',
    ),
    path(
        '<int:business_pk>/space-material-requests/<int:pk>/',
        space_material_request_detail,
        name='business-space-material-request-detail',
    ),
    path(
        '<int:business_pk>/department-activity-records/',
        department_activity_record_list,
        name='business-department-activity-record-list',
    ),
    path(
        '<int:business_pk>/department-activity-records/<int:pk>/',
        department_activity_record_detail,
        name='business-department-activity-record-detail',
    ),
    path(
        '<int:business_pk>/department-activity-records/export/',
        DepartmentActivityExportView.as_view(),
        name='business-department-activity-record-export',
    ),
    path(
        '<int:business_pk>/department-activity-records/import/',
        DepartmentActivityImportView.as_view(),
        name='business-department-activity-record-import',
    ),
    path(
        '<int:business_pk>/department-activity-records/reports/daily/',
        DepartmentActivityDailyReportView.as_view(),
        name='business-department-activity-record-daily-report',
    ),
    path(
        '<int:business_pk>/department-activity-records/reports/weekly/',
        DepartmentActivityWeeklyReportView.as_view(),
        name='business-department-activity-record-weekly-report',
    ),
]

