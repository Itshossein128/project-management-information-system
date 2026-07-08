from rest_framework.routers import DefaultRouter
from .views import RelationDefinitionViewSet

# Router for relation definitions, handling standard viewset actions
router = DefaultRouter()
router.register(r'', RelationDefinitionViewSet, basename='relationdefinition')

# Expose router URLs for relations
urlpatterns = router.urls
