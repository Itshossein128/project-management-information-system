from django.urls import path

from risk.views import BarrierLogViewSet, RiskEventViewSet, RiskMatrixView

barrier_list = BarrierLogViewSet.as_view({'get': 'list', 'post': 'create'})
barrier_detail = BarrierLogViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
risk_list = RiskEventViewSet.as_view({'get': 'list', 'post': 'create'})
risk_detail = RiskEventViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

urlpatterns = [
    path('barriers/', barrier_list, name='project-barriers-list'),
    path('barriers/<uuid:pk>/', barrier_detail, name='project-barriers-detail'),
    path('risk-events/', risk_list, name='project-risk-events-list'),
    path('risk-events/matrix/', RiskMatrixView.as_view(), name='project-risk-events-matrix'),
    path('risk-events/<uuid:pk>/', risk_detail, name='project-risk-events-detail'),
]
