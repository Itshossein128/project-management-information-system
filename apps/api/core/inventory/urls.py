from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

# Global router for general inventory entities
router = DefaultRouter()
router.register(r'items', ItemViewSet)

# Global inventory URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
