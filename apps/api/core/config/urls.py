"""
URL configuration for inventory-backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Main URL patterns for the backend API
urlpatterns = [
    # Django admin panel route
    path('admin/', admin.site.urls),

    # Authentication routes (login, register, password reset, etc.)
    path('api/auth/', include('authentication.urls')),

    # Business metadata routes (businesses, tables, fields, etc.)
    path('api/businesses/', include('business_meta.urls')),

    # Business relations routes
    path('api/relations/', include('business_meta.relations_urls')),

    # Inventory routes (items, etc.)
    path('api/', include('inventory.urls')),

    # Swagger/OpenAPI schema generation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI documentation endpoint
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    # ReDoc UI documentation endpoint
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]