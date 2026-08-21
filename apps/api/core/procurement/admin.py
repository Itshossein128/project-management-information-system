from django.contrib import admin
from .models import (
    Block,
    RequisitionHeader,
    RequisitionItem,
    ApprovalLog,
    InventoryAllocation,
    InternalTransfer,
)


class RequisitionItemInline(admin.TabularInline):
    model = RequisitionItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class ApprovalLogInline(admin.TabularInline):
    model = ApprovalLog
    extra = 0
    readonly_fields = ('performed_at',)
    can_delete = False


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('block_code', 'block_name', 'project', 'budget', 'is_active')
    list_filter = ('project', 'is_active')
    search_fields = ('block_code', 'block_name')


@admin.register(RequisitionHeader)
class RequisitionHeaderAdmin(admin.ModelAdmin):
    list_display = ('requisition_number', 'project', 'block', 'status', 'requisition_type', 'priority', 'request_date')
    list_filter = ('status', 'requisition_type', 'priority', 'project')
    search_fields = ('requisition_number', 'notes')
    inlines = [RequisitionItemInline, ApprovalLogInline]
    readonly_fields = ('requisition_number', 'created_at', 'updated_at')


@admin.register(RequisitionItem)
class RequisitionItemAdmin(admin.ModelAdmin):
    list_display = ('header', 'line_number', 'material', 'requested_qty', 'approved_qty', 'status')
    list_filter = ('status',)


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('requisition', 'step_from', 'step_to', 'action', 'performed_by', 'performed_at')
    readonly_fields = ('performed_at',)
    can_delete = False


@admin.register(InventoryAllocation)
class InventoryAllocationAdmin(admin.ModelAdmin):
    list_display = ('mr_tag', 'block', 'material', 'allocated_qty', 'received_qty', 'issued_qty')
    list_filter = ('block',)
    search_fields = ('mr_tag',)


@admin.register(InternalTransfer)
class InternalTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_block', 'target_block', 'material', 'quantity', 'status')
    list_filter = ('status',)
