from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from projects.member_views import RoleListView, UserLookupView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/v1/', include('storage.urls')),
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/roles/', RoleListView.as_view(), name='role-list'),
    path('api/v1/users/lookup/', UserLookupView.as_view(), name='user-lookup'),
    path('api/relations/', include('business_meta.relations_urls')),
    path('api/', include('inventory.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
