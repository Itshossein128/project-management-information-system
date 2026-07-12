from django.urls import path

from project_templates.views import ProjectTemplateViewSet

# Viewset action routing for template_list.
template_list = ProjectTemplateViewSet.as_view({'get': 'list', 'post': 'create'})
# Viewset action routing for template_detail.
template_detail = ProjectTemplateViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
# Definition of template_apply.
template_apply = ProjectTemplateViewSet.as_view({'post': 'apply'})

# List of URL patterns for urlpatterns routing.
urlpatterns = [
    path('', template_list, name='project-template-list'),
    path('<uuid:pk>/', template_detail, name='project-template-detail'),
    path('<uuid:pk>/apply/<uuid:project_id>/', template_apply, name='project-template-apply'),
]

# Definition of project_template_urls.
project_template_urls = urlpatterns
