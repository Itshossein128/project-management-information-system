from django.urls import path

from cash_flow.views import (
    CashFlowForecastListView,
    CashFlowForecastUpsertView,
    CashFlowListView,
    CashFlowMonthlyView,
    CashTransactionViewSet,
    GapAnalysisView,
    PortfolioCycleListCreateView,
    PortfolioDecisionCreateView,
    PortfolioProposeView,
    PortfolioReportView,
    PortfolioSimulationCompareView,
    PortfolioSimulationCreateView,
    PriorityScoreView,
    ProjectionView,
    ReceivablesView,
    SuggestedNeedView,
)

transaction_list = CashTransactionViewSet.as_view({'post': 'create'})
transaction_detail = CashTransactionViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = [
    path('cash-flow/', CashFlowListView.as_view(), name='cash-flow-list'),
    path('cash-flow/transactions/', transaction_list, name='cash-transaction-create'),
    path('cash-flow/transactions/<uuid:pk>/', transaction_detail, name='cash-transaction-detail'),
    path('cash-flow/monthly/', CashFlowMonthlyView.as_view(), name='cash-flow-monthly'),
    path('cash-flow/forecast/', CashFlowForecastListView.as_view(), name='cash-flow-forecast-list'),
    path('cash-flow/forecast/<str:month>/', CashFlowForecastUpsertView.as_view(), name='cash-flow-forecast-upsert'),
    path('cash-flow/gap-analysis/', GapAnalysisView.as_view(), name='cash-flow-gap-analysis'),
    path('cash-flow/receivables/', ReceivablesView.as_view(), name='cash-flow-receivables'),
    path('cash-flow/projection/', ProjectionView.as_view(), name='cash-flow-projection'),
    path('cash-flow/suggested-need/', SuggestedNeedView.as_view(), name='cash-flow-suggested-need'),
    path('cash-flow/priority-score/', PriorityScoreView.as_view(), name='cash-flow-priority-score'),
]

global_urlpatterns = [
    path(
        'api/v1/cash-flow/portfolio/cycles/',
        PortfolioCycleListCreateView.as_view(),
        name='cash-flow-portfolio-cycles',
    ),
    path(
        'api/v1/cash-flow/portfolio/cycles/<uuid:cycle_id>/propose/',
        PortfolioProposeView.as_view(),
        name='cash-flow-portfolio-propose',
    ),
    path(
        'api/v1/cash-flow/portfolio/cycles/<uuid:cycle_id>/decisions/',
        PortfolioDecisionCreateView.as_view(),
        name='cash-flow-portfolio-decisions',
    ),
    path(
        'api/v1/cash-flow/portfolio/cycles/<uuid:cycle_id>/simulations/',
        PortfolioSimulationCreateView.as_view(),
        name='cash-flow-portfolio-simulations',
    ),
    path(
        'api/v1/cash-flow/portfolio/cycles/<uuid:cycle_id>/simulations/<uuid:sim_id>/compare/',
        PortfolioSimulationCompareView.as_view(),
        name='cash-flow-portfolio-simulation-compare',
    ),
    path(
        'api/v1/cash-flow/portfolio/report/',
        PortfolioReportView.as_view(),
        name='cash-flow-portfolio-report',
    ),
]
