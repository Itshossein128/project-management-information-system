from django.urls import path

from .views import NotificationViewSet

# Viewset action routing for notification_list.
notification_list = NotificationViewSet.as_view({'get': 'list'})
# Viewset action routing for notification_detail.
notification_detail = NotificationViewSet.as_view({'get': 'retrieve'})
# Definition of unread_count.
unread_count = NotificationViewSet.as_view({'get': 'unread_count'})
# Definition of mark_read.
mark_read = NotificationViewSet.as_view({'post': 'mark_read'})
# Definition of mark_all_read.
mark_all_read = NotificationViewSet.as_view({'post': 'mark_all_read'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('', notification_list, name='notification-list'),
    path('unread-count/', unread_count, name='notification-unread-count'),
    path('mark-all-read/', mark_all_read, name='notification-mark-all-read'),
    path('<uuid:pk>/', notification_detail, name='notification-detail'),
    path('<uuid:pk>/mark-read/', mark_read, name='notification-mark-read'),
]
