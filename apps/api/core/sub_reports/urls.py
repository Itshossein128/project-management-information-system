from django.urls import path

from sub_reports.views import DisciplineSubReportViewSet

list_view = DisciplineSubReportViewSet.as_view({'get': 'list', 'post': 'create'})
detail_view = DisciplineSubReportViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)
submit_view = DisciplineSubReportViewSet.as_view({'post': 'submit'})
approve_view = DisciplineSubReportViewSet.as_view({'post': 'approve'})
reject_view = DisciplineSubReportViewSet.as_view({'post': 'reject'})

urlpatterns = [
    path('sub-reports/', list_view, name='sub-reports-list'),
    path('sub-reports/<uuid:pk>/', detail_view, name='sub-reports-detail'),
    path('sub-reports/<uuid:pk>/submit/', submit_view, name='sub-reports-submit'),
    path('sub-reports/<uuid:pk>/approve/', approve_view, name='sub-reports-approve'),
    path('sub-reports/<uuid:pk>/reject/', reject_view, name='sub-reports-reject'),
]
