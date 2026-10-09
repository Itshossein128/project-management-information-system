from django.urls import path, include

from projects.views import (
    ProjectChangeRequestActionView,
    ProjectChangeRequestDetailView,
    ProjectChangeRequestListCreateView,
    ProjectKickoffCharterView,
    ProjectViewSet,
)
from projects.kpi_views import ProjectHealthView, ProjectKpiDrillView, ProjectKpisView
from projects.dashboard_views import ProjectDashboardPackView
from projects.report_views import (
    ProjectReportCatalogView,
    ProjectReportExportDetailView,
    ProjectReportExportDownloadView,
    ProjectReportExportView,
    ProjectReportRunView,
)
from projects.member_views import ProjectMemberViewSet, RoleListView, UserLookupView
from projects.core_principle_views import (
    FiscalPeriodLockDeactivateView,
    FiscalPeriodLockListCreateView,
    ProjectCapabilityDetailView,
    ProjectCapabilityListView,
)
from projects.stakeholder_views import (
    CommunicationPlanViewSet,
    StakeholderMatrixView,
    StakeholderViewSet,
)
from project_templates.views import SaveProjectAsTemplateView
from business_meta.views import (
    TableDefinitionViewSet,
    FieldDefinitionViewSet,
    ProjectPositionViewSet,
)
from business_meta.data_views import (
    DynamicRowsView,
    DynamicRowDetailView,
    DynamicRowsExportView,
    DynamicRowsImportView,
)

# --- ViewSet Actions Setup ---

# Dynamic Table Definitions
table_list = TableDefinitionViewSet.as_view({'get': 'list', 'post': 'create'})
table_detail = TableDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Dynamic Table Fields
field_list = FieldDefinitionViewSet.as_view({'get': 'list', 'post': 'create'})
field_detail = FieldDefinitionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Project Organizational Positions
position_list = ProjectPositionViewSet.as_view({'get': 'list', 'post': 'create'})
position_detail = ProjectPositionViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
)

# Project Members (User Assignments)
member_list = ProjectMemberViewSet.as_view({'get': 'list', 'post': 'create'})
member_detail = ProjectMemberViewSet.as_view({'patch': 'partial_update'})
member_permissions = ProjectMemberViewSet.as_view({'get': 'permissions', 'post': 'permissions', 'delete': 'permissions'})

stakeholder_list = StakeholderViewSet.as_view({'get': 'list', 'post': 'create'})
stakeholder_detail = StakeholderViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)

communication_plan_list = CommunicationPlanViewSet.as_view({'get': 'list', 'post': 'create'})
communication_plan_detail = CommunicationPlanViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)

