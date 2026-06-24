from rest_framework.routers import DefaultRouter
from .views import RelationDefinitionViewSet

router = DefaultRouter()
router.register(r'', RelationDefinitionViewSet, basename='relationdefinition')

urlpatterns = router.urls
