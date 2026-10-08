from django.urls import path

from projects.portfolio_views import PortfolioSummaryView

urlpatterns = [
    path('summary/', PortfolioSummaryView.as_view(), name='portfolio-summary'),
]
