from django.urls import path

from project_templates.views import (
    LaborCatalogTitleAPIView,
    LaborCatalogTitleDetailAPIView,
    LaborCatalogViewSet,
    ProjectTemplateViewSet,
)

template_list = ProjectTemplateViewSet.as_view({'get': 'list', 'post': 'create'})
template_detail = ProjectTemplateViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
template_apply = ProjectTemplateViewSet.as_view({'post': 'apply'})

labor_catalog_list_create = LaborCatalogViewSet.as_view({'get': 'list', 'post': 'create'})
labor_catalog_detail = LaborCatalogViewSet.as_view({'get': 'retrieve', 'put': 'partial_update', 'patch': 'partial_update'})

urlpatterns = [
    path('', template_list, name='project-template-list'),
    path('<uuid:pk>/', template_detail, name='project-template-detail'),
    path('<uuid:pk>/apply/<uuid:project_id>/', template_apply, name='project-template-apply'),
    # Feature 033 (contract reporting-configuration-catalog-api.md §1): draft
    # labor-title catalogs per project template.
    path('<uuid:pk>/labor-catalogs/', labor_catalog_list_create, name='project-template-labor-catalogs'),
    path(
        '<uuid:pk>/labor-catalogs/<uuid:catalog_pk>/',
        labor_catalog_detail,
        name='project-template-labor-catalog-detail',
    ),
    path(
        '<uuid:pk>/labor-catalogs/<uuid:catalog_pk>/titles/',
        LaborCatalogTitleAPIView.as_view(),
        name='project-template-labor-catalog-titles',
    ),
    path(
        '<uuid:pk>/labor-catalogs/<uuid:catalog_pk>/titles/<uuid:title_pk>/',
        LaborCatalogTitleDetailAPIView.as_view(),
        name='project-template-labor-catalog-title-detail',
    ),
]

from project_templates.project_urls import urlpatterns as project_reporting_configuration_urls

project_template_urls = urlpatterns
