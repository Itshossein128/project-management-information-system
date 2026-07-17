from django.urls import path

from economic.views import (
    CashFlowRealView,
    EconomicForecastView,
    EconomicHistoryView,
    EconomicSnapshotView,
    FinancingCostView,
    InflationIndexUpsertView,
    InflationIndicesView,
    InflationMappingDetailView,
    InflationMappingListCreateView,
    LatestSimulationView,
    SensitivityView,
    SimulateStatusView,
    SimulateView,
    WorkingCapitalView,
)

project_urlpatterns = [
    path('economic/snapshot/', EconomicSnapshotView.as_view(), name='economic-snapshot'),
    path('economic/history/', EconomicHistoryView.as_view(), name='economic-history'),
    path('economic/financing-cost/', FinancingCostView.as_view(), name='economic-financing'),
    path('economic/inflation-indices/', InflationIndicesView.as_view(), name='economic-inflation-indices'),
    path('economic/forecast/', EconomicForecastView.as_view(), name='economic-forecast'),
    path('economic/working-capital/', WorkingCapitalView.as_view(), name='economic-working-capital'),
    path('economic/cash-flow-real/', CashFlowRealView.as_view(), name='economic-cash-flow-real'),
    path(
        'economic/inflation-mappings/',
        InflationMappingListCreateView.as_view(),
        name='economic-inflation-mappings',
    ),
    path(
        'economic/inflation-mappings/<uuid:mapping_id>/',
        InflationMappingDetailView.as_view(),
        name='economic-inflation-mapping-detail',
    ),
    path('economic/sensitivity/', SensitivityView.as_view(), name='economic-sensitivity'),
    path('economic/simulate/', SimulateView.as_view(), name='economic-simulate'),
    path('economic/simulate/status/<str:task_id>/', SimulateStatusView.as_view(), name='economic-simulate-status'),
    path('economic/simulate/latest/', LatestSimulationView.as_view(), name='economic-simulate-latest'),
]

global_urlpatterns = [
    path(
        'api/v1/inflation-indices/<str:name>/<str:index_date>/',
        InflationIndexUpsertView.as_view(),
        name='inflation-index-upsert',
    ),
]

urlpatterns = project_urlpatterns
