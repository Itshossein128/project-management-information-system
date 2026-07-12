from django.urls import path

from .views import NotificationViewSet

notification_list = NotificationViewSet.as_view({'get': 'list'})
notification_detail = NotificationViewSet.as_view({'get': 'retrieve'})
unread_count = NotificationViewSet.as_view({'get': 'unread_count'})
mark_read = NotificationViewSet.as_view({'post': 'mark_read'})
mark_all_read = NotificationViewSet.as_view({'post': 'mark_all_read'})

urlpatterns = [
    path('', notification_list, name='notification-list'),
    path('unread-count/', unread_count, name='notification-unread-count'),
    path('mark-all-read/', mark_all_read, name='notification-mark-all-read'),
    path('<uuid:pk>/', notification_detail, name='notification-detail'),
    path('<uuid:pk>/mark-read/', mark_read, name='notification-mark-read'),
]
