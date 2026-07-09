from django.urls import path

from .department_activity_data_views import (
    DepartmentActivityDailyReportView,
    DepartmentActivityExportView,
    DepartmentActivityImportView,
    DepartmentActivityWeeklyReportView,
)
from .views import SpaceMaterialRequestViewSet, DepartmentActivityRecordViewSet

# View bindings for listing and creating space material requests nested under a business.
# Maps GET to list and POST to create.
space_material_request_list = SpaceMaterialRequestViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# View bindings for retrieving, updating, and deleting a specific space material request.
# Maps GET to retrieve, PUT to update, PATCH to partial_update, and DELETE to destroy.
space_material_request_detail = SpaceMaterialRequestViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# View bindings for listing and creating department activity records nested under a business.
# Maps GET to list and POST to create.
department_activity_record_list = DepartmentActivityRecordViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# View bindings for retrieving, updating, and deleting a specific department activity record.
# Maps GET to retrieve, PUT to update, PATCH to partial_update, and DELETE to destroy.
department_activity_record_detail = DepartmentActivityRecordViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# List of business-scoped URL routes for the inventory application.
# Includes endpoints for managing space material requests, department activity records,
# and related data export/import and reporting functionalities.
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

