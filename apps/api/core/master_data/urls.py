from django.urls import path

from master_data.ref_views import (
    ManagedContractTypeListCreateView,
    OrganizationUnitDetailView,
    OrganizationUnitListCreateView,
    UnitListView,
)

urlpatterns = [
    path(
        'organization-units/',
        OrganizationUnitListCreateView.as_view(),
        name='organization-unit-list',
    ),
    path(
        'organization-units/<uuid:pk>/',
        OrganizationUnitDetailView.as_view(),
        name='organization-unit-detail',
    ),
    path(
        'contract-types/',
        ManagedContractTypeListCreateView.as_view(),
        name='managed-contract-type-list',
    ),
    path(
        'measurement-units/',
        UnitListView.as_view(),
        name='measurement-unit-list',
    ),
]
