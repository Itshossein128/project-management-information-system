"""Procurement URL configuration.

All routes are nested under /api/v1/projects/{project_pk}/ in the main urls.py.

Endpoints:
  Blocks:
    GET/POST   /projects/{pid}/blocks/
    GET/PATCH/DELETE /projects/{pid}/blocks/{id}/

  Requisitions:
    GET/POST   /projects/{pid}/requisitions/
    GET/PATCH/DELETE /projects/{pid}/requisitions/{id}/
    POST       /projects/{pid}/requisitions/{id}/submit/
    POST       /projects/{pid}/requisitions/{id}/approve/
    POST       /projects/{pid}/requisitions/{id}/reject/
    POST       /projects/{pid}/requisitions/{id}/return/
    GET        /projects/{pid}/requisitions/{id}/approval-logs/
    POST       /projects/{pid}/requisitions/{id}/assign-items/
    POST       /projects/{pid}/requisitions/{id}/partial-approve/

  Requisition Items:
    PATCH      /projects/{pid}/requisition-items/{id}/hold/

  Inventory (block-level):
    POST       /projects/{pid}/blocks/{bid}/grn/
    POST       /projects/{pid}/blocks/{bid}/issue/
    GET        /projects/{pid}/blocks/{bid}/stock/

  Transfers:
    GET/POST   /projects/{pid}/transfers/
    POST       /projects/{pid}/transfers/{id}/approve/
    POST       /projects/{pid}/transfers/{id}/reject/

  Reports:
    GET        /projects/{pid}/reports/liquidity/
    GET        /projects/{pid}/reports/material-deviation/
    GET        /projects/{pid}/reports/audit-trail/
    GET        /projects/{pid}/reports/procurement-status/
"""
from django.urls import path

from procurement.views import (
    ApprovalLogListView,
    AssignItemsView,
    BlockStockView,
    BlockViewSet,
    GRNView,
    InternalTransferViewSet,
    IssueStockView,
    LiquidityDashboardView,
    MaterialDeviationReportView,
    AuditTrailReportView,
    PartialApproveView,
    ProcurementStatusReportView,
    RequisitionApproveView,
    RequisitionHeaderViewSet,
    RequisitionItemHoldView,
    RequisitionRejectView,
    RequisitionReturnView,
    RequisitionSubmitView,
    TransferApproveView,
    TransferRejectView,
)

# Block CRUD
block_list = BlockViewSet.as_view({'get': 'list', 'post': 'create'})
block_detail = BlockViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

# Requisition CRUD
req_list = RequisitionHeaderViewSet.as_view({'get': 'list', 'post': 'create'})
req_detail = RequisitionHeaderViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})

# Transfer CRUD
transfer_list = InternalTransferViewSet.as_view({'get': 'list', 'post': 'create'})
transfer_detail = InternalTransferViewSet.as_view({'get': 'retrieve'})

# These are registered under projects/<project_pk>/ in projects/urls.py (or config/urls.py)
urlpatterns = [
    # ---- Blocks ----
    path('blocks/', block_list, name='procurement-block-list'),
    path('blocks/<uuid:pk>/', block_detail, name='procurement-block-detail'),

    # ---- Block-level inventory ----
    path('blocks/<uuid:block_pk>/grn/', GRNView.as_view(), name='procurement-block-grn'),
    path('blocks/<uuid:block_pk>/issue/', IssueStockView.as_view(), name='procurement-block-issue'),
    path('blocks/<uuid:block_pk>/stock/', BlockStockView.as_view(), name='procurement-block-stock'),

    # ---- Requisitions ----
    path('requisitions/', req_list, name='procurement-req-list'),
    path('requisitions/<uuid:pk>/', req_detail, name='procurement-req-detail'),
    path('requisitions/<uuid:pk>/submit/', RequisitionSubmitView.as_view(), name='procurement-req-submit'),
    path('requisitions/<uuid:pk>/approve/', RequisitionApproveView.as_view(), name='procurement-req-approve'),
    path('requisitions/<uuid:pk>/reject/', RequisitionRejectView.as_view(), name='procurement-req-reject'),
    path('requisitions/<uuid:pk>/return/', RequisitionReturnView.as_view(), name='procurement-req-return'),
    path('requisitions/<uuid:pk>/approval-logs/', ApprovalLogListView.as_view(), name='procurement-req-approval-logs'),
    path('requisitions/<uuid:pk>/assign-items/', AssignItemsView.as_view(), name='procurement-req-assign-items'),
    path('requisitions/<uuid:pk>/partial-approve/', PartialApproveView.as_view(), name='procurement-req-partial-approve'),

    # ---- Requisition items ----
    path('requisition-items/<uuid:pk>/hold/', RequisitionItemHoldView.as_view(), name='procurement-item-hold'),

    # ---- Inter-block transfers ----
    path('transfers/', transfer_list, name='procurement-transfer-list'),
    path('transfers/<uuid:pk>/', transfer_detail, name='procurement-transfer-detail'),
    path('transfers/<uuid:pk>/approve/', TransferApproveView.as_view(), name='procurement-transfer-approve'),
    path('transfers/<uuid:pk>/reject/', TransferRejectView.as_view(), name='procurement-transfer-reject'),

    # ---- Reports ----
    path('reports/liquidity/', LiquidityDashboardView.as_view(), name='procurement-report-liquidity'),
    path('reports/material-deviation/', MaterialDeviationReportView.as_view(), name='procurement-report-deviation'),
    path('reports/audit-trail/', AuditTrailReportView.as_view(), name='procurement-report-audit'),
    path('reports/procurement-status/', ProcurementStatusReportView.as_view(), name='procurement-report-status'),
]
