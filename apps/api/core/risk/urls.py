from django.urls import path

from risk.views import BarrierLogViewSet

barrier_list = BarrierLogViewSet.as_view({'get': 'list', 'post': 'create'})
barrier_detail = BarrierLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

urlpatterns = [
    path('barriers/', barrier_list, name='project-barriers-list'),
    path('barriers/<uuid:pk>/', barrier_detail, name='project-barriers-detail'),
]
