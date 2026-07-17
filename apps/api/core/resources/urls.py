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
tx_list = InventoryTransactionViewSet.as_view({'get': 'list', 'post': 'create'})
tx_detail = InventoryTransactionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    path('materials/', material_list, name='material-list'),
    path('materials/<uuid:pk>/', material_detail, name='material-detail'),
    path('material-requests/', request_list, name='material-request-list'),
    path('material-requests/<uuid:pk>/', request_detail, name='material-request-detail'),
    path('inventory-transactions/', tx_list, name='inventory-tx-list'),
    path('inventory-transactions/balance/', InventoryRunningBalanceView.as_view(), name='inventory-tx-balance'),
    path('inventory-transactions/<uuid:pk>/', tx_detail, name='inventory-tx-detail'),
    path('material-balance/', MaterialBalanceListView.as_view(), name='material-balance-list'),
    path('material-balance/consumption/', MaterialConsumptionView.as_view(), name='material-balance-consumption'),
    path('material-balance/<uuid:mid>/', MaterialBalanceDetailView.as_view(), name='material-balance-detail'),
]
