from rest_framework.routers import DefaultRouter
from .views import RelationDefinitionViewSet

# Default Router for automatically generating URL patterns for RelationDefinitionViewSet.
router = DefaultRouter()
router.register(r'', RelationDefinitionViewSet, basename='relationdefinition')

# URL routing definitions for relations in the business_meta app.
# Generated automatically by the router for RelationDefinition endpoints.
urlpatterns = router.urls
