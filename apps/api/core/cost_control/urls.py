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

# Viewset action routing for budget_list.
budget_list = BudgetViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for budget_detail.
budget_detail = BudgetViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
# Viewset action routing for cost_list.
cost_list = ActualCostViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for cost_detail.
cost_detail = ActualCostViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
# Viewset action routing for pool_list.
pool_list = CostPoolViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for pool_detail.
pool_detail = CostPoolViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
# Viewset action routing for supplier_list.
supplier_list = SupplierViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for supplier_detail.
supplier_detail = SupplierViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

# List of URL patterns for urlpatterns routing.
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

# List of URL patterns for global_urlpatterns routing.
global_urlpatterns = [
    path('api/v1/suppliers/', GlobalSupplierListView.as_view(), name='global-supplier-list'),
]
