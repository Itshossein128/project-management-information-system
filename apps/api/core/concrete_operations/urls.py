from django.urls import path

from concrete_operations.views import ConcreteBatchViewSet, ConcreteOperationsReportView, ReadyMixDeliveryViewSet

batch_list = ConcreteBatchViewSet.as_view({'get': 'list', 'post': 'create'})
batch_detail = ConcreteBatchViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
delivery_list = ReadyMixDeliveryViewSet.as_view({'get': 'list', 'post': 'create'})
delivery_detail = ReadyMixDeliveryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    path('concrete-batches/', batch_list, name='concrete-batch-list'),
    path('concrete-batches/<uuid:pk>/', batch_detail, name='concrete-batch-detail'),
    path('ready-mix-deliveries/', delivery_list, name='ready-mix-delivery-list'),
    path('ready-mix-deliveries/<uuid:pk>/', delivery_detail, name='ready-mix-delivery-detail'),
    path('concrete-operations/summary/', ConcreteOperationsReportView.as_view(), name='concrete-operations-summary'),
    path('concrete-operations/export/', ConcreteOperationsReportView.as_view(), {'export': True}, name='concrete-operations-export'),
]
