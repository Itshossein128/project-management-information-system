"""Populate a project with cross-domain demo data for local development."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from cash_flow.models import (
    CashFlowForecast,
    CashTransaction,
    CashTransactionType,
    InflowCategory,
    OutflowCategory,
)
from contracts.models import Contract, ContractItem, ContractStatus, ContractType
from cost_control.models import ActualCost, Budget, CostCategory, CostPool, CostType
from documents.models import (
    Correspondence,
    CorrStatus,
    CorrType,
    DocType,
    MeetingMinutes,
    MeetingType,
    ProjectDocument,
)
from economic.models import EconomicSnapshot
from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    DailyReportLabor,
    LaborCategory,
    LaborJobTitle,
    ReportShift,
    ReportStatus,
    WeatherCondition,
)
from hr.models import LeaveRequest, LeaveStatus, LeaveType, OvertimeRequest, OvertimeStatus
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role, Unit
from project_templates.models import ProjectTemplate
from project_templates.services import apply_template_to_project
from projects.models import Activity, ActivityStatus, Project, WBS
from resources.models import InventoryTransaction, Material, Supplier, TransactionType
from risk.models import BarrierCategory, BarrierStatus, EventType, RiskEvent, Severity
from schedule.models import ActivityProgress, BaselineActivity, BaselineSchedule
from subcontractors.models import Subcontractor, SubcontractorPerformanceScore, SubcontractorStatus

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


@dataclass(frozen=True)
class DemoProjectSpec:
    project_code: str
    project_name: str
    template_type: str
    employer: str
    contractor: str
    consultant: str
    location: str
    start_date: date
    planned_finish_date: date
    contract_amount: Decimal
    contract_type: str
    progress_factor: Decimal
    contract_prefix: str


DEMO_PROJECT_SPECS: tuple[DemoProjectSpec, ...] = (
    DemoProjectSpec(
        project_code='acme',
        project_name='Acme Construction',
        template_type='residential',
        employer='Acme Development Co.',
        contractor='IPCAS Builders',
        consultant='Urban Design Partners',
        location='Tehran, District 2 — Residential complex',
        start_date=date(2025, 3, 1),
        planned_finish_date=date(2026, 12, 31),
        contract_amount=Decimal('85000000000'),
        contract_type='lump_sum',
        progress_factor=Decimal('0.35'),
        contract_prefix='ACME',
    ),
    DemoProjectSpec(
        project_code='buildco',
        project_name='BuildCo',
        template_type='epc',
        employer='National Infrastructure Authority',
        contractor='BuildCo EPC Consortium',
        consultant='Global Engineering Ltd.',
        location='Isfahan Industrial Zone — EPC plant',
        start_date=date(2025, 9, 1),
        planned_finish_date=date(2028, 6, 30),
        contract_amount=Decimal('320000000000'),
        contract_type='epc_turnkey',
        progress_factor=Decimal('0.12'),
        contract_prefix='BLD',
    ),
)


def _audit(user) -> dict:
    return {'created_by': user, 'updated_by': user}


def _assign_role(member: ProjectMember, role_name: str) -> None:
    role = Role.objects.get(role_name=role_name)
    ProjectMemberRole.objects.get_or_create(member=member, role=role)


def _update_project_metadata(project: Project, spec: DemoProjectSpec, manager) -> None:
    project.project_name = spec.project_name
    project.employer = spec.employer
    project.contractor = spec.contractor
    project.consultant = spec.consultant
    project.location = spec.location
    project.start_date = spec.start_date
    project.planned_finish_date = spec.planned_finish_date
    project.contract_amount = spec.contract_amount
    project.contract_type = spec.contract_type
    project.project_manager = manager
    project.save(
        update_fields=[
            'project_name',
            'employer',
            'contractor',
            'consultant',
            'location',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'project_manager',
        ]
    )


def _apply_wbs_template(project: Project, spec: DemoProjectSpec, user) -> None:
    if WBS.objects.filter(project=project).exists():
        return

    template = ProjectTemplate.objects.filter(
        project_type=spec.template_type,
        is_system=True,
    ).first()
    if template is None:
        raise ValueError(f'No system template found for type {spec.template_type!r}')

    apply_template_to_project(template, project, user=user)


def _ensure_leaf_activities(project: Project, spec: DemoProjectSpec, user) -> list[Activity]:
    unit = Unit.objects.filter(unit_symbol='m3').first()
    activities: list[Activity] = []
    leaf_nodes = [node for node in WBS.objects.filter(project=project) if node.is_leaf()]
    duration_days = (spec.planned_finish_date - spec.start_date).days
    chunk = max(duration_days // max(len(leaf_nodes), 1), 30)

    for idx, wbs in enumerate(leaf_nodes):
        code = f'{wbs.wbs_code.replace(".", "-")}-A1'
        planned_start = spec.start_date + timedelta(days=idx * chunk)
        planned_finish = min(planned_start + timedelta(days=chunk - 1), spec.planned_finish_date)
        status = ActivityStatus.IN_PROGRESS if idx % 2 == 0 else ActivityStatus.NOT_STARTED
        activity, _ = Activity.objects.get_or_create(
            project=project,
            activity_code=code,
            defaults={
                'wbs': wbs,
                'activity_name': f'{wbs.wbs_name} — execution',
                'unit': unit,
                'total_quantity': Decimal('1000'),
                'weight': Decimal('1') / Decimal(len(leaf_nodes)),
                'planned_start': planned_start,
                'planned_finish': planned_finish,
                'status': status,
                'created_by': user,
                'updated_by': user,
            },
        )
        activities.append(activity)
    return activities


def _seed_schedule(project: Project, spec: DemoProjectSpec, activities: list[Activity], user) -> None:
    baseline, _ = BaselineSchedule.objects.get_or_create(
        project=project,
        version_name='Baseline v1',
        defaults={
            'approved_at': spec.start_date,
            'approved_by': user,
            'is_current': True,
        },
    )
    if not baseline.is_current:
        baseline.is_current = True
        baseline.save(update_fields=['is_current'])

    for activity in activities:
        BaselineActivity.objects.get_or_create(
            baseline=baseline,
            activity=activity,
            defaults={
                'planned_start': activity.planned_start,
                'planned_finish': activity.planned_finish,
                'planned_duration': activity.planned_duration,
                'planned_quantity': activity.total_quantity,
                'planned_progress': Decimal('1.0'),
            },
        )

        progress_date = spec.start_date + timedelta(days=90)
        ActivityProgress.objects.update_or_create(
            activity=activity,
            report_date=progress_date,
            defaults={
                'actual_progress': spec.progress_factor,
                'source': ActivityProgress.ProgressSource.MANUAL,
                'updated_by': user,
            },
        )


def _seed_costs(
    project: Project,
    spec: DemoProjectSpec,
    activities: list[Activity],
    supplier: Supplier,
    user,
) -> None:
    if not activities:
        return

    primary = activities[0]
    budget_total = spec.contract_amount * Decimal('0.6')
    categories = (
        (CostCategory.LABOR, Decimal('0.35')),
        (CostCategory.MATERIAL, Decimal('0.40')),
        (CostCategory.EQUIPMENT, Decimal('0.15')),
        (CostCategory.SUBCONTRACT, Decimal('0.10')),
    )
    for category, weight in categories:
        Budget.objects.get_or_create(
            project=project,
            activity=primary,
            cost_category=category,
            defaults={
                'wbs': primary.wbs,
                'budget_amount': (budget_total * weight).quantize(Decimal('0.01')),
                **_audit(user),
            },
        )

    CostPool.objects.get_or_create(
        project=project,
        pool_name=f'{spec.contract_prefix} shared overhead',
        defaults={
            'cost_category': CostCategory.SITE_OVERHEAD,
            'total_amount': spec.contract_amount * Decimal('0.05'),
            **_audit(user),
        },
    )

    ActualCost.objects.get_or_create(
        project=project,
        invoice_number=f'{spec.contract_prefix}-INV-001',
        defaults={
            'activity': primary,
            'wbs': primary.wbs,
            'cost_date': spec.start_date + timedelta(days=45),
            'cost_category': CostCategory.MATERIAL,
            'amount': spec.contract_amount * Decimal('0.08'),
            'description': 'Initial material procurement',
            'supplier': supplier,
            'cost_type': CostType.DIRECT,
            **_audit(user),
        },
    )


def _seed_resources(project: Project, spec: DemoProjectSpec, activities: list[Activity], user) -> Supplier:
    supplier, _ = Supplier.objects.get_or_create(
        project=project,
        supplier_code=f'{spec.contract_prefix}-SUP-01',
        defaults={
            'supplier_name': f'{spec.contract_prefix} Materials Ltd.',
            'contact_person': 'Supply Desk',
            'phone': '+982112345678',
            'email': f'supply@{spec.project_code}.demo',
            **_audit(user),
        },
    )

    unit = Unit.objects.filter(unit_symbol='ton').first()
    material, _ = Material.objects.get_or_create(
        project=project,
        material_code=f'{spec.contract_prefix}-MAT-01',
        defaults={
            'material_name': 'Structural steel',
            'unit': unit,
            'category': 'structural',
            'estimated_total_qty': Decimal('500'),
            'min_stock_level': Decimal('50'),
        },
    )

    if activities:
        InventoryTransaction.objects.get_or_create(
            project=project,
            material=material,
            tx_date=spec.start_date + timedelta(days=30),
            tx_type=TransactionType.IN,
            defaults={
                'quantity': Decimal('120'),
                'unit_cost': Decimal('2500000'),
                'supplier': supplier,
                'activity': activities[0],
                'document_ref': f'{spec.contract_prefix}-GRN-001',
                'notes': 'Initial steel delivery',
                **_audit(user),
            },
        )
    return supplier


def _seed_contracts(
    project: Project,
    spec: DemoProjectSpec,
    activities: list[Activity],
    user,
) -> tuple[Contract | None, Contract | None]:
    if not activities:
        return None, None

    main, _ = Contract.objects.get_or_create(
        project=project,
        contract_number=f'{spec.contract_prefix}-MAIN-001',
        defaults={
            'contract_type': ContractType.MAIN,
            'counterparty': spec.employer,
            'start_date': spec.start_date,
            'finish_date': spec.planned_finish_date,
            'original_amount': spec.contract_amount,
            'adjusted_amount': spec.contract_amount,
            'retention_pct': Decimal('10'),
            'tax_pct': Decimal('9'),
            'insurance_pct': Decimal('1'),
            'advance_payment_pct': Decimal('20'),
            'status': ContractStatus.ACTIVE,
            **_audit(user),
        },
    )
    sub, _ = Contract.objects.get_or_create(
        project=project,
        contract_number=f'{spec.contract_prefix}-SUB-001',
        defaults={
            'contract_type': ContractType.SUBCONTRACT,
            'counterparty': f'{spec.contract_prefix} Specialty Works',
            'start_date': spec.start_date,
            'finish_date': spec.planned_finish_date,
            'original_amount': spec.contract_amount * Decimal('0.15'),
            'adjusted_amount': spec.contract_amount * Decimal('0.15'),
            'retention_pct': Decimal('5'),
            'tax_pct': Decimal('9'),
            'advance_payment_pct': Decimal('10'),
            'status': ContractStatus.ACTIVE,
            **_audit(user),
        },
    )

    for idx, (contract, activity) in enumerate(
        ((main, activities[0]), (sub, activities[min(1, len(activities) - 1)]))
    ):
        ContractItem.objects.get_or_create(
            contract=contract,
            boq_code=f'{spec.contract_prefix}-BOQ-{idx + 1}',
            defaults={
                'activity': activity,
                'description': activity.activity_name,
                'unit_price': Decimal('10000'),
                'quantity': activity.total_quantity or Decimal('100'),
                **_audit(user),
            },
        )
    return main, sub


def _seed_field_reports(
    project: Project,
    spec: DemoProjectSpec,
    activities: list[Activity],
    user,
) -> None:
    if not activities:
        return

    report_date = spec.start_date + timedelta(days=60)
    report, _ = DailyReport.objects.get_or_create(
        project=project,
        report_date=report_date,
        shift=ReportShift.FULL,
        defaults={
            'weather_condition': WeatherCondition.SUNNY,
            'temp_max': Decimal('28.0'),
            'temp_min': Decimal('16.0'),
            'general_notes': f'Demo daily report for {spec.project_name}',
            'prepared_by': user,
            'submitted_by': user,
            'approved_by': user,
            'status': ReportStatus.APPROVED,
            'submitted_at': timezone.now(),
            'approved_at': timezone.now(),
            **_audit(user),
        },
    )

    DailyReportActivity.objects.get_or_create(
        report=report,
        activity_ref=activities[0],
        shift=ActivityRowShift.SHIFT_1,
        defaults={
            'activity_description': activities[0].activity_name,
            'headcount': 12,
            'quantity': Decimal('45'),
            'unit': 'm3',
            'execution_percentage': spec.progress_factor * Decimal('100'),
        },
    )

    labor_title = LaborJobTitle.objects.filter(category=LaborCategory.DIRECT).order_by('display_order').first()
    if labor_title:
        DailyReportLabor.objects.get_or_create(
            report=report,
            labor_category=LaborCategory.DIRECT,
            job_title=labor_title.title,
            defaults={
                'shift_1_count': 8,
                'work_hours': Decimal('8'),
            },
        )


def _seed_cash_flow(project: Project, spec: DemoProjectSpec, main_contract: Contract | None, user) -> None:
    CashTransaction.objects.get_or_create(
        project=project,
        document_ref=f'{spec.contract_prefix}-CASH-IN-001',
        defaults={
            'tx_date': spec.start_date + timedelta(days=15),
            'tx_type': CashTransactionType.IN,
            'category': InflowCategory.ADVANCE_RECEIPT,
            'amount': spec.contract_amount * Decimal('0.20'),
            'description': 'Advance payment received',
            'contract': main_contract,
            'counterparty': spec.employer,
            **_audit(user),
        },
    )
    CashTransaction.objects.get_or_create(
        project=project,
        document_ref=f'{spec.contract_prefix}-CASH-OUT-001',
        defaults={
            'tx_date': spec.start_date + timedelta(days=50),
            'tx_type': CashTransactionType.OUT,
            'category': OutflowCategory.SUPPLIER_PAYMENT,
            'amount': spec.contract_amount * Decimal('0.06'),
            'description': 'Supplier payment — materials',
            'counterparty': f'{spec.contract_prefix} Materials Ltd.',
            **_audit(user),
        },
    )

    forecast_month = date(spec.start_date.year, spec.start_date.month, 1)
    CashFlowForecast.objects.get_or_create(
        project=project,
        month=forecast_month,
        defaults={
            'expected_inflow': spec.contract_amount * Decimal('0.10'),
            'expected_outflow': spec.contract_amount * Decimal('0.05'),
            'confidence_pct': Decimal('80'),
            'notes': 'Demo monthly forecast',
            **_audit(user),
        },
    )


def _seed_risk(project: Project, spec: DemoProjectSpec, activities: list[Activity], user) -> None:
    activity = activities[0] if activities else None
    RiskEvent.objects.get_or_create(
        project=project,
        description=f'{spec.project_name}: material delivery delay risk',
        defaults={
            'activity': activity,
            'event_date': spec.start_date + timedelta(days=40),
            'event_type': EventType.RISK,
            'category': BarrierCategory.SUBCONTRACTOR,
            'impact_on_schedule': True,
            'impact_on_cost': True,
            'time_impact_days': 14,
            'cost_impact': spec.contract_amount * Decimal('0.01'),
            'probability': Decimal('0.35'),
            'severity': Severity.MEDIUM,
            'status': BarrierStatus.IN_PROGRESS,
            'corrective_action': 'Expedite supplier shipment and add buffer to schedule',
            'owner': user,
            **_audit(user),
        },
    )


def _seed_subcontractors(
    project: Project,
    spec: DemoProjectSpec,
    sub_contract: Contract | None,
    user,
) -> None:
    subcontractor, _ = Subcontractor.objects.get_or_create(
        project=project,
        company_name=f'{spec.contract_prefix} Specialty Works',
        defaults={
            'contract': sub_contract,
            'discipline': 'civil',
            'responsible_person': 'Site Lead',
            'phone': '+982198765432',
            'status': SubcontractorStatus.ACTIVE,
            **_audit(user),
        },
    )
    SubcontractorPerformanceScore.objects.get_or_create(
        subcontractor=subcontractor,
        score_date=spec.start_date + timedelta(days=75),
        defaults={
            'progress_score': Decimal('7.5'),
            'quality_score': Decimal('8.0'),
            'hse_score': Decimal('8.5'),
            'payment_compliance_score': Decimal('7.0'),
            'cooperation_score': Decimal('8.0'),
            'evaluator': user,
            'notes': 'Demo performance review',
            **_audit(user),
        },
    )


def _seed_documents(project: Project, spec: DemoProjectSpec, activities: list[Activity], user) -> None:
    activity = activities[0] if activities else None
    wbs = activity.wbs if activity else None
    document, _ = ProjectDocument.objects.get_or_create(
        project=project,
        doc_code=f'{spec.contract_prefix}-DOC-001',
        defaults={
            'title': f'{spec.project_name} — master schedule',
            'doc_type': DocType.REPORT,
            'discipline': 'planning',
            'revision': 'A',
            'revision_date': spec.start_date,
            'file_name': f'{spec.contract_prefix.lower()}-schedule.pdf',
            'uploaded_by': user,
            'related_activity': activity,
            'related_wbs': wbs,
            **_audit(user),
        },
    )
    Correspondence.objects.get_or_create(
        project=project,
        corr_number=f'{spec.contract_prefix}-CORR-001',
        defaults={
            'corr_type': CorrType.INCOMING,
            'subject': 'Employer instruction — mobilization',
            'from_party': spec.employer,
            'to_party': spec.contractor,
            'corr_date': spec.start_date + timedelta(days=7),
            'status': CorrStatus.CLOSED,
            'summary': 'Mobilization and site handover instructions',
            'related_document': document,
            **_audit(user),
        },
    )
    MeetingMinutes.objects.get_or_create(
        project=project,
        meeting_date=spec.start_date + timedelta(days=14),
        meeting_type=MeetingType.WEEKLY_PROGRESS,
        defaults={
            'location': 'Site office',
            'chairperson': user,
            'agenda': 'Weekly progress and lookahead',
            'decisions': 'Approve procurement plan and baseline schedule',
            'action_items': 'Issue revised look-ahead for next 4 weeks',
            **_audit(user),
        },
    )


def _seed_hr(project: Project, spec: DemoProjectSpec, members: list[ProjectMember], user) -> None:
    requester = members[0].user if members else user
    OvertimeRequest.objects.get_or_create(
        project=project,
        requester=requester,
        overtime_date=spec.start_date + timedelta(days=20),
        defaults={
            'department': 'Site operations',
            'requested_hours': Decimal('4'),
            'reason': 'Concrete pour completion',
            'supervisor': user,
            'supervisor_approved': True,
            'status': OvertimeStatus.MANAGER_APPROVED,
            **_audit(user),
        },
    )
    LeaveRequest.objects.get_or_create(
        project=project,
        requester=requester,
        leave_date=spec.start_date + timedelta(days=25),
        defaults={
            'department': 'Site operations',
            'request_type': LeaveType.DAILY,
            'supervisor': user,
            'supervisor_approved': True,
            'status': LeaveStatus.MANAGER_APPROVED,
            **_audit(user),
        },
    )


def _seed_economic(project: Project, spec: DemoProjectSpec) -> None:
    EconomicSnapshot.objects.get_or_create(
        project=project,
        snapshot_date=spec.start_date + timedelta(days=90),
        defaults={
            'actual_cost': spec.contract_amount * Decimal('0.10'),
            'inflation_adj_cost': spec.contract_amount * Decimal('0.105'),
            'revenue_to_date': spec.contract_amount * spec.progress_factor,
            'accounting_profit': spec.contract_amount * Decimal('0.02'),
            'real_profit': spec.contract_amount * Decimal('0.015'),
            'working_capital': spec.contract_amount * Decimal('0.04'),
            'avg_payment_delay_days': Decimal('32'),
        },
    )


@transaction.atomic
def seed_full_project(
    *,
    project: Project,
    spec: DemoProjectSpec,
    creator: AbstractBaseUser,
    members: list[ProjectMember],
) -> dict:
    """Idempotently enrich one project with demo data across IPCAS domains."""
    _update_project_metadata(project, spec, creator)
    _apply_wbs_template(project, spec, creator)

    for member in members:
        if member.status == MemberStatus.ACTIVE and not member.member_roles.exists():
            if member.user_id == creator.id:
                _assign_role(member, 'project_manager')
            elif member.position and member.position.slug == 'worker':
                _assign_role(member, 'site_supervisor')
            elif member.position and member.position.slug in ('electrician', 'supervisor'):
                _assign_role(member, 'planning_engineer')

    activities = list(Activity.objects.filter(project=project, is_deleted=False).order_by('activity_code'))
    if not activities:
        activities = _ensure_leaf_activities(project, spec, creator)

    _seed_schedule(project, spec, activities, creator)
    supplier = _seed_resources(project, spec, activities, creator)
    _seed_costs(project, spec, activities, supplier, creator)
    main_contract, sub_contract = _seed_contracts(project, spec, activities, creator)
    _seed_field_reports(project, spec, activities, creator)
    _seed_cash_flow(project, spec, main_contract, creator)
    _seed_risk(project, spec, activities, creator)
    _seed_subcontractors(project, spec, sub_contract, creator)
    _seed_documents(project, spec, activities, creator)
    _seed_hr(project, spec, members, creator)
    _seed_economic(project, spec)

    return {
        'project_code': spec.project_code,
        'wbs_nodes': WBS.objects.filter(project=project).count(),
        'activities': len(activities),
        'members': len(members),
    }
