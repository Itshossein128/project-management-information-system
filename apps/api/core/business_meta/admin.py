from django.contrib import admin
from .models import (
    Business,
    UserBusinessAssignment,
    BusinessJobPosition,
    TableDefinition,
    FieldDefinition,
    RelationDefinition,
)


@admin.register(BusinessJobPosition)
# Class representing BusinessJobPositionAdmin
class BusinessJobPositionAdmin(admin.ModelAdmin):
    list_display = ('business', 'slug', 'label', 'ordering', 'updated_at')
    list_filter = ('business',)
    search_fields = ('slug', 'label', 'business__name')
    raw_id_fields = ('business',)


@admin.register(UserBusinessAssignment)
# Class representing UserBusinessAssignmentAdmin
class UserBusinessAssignmentAdmin(admin.ModelAdmin):
    list_display = ('business', 'user', 'job_position', 'status', 'wage', 'created_at')
    list_filter = ('status', 'business', 'job_position')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name')
    raw_id_fields = ('business', 'user', 'job_position')


@admin.register(Business)
# Class representing BusinessAdmin
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {}


@admin.register(TableDefinition)
# Class representing TableDefinitionAdmin
class TableDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'business', 'ordering', 'created_at')
    list_filter = ('business',)
    search_fields = ('name', 'slug')
    raw_id_fields = ('business',)


@admin.register(FieldDefinition)
# Class representing FieldDefinitionAdmin
class FieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'table', 'field_type', 'required', 'ordering')
    list_filter = ('field_type', 'table__business')
    search_fields = ('name', 'slug')
    raw_id_fields = ('table', 'target_table')


@admin.register(RelationDefinition)
# Class representing RelationDefinitionAdmin
class RelationDefinitionAdmin(admin.ModelAdmin):
    list_display = ('from_table', 'from_field', 'to_table', 'to_field', 'kind')
    list_filter = ('kind',)
    raw_id_fields = ('from_table', 'to_table', 'from_field', 'to_field')
