from django.contrib import admin

from master_data.models import ProjectMember, ProjectPosition, Unit, Role
from projects.models import Project
from business_meta.models import TableDefinition, FieldDefinition, DynamicTableRow


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'project_name', 'status', 'created_at')


@admin.register(ProjectPosition)
class ProjectPositionAdmin(admin.ModelAdmin):
    list_display = ('project', 'slug', 'position_name', 'ordering')


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'position', 'status')


@admin.register(TableDefinition)
class TableDefinitionAdmin(admin.ModelAdmin):
    list_display = ('project', 'slug', 'name')


admin.site.register(Unit)
admin.site.register(Role)
admin.site.register(FieldDefinition)
admin.site.register(DynamicTableRow)
