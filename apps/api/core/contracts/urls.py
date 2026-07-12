from django.urls import path

from contracts.views import (
    ChangeOrderApproveView,
    ChangeOrderDetailView,
    ChangeOrderView,
    ContractItemsBulkView,
    ContractViewSet,
    IPCApproveView,
    IPCDeductionDetailView,
    IPCDeductionListView,
    IPCItemUpdateView,
    IPCPayView,
    IPCPdfView,
    IPCPopulateView,
    IPCRejectView,
    IPCSubmitView,
    IPCViewSet,
)

contract_list = ContractViewSet.as_view({'get': 'list', 'post': 'create'})
contract_detail = ContractViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
ipc_list = IPCViewSet.as_view({'get': 'list', 'post': 'create'})
ipc_detail = IPCViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})

urlpatterns = [
    path('contracts/', contract_list, name='contract-list'),
    path('contracts/<uuid:pk>/', contract_detail, name='contract-detail'),
    path('contracts/<uuid:pk>/items/', ContractItemsBulkView.as_view(), name='contract-items-bulk'),
    path('contracts/<uuid:pk>/change-orders/', ChangeOrderView.as_view(), name='change-order-create'),
    path(
        'contracts/<uuid:pk>/change-orders/<uuid:chid>/',
        ChangeOrderDetailView.as_view(),
        name='change-order-detail',
    ),
    path(
        'contracts/<uuid:pk>/change-orders/<uuid:chid>/approve/',
        ChangeOrderApproveView.as_view(),
        name='change-order-approve',
    ),
    path('ipcs/', ipc_list, name='ipc-list'),
    path('ipcs/<uuid:pk>/', ipc_detail, name='ipc-detail'),
    path('ipcs/<uuid:pk>/populate/', IPCPopulateView.as_view(), name='ipc-populate'),
    path('ipcs/<uuid:pk>/items/<uuid:itemid>/', IPCItemUpdateView.as_view(), name='ipc-item-update'),
    path('ipcs/<uuid:pk>/deductions/', IPCDeductionListView.as_view(), name='ipc-deduction-list'),
    path('ipcs/<uuid:pk>/deductions/<uuid:did>/', IPCDeductionDetailView.as_view(), name='ipc-deduction-detail'),
    path('ipcs/<uuid:pk>/submit/', IPCSubmitView.as_view(), name='ipc-submit'),
    path('ipcs/<uuid:pk>/approve/', IPCApproveView.as_view(), name='ipc-approve'),
    path('ipcs/<uuid:pk>/pay/', IPCPayView.as_view(), name='ipc-pay'),
    path('ipcs/<uuid:pk>/reject/', IPCRejectView.as_view(), name='ipc-reject'),
    path('ipcs/<uuid:pk>/pdf/', IPCPdfView.as_view(), name='ipc-pdf'),
]
