from django.urls import path

from hr.capacity_views import (
    ApprovedLaborRateViewSet,
    CapacityExceptionViewSet,
    CapacityPreviewView,
    LaborCostEstimateView,
    PersonDossierView,
    ResourceAllocationViewSet,
)
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

allocation_list = ResourceAllocationViewSet.as_view({'get': 'list', 'post': 'create'})
allocation_detail = ResourceAllocationViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)
capacity_exception_list = CapacityExceptionViewSet.as_view({'get': 'list', 'post': 'create'})
capacity_exception_submit = CapacityExceptionViewSet.as_view({'post': 'submit'})
capacity_exception_approve = CapacityExceptionViewSet.as_view({'post': 'approve'})
capacity_exception_reject = CapacityExceptionViewSet.as_view({'post': 'reject'})
approved_rate_list = ApprovedLaborRateViewSet.as_view({'get': 'list', 'post': 'create'})
approved_rate_detail = ApprovedLaborRateViewSet.as_view({'delete': 'destroy'})

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
    path('people/<uuid:user_id>/dossier/', PersonDossierView.as_view(), name='person-dossier'),
    path('resource-allocations/capacity-preview/', CapacityPreviewView.as_view(), name='capacity-preview'),
    path('resource-allocations/', allocation_list, name='resource-allocation-list'),
    path('resource-allocations/<uuid:pk>/', allocation_detail, name='resource-allocation-detail'),
    path('capacity-exceptions/', capacity_exception_list, name='capacity-exception-list'),
    path('capacity-exceptions/<uuid:pk>/submit/', capacity_exception_submit, name='capacity-exception-submit'),
    path('capacity-exceptions/<uuid:pk>/approve/', capacity_exception_approve, name='capacity-exception-approve'),
    path('capacity-exceptions/<uuid:pk>/reject/', capacity_exception_reject, name='capacity-exception-reject'),
    path('approved-labor-rates/', approved_rate_list, name='approved-labor-rate-list'),
    path('approved-labor-rates/<uuid:pk>/', approved_rate_detail, name='approved-labor-rate-detail'),
    path('labor-cost-estimate/', LaborCostEstimateView.as_view(), name='labor-cost-estimate'),
]
