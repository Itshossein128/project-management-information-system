from django.urls import path

from workflow.views import (
    ManagementDecisionViewSet,
    WorkflowDefinitionActivateView,
    WorkflowDefinitionRetireView,
    WorkflowDefinitionViewSet,
    WorkflowInstanceActionView,
    WorkflowInstanceLogView,
    WorkflowInstanceViewSet,
)

decision_list = ManagementDecisionViewSet.as_view({'get': 'list', 'post': 'create'})
decision_detail = ManagementDecisionViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
)

definition_list = WorkflowDefinitionViewSet.as_view({'get': 'list', 'post': 'create'})
definition_detail = WorkflowDefinitionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})

instance_list = WorkflowInstanceViewSet.as_view({'get': 'list', 'post': 'create'})
instance_detail = WorkflowInstanceViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path('decisions/', decision_list, name='management-decision-list'),
    path('decisions/<uuid:pk>/', decision_detail, name='management-decision-detail'),
    path('workflows/definitions/', definition_list, name='workflow-definition-list'),
    path('workflows/definitions/<uuid:pk>/', definition_detail, name='workflow-definition-detail'),
    path(
        'workflows/definitions/<uuid:pk>/activate/',
        WorkflowDefinitionActivateView.as_view(),
        name='workflow-definition-activate',
    ),
    path(
        'workflows/definitions/<uuid:pk>/retire/',
        WorkflowDefinitionRetireView.as_view(),
        name='workflow-definition-retire',
    ),
    path('workflows/instances/', instance_list, name='workflow-instance-list'),
    path('workflows/instances/<uuid:pk>/', instance_detail, name='workflow-instance-detail'),
    path(
        'workflows/instances/<uuid:pk>/approve/',
        WorkflowInstanceActionView.as_view(),
        {'action_name': 'approve'},
        name='workflow-instance-approve',
    ),
    path(
        'workflows/instances/<uuid:pk>/reject/',
        WorkflowInstanceActionView.as_view(),
        {'action_name': 'reject'},
        name='workflow-instance-reject',
    ),
    path(
        'workflows/instances/<uuid:pk>/cancel/',
        WorkflowInstanceActionView.as_view(),
        {'action_name': 'cancel'},
        name='workflow-instance-cancel',
    ),
    path(
        'workflows/instances/<uuid:pk>/log/',
        WorkflowInstanceLogView.as_view(),
        name='workflow-instance-log',
    ),
]
