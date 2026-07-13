from django.urls import path, include

from projects.views import ProjectViewSet
from projects.member_views import ProjectMemberViewSet, RoleListView, UserLookupView
from project_templates.views import SaveProjectAsTemplateView
from business_meta.views import (
    TableDefinitionViewSet,
    FieldDefinitionViewSet,
    ProjectPositionViewSet,
)
from business_meta.data_views import (
    DynamicRowsView,
    DynamicRowDetailView,
    DynamicRowsExportView,
    DynamicRowsImportView,
)

# --- ViewSet Actions Setup ---

# Dynamic Table Definitions
table_list = TableDefinitionViewSet.as_view({'get': 'list', 'post': 'create'})
table_detail = TableDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Dynamic Table Fields
field_list = FieldDefinitionViewSet.as_view({'get': 'list', 'post': 'create'})
field_detail = FieldDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Project Organizational Positions
position_list = ProjectPositionViewSet.as_view({'get': 'list', 'post': 'create'})
position_detail = ProjectPositionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Project Members (User Assignments)
member_list = ProjectMemberViewSet.as_view({'get': 'list', 'post': 'create'})
member_detail = ProjectMemberViewSet.as_view({'patch': 'partial_update'})
member_permissions = ProjectMemberViewSet.as_view({'get': 'permissions', 'post': 'permissions', 'delete': 'permissions'})

# --- Project URLs ---
urlpatterns = [
    # Project CRUD
    path('', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),

    # Project Templates
    path('templates/', ProjectViewSet.as_view({'get': 'templates'}), name='project-templates'),
    path('from_template/', ProjectViewSet.as_view({'post': 'from_template'}), name='project-from-template'),

    # Project Details (Specific Project)
    path('<uuid:project_pk>/', ProjectViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update'}
    ), name='project-detail'),

    # Project Positions
    path('<uuid:project_pk>/positions/', position_list, name='project-position-list'),
    path('<uuid:project_pk>/positions/<uuid:pk>/', position_detail, name='project-position-detail'),

    # Project Members
    path('<uuid:project_pk>/members/', member_list, name='project-member-list'),
    path('<uuid:project_pk>/members/<uuid:user_id>/', member_detail, name='project-member-detail'),
    path(
        '<uuid:project_pk>/members/<uuid:user_id>/permissions/',
        member_permissions,
        name='project-member-permissions',
    ),

    # Project Dynamic Tables (Business Meta)
    path('<uuid:project_pk>/tables/', table_list, name='tabledefinition-list'),
    path('<uuid:project_pk>/tables/<int:pk>/', table_detail, name='tabledefinition-detail'),
    path(
        '<uuid:project_pk>/tables/by_slug/<str:table_slug>/',
        TableDefinitionViewSet.as_view({'get': 'by_slug'}),
        name='tabledefinition-by-slug',
    ),

    # Fields within Dynamic Tables
    path('<uuid:project_pk>/tables/<int:table_pk>/fields/', field_list, name='fielddefinition-list'),
    path('<uuid:project_pk>/tables/<int:table_pk>/fields/<int:pk>/', field_detail, name='fielddefinition-detail'),

    # Dynamic Table Data (Rows)
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/', DynamicRowsView.as_view(), name='dynamic-rows-list'),
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/export/', DynamicRowsExportView.as_view(), name='dynamic-rows-export'),
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/import/', DynamicRowsImportView.as_view(), name='dynamic-rows-import'),
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/<str:row_id>/', DynamicRowDetailView.as_view(), name='dynamic-row-detail'),

    # Save Project as Template
    path('<uuid:project_pk>/save-as-template/', SaveProjectAsTemplateView.as_view(), name='project-save-as-template'),

    # --- Nested Apps ---
    # These apps have endpoints nested under a specific project context
    path('<uuid:project_pk>/', include('inventory.project_urls')),
    path('<uuid:project_pk>/', include('wbs.urls')),
    path('<uuid:project_pk>/', include('schedule.urls')),
    path('<uuid:project_pk>/', include('field_reports.urls')),
    path('<uuid:project_pk>/', include('risk.urls')),
    path('<uuid:project_pk>/', include('hr.urls')),
    path('<uuid:project_pk>/', include('sub_reports.urls')),
    path('<uuid:project_pk>/', include('cost_control.urls')),
    path('<uuid:project_pk>/', include('resources.urls')),
    path('<uuid:project_pk>/', include('cash_flow.urls')),
    path('<uuid:project_pk>/', include('contracts.urls')),
    path('<uuid:project_pk>/', include('subcontractors.urls')),
    path('<uuid:project_pk>/', include('documents.urls')),
]
