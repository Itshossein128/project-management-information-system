from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sub_reports.models import UnitReportMigrationQuarantine
from sub_reports.quarantine_serializers import UnitReportMigrationQuarantineSerializer


class UnitReportMigrationQuarantineViewSet(viewsets.ReadOnlyModelViewSet):
    """Quarantine resolution surface for authorized migration operators (data-model §10).

    Quarantined rows remain readable, are never current, and never contribute.
    Only admin operators may list, inspect, and record resolutions.
    """

    queryset = UnitReportMigrationQuarantine.objects.select_related('trace', 'resolved_by').all()
    serializer_class = UnitReportMigrationQuarantineSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        quarantine = self.get_object()
        notes = request.data.get('resolution_notes', '').strip()
        quarantine.resolved_by = request.user
        quarantine.resolved_at = timezone.now()
        quarantine.resolution_notes = notes
        quarantine.save(update_fields=['resolved_by', 'resolved_at', 'resolution_notes'])
        serializer = self.get_serializer(quarantine)
        return Response(serializer.data, status=status.HTTP_200_OK)
