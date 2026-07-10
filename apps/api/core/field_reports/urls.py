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
from field_reports.views import WeatherLogViewSet

weather_list = WeatherLogViewSet.as_view({'get': 'list', 'post': 'create'})
weather_detail = WeatherLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

report_list = DailyReportViewSet.as_view({'get': 'list', 'post': 'create'})
report_detail = DailyReportViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
report_sync_batch = DailyReportViewSet.as_view({'post': 'sync_batch'})
report_submit = DailyReportViewSet.as_view({'post': 'submit'})
report_review = DailyReportViewSet.as_view({'post': 'review'})
report_approve = DailyReportViewSet.as_view({'post': 'approve'})
report_reject = DailyReportViewSet.as_view({'post': 'reject'})
report_pdf = DailyReportViewSet.as_view({'get': 'pdf'})


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

labor_camp_report_list = LaborCampReportViewSet.as_view({'get': 'list', 'post': 'create'})
labor_camp_report_detail = LaborCampReportViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)
equipment_log_list = EquipmentLogViewSet.as_view({'get': 'list', 'post': 'create'})
equipment_log_detail = EquipmentLogViewSet.as_view(
    {'patch': 'partial_update', 'delete': 'destroy'},
)
manpower_list = StandaloneManpowerViewSet.as_view({'get': 'list', 'post': 'create'})
manpower_detail = StandaloneManpowerViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})

DR = 'daily-reports'
RID = '<uuid:report_pk>'

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
