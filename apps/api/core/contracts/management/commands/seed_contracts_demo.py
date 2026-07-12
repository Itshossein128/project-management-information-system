"""Seed demo contracts with BoQ items linked to project activities."""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from contracts.models import Contract, ContractItem, ContractStatus, ContractType
from projects.models import Activity, Project
from schedule.models import ActivityProgress


class Command(BaseCommand):
    help = 'Create demo main + subcontract with BoQ lines and sample progress for IPC auto-fill.'

    def add_arguments(self, parser):
        parser.add_argument('--project-id', required=True, help='Project UUID')
        parser.add_argument('--user-id', help='User UUID for audit fields (optional)')

    @transaction.atomic
    def handle(self, *args, **options):
        project = Project.objects.get(pk=options['project_id'])
        user = None
        if options.get('user_id'):
            from django.contrib.auth import get_user_model

            user = get_user_model().objects.get(pk=options['user_id'])

        activities = list(Activity.objects.filter(project=project, is_deleted=False)[:3])
        if not activities:
            self.stderr.write('No activities found — create WBS/activities first.')
            return

        audit = {'created_by': user, 'updated_by': user} if user else {}

        main, created = Contract.objects.get_or_create(
            project=project,
            contract_number='DEMO-MAIN-001',
            defaults={
                'contract_type': ContractType.MAIN,
                'counterparty': project.employer or 'Employer',
                'original_amount': Decimal('1000000000'),
                'adjusted_amount': Decimal('1000000000'),
                'retention_pct': Decimal('10'),
                'tax_pct': Decimal('9'),
                'insurance_pct': Decimal('1'),
                'advance_payment_pct': Decimal('20'),
                'status': ContractStatus.ACTIVE,
                **audit,
            },
        )
        self.stdout.write(f'Main contract: {main.id} ({ "created" if created else "exists" })')

        sub, created = Contract.objects.get_or_create(
            project=project,
            contract_number='DEMO-SUB-001',
            defaults={
                'contract_type': ContractType.SUBCONTRACT,
                'counterparty': 'Demo Subcontractor',
                'original_amount': Decimal('200000000'),
                'adjusted_amount': Decimal('200000000'),
                'retention_pct': Decimal('5'),
                'tax_pct': Decimal('9'),
                'advance_payment_pct': Decimal('10'),
                'status': ContractStatus.ACTIVE,
                **audit,
            },
        )
        self.stdout.write(f'Subcontract: {sub.id} ({ "created" if created else "exists" })')

        for idx, (contract, activity) in enumerate([(main, activities[0]), (sub, activities[min(1, len(activities) - 1)])]):
            item, _ = ContractItem.objects.get_or_create(
                contract=contract,
                boq_code=f'DEMO-BOQ-{idx + 1}',
                defaults={
                    'activity': activity,
                    'description': activity.activity_name,
                    'unit_price': Decimal('10000'),
                    'quantity': activity.total_quantity or Decimal('100'),
                    **audit,
                },
            )
            ActivityProgress.objects.update_or_create(
                activity=activity,
                report_date=date(2024, 3, 1),
                defaults={'actual_progress': Decimal('0.10'), 'source': 'manual'},
            )
            ActivityProgress.objects.update_or_create(
                activity=activity,
                report_date=date(2024, 3, 31),
                defaults={'actual_progress': Decimal('0.25'), 'source': 'manual'},
            )
            self.stdout.write(f'  BoQ item {item.boq_code} -> activity {activity.activity_code}')

        self.stdout.write(self.style.SUCCESS('Demo contracts seeded. Create IPC for period 2024-03-01..2024-03-31.'))
