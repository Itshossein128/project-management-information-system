from django.urls import path

from hr.views import LeaveRequestViewSet, OvertimeRequestViewSet

overtime_list = OvertimeRequestViewSet.as_view({'get': 'list', 'post': 'create'})
overtime_detail = OvertimeRequestViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
overtime_submit = OvertimeRequestViewSet.as_view({'post': 'submit'})
overtime_supervisor = OvertimeRequestViewSet.as_view({'post': 'supervisor_approve'})
overtime_manager = OvertimeRequestViewSet.as_view({'post': 'manager_approve'})

leave_list = LeaveRequestViewSet.as_view({'get': 'list', 'post': 'create'})
leave_detail = LeaveRequestViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'})
leave_submit = LeaveRequestViewSet.as_view({'post': 'submit'})
leave_supervisor = LeaveRequestViewSet.as_view({'post': 'supervisor_approve'})
leave_manager = LeaveRequestViewSet.as_view({'post': 'manager_approve'})
leave_security = LeaveRequestViewSet.as_view({'post': 'security_approve'})

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
