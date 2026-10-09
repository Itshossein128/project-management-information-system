from django.urls import path

from documents.views import (
    CorrespondenceRespondView,
    CorrespondenceViewSet,
    DocumentRevisionUploadView,
    MeetingActionDetailView,
    MeetingActionNestedView,
    MeetingMinutesViewSet,
    OpenMeetingActionsView,
    ProjectDocumentViewSet,
)

# View actions for listing all project documents or creating a new document
doc_list = ProjectDocumentViewSet.as_view({'get': 'list', 'post': 'create'})
# View actions for retrieving details of a specific document or deleting it
doc_detail = ProjectDocumentViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

# View actions for listing all correspondences or creating a new correspondence
corr_list = CorrespondenceViewSet.as_view({'get': 'list', 'post': 'create'})
# View actions for updating (partially) or deleting a specific correspondence
corr_detail = CorrespondenceViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})

# View actions for listing all meeting minutes or creating a new meeting minute entry
meeting_list = MeetingMinutesViewSet.as_view({'get': 'list', 'post': 'create'})
# View actions for retrieving, partially updating, or deleting a specific meeting minute entry
meeting_detail = MeetingMinutesViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

meeting_action_list = MeetingActionNestedView.as_view({'get': 'list', 'post': 'create'})
meeting_action_patch = MeetingActionDetailView.as_view({'patch': 'partial_update'})
open_meeting_actions = OpenMeetingActionsView.as_view({'get': 'list'})

# URL routing patterns for the documents app. These define the endpoints for accessing and managing
# documents, revisions, correspondences, and meeting minutes within a project context.
urlpatterns = [
    path('documents/', doc_list, name='document-list'),
    path('documents/<uuid:pk>/', doc_detail, name='document-detail'),
    path('documents/<uuid:pk>/revisions/', DocumentRevisionUploadView.as_view(), name='document-revision'),
    path('correspondence/', corr_list, name='correspondence-list'),
    path('correspondence/<uuid:pk>/', corr_detail, name='correspondence-detail'),
    path('correspondence/<uuid:pk>/respond/', CorrespondenceRespondView.as_view(), name='correspondence-respond'),
    path('meetings/', meeting_list, name='meeting-list'),
    path('meetings/<uuid:pk>/', meeting_detail, name='meeting-detail'),
    path(
        'meetings/<uuid:meeting_pk>/actions/',
        meeting_action_list,
        name='meeting-action-list',
    ),
    path(
        'meeting-actions/open/',
        open_meeting_actions,
        name='meeting-action-open',
    ),
    path(
        'meeting-actions/<uuid:pk>/',
        meeting_action_patch,
        name='meeting-action-detail',
    ),
]
