from django.urls import path

from project_templates.views import ProjectTemplateViewSet

template_list = ProjectTemplateViewSet.as_view({'get': 'list', 'post': 'create'})
template_detail = ProjectTemplateViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
template_apply = ProjectTemplateViewSet.as_view({'post': 'apply'})

urlpatterns = [
    path('', template_list, name='project-template-list'),
    path('<uuid:pk>/', template_detail, name='project-template-detail'),
    path('<uuid:pk>/apply/<uuid:project_id>/', template_apply, name='project-template-apply'),
]

project_template_urls = urlpatterns
