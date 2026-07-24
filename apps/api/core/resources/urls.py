from django.urls import path

from resources.views import (
    InventoryRunningBalanceView,
    InventoryTransactionViewSet,
    MaterialBalanceDetailView,
    MaterialBalanceListView,
    MaterialConsumptionView,
    MaterialRequestViewSet,
    MaterialViewSet,
)

material_list = MaterialViewSet.as_view({'get': 'list', 'post': 'create'})
material_detail = MaterialViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
request_list = MaterialRequestViewSet.as_view({'get': 'list', 'post': 'create'})
request_detail = MaterialRequestViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
request_approve = MaterialRequestViewSet.as_view({'post': 'approve'})
request_place_order = MaterialRequestViewSet.as_view({'post': 'place_order'})
request_deliver = MaterialRequestViewSet.as_view({'post': 'deliver'})
request_cancel = MaterialRequestViewSet.as_view({'post': 'cancel'})
tx_list = InventoryTransactionViewSet.as_view({'get': 'list', 'post': 'create'})
tx_detail = InventoryTransactionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    path('materials/', material_list, name='material-list'),
    path('materials/<uuid:pk>/', material_detail, name='material-detail'),
    path('material-requests/', request_list, name='material-request-list'),
    path('material-requests/<uuid:pk>/', request_detail, name='material-request-detail'),
    path('material-requests/<uuid:pk>/approve/', request_approve, name='material-request-approve'),
    path('material-requests/<uuid:pk>/place-order/', request_place_order, name='material-request-place-order'),
    path('material-requests/<uuid:pk>/deliver/', request_deliver, name='material-request-deliver'),
    path('material-requests/<uuid:pk>/cancel/', request_cancel, name='material-request-cancel'),
    path('inventory-transactions/', tx_list, name='inventory-tx-list'),
    path('inventory-transactions/balance/', InventoryRunningBalanceView.as_view(), name='inventory-tx-balance'),
    path('inventory-transactions/<uuid:pk>/', tx_detail, name='inventory-tx-detail'),
    path('material-balance/', MaterialBalanceListView.as_view(), name='material-balance-list'),
    path('material-balance/consumption/', MaterialConsumptionView.as_view(), name='material-balance-consumption'),
    path('material-balance/<uuid:mid>/', MaterialBalanceDetailView.as_view(), name='material-balance-detail'),
]
