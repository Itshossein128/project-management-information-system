from rest_framework.routers import DefaultRouter
from .views import RelationDefinitionViewSet

# Default router instance for viewsets.
router = DefaultRouter()
router.register(r'', RelationDefinitionViewSet, basename='relationdefinition')

# List of URL patterns for urlpatterns routing.
urlpatterns = router.urls
