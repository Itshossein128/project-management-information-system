from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

# Default router instance for viewsets.
router = DefaultRouter()
router.register(r'items', ItemViewSet)

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('', include(router.urls)),
]
