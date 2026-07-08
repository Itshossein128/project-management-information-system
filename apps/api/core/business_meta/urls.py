from django.urls import path, include
from .views import (
    BusinessViewSet,
    UserBusinessAssignmentViewSet,
    BusinessJobPositionViewSet,
    TableDefinitionViewSet,
    FieldDefinitionViewSet,
)
from .data_views import (
    DynamicRowsView,
    DynamicRowDetailView,
    DynamicRowsExportView,
    DynamicRowsImportView,
)

# Table definition viewsets for listing and creating table metadata within a business
table_list = TableDefinitionViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)

# Table definition viewsets for detailed operations (retrieve, update, delete)
table_detail = TableDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Field definition viewsets for listing and creating fields within a specific table
field_list = FieldDefinitionViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)

# Field definition viewsets for detailed operations (retrieve, update, delete)
field_detail = FieldDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Job position viewsets for listing and creating job positions within a business
job_position_list = BusinessJobPositionViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)

# Job position viewsets for detailed operations (retrieve, update, delete)
job_position_detail = BusinessJobPositionViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }
)

# User-business assignment viewsets for assigning users to businesses (list/create)
assignment_list = UserBusinessAssignmentViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)

# User-business assignment viewsets for detailed operations (retrieve, update, delete)
assignment_detail = UserBusinessAssignmentViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }
)

# URL routing for the business_meta app
urlpatterns = [
    path(
        '',
        BusinessViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='business-list',
    ),
    path(
        'templates/',
        BusinessViewSet.as_view({'get': 'templates'}),
        name='business-templates',
    ),
    path(
        'from_template/',
        BusinessViewSet.as_view({'post': 'from_template'}),
        name='business-from-template',
    ),
    path(
        '<int:business_pk>/job-positions/',
        job_position_list,
        name='business-job-position-list',
    ),
    path(
        '<int:business_pk>/job-positions/<int:pk>/',
        job_position_detail,
        name='business-job-position-detail',
    ),
    path(
        '<int:business_pk>/assignments/',
        assignment_list,
        name='business-assignment-list',
    ),
    path(
        '<int:business_pk>/assignments/<int:pk>/',
        assignment_detail,
        name='business-assignment-detail',
    ),
    path(
        '<int:pk>/',
        BusinessViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='business-detail',
    ),
    path(
        '<int:business_pk>/tables/',
        table_list,
        name='tabledefinition-list',
    ),
    path(
        '<int:business_pk>/tables/<int:pk>/',
        table_detail,
        name='tabledefinition-detail',
    ),
    path(
        '<int:business_pk>/tables/by_slug/<str:table_slug>/',
        TableDefinitionViewSet.as_view({'get': 'by_slug'}),
        name='tabledefinition-by-slug',
    ),
    path(
        '<int:business_pk>/tables/<int:table_pk>/fields/',
        field_list,
        name='fielddefinition-list',
    ),
    path(
        '<int:business_pk>/tables/<int:table_pk>/fields/<int:pk>/',
        field_detail,
        name='fielddefinition-detail',
    ),
    # Data API: rows (table identified by slug)
    path(
        '<int:business_pk>/tables/<str:table_slug>/rows/',
        DynamicRowsView.as_view(),
        name='dynamic-rows-list',
    ),
    path(
        '<int:business_pk>/tables/<str:table_slug>/rows/export/',
        DynamicRowsExportView.as_view(),
        name='dynamic-rows-export',
    ),
    path(
        '<int:business_pk>/tables/<str:table_slug>/rows/import/',
        DynamicRowsImportView.as_view(),
        name='dynamic-rows-import',
    ),
    path(
        '<int:business_pk>/tables/<str:table_slug>/rows/<str:row_id>/',
        DynamicRowDetailView.as_view(),
        name='dynamic-row-detail',
    ),
    # Inventory (business-scoped)
    path('', include('inventory.business_urls')),
]
