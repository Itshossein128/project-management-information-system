"""Backfill legacy discipline sub-reports into canonical unit taxonomy (feature 032, US6, T064).

Deterministic, resumable, and idempotent. Snapshots source_checksum and records
trace ledger entries in UnitReportMigrationTrace and UnitReportMigrationQuarantine.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from sub_reports.services.migration import migrate_legacy_sub_reports


class Command(BaseCommand):
    help = 'Deterministic, resumable backfill of legacy sub-reports into canonical unit taxonomy.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=str,
            default=None,
            help='Optional UUID of a specific project to backfill.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Execute backfill in a transaction and roll back changes at the end.',
        )

    def handle(self, *args, **options):
        project_id = options.get('project_id')
        dry_run = options.get('dry_run', False)

        self.stdout.write(self.style.NOTICE(
            f"Starting unit-report backfill (project_id={project_id or 'ALL'}, dry_run={dry_run})..."
        ))

        if dry_run:
            with transaction.atomic():
                stats = migrate_legacy_sub_reports(project_id=project_id)
                self.stdout.write(self.style.WARNING(
                    f"DRY RUN completed: {stats['total_traces']} total traces, {stats['quarantined']} quarantined. Rolling back..."
                ))
                transaction.set_rollback(True)
        else:
            stats = migrate_legacy_sub_reports(project_id=project_id)
            self.stdout.write(self.style.SUCCESS(
                f"Backfill successfully completed: {stats['total_traces']} traces recorded, "
                f"{stats['quarantined']} records quarantined."
            ))
