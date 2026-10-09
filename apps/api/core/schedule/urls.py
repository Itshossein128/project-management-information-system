from django.urls import path

from schedule.activity_views import ActivityViewSet
from schedule.baseline_views import (
    BaselineActivityDetailView,
    BaselineApproveLockView,
    BaselineListCreateView,
)
from schedule.calendar_views import (
    CalendarExceptionDetailView,
    CalendarExceptionListCreateView,
    WorkingCalendarDetailView,
    WorkingCalendarListCreateView,
)
from schedule.change_request_views import (
    ScheduleChangeRequestApproveView,
    ScheduleChangeRequestDetailView,
    ScheduleChangeRequestListCreateView,
    ScheduleChangeRequestRejectView,
    ScheduleChangeRequestSubmitView,
)
from schedule.measurement_views import (
    ActivityMeasurementApproveView,
    ActivityMeasurementChangeView,
    ActivityMeasurementView,
    ActivityQuantityChangeApproveView,
    ActivityQuantityChangeListCreateView,
    ProgressTechnicalApproveView,
)
from schedule.period_report_views import (
    ProgressReportDetailView,
    ProgressReportFigureOverrideView,
    ProgressReportFigureView,
    ProgressReportListCreateView,
)
from schedule.progress_views import (
    ProjectActivityProgressView,
    ProjectManualProgressView,
    ProjectProgressHistoryView,
    ProjectProgressKpisView,
    ProjectProgressSnapshotView,
    ProjectSCurveView,
)
from schedule.gantt_views import GanttDataView, GanttPdfView
from schedule.status_views import ScheduleStatusView
from schedule.views import (
    MspImportPreviewView,
    MspImportStartView,
    MspImportStatusView,
    P6ImportPreviewView,
    P6ImportStartView,
    P6ImportStatusView,
)

activity_list = ActivityViewSet.as_view({'get': 'list', 'post': 'create'})
activity_detail = ActivityViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
activity_restore = ActivityViewSet.as_view({'post': 'restore'})
activity_weight_summary = ActivityViewSet.as_view({'get': 'weight_summary'})
activity_network = ActivityViewSet.as_view({'get': 'network'})
activity_relations = ActivityViewSet.as_view({'post': 'relations'})
activity_relation_delete = ActivityViewSet.as_view({'delete': 'delete_relation'})

