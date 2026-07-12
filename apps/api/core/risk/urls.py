from django.urls import path

from risk.views import BarrierLogViewSet

# Viewset action routing for barrier_list.
barrier_list = BarrierLogViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for barrier_detail.
barrier_detail = BarrierLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('barriers/', barrier_list, name='project-barriers-list'),
    path('barriers/<uuid:pk>/', barrier_detail, name='project-barriers-detail'),
]
