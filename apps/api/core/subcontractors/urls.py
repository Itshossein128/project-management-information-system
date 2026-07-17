from django.urls import path

from subcontractors.views import (
    RiskSummaryView,
    ScoreDetailView,
    ScoreListCreateView,
    SubcontractorViewSet,
    WarningListCreateView,
    WarningPatchView,
)

sub_list = SubcontractorViewSet.as_view({'get': 'list', 'post': 'create'})
sub_detail = SubcontractorViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    path('subcontractors/', sub_list, name='subcontractor-list'),
    path('subcontractors/risk-summary/', RiskSummaryView.as_view(), name='subcontractor-risk-summary'),
    path('subcontractors/<uuid:pk>/', sub_detail, name='subcontractor-detail'),
    path('subcontractors/<uuid:pk>/scores/', ScoreListCreateView.as_view(), name='subcontractor-scores'),
    path(
        'subcontractors/<uuid:pk>/scores/<uuid:scid>/',
        ScoreDetailView.as_view(),
        name='subcontractor-score-detail',
    ),
    path('subcontractors/<uuid:pk>/warnings/', WarningListCreateView.as_view(), name='subcontractor-warnings'),
    path(
        'subcontractors/<uuid:pk>/warnings/<uuid:wid>/',
        WarningPatchView.as_view(),
        name='subcontractor-warning-patch',
    ),
]
