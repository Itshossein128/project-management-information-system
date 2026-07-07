from django.urls import path

from projects.role_views import RoleViewSet

role_list = RoleViewSet.as_view({'get': 'list', 'post': 'create'})
role_detail = RoleViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
role_permissions = RoleViewSet.as_view({'put': 'permissions', 'patch': 'permissions'})

urlpatterns = [
    path('', role_list, name='role-list'),
    path('<uuid:pk>/', role_detail, name='role-detail'),
    path('<uuid:pk>/permissions/', role_permissions, name='role-permissions'),
]
