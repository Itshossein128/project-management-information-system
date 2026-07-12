from django.urls import path

from projects.role_views import RoleViewSet

# Viewset action routing for role_list.
role_list = RoleViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for role_detail.
role_detail = RoleViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
# Definition of role_permissions.
role_permissions = RoleViewSet.as_view({'put': 'permissions', 'patch': 'permissions'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('', role_list, name='role-list'),
    path('<uuid:pk>/', role_detail, name='role-detail'),
    path('<uuid:pk>/permissions/', role_permissions, name='role-permissions'),
]
