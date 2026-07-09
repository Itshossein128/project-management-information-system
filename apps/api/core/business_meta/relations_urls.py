from rest_framework.routers import DefaultRouter
from .views import RelationDefinitionViewSet

# DefaultRouter instance to automatically generate URL routes for viewsets.
router = DefaultRouter()
# Register the RelationDefinitionViewSet for handling relation definitions.
# Maps to the root URL of this module.
router.register(r'', RelationDefinitionViewSet, basename='relationdefinition')

# Expose the automatically generated URL patterns from the router.
urlpatterns = router.urls
