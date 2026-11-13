"""Reconcile and expire schedule-import jobs without printing file contents."""

from django.core.management.base import BaseCommand, CommandError

from schedule.services.import_operations import run_maintenance
from schedule.services.import_process import reconcile_abandoned_scratch


class Command(BaseCommand):
    help = 'Reconcile dispatch, reclaim scratch, or purge expired import originals.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--batch-size', type=int, default=None)
        parser.add_argument('--operation', choices=('recovery', 'purge', 'scratch', 'all'), default='all')

    def handle(self, *args, **options):
        from django.conf import settings

        if options['batch_size'] is not None:
            if options['batch_size'] < 1 or options['batch_size'] > 100:
                raise CommandError('batch-size must be 1..100')
            settings.IMPORT_MAINTENANCE_BATCH_SIZE = options['batch_size']
        operations = ['recovery', 'scratch', 'purge'] if options['operation'] == 'all' else [options['operation']]
        failed = False
        for name in operations:
            if name == 'scratch':
                result = reconcile_abandoned_scratch(dry_run=options['dry_run'])
                action = 'would_remove' if options['dry_run'] else 'removed'
                self.stdout.write(f'scratch {action}={len(result["removed"])} preserved={len(result["preserved"])}')
                if result['status'] != 'ok':
                    failed = True
                continue
            result = run_maintenance(name, dry_run=options['dry_run'])
            self.stdout.write(
                f'{name} status={result["status"]} n={result.get("n", 0)} '
                f'elapsed={result.get("elapsed_seconds", 0)} bound={result.get("bound_seconds", "")}'
            )
            if result['status'] != 'ok':
                failed = True
        if failed:
            raise CommandError('import maintenance failed')
