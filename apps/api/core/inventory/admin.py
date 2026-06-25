from django.contrib import admin
from .models import Category, Item, SpaceMaterialRequest, DepartmentActivityRecord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'category']
    list_filter = ['category']
    search_fields = ['name']
    list_editable = ['quantity']


@admin.register(SpaceMaterialRequest)
class SpaceMaterialRequestAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'block_number',
        'floor_number',
        'unit_number',
        'space_name',
        'material_code',
        'approved_quantity_technical_office',
        'deliverable_quantity_inventory_unit',
        'unit',
        'created_at',
    ]
    list_filter = ['project', 'unit']
    search_fields = ['material_code', 'space_name', 'unit_number', 'item_description']


@admin.register(DepartmentActivityRecord)
class DepartmentActivityRecordAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'department',
        'date',
        'location',
        'activity_description',
        'contractor',
        'unit',
        'created_at',
    ]
    list_filter = ['project', 'department', 'unit']
    search_fields = ['location', 'activity_description', 'contractor', 'unit', 'description']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
