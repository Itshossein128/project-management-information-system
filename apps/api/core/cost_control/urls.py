from django.urls import path

from cost_control.views import (
    ActualCostViewSet,
    BudgetBulkView,
    BudgetViewSet,
    CostPoolAllocateView,
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

urlpatterns = [
    path('budgets/', budget_list, name='budget-list'),
    path('budgets/bulk/', BudgetBulkView.as_view(), name='budget-bulk'),
    path('budgets/<uuid:pk>/', budget_detail, name='budget-detail'),
    path('costs/', cost_list, name='cost-list'),
    path('costs/variance/', VarianceView.as_view(), name='cost-variance'),
    path('costs/summary/', CostSummaryView.as_view(), name='cost-summary'),
    path('costs/<uuid:pk>/', cost_detail, name='cost-detail'),
    path('cost-pools/', pool_list, name='cost-pool-list'),
    path('cost-pools/<uuid:pk>/', pool_detail, name='cost-pool-detail'),
    path('cost-pools/<uuid:pk>/allocate/', CostPoolAllocateView.as_view(), name='cost-pool-allocate'),
    path('suppliers/', supplier_list, name='supplier-list'),
    path('suppliers/<uuid:pk>/', supplier_detail, name='supplier-detail'),
]

global_urlpatterns = [
    path('api/v1/suppliers/', GlobalSupplierListView.as_view(), name='global-supplier-list'),
]
