from django.urls import path

from cash_flow.views import (
    CashFlowForecastListView,
    CashFlowForecastUpsertView,
    CashFlowListView,
    CashFlowMonthlyView,
    CashTransactionViewSet,
    GapAnalysisView,
    ReceivablesView,
)

# Viewset action routing for transaction_list.
transaction_list = CashTransactionViewSet.as_view({'post': 'create'})
# Viewset action routing for transaction_detail.
transaction_detail = CashTransactionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('cash-flow/', CashFlowListView.as_view(), name='cash-flow-list'),
    path('cash-flow/transactions/', transaction_list, name='cash-transaction-create'),
    path('cash-flow/transactions/<uuid:pk>/', transaction_detail, name='cash-transaction-detail'),
    path('cash-flow/monthly/', CashFlowMonthlyView.as_view(), name='cash-flow-monthly'),
    path('cash-flow/forecast/', CashFlowForecastListView.as_view(), name='cash-flow-forecast-list'),
    path('cash-flow/forecast/<str:month>/', CashFlowForecastUpsertView.as_view(), name='cash-flow-forecast-upsert'),
    path('cash-flow/gap-analysis/', GapAnalysisView.as_view(), name='cash-flow-gap-analysis'),
    path('cash-flow/receivables/', ReceivablesView.as_view(), name='cash-flow-receivables'),
]
