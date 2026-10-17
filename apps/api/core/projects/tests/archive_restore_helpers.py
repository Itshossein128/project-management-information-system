"""Known-origin archive fixtures shared by restore tests (no legacy inference)."""
from uuid import uuid4
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APIClient
from projects.models import Project
from projects import lifecycle_service


def actor(*, admin=False, superuser=False):
    user = get_user_model().objects.create_user(
        username=f'restore-{uuid4().hex[:16]}', full_name='Restore administrator',
        is_superuser=superuser, password=None,
    )
    if admin:
        user.groups.add(Group.objects.get_or_create(name='admin')[0])
    return user


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def ready_project(user, origin='active'):
    project = Project.objects.create(
        project_code=uuid4().hex[:20], project_name='Archive test project',
        employer='Employer', project_manager=user, scope_description='Approved scope',
        contract_amount=Decimal('1000.00'), budget_approved_at=timezone.now(),
        budget_approved_by=user, status='active',
    )

    if origin == 'suspended': project = lifecycle_service.suspend(project, user)
    elif origin == 'completed': project = lifecycle_service.complete(project, user)
    elif origin != 'active':
        project.status = origin; project.save(update_fields=['status'])
    return project

def archived_project(user, origin='active'):
    return lifecycle_service.archive(ready_project(user, origin), user)


def state(project):
    return Project.objects.filter(pk=project.pk).values().get()


def base(project):
    return f'/api/v1/projects/{project.pk}/'


def populate_business_records(project,user):
    """Stored production-model references; does not claim an external object-store download."""
    from datetime import date
    from documents.models import ProjectDocument, DocumentRevision
    from contracts.models import Contract, IPC, IPCCollection
    from cost_control.models import Commitment, Payment
    from cash_flow.models import CashTransaction
    from schedule.models import BaselineSchedule
    from projects.models import ProjectKickoffCharter, ProjectChangeRequest
    from audit.models import AuditLog
    now=timezone.now();today=date.today()
    doc=ProjectDocument.objects.create(created_by=user,project=project,title='Approved drawing',doc_code='D-01',file_url='s3://velora-test/sha256-original.pdf',file_name='original.pdf',file_size_kb=42,status='approved',uploaded_by=user,approver=user)
    doc.restricted_to.add(user)
    revision=DocumentRevision.objects.create(document=doc,revision_label='A',revision_date=today,file_url=doc.file_url,uploaded_by=user,change_description='Original approved bytes reference')
    contract=Contract.objects.create(created_by=user,project=project,contract_number='C-01',original_amount=Decimal('7654.32'),status='active',file_url=doc.file_url)
    ipc=IPC.objects.create(created_by=user,project=project,contract=contract,ipc_number=1,status='paid',gross_amount=Decimal('123.45'),approved_amount=Decimal('120.00'),net_amount=Decimal('110.00'),approval_date=today,actual_payment_date=today)
    collection=IPCCollection.objects.create(created_by=user,ipc=ipc,amount=Decimal('110.00'),collected_at=today,reference='BANK-ORIGINAL')
    commitment=Commitment.objects.create(created_by=user,project=project,contract=contract,commitment_number='COM-1',amount=Decimal('321.09'),commitment_date=today,status='approved',document_ref='D-01')
    payment=Payment.objects.create(created_by=user,project=project,commitment=commitment,amount=Decimal('50.00'),paid_at=today,status='posted',document_ref='PAY-ORIGINAL')
    cash=CashTransaction.objects.create(created_by=user,project=project,ipc=ipc,contract=contract,tx_date=today,actual_date=today,tx_type='in',category='ipc_receipt',amount=Decimal('110.00'),document_ref='BANK-ORIGINAL')
    baseline=BaselineSchedule.objects.create(created_by=user,project=project,version_name='Approved original',approved_at=today,approved_by=user,is_locked=True,locked_at=now,locked_by=user)
    charter=ProjectKickoffCharter.objects.create(created_by=user,project=project,justification='Original charter',success_criteria='Original criteria')
    cr=ProjectChangeRequest.objects.create(created_by=user,project=project,reason='Original approval',status='approved',proposed_changes={'contract_amount':'1000.00'},previous_values={'contract_amount':'900.00'},requested_by=user,decided_by=actor(admin=True),decided_at=now)
    audit=AuditLog.objects.create(project=project,actor=user,http_method='POST',path='/original-approval/',changes={'approved':True})
    return [doc,revision,contract,ipc,collection,commitment,payment,cash,baseline,charter,cr,audit]


def business_snapshot(records):
    return [(row._meta.label,list(type(row)._base_manager.filter(pk=row.pk).values())) for row in records]