# --- Project URLs ---
urlpatterns = [
    # Project CRUD
    path('', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),

    # Project Templates
    path('templates/', ProjectViewSet.as_view({'get': 'templates'}), name='project-templates'),
    path('from_template/', ProjectViewSet.as_view({'post': 'from_template'}), name='project-from-template'),

    # Project Details (Specific Project)
    path('<uuid:project_pk>/', ProjectViewSet.as_view(
        {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
    ), name='project-detail'),

    # Lifecycle (FR-PRJ)
    path('<uuid:project_pk>/submit/', ProjectViewSet.as_view({'post': 'submit'}), name='project-submit'),
    path('<uuid:project_pk>/approve/', ProjectViewSet.as_view({'post': 'approve'}), name='project-approve'),
    path('<uuid:project_pk>/reject/', ProjectViewSet.as_view({'post': 'reject'}), name='project-reject'),
    path('<uuid:project_pk>/suspend/', ProjectViewSet.as_view({'post': 'suspend'}), name='project-suspend'),
    path('<uuid:project_pk>/resume/', ProjectViewSet.as_view({'post': 'resume'}), name='project-resume'),
    path('<uuid:project_pk>/complete/', ProjectViewSet.as_view({'post': 'complete'}), name='project-complete'),
    path('<uuid:project_pk>/archive/', ProjectViewSet.as_view({'post': 'archive'}), name='project-archive'),

    # Kickoff charter
    path(
        '<uuid:project_pk>/kickoff-charter/',
        ProjectKickoffCharterView.as_view(),
        name='project-kickoff-charter',
    ),

    # Project change requests
    path(
        '<uuid:project_pk>/change-requests/',
        ProjectChangeRequestListCreateView.as_view(),
        name='project-change-request-list',
    ),
    path(
        '<uuid:project_pk>/change-requests/<uuid:pk>/',
        ProjectChangeRequestDetailView.as_view(),
        name='project-change-request-detail',
    ),
    path(
        '<uuid:project_pk>/change-requests/<uuid:pk>/<str:action_name>/',
        ProjectChangeRequestActionView.as_view(),
        name='project-change-request-action',
    ),

    # Project Positions
    path('<uuid:project_pk>/positions/', position_list, name='project-position-list'),
    path('<uuid:project_pk>/positions/<uuid:pk>/', position_detail, name='project-position-detail'),

    # Project Members
    path('<uuid:project_pk>/members/', member_list, name='project-member-list'),
    path('<uuid:project_pk>/members/<uuid:user_id>/', member_detail, name='project-member-detail'),
    path(
        '<uuid:project_pk>/members/<uuid:user_id>/permissions/',
        member_permissions,
        name='project-member-permissions',
    ),

    # Stakeholders (FR-DATA)
    path('<uuid:project_pk>/stakeholders/', stakeholder_list, name='project-stakeholder-list'),
    path(
        '<uuid:project_pk>/stakeholders/<uuid:pk>/',
        stakeholder_detail,
        name='project-stakeholder-detail',
    ),
    path(
        '<uuid:project_pk>/stakeholders/matrix/',
        StakeholderMatrixView.as_view(),
        name='project-stakeholder-matrix',
    ),
    path(
        '<uuid:project_pk>/communication-plans/',
        communication_plan_list,
        name='project-communication-plan-list',
    ),
    path(
        '<uuid:project_pk>/communication-plans/<uuid:pk>/',
        communication_plan_detail,
        name='project-communication-plan-detail',
    ),

    # Project Dynamic Tables (Business Meta)
    path('<uuid:project_pk>/tables/', table_list, name='tabledefinition-list'),
    path('<uuid:project_pk>/tables/<int:pk>/', table_detail, name='tabledefinition-detail'),
    path(
        '<uuid:project_pk>/tables/by_slug/<str:table_slug>/',
        TableDefinitionViewSet.as_view({'get': 'by_slug'}),
        name='tabledefinition-by-slug',
    ),

    # Fields within Dynamic Tables
    path('<uuid:project_pk>/tables/<int:table_pk>/fields/', field_list, name='fielddefinition-list'),
    path('<uuid:project_pk>/tables/<int:table_pk>/fields/<int:pk>/', field_detail, name='fielddefinition-detail'),

    # Dynamic Table Data (Rows)
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/', DynamicRowsView.as_view(), name='dynamic-rows-list'),
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/export/', DynamicRowsExportView.as_view(), name='dynamic-rows-export'),
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/import/', DynamicRowsImportView.as_view(), name='dynamic-rows-import'),
    path('<uuid:project_pk>/tables/<str:table_slug>/rows/<str:row_id>/', DynamicRowDetailView.as_view(), name='dynamic-row-detail'),

    # Save Project as Template
    path('<uuid:project_pk>/save-as-template/', SaveProjectAsTemplateView.as_view(), name='project-save-as-template'),

    # Unified KPIs / health (Sprint 13 / K-02)
    path('<uuid:project_pk>/kpis/', ProjectKpisView.as_view(), name='project-kpis'),
    path('<uuid:project_pk>/kpis/drill/', ProjectKpiDrillView.as_view(), name='project-kpi-drill'),
    path('<uuid:project_pk>/health/', ProjectHealthView.as_view(), name='project-health'),
    path(
        '<uuid:project_pk>/dashboard/pack/',
        ProjectDashboardPackView.as_view(),
        name='project-dashboard-pack',
    ),
    path(
        '<uuid:project_pk>/reports/catalog/',
        ProjectReportCatalogView.as_view(),
        name='project-report-catalog',
    ),
    path(
        '<uuid:project_pk>/reports/<str:report_type>/',
        ProjectReportRunView.as_view(),
        name='project-report-run',
    ),
    path(
        '<uuid:project_pk>/reports/<str:report_type>/export/',
        ProjectReportExportView.as_view(),
        name='project-report-export',
    ),
    path(
        '<uuid:project_pk>/reports/exports/<uuid:export_id>/',
        ProjectReportExportDetailView.as_view(),
        name='project-report-export-detail',
    ),
    path(
        '<uuid:project_pk>/reports/exports/<uuid:export_id>/download/',
        ProjectReportExportDownloadView.as_view(),
        name='project-report-export-download',
    ),

    # Core principles: capabilities + fiscal locks
    path(
        '<uuid:project_pk>/capabilities/',
        ProjectCapabilityListView.as_view(),
        name='project-capabilities',
    ),
    path(
        '<uuid:project_pk>/capabilities/<str:capability_key>/',
        ProjectCapabilityDetailView.as_view(),
        name='project-capability-detail',
    ),
    path(
        '<uuid:project_pk>/fiscal-period-locks/',
        FiscalPeriodLockListCreateView.as_view(),
        name='project-fiscal-locks',
    ),
    path(
        '<uuid:project_pk>/fiscal-period-locks/<uuid:lock_id>/deactivate/',
        FiscalPeriodLockDeactivateView.as_view(),
        name='project-fiscal-lock-deactivate',
    ),

    # --- Nested Apps ---
    # These apps have endpoints nested under a specific project context
    path('<uuid:project_pk>/', include('inventory.project_urls')),
    path('<uuid:project_pk>/', include('wbs.urls')),
    path('<uuid:project_pk>/', include('schedule.urls')),
    path('<uuid:project_pk>/', include('field_reports.urls')),
    path('<uuid:project_pk>/', include('concrete_operations.urls')),
    path('<uuid:project_pk>/', include('risk.urls')),
    path('<uuid:project_pk>/', include('hr.urls')),
    path('<uuid:project_pk>/', include('sub_reports.urls')),
    path('<uuid:project_pk>/', include('cost_control.urls')),
    path('<uuid:project_pk>/', include('resources.urls')),
    path('<uuid:project_pk>/', include('cash_flow.urls')),
    path('<uuid:project_pk>/', include('contracts.urls')),
    path('<uuid:project_pk>/', include('subcontractors.urls')),
    path('<uuid:project_pk>/', include('documents.urls')),
    path('<uuid:project_pk>/', include('workflow.urls')),
    path('<uuid:project_pk>/', include('alerts.urls')),
    path('<uuid:project_pk>/', include('economic.urls')),
]
