from django.urls import path

from field_reports.daily_report_views import (
    DailyReportActivityViewSet,
    DailyReportConcreteLogViewSet,
    DailyReportEquipmentViewSet,
    DailyReportIncidentViewSet,
    DailyReportLaborCampViewSet,
    DailyReportLaborViewSet,
    DailyReportMaterialViewSet,
    DailyReportViewSet,
    LaborJobTitleListView,
)
from field_reports.standalone_forms_views import (
    EquipmentLogSummaryView,
    EquipmentLogViewSet,
    LaborCampReportViewSet,
    StandaloneManpowerViewSet,
)
from field_reports.report_views import (
    ActivityLogFilterOptionsView,
    ActivityLogView,
    PersonnelSummaryView,
)
from field_reports.views import WeatherLogViewSet

# Viewset action routing for weather_list.
weather_list = WeatherLogViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for weather_detail.
weather_detail = WeatherLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

# Viewset action routing for report_list.
report_list = DailyReportViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for report_detail.
report_detail = DailyReportViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
# Definition of report_sync_batch.
report_sync_batch = DailyReportViewSet.as_view({'post': 'sync_batch'})
# Definition of report_submit.
report_submit = DailyReportViewSet.as_view({'post': 'submit'})
# Definition of report_review.
report_review = DailyReportViewSet.as_view({'post': 'review'})
# Definition of report_approve.
report_approve = DailyReportViewSet.as_view({'post': 'approve'})
# Definition of report_reject.
report_reject = DailyReportViewSet.as_view({'post': 'reject'})
# Definition of report_pdf.
report_pdf = DailyReportViewSet.as_view({'get': 'pdf'})


# Function _child handles specific URL routing logic.
def _child(viewset):
    return (
        viewset.as_view({'get': 'list', 'post': 'create'}),
        viewset.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
    )


activity_list, activity_detail = _child(DailyReportActivityViewSet)
labor_list, labor_detail = _child(DailyReportLaborViewSet)
equipment_list, equipment_detail = _child(DailyReportEquipmentViewSet)
material_list, material_detail = _child(DailyReportMaterialViewSet)
concrete_list, concrete_detail = _child(DailyReportConcreteLogViewSet)
labor_camp_list, labor_camp_detail = _child(DailyReportLaborCampViewSet)
incident_list, incident_detail = _child(DailyReportIncidentViewSet)

# Viewset action routing for labor_camp_report_list.
labor_camp_report_list = LaborCampReportViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for labor_camp_report_detail.
labor_camp_report_detail = LaborCampReportViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)
# Viewset action routing for equipment_log_list.
equipment_log_list = EquipmentLogViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for equipment_log_detail.
equipment_log_detail = EquipmentLogViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)
# Viewset action routing for manpower_list.
manpower_list = StandaloneManpowerViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for manpower_detail.
manpower_detail = StandaloneManpowerViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})

# Definition of DR.
DR = 'daily-reports'
# Definition of RID.
RID = '<uuid:report_pk>'

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('weather/', weather_list, name='project-weather-list'),
    path('weather/<uuid:pk>/', weather_detail, name='project-weather-detail'),

    path('manpower/job-titles/', LaborJobTitleListView.as_view(), name='labor-job-titles'),
    path('manpower/', manpower_list, name='standalone-manpower-list'),
    path('manpower/<uuid:pk>/', manpower_detail, name='standalone-manpower-detail'),
    path('labor-camp/', labor_camp_report_list, name='labor-camp-list'),
    path('labor-camp/<uuid:pk>/', labor_camp_report_detail, name='labor-camp-detail'),
    path('equipment-log/', equipment_log_list, name='equipment-log-list'),
    path('equipment-log/summary/', EquipmentLogSummaryView.as_view(), name='equipment-log-summary'),
    path('equipment-log/<uuid:pk>/', equipment_log_detail, name='equipment-log-detail'),

    path('personnel-summary/', PersonnelSummaryView.as_view(), name='personnel-summary'),
    path('activity-log/', ActivityLogView.as_view(), name='activity-log'),
    path('activity-log/filters/', ActivityLogFilterOptionsView.as_view(), name='activity-log-filters'),

    path(f'{DR}/', report_list, name='daily-report-list'),
    path(f'{DR}/sync-batch/', report_sync_batch, name='daily-report-sync-batch'),
    path(f'{DR}/<uuid:pk>/', report_detail, name='daily-report-detail'),
    path(f'{DR}/<uuid:pk>/submit/', report_submit, name='daily-report-submit'),
    path(f'{DR}/<uuid:pk>/review/', report_review, name='daily-report-review'),
    path(f'{DR}/<uuid:pk>/approve/', report_approve, name='daily-report-approve'),
    path(f'{DR}/<uuid:pk>/reject/', report_reject, name='daily-report-reject'),
    path(f'{DR}/<uuid:pk>/pdf/', report_pdf, name='daily-report-pdf'),

    path(f'{DR}/{RID}/activities/', activity_list, name='daily-report-activities'),
    path(f'{DR}/{RID}/activities/<uuid:pk>/', activity_detail, name='daily-report-activity-detail'),
    path(f'{DR}/{RID}/labor/', labor_list, name='daily-report-labor'),
    path(f'{DR}/{RID}/labor/<uuid:pk>/', labor_detail, name='daily-report-labor-detail'),
    path(f'{DR}/{RID}/equipment/', equipment_list, name='daily-report-equipment'),
    path(f'{DR}/{RID}/equipment/<uuid:pk>/', equipment_detail, name='daily-report-equipment-detail'),
    path(f'{DR}/{RID}/materials/', material_list, name='daily-report-materials'),
    path(f'{DR}/{RID}/materials/<uuid:pk>/', material_detail, name='daily-report-material-detail'),
    path(f'{DR}/{RID}/concrete-logs/', concrete_list, name='daily-report-concrete'),
    path(f'{DR}/{RID}/concrete-logs/<uuid:pk>/', concrete_detail, name='daily-report-concrete-detail'),
    path(f'{DR}/{RID}/labor-camp/', labor_camp_list, name='daily-report-labor-camp'),
    path(f'{DR}/{RID}/labor-camp/<uuid:pk>/', labor_camp_detail, name='daily-report-labor-camp-detail'),
    path(f'{DR}/{RID}/incidents/', incident_list, name='daily-report-incidents'),
    path(f'{DR}/{RID}/incidents/<uuid:pk>/', incident_detail, name='daily-report-incident-detail'),
]
