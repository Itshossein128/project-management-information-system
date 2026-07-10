from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

# Default Router for automatically generating URL patterns for ItemViewSet endpoints.
router = DefaultRouter()
router.register(r'items', ItemViewSet)

# URL routing definitions for the inventory app.
# Include automatically generated routes from the router.
urlpatterns = [
    path('', include(router.urls)),
]
