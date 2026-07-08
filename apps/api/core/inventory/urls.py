from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

# Router for inventory items, handling standard viewset actions
router = DefaultRouter()
router.register(r'items', ItemViewSet)

# URL routing for the inventory app (global endpoints)
urlpatterns = [
    path('', include(router.urls)),
]
