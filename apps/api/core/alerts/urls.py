from django.urls import path

from alerts.views import (
    ActiveAlertsView,
    AlertAcknowledgeView,
    AlertLogListView,
    AlertRuleDetailView,
    AlertRuleListCreateView,
)

urlpatterns = [
    path('alert-rules/', AlertRuleListCreateView.as_view(), name='alert-rule-list'),
    path('alert-rules/<uuid:rid>/', AlertRuleDetailView.as_view(), name='alert-rule-detail'),
    path('alerts/', AlertLogListView.as_view(), name='alert-log-list'),
    path('alerts/active/', ActiveAlertsView.as_view(), name='alert-active-counts'),
    path('alerts/<uuid:lid>/acknowledge/', AlertAcknowledgeView.as_view(), name='alert-acknowledge'),
]
