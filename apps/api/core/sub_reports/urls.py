from django.urls import path

from sub_reports.views import DisciplineSubReportViewSet

# Viewset action routing for list_view.
list_view = DisciplineSubReportViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for detail_view.
detail_view = DisciplineSubReportViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
# Viewset action routing for submit_view.
submit_view = DisciplineSubReportViewSet.as_view({'post': 'submit'})
# Viewset action routing for approve_view.
approve_view = DisciplineSubReportViewSet.as_view({'post': 'approve'})
# Viewset action routing for reject_view.
reject_view = DisciplineSubReportViewSet.as_view({'post': 'reject'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('sub-reports/', list_view, name='sub-reports-list'),
    path('sub-reports/<uuid:pk>/', detail_view, name='sub-reports-detail'),
    path('sub-reports/<uuid:pk>/submit/', submit_view, name='sub-reports-submit'),
    path('sub-reports/<uuid:pk>/approve/', approve_view, name='sub-reports-approve'),
    path('sub-reports/<uuid:pk>/reject/', reject_view, name='sub-reports-reject'),
]
