from django.urls import path

from wbs.views import WBSViewSet

# Viewset action routing for wbs_list.
wbs_list = WBSViewSet.as_view({'get': 'list', 'post': 'create'})
# Definition of wbs_flat.
wbs_flat = WBSViewSet.as_view({'get': 'flat'})
# Viewset action routing for wbs_detail.
wbs_detail = WBSViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
# Definition of wbs_move.
wbs_move = WBSViewSet.as_view({'post': 'move'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('wbs/', wbs_list, name='wbs-list'),
    path('wbs/flat/', wbs_flat, name='wbs-flat'),
    path('wbs/<uuid:wbs_id>/', wbs_detail, name='wbs-detail'),
    path('wbs/<uuid:wbs_id>/move/', wbs_move, name='wbs-move'),
]
