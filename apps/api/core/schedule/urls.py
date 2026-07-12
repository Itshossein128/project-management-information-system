from django.urls import path

from schedule.activity_views import ActivityViewSet
from schedule.progress_views import (
    ProjectActivityProgressView,
    ProjectManualProgressView,
    ProjectProgressHistoryView,
    ProjectProgressKpisView,
    ProjectProgressSnapshotView,
    ProjectSCurveView,
)
from schedule.views import MspImportPreviewView, MspImportStartView, MspImportStatusView

# Viewset action routing for activity_list.
activity_list = ActivityViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for activity_detail.
activity_detail = ActivityViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
# Definition of activity_weight_summary.
activity_weight_summary = ActivityViewSet.as_view({'get': 'weight_summary'})
# Definition of activity_network.
activity_network = ActivityViewSet.as_view({'get': 'network'})
# Definition of activity_relations.
activity_relations = ActivityViewSet.as_view({'post': 'relations'})
# Definition of activity_relation_delete.
activity_relation_delete = ActivityViewSet.as_view({'delete': 'delete_relation'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('activities/', activity_list, name='activity-list'),
    path('activities/weight-summary/', activity_weight_summary, name='activity-weight-summary'),
    path('activities/network/', activity_network, name='activity-network'),
    path('activities/<uuid:activity_id>/', activity_detail, name='activity-detail'),
    path('activities/<uuid:activity_id>/relations/', activity_relations, name='activity-relations'),
    path(
        'activities/<uuid:activity_id>/relations/<uuid:relation_id>/',
        activity_relation_delete,
        name='activity-relation-delete',
    ),
    path('import/msp/preview/', MspImportPreviewView.as_view(), name='msp-import-preview'),
    path('import/msp/', MspImportStartView.as_view(), name='msp-import-start'),
    path('import/msp/status/<uuid:task_id>/', MspImportStatusView.as_view(), name='msp-import-status'),
    path('progress/', ProjectProgressSnapshotView.as_view(), name='project-progress-snapshot'),
    path('progress/s-curve/', ProjectSCurveView.as_view(), name='project-progress-s-curve'),
    path('progress/activities/', ProjectActivityProgressView.as_view(), name='project-progress-activities'),
    path('progress/kpis/', ProjectProgressKpisView.as_view(), name='project-progress-kpis'),
    path('progress/history/', ProjectProgressHistoryView.as_view(), name='project-progress-history'),
    path('progress/manual/', ProjectManualProgressView.as_view(), name='project-progress-manual'),
]
