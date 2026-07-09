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

# View bindings for listing and creating table definitions nested under a business.
# Maps GET to list and POST to create.
# Nested under: /api/businesses/<business_pk>/tables/
table_list = TableDefinitionViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# View bindings for retrieving, updating, and deleting a specific table definition.
# Maps GET to retrieve, PUT to update, PATCH to partial_update, and DELETE to destroy.
# Nested under: /api/businesses/<business_pk>/tables/<pk>/
table_detail = TableDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# View bindings for listing and creating field definitions nested under a specific table.
# Maps GET to list and POST to create.
# Nested under: /api/businesses/<business_pk>/tables/<table_pk>/fields/
field_list = FieldDefinitionViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# View bindings for retrieving, updating, and deleting a specific field definition.
# Maps GET to retrieve, PUT to update, PATCH to partial_update, and DELETE to destroy.
# Nested under: /api/businesses/<business_pk>/tables/<table_pk>/fields/<pk>/
field_detail = FieldDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# View bindings for listing and creating job positions nested under a business.
# Maps GET to list and POST to create.
job_position_list = BusinessJobPositionViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# View bindings for retrieving, updating, and deleting a specific job position.
job_position_detail = BusinessJobPositionViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }
)

# View bindings for listing and creating user-business assignments nested under a business.
# Maps GET to list and POST to create.
assignment_list = UserBusinessAssignmentViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
# View bindings for retrieving, updating, and deleting a specific user-business assignment.
assignment_detail = UserBusinessAssignmentViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }
)

# List of URL routes for the business meta application.
# Includes endpoints for managing businesses, templates, job positions, user assignments,
# table definitions, field definitions, and dynamic data rows.
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