urlpatterns = [
    path('activities/', activity_list, name='activity-list'),
    path('activities/weight-summary/', activity_weight_summary, name='activity-weight-summary'),
    path('activities/network/', activity_network, name='activity-network'),
    path('activities/<uuid:activity_id>/', activity_detail, name='activity-detail'),
    path('activities/<uuid:activity_id>/restore/', activity_restore, name='activity-restore'),
    path('activities/<uuid:activity_id>/relations/', activity_relations, name='activity-relations'),
    path(
        'activities/<uuid:activity_id>/relations/<uuid:relation_id>/',
        activity_relation_delete,
        name='activity-relation-delete',
    ),
    path(
        'activities/<uuid:activity_id>/measurement/',
        ActivityMeasurementView.as_view(),
        name='activity-measurement',
    ),
    path(
        'activities/<uuid:activity_id>/measurement/approve/',
        ActivityMeasurementApproveView.as_view(),
        name='activity-measurement-approve',
    ),
    path(
        'activities/<uuid:activity_id>/measurement/change/',
        ActivityMeasurementChangeView.as_view(),
        name='activity-measurement-change',
    ),
    path(
        'activities/<uuid:activity_id>/quantity-changes/',
        ActivityQuantityChangeListCreateView.as_view(),
        name='activity-quantity-change-list',
    ),
    path(
        'activities/<uuid:activity_id>/quantity-changes/<uuid:change_id>/approve/',
        ActivityQuantityChangeApproveView.as_view(),
        name='activity-quantity-change-approve',
    ),
    path(
        'quantity-changes/<uuid:change_id>/approve/',
        ActivityQuantityChangeApproveView.as_view(),
        name='quantity-change-approve',
    ),
    path('working-calendars/', WorkingCalendarListCreateView.as_view(), name='working-calendar-list'),
    path(
        'working-calendars/<uuid:calendar_id>/',
        WorkingCalendarDetailView.as_view(),
        name='working-calendar-detail',
    ),
    path(
        'working-calendars/<uuid:calendar_id>/exceptions/',
        CalendarExceptionListCreateView.as_view(),
        name='calendar-exception-list',
    ),
    path(
        'working-calendars/<uuid:calendar_id>/exceptions/<uuid:exception_id>/',
        CalendarExceptionDetailView.as_view(),
        name='calendar-exception-detail',
    ),
    path('baselines/', BaselineListCreateView.as_view(), name='baseline-list'),
    path(
        'baselines/<uuid:baseline_id>/approve-lock/',
        BaselineApproveLockView.as_view(),
        name='baseline-approve-lock',
    ),
    path(
        'baselines/<uuid:baseline_id>/activities/<uuid:ba_id>/',
        BaselineActivityDetailView.as_view(),
        name='baseline-activity-detail',
    ),
    path(
        'schedule-change-requests/',
        ScheduleChangeRequestListCreateView.as_view(),
        name='schedule-change-request-list',
    ),
    path(
        'schedule-change-requests/<uuid:scr_id>/',
        ScheduleChangeRequestDetailView.as_view(),
        name='schedule-change-request-detail',
    ),
    path(
        'schedule-change-requests/<uuid:scr_id>/submit/',
        ScheduleChangeRequestSubmitView.as_view(),
        name='schedule-change-request-submit',
    ),
    path(
        'schedule-change-requests/<uuid:scr_id>/approve/',
        ScheduleChangeRequestApproveView.as_view(),
        name='schedule-change-request-approve',
    ),
    path(
        'schedule-change-requests/<uuid:scr_id>/reject/',
        ScheduleChangeRequestRejectView.as_view(),
        name='schedule-change-request-reject',
    ),
    path('schedule-status/', ScheduleStatusView.as_view(), name='schedule-status'),
    path('import/msp/preview/', MspImportPreviewView.as_view(), name='msp-import-preview'),
    path('import/msp/', MspImportStartView.as_view(), name='msp-import-start'),
    path('import/msp/status/<uuid:task_id>/', MspImportStatusView.as_view(), name='msp-import-status'),
    path('import/p6/preview/', P6ImportPreviewView.as_view(), name='p6-import-preview'),
    path('import/p6/', P6ImportStartView.as_view(), name='p6-import-start'),
    path('import/p6/status/<uuid:task_id>/', P6ImportStatusView.as_view(), name='p6-import-status'),
    path('progress/', ProjectProgressSnapshotView.as_view(), name='project-progress-snapshot'),
    path('progress/s-curve/', ProjectSCurveView.as_view(), name='project-progress-s-curve'),
    path('progress/activities/', ProjectActivityProgressView.as_view(), name='project-progress-activities'),
    path('progress/kpis/', ProjectProgressKpisView.as_view(), name='project-progress-kpis'),
    path('progress/history/', ProjectProgressHistoryView.as_view(), name='project-progress-history'),
    path('progress/manual/', ProjectManualProgressView.as_view(), name='project-progress-manual'),
    path(
        'progress/<uuid:activity_id>/technical-approve/',
        ProgressTechnicalApproveView.as_view(),
        name='project-progress-technical-approve',
    ),
    path('progress-reports/', ProgressReportListCreateView.as_view(), name='progress-report-list'),
    path(
        'progress-reports/figures/<uuid:figure_id>/',
        ProgressReportFigureView.as_view(),
        name='progress-report-figure',
    ),
    path(
        'progress-reports/figures/<uuid:figure_id>/overrides/',
        ProgressReportFigureOverrideView.as_view(),
        name='progress-report-figure-override',
    ),
    path(
        'progress-reports/<uuid:report_id>/',
        ProgressReportDetailView.as_view(),
        name='progress-report-detail',
    ),
    path('gantt/', GanttDataView.as_view(), name='project-gantt'),
    path('gantt/pdf/', GanttPdfView.as_view(), name='project-gantt-pdf'),
]
