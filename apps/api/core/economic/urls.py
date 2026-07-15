from django.urls import path

from economic.views import (
    EconomicHistoryView,
    EconomicSnapshotView,
    FinancingCostView,
    InflationIndexUpsertView,
    InflationIndicesView,
    LatestSimulationView,
    SimulateStatusView,
    SimulateView,
)

project_urlpatterns = [
    path('economic/snapshot/', EconomicSnapshotView.as_view(), name='economic-snapshot'),
    path('economic/history/', EconomicHistoryView.as_view(), name='economic-history'),
    path('economic/financing-cost/', FinancingCostView.as_view(), name='economic-financing'),
    path('economic/inflation-indices/', InflationIndicesView.as_view(), name='economic-inflation-indices'),
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
