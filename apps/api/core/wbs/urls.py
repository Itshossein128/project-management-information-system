from django.urls import path

from wbs.views import WBSViewSet

wbs_list = WBSViewSet.as_view({'get': 'list', 'post': 'create'})
wbs_flat = WBSViewSet.as_view({'get': 'flat'})
wbs_detail = WBSViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
wbs_move = WBSViewSet.as_view({'post': 'move'})

urlpatterns = [
    path('wbs/', wbs_list, name='wbs-list'),
    path('wbs/flat/', wbs_flat, name='wbs-flat'),
    path('wbs/<uuid:wbs_id>/', wbs_detail, name='wbs-detail'),
    path('wbs/<uuid:wbs_id>/move/', wbs_move, name='wbs-move'),
]
