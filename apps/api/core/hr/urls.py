from django.urls import path

from hr.views import LeaveRequestViewSet, OvertimeRequestViewSet

# Viewset action routing for overtime_list.
overtime_list = OvertimeRequestViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for overtime_detail.
overtime_detail = OvertimeRequestViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
# Viewset action routing for overtime_submit.
overtime_submit = OvertimeRequestViewSet.as_view({'post': 'submit'})
# Viewset action routing for overtime_supervisor.
overtime_supervisor = OvertimeRequestViewSet.as_view({'post': 'supervisor_approve'})
# Viewset action routing for overtime_manager.
overtime_manager = OvertimeRequestViewSet.as_view({'post': 'manager_approve'})

# Viewset action routing for leave_list.
leave_list = LeaveRequestViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for leave_detail.
leave_detail = LeaveRequestViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
# Viewset action routing for leave_submit.
leave_submit = LeaveRequestViewSet.as_view({'post': 'submit'})
# Viewset action routing for leave_supervisor.
leave_supervisor = LeaveRequestViewSet.as_view({'post': 'supervisor_approve'})
# Viewset action routing for leave_manager.
leave_manager = LeaveRequestViewSet.as_view({'post': 'manager_approve'})
# Viewset action routing for leave_security.
leave_security = LeaveRequestViewSet.as_view({'post': 'security_approve'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('overtime-requests/', overtime_list, name='overtime-list'),
    path('overtime-requests/<uuid:pk>/', overtime_detail, name='overtime-detail'),
    path('overtime-requests/<uuid:pk>/submit/', overtime_submit, name='overtime-submit'),
    path('overtime-requests/<uuid:pk>/supervisor-approve/', overtime_supervisor, name='overtime-supervisor'),
    path('overtime-requests/<uuid:pk>/manager-approve/', overtime_manager, name='overtime-manager'),
    path('leave-requests/', leave_list, name='leave-list'),
    path('leave-requests/<uuid:pk>/', leave_detail, name='leave-detail'),
    path('leave-requests/<uuid:pk>/submit/', leave_submit, name='leave-submit'),
    path('leave-requests/<uuid:pk>/supervisor-approve/', leave_supervisor, name='leave-supervisor'),
    path('leave-requests/<uuid:pk>/manager-approve/', leave_manager, name='leave-manager'),
    path('leave-requests/<uuid:pk>/security-approve/', leave_security, name='leave-security'),
]
