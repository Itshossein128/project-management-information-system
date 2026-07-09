from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

# DefaultRouter instance to automatically generate URL routes for viewsets.
router = DefaultRouter()
# Register the ItemViewSet for handling general inventory item operations.
# Maps to the /items/ URL prefix.
router.register(r'items', ItemViewSet)

# List of URL routes for general inventory endpoints.
# Includes the automatically generated routes from the router.
urlpatterns = [
    path('', include(router.urls)),
]
