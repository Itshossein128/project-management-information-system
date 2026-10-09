from django.urls import path

from cost_control.budget_version_views import (
    BudgetChangeRequestActionView,
    BudgetChangeRequestDetailView,
    BudgetChangeRequestListCreateView,
    BudgetRemainingView,
    BudgetTransferView,
    BudgetVersionActionView,
    BudgetVersionCompareView,
    BudgetVersionDetailView,
    BudgetVersionLinesView,
    BudgetVersionListCreateView,
)
from cost_control.cbs_views import (
    CBSDetailView,
    CBSListCreateView,
    CommitmentViewSet,
    PaymentListCreateView,
)
from cost_control.views import (
    ActualCostViewSet,
    BudgetBulkView,
    BudgetViewSet,
    CostPoolAllocateView,
    CostPoolAutoAllocateView,
    CostPoolViewSet,
    CostSummaryView,
    GlobalSupplierListView,
    SupplierViewSet,
    VarianceView,
)

budget_list = BudgetViewSet.as_view({'get': 'list', 'post': 'create'})
budget_detail = BudgetViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
cost_list = ActualCostViewSet.as_view({'get': 'list', 'post': 'create'})
cost_detail = ActualCostViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
pool_list = CostPoolViewSet.as_view({'get': 'list', 'post': 'create'})
pool_detail = CostPoolViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
supplier_list = SupplierViewSet.as_view({'get': 'list', 'post': 'create'})
supplier_detail = SupplierViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
commitment_list = CommitmentViewSet.as_view({'get': 'list', 'post': 'create'})
commitment_detail = CommitmentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
commitment_approve = CommitmentViewSet.as_view({'post': 'approve'})

urlpatterns = [
    path('budgets/', budget_list, name='budget-list'),
    path('budgets/bulk/', BudgetBulkView.as_view(), name='budget-bulk'),
    path('budgets/remaining/', BudgetRemainingView.as_view(), name='budget-remaining'),
    path('budgets/transfers/', BudgetTransferView.as_view(), name='budget-transfers'),
    path('budgets/<uuid:pk>/', budget_detail, name='budget-detail'),
    path('budget-versions/', BudgetVersionListCreateView.as_view(), name='budget-version-list'),
    path(
        'budget-versions/compare/',
        BudgetVersionCompareView.as_view(),
        name='budget-version-compare',
    ),
    path(
        'budget-versions/<uuid:pk>/',
        BudgetVersionDetailView.as_view(),
        name='budget-version-detail',
    ),
    path(
        'budget-versions/<uuid:version_id>/lines/',
        BudgetVersionLinesView.as_view(),
        name='budget-version-lines',
    ),
    path(
        'budget-versions/<uuid:pk>/<str:action_name>/',
        BudgetVersionActionView.as_view(),
        name='budget-version-action',
    ),
    path(
        'budget-change-requests/',
        BudgetChangeRequestListCreateView.as_view(),
        name='budget-change-request-list',
    ),
    path(
        'budget-change-requests/<uuid:pk>/',
        BudgetChangeRequestDetailView.as_view(),
        name='budget-change-request-detail',
    ),
    path(
        'budget-change-requests/<uuid:pk>/<str:action_name>/',
        BudgetChangeRequestActionView.as_view(),
        name='budget-change-request-action',
    ),
    path('costs/', cost_list, name='cost-list'),
    path('costs/variance/', VarianceView.as_view(), name='cost-variance'),
    path('costs/summary/', CostSummaryView.as_view(), name='cost-summary'),
    path('costs/<uuid:pk>/', cost_detail, name='cost-detail'),
    path('cost-pools/', pool_list, name='cost-pool-list'),
    path('cost-pools/<uuid:pk>/', pool_detail, name='cost-pool-detail'),
    path('cost-pools/<uuid:pk>/allocate/', CostPoolAllocateView.as_view(), name='cost-pool-allocate'),
    path('cost-pools/<uuid:pk>/auto-allocate/', CostPoolAutoAllocateView.as_view(), name='cost-pool-auto-allocate'),
    path('suppliers/', supplier_list, name='supplier-list'),
    path('suppliers/<uuid:pk>/', supplier_detail, name='supplier-detail'),
    path('cbs/', CBSListCreateView.as_view(), name='cbs-list'),
    path('cbs/<uuid:pk>/', CBSDetailView.as_view(), name='cbs-detail'),
    path('commitments/', commitment_list, name='commitment-list'),
    path('commitments/<uuid:pk>/', commitment_detail, name='commitment-detail'),
    path('commitments/<uuid:pk>/approve/', commitment_approve, name='commitment-approve'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list'),
]

global_urlpatterns = [
    path('api/v1/suppliers/', GlobalSupplierListView.as_view(), name='global-supplier-list'),
]
