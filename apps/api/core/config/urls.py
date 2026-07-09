"""
URL configuration for inventory-backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# The primary list of URL routes for the backend application.
# Routes are delegated to specific app modules (e.g., authentication, business_meta, inventory)
# and include built-in Django admin as well as API schema documentation (Swagger/Redoc).
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/businesses/', include('business_meta.urls')),
    path('api/relations/', include('business_meta.relations_urls')),
    path('api/', include('inventory.urls')),
    # Swagger/OpenAPI documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]