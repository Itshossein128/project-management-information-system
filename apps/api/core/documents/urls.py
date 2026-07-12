from django.urls import path

from documents.views import (
    CorrespondenceRespondView,
    CorrespondenceViewSet,
    DocumentRevisionUploadView,
    MeetingMinutesViewSet,
    ProjectDocumentViewSet,
)

# Viewset action routing for doc_list.
doc_list = ProjectDocumentViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for doc_detail.
doc_detail = ProjectDocumentViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
# Viewset action routing for corr_list.
corr_list = CorrespondenceViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for corr_detail.
corr_detail = CorrespondenceViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
# Viewset action routing for meeting_list.
meeting_list = MeetingMinutesViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for meeting_detail.
meeting_detail = MeetingMinutesViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('documents/', doc_list, name='document-list'),
    path('documents/<uuid:pk>/', doc_detail, name='document-detail'),
    path('documents/<uuid:pk>/revisions/', DocumentRevisionUploadView.as_view(), name='document-revision'),
    path('correspondence/', corr_list, name='correspondence-list'),
    path('correspondence/<uuid:pk>/', corr_detail, name='correspondence-detail'),
    path('correspondence/<uuid:pk>/respond/', CorrespondenceRespondView.as_view(), name='correspondence-respond'),
    path('meetings/', meeting_list, name='meeting-list'),
    path('meetings/<uuid:pk>/', meeting_detail, name='meeting-detail'),
]
