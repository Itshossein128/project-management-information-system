from django.urls import path

from projects.dashboard_views import PortfolioDashboardView
from projects.portfolio_views import PortfolioSummaryView
from projects.report_views import PortfolioReportCatalogView, PortfolioReportExportView

urlpatterns = [
    path('summary/', PortfolioSummaryView.as_view(), name='portfolio-summary'),
    path('dashboard/', PortfolioDashboardView.as_view(), name='portfolio-dashboard'),
    path('reports/catalog/', PortfolioReportCatalogView.as_view(), name='portfolio-report-catalog'),
    path(
        'reports/<str:report_type>/export/',
        PortfolioReportExportView.as_view(),
        name='portfolio-report-export',
    ),
]
