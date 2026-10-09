from django.urls import path

from risk.views import (
    BarrierLogViewSet,
    CorrectiveActionViewSet,
    HseEventViewSet,
    InspectionViewSet,
    NonconformityViewSet,
    QualitySafetyPeriodReportView,
    RiskActionViewSet,
    RiskEventViewSet,
    RiskMatrixView,
    SafetyTrainingViewSet,
    WorkPermitViewSet,
)

barrier_list = BarrierLogViewSet.as_view({'get': 'list', 'post': 'create'})
barrier_detail = BarrierLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
risk_list = RiskEventViewSet.as_view({'get': 'list', 'post': 'create'})
risk_detail = RiskEventViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
action_list = RiskActionViewSet.as_view({'get': 'list', 'post': 'create'})
action_detail = RiskActionViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
inspection_list = InspectionViewSet.as_view({'get': 'list', 'post': 'create'})
inspection_detail = InspectionViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
ncr_list = NonconformityViewSet.as_view({'get': 'list', 'post': 'create'})
ncr_detail = NonconformityViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
ca_list = CorrectiveActionViewSet.as_view({'get': 'list', 'post': 'create'})
ca_detail = CorrectiveActionViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
hse_list = HseEventViewSet.as_view({'get': 'list', 'post': 'create'})
hse_detail = HseEventViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
permit_list = WorkPermitViewSet.as_view({'get': 'list', 'post': 'create'})
permit_detail = WorkPermitViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
train_list = SafetyTrainingViewSet.as_view({'get': 'list', 'post': 'create'})
train_detail = SafetyTrainingViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

urlpatterns = [
    path('barriers/', barrier_list, name='project-barriers-list'),
    path('barriers/<uuid:pk>/', barrier_detail, name='project-barriers-detail'),
    path('risk-events/', risk_list, name='project-risk-events-list'),
    path('risk-events/matrix/', RiskMatrixView.as_view(), name='project-risk-events-matrix'),
    path('risk-events/<uuid:pk>/', risk_detail, name='project-risk-events-detail'),
    path('risk-actions/', action_list, name='project-risk-actions-list'),
    path('risk-actions/<uuid:pk>/', action_detail, name='project-risk-actions-detail'),
    path('inspections/', inspection_list, name='project-inspections-list'),
    path('inspections/<uuid:pk>/', inspection_detail, name='project-inspections-detail'),
    path('nonconformities/', ncr_list, name='project-nonconformities-list'),
    path('nonconformities/<uuid:pk>/', ncr_detail, name='project-nonconformities-detail'),
    path('corrective-actions/', ca_list, name='project-corrective-actions-list'),
    path('corrective-actions/<uuid:pk>/', ca_detail, name='project-corrective-actions-detail'),
    path('hse-events/', hse_list, name='project-hse-events-list'),
    path('hse-events/<uuid:pk>/', hse_detail, name='project-hse-events-detail'),
    path('work-permits/', permit_list, name='project-work-permits-list'),
    path('work-permits/<uuid:pk>/', permit_detail, name='project-work-permits-detail'),
    path('safety-trainings/', train_list, name='project-safety-trainings-list'),
    path('safety-trainings/<uuid:pk>/', train_detail, name='project-safety-trainings-detail'),
    path(
        'quality-safety/report/',
        QualitySafetyPeriodReportView.as_view(),
        name='project-quality-safety-report',
    ),
]
