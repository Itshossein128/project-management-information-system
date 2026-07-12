from django.urls import path

from subcontractors.views import (
    RiskSummaryView,
    ScoreCreateView,
    SubcontractorViewSet,
    WarningCreateView,
    WarningPatchView,
)

# Viewset action routing for sub_list.
sub_list = SubcontractorViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for sub_detail.
sub_detail = SubcontractorViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('subcontractors/', sub_list, name='subcontractor-list'),
    path('subcontractors/risk-summary/', RiskSummaryView.as_view(), name='subcontractor-risk-summary'),
    path('subcontractors/<uuid:pk>/', sub_detail, name='subcontractor-detail'),
    path('subcontractors/<uuid:pk>/scores/', ScoreCreateView.as_view(), name='subcontractor-score-create'),
    path('subcontractors/<uuid:pk>/warnings/', WarningCreateView.as_view(), name='subcontractor-warning-create'),
    path(
        'subcontractors/<uuid:pk>/warnings/<uuid:wid>/',
        WarningPatchView.as_view(),
        name='subcontractor-warning-patch',
    ),
]
