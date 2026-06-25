from django.core.management.base import BaseCommand
from django.apps import apps

BLUEPRINT_TABLES = {
    'users', 'roles', 'project_members', 'project_member_roles', 'project_positions', 'units',
    'projects', 'wbs', 'activities', 'activity_relations',
    'baseline_schedules', 'baseline_activities', 'activity_progress',
    'daily_reports', 'daily_activities', 'daily_labor', 'daily_equipment', 'daily_material_usage', 'daily_incidents',
    'materials', 'inventory_transactions', 'suppliers',
    'budgets', 'actual_costs', 'cost_pools',
    'contracts', 'contract_items', 'ipcs', 'ipc_items', 'ipc_deductions',
    'cash_transactions', 'cash_flow_forecasts',
    'inflation_indices', 'economic_snapshots', 'simulation_results',
    'risk_events', 'alert_rules', 'alert_log', 'audit_log', 'stored_files',
}


class Command(BaseCommand):
    help = 'Verify blueprint Sprint 1 tables exist in Django models.'

    def handle(self, *args, **options):
        found = set()
        for model in apps.get_models():
            table = model._meta.db_table
            if table in BLUEPRINT_TABLES:
                found.add(table)
        missing = BLUEPRINT_TABLES - found
        self.stdout.write(f'Found {len(found)}/{len(BLUEPRINT_TABLES)} blueprint tables.')
        if missing:
            self.stderr.write(self.style.ERROR(f'Missing: {sorted(missing)}'))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS('All blueprint tables present.'))
