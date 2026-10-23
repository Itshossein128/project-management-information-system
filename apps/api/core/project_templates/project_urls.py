from django.urls import path

from project_templates.views import ProjectReportingConfigurationViewSet

reporting_config_list = ProjectReportingConfigurationViewSet.as_view({'get': 'list', 'post': 'create'})
reporting_config_preview = ProjectReportingConfigurationViewSet.as_view({'post': 'preview'})

urlpatterns = [
    path('preview/', reporting_config_preview, name='project-reporting-configuration-preview'),
    path('', reporting_config_list, name='project-reporting-configuration-list'),
]
