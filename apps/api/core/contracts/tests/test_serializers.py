from decimal import Decimal

import pytest

from contracts.models import ContractItem
from contracts.pdf import render_ipc_pdf
from contracts.serializers import (
    ContractDetailSerializer,
    ContractListSerializer,
    IPCDetailSerializer,
    IPCListSerializer,
)


def test_contract_list_serializer_ipc_stats(contract, user, project):
    from contracts.models import IPC, IPCStatus

    contract._ipc_stats = None
    IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        status=IPCStatus.PAID,
        gross_amount=Decimal('100'),
        net_amount=Decimal('80'),
        created_by=user,
        updated_by=user,
    )
    data = ContractListSerializer(contract).data
    assert data['total_ipc_count'] == 1
    assert data['paid_ipc_count'] == 1


def test_contract_detail_serializer(contract):
    data = ContractDetailSerializer(contract).data
    assert data['contract_number'] == 'C-001'
    assert 'items' in data


def test_ipc_detail_serializer_deductions(db, ipc, user):
    from contracts.models import IPCDeduction

    ipc.gross_amount = Decimal('1000')
    ipc.save()
    IPCDeduction.objects.create(
        ipc=ipc,
        deduction_type='other',
        amount=Decimal('100'),
        created_by=user,
        updated_by=user,
    )
    data = IPCDetailSerializer(ipc).data
    assert data['deductions_total'] == 100.0
    assert data['net_amount_computed'] == 900.0


def test_ipc_list_days_overdue(db, project, contract, user):
    from datetime import date, timedelta

    from contracts.models import IPC, IPCStatus

    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=5,
        status=IPCStatus.APPROVED,
        planned_payment_date=date.today() - timedelta(days=2),
        gross_amount=Decimal('1'),
        created_by=user,
        updated_by=user,
    )
    data = IPCListSerializer(ipc).data
    assert data['days_overdue'] == 2


def test_render_ipc_pdf(ipc, contract_item, user):
    from contracts.models import IPCItem

    IPCItem.objects.create(
        ipc=ipc,
        contract_item=contract_item,
        description='Work',
        qty_current=Decimal('1'),
        unit_price=Decimal('100'),
        amount_current=Decimal('100'),
        created_by=user,
        updated_by=user,
    )
    ipc.gross_amount = Decimal('100')
    ipc.net_amount = Decimal('90')
    ipc.save()
    pdf = render_ipc_pdf(ipc)
    assert pdf.startswith(b'%PDF')
