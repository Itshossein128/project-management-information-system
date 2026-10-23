from rest_framework.routers import SimpleRouter

from sub_reports.quarantine_views import UnitReportMigrationQuarantineViewSet

router = SimpleRouter()
router.register('', UnitReportMigrationQuarantineViewSet, basename='unit-report-quarantine')

urlpatterns = router.urls
