"""User-scoped in-app notification API (Sprint 4, Section 5)."""
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import DefaultPageNumberPagination

from .models import Notification
from .serializers import NotificationSerializer


@extend_schema_view(
    list=extend_schema(
        summary='List current user notifications',
        description='Newest first. Filter with `is_read=true|false` and `project`.',
        parameters=[
            OpenApiParameter('is_read', bool, description='Filter by read state'),
            OpenApiParameter('project', str, description='Filter by project id'),
        ],
        tags=['Notifications'],
    ),
    retrieve=extend_schema(summary='Get a notification', tags=['Notifications']),
)
class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination

    # Filters notifications for the authenticated user and handles optional query parameters like `is_read` and `project`
    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).select_related('project')
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() in ('1', 'true', 'yes'))
        project = self.request.query_params.get('project')
        if project:
            qs = qs.filter(project_id=project)
        return qs

    @extend_schema(
        summary='Unread notification count',
        responses={200: OpenApiResponse(description='{"unread": <int>}')},
        tags=['Notifications'],
    )
    @action(detail=False, methods=['get'], url_path='unread-count')
    # Returns the number of unread notifications for the user
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread': count})

    @extend_schema(summary='Mark one notification as read', tags=['Notifications'])
    @action(detail=True, methods=['post'], url_path='mark-read')
    # Marks a specific notification as read and updates the `read_at` timestamp
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at', 'updated_at'])
        return Response(self.get_serializer(notification).data)

    @extend_schema(
        summary='Mark all notifications as read',
        responses={200: OpenApiResponse(description='{"updated": <int>}')},
        tags=['Notifications'],
    )
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    # Batch updates all unread notifications for the current user
    def mark_all_read(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
        return Response({'updated': updated}, status=status.HTTP_200_OK)
