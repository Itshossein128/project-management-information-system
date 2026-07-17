from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.models import AlertLog, AlertRule
from alerts.serializers import AlertLogSerializer, AlertRuleSerializer
from common.cache_helpers import cache_key, get_cached_or_compute, params_fingerprint
from permissions.project import HasProjectPermission, IsProjectMember


class AlertRuleListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_project'

    @extend_schema(summary='List alert rules', tags=['Alerts'])
    def get(self, request, project_pk=None):
        rules = AlertRule.objects.filter(is_deleted=False).filter(
            models.Q(project_id=project_pk) | models.Q(project__isnull=True)
        )
        return Response({'results': AlertRuleSerializer(rules, many=True).data})

    @extend_schema(summary='Create project alert rule', tags=['Alerts'])
    def post(self, request, project_pk=None):
        ser = AlertRuleSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        rule = AlertRule.objects.create(project_id=project_pk, **ser.validated_data)
        return Response(AlertRuleSerializer(rule).data, status=status.HTTP_201_CREATED)


class AlertRuleDetailView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_project'

    def patch(self, request, project_pk=None, rid=None):
        rule = AlertRule.objects.filter(id=rid, is_deleted=False).filter(
            models.Q(project_id=project_pk) | models.Q(project__isnull=True)
        ).first()
        if not rule:
            return Response({'detail': 'Not found'}, status=404)
        ser = AlertRuleSerializer(rule, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for k, v in ser.validated_data.items():
            setattr(rule, k, v)
        rule.save()
        return Response(AlertRuleSerializer(rule).data)

    def delete(self, request, project_pk=None, rid=None):
        rule = AlertRule.objects.filter(id=rid, project_id=project_pk, is_deleted=False).first()
        if not rule:
            return Response({'detail': 'Cannot delete system rules'}, status=400)
        rule.is_deleted = True
        rule.deleted_at = timezone.now()
        rule.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlertLogListView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_project'

    @extend_schema(summary='List alert log entries', tags=['Alerts'])
    def get(self, request, project_pk=None):
        qs = AlertLog.objects.filter(project_id=project_pk).select_related('rule').order_by('-fired_at')
        if request.query_params.get('acknowledged') == 'false':
            qs = qs.filter(acknowledged_at__isnull=True)
        alert_type = request.query_params.get('alert_type')
        if alert_type:
            qs = qs.filter(rule__alert_type=alert_type)
        date_from = request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(fired_at__date__gte=date_from)
        date_to = request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(fired_at__date__lte=date_to)
        return Response({'results': AlertLogSerializer(qs[:200], many=True).data})


class AlertAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_project'

    def post(self, request, project_pk=None, lid=None):
        log = AlertLog.objects.filter(id=lid, project_id=project_pk).first()
        if not log:
            return Response({'detail': 'Not found'}, status=404)
        log.acknowledged_at = timezone.now()
        log.acknowledged_by = request.user
        log.save(update_fields=['acknowledged_at', 'acknowledged_by'])
        return Response(AlertLogSerializer(log).data)


class ActiveAlertsView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_project'

    @extend_schema(summary='Unacknowledged alert counts by type', tags=['Alerts'])
    def get(self, request, project_pk=None):
        fp = params_fingerprint({})
        key = cache_key('alerts_active', project_pk, fp)

        def compute():
            qs = AlertLog.objects.filter(project_id=project_pk, acknowledged_at__isnull=True)
            counts = {}
            for row in qs.values('rule__alert_type').annotate(c=models.Count('id')):
                t = row['rule__alert_type'] or 'unknown'
                counts[t] = row['c']
            return {'counts': counts, 'total': sum(counts.values())}

        return Response(get_cached_or_compute(key, 300, compute))
