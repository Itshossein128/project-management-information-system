"""Subcontractor module tests."""

from datetime import date
from decimal import Decimal

import pytest

from contracts.models import Contract, ContractItem, ContractType, IPC, IPCStatus
from master_data.models import ProjectMember, ProjectMemberRole
from schedule.models import ActivityProgress
from subcontractors.models import (
    Subcontractor,
    SubcontractorPerformanceScore,
    SubcontractorStatus,
    SubcontractorWarning,
    WarningType,
)
from subcontractors.services.risk_service import compute_risk_flag, financial_summary, score_trend

BASE = '/api/v1/projects/{project_id}/subcontractors'


@pytest.fixture
def finance_client(api_client, user, project, finance_manager_role):
    member = ProjectMember.objects.get(project=project, user=user)
    ProjectMemberRole.objects.create(member=member, role=finance_manager_role)
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def finance_manager_role(db):
    from master_data.models import Role

    return Role.objects.get(role_name='finance_manager')


@pytest.fixture
def sub_contract(db, project, user):
    return Contract.objects.create(
        project=project,
        contract_number='SUB-001',
        contract_type=ContractType.SUBCONTRACT,
        counterparty='Sub Co',
        original_amount=Decimal('500000000'),
        adjusted_amount=Decimal('500000000'),
        advance_payment_pct=Decimal('10'),
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def subcontractor(db, project, sub_contract, user):
    return Subcontractor.objects.create(
        project=project,
        company_name='پیمانکار آلفا',
        contract=sub_contract,
        discipline='سازه',
        status=SubcontractorStatus.ACTIVE,
        created_by=user,
        updated_by=user,
    )


def test_overall_score_normalized(subcontractor, user):
    score = SubcontractorPerformanceScore(
        subcontractor=subcontractor,
        score_date=date.today(),
        progress_score=Decimal('8'),
        quality_score=None,
        hse_score=Decimal('6'),
        payment_compliance_score=None,
        cooperation_score=None,
        evaluator=user,
        created_by=user,
        updated_by=user,
    )
    assert score.compute_overall() == pytest.approx(7.09, abs=0.01)


def test_score_validation_rejects_out_of_range(finance_client, project, subcontractor):
    url = f'{BASE.format(project_id=project.id)}/{subcontractor.id}/scores/'
    resp = finance_client.post(url, {'score_date': '2024-05-01', 'progress_score': 11, 'hse_score': 5}, format='json')
    assert resp.status_code == 400


def test_risk_flag_low_score(subcontractor, user):
    SubcontractorPerformanceScore.objects.create(
        subcontractor=subcontractor,
        score_date=date.today(),
        progress_score=Decimal('5'),
        hse_score=Decimal('5'),
        evaluator=user,
        created_by=user,
        updated_by=user,
    )
    flag, reasons = compute_risk_flag(subcontractor)
    assert flag is True
    assert any('نمره' in r for r in reasons)


def test_risk_flag_progress_behind(subcontractor, user, activity, sub_contract):
    ContractItem.objects.create(
        contract=sub_contract,
        activity=activity,
        boq_code='BOQ-1',
        description='Work',
        unit_price=Decimal('1000'),
        quantity=Decimal('100'),
        created_by=user,
        updated_by=user,
    )
    ActivityProgress.objects.create(
        activity=activity,
        report_date=date.today(),
        planned_progress=Decimal('0.60'),
        actual_progress=Decimal('0.40'),
    )
    flag, reasons = compute_risk_flag(subcontractor)
    assert flag is True
    assert 'پیشرفت بیش از 15٪ از برنامه عقب است' in reasons


def test_financial_summary_from_ipc(subcontractor, project, sub_contract, user):
    IPC.objects.create(
        project=project,
        contract=sub_contract,
        ipc_number=1,
        status=IPCStatus.PAID,
        gross_amount=Decimal('100000'),
        net_amount=Decimal('90000'),
        created_by=user,
        updated_by=user,
    )
    summary = financial_summary(subcontractor)
    assert summary['total_billed'] == pytest.approx(100000.0)
    assert summary['total_paid'] == pytest.approx(90000.0)
    assert summary['outstanding'] == pytest.approx(10000.0)


def test_create_subcontractor(auth_client, project):
    url = f'{BASE.format(project_id=project.id)}/'
    resp = auth_client.post(
        url,
        {'company_name': 'شرکت بتا', 'discipline': 'تاسیسات', 'status': 'active'},
        format='json',
    )
    assert resp.status_code == 201
    assert resp.data['company_name'] == 'شرکت بتا'


def test_list_filters_risk_only(finance_client, project, subcontractor, user):
    subcontractor.status = SubcontractorStatus.SUSPENDED
    subcontractor.save()
    url = f'{BASE.format(project_id=project.id)}/?risk_only=true'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1


def test_score_trend_improving(subcontractor, user):
    for i, val in enumerate([6.0, 7.0, 8.5]):
        SubcontractorPerformanceScore.objects.create(
            subcontractor=subcontractor,
            score_date=date(2024, 1, i + 1),
            progress_score=Decimal(str(val)),
            hse_score=Decimal(str(val)),
            evaluator=user,
            created_by=user,
            updated_by=user,
        )
    assert score_trend(subcontractor) == 'improving'


def test_warning_requires_resolved_date(finance_client, project, subcontractor):
    url = f'{BASE.format(project_id=project.id)}/{subcontractor.id}/warnings/'
    resp = finance_client.post(
        url,
        {
            'warning_date': '2024-05-01',
            'warning_type': 'written',
            'reason': 'عدم رعایت الزامات ایمنی در کارگاه',
            'resolved': True,
        },
        format='json',
    )
    assert resp.status_code == 400


def test_warning_resolve(finance_client, project, subcontractor, user):
    w = SubcontractorWarning.objects.create(
        subcontractor=subcontractor,
        warning_date=date.today(),
        warning_type=WarningType.WRITTEN,
        reason='تأخیر در تحویل مصالح',
        issued_by=user,
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{subcontractor.id}/warnings/{w.id}/'
    resp = finance_client.patch(
        url,
        {'resolved': True, 'resolved_date': '2024-06-01', 'resolution_notes': 'رفع شد'},
        format='json',
    )
    assert resp.status_code == 200
    assert resp.data['resolved'] is True


def test_list_scores(finance_client, project, subcontractor, user):
    SubcontractorPerformanceScore.objects.create(
        subcontractor=subcontractor,
        score_date=date(2024, 5, 1),
        progress_score=Decimal('8'),
        hse_score=Decimal('7'),
        evaluator=user,
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{subcontractor.id}/scores/'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1


def test_subcontractor_detail_includes_financial_status(finance_client, project, subcontractor, sub_contract, user):
    IPC.objects.create(
        project=project,
        contract=sub_contract,
        ipc_number=2,
        status=IPCStatus.APPROVED,
        gross_amount=Decimal('50000'),
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{subcontractor.id}/'
    resp = finance_client.get(url)
    assert resp.status_code == 200
    assert resp.data['financial_status'] is not None
    assert 'contract_summary' in resp.data


def test_delete_score(finance_client, project, subcontractor, user):
    score = SubcontractorPerformanceScore.objects.create(
        subcontractor=subcontractor,
        score_date=date(2024, 4, 1),
        progress_score=Decimal('7'),
        hse_score=Decimal('7'),
        evaluator=user,
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/{subcontractor.id}/scores/{score.id}/'
    resp = finance_client.delete(url)
    assert resp.status_code == 204
    assert not SubcontractorPerformanceScore.objects.filter(id=score.id, is_deleted=False).exists()
