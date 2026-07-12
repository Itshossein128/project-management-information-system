from django.core.management.base import BaseCommand
from django.apps import apps

# Required tables — names match actual model db_table values in the monorepo.
BLUEPRINT_TABLES = {
    'users', 'roles', 'project_members', 'project_member_roles', 'project_positions', 'units',
    'projects', 'wbs', 'activities', 'activity_relations',
    'baseline_schedules', 'baseline_activities', 'activity_progress',
    'daily_reports', 'daily_report_activities', 'daily_report_labor',
    'daily_report_equipment', 'daily_report_materials', 'daily_report_incidents',
    'materials', 'inventory_transactions', 'suppliers',
    'budgets', 'actual_costs', 'cost_pools',
    'contracts', 'contract_items', 'ipcs', 'ipc_items', 'ipc_deductions',
    'cash_transactions', 'cash_flow_forecasts',
    'inflation_indices', 'economic_snapshots', 'simulation_results',
    'risk_events', 'alert_rules', 'alert_log', 'audit_log', 'stored_files',
}

# Extension tables beyond the original blueprint — logged but not required.
OPTIONAL_EXTENSION_TABLES = {
    'discipline_sub_reports', 'discipline_sub_report_activities',
    'labor_job_titles', 'daily_report_concrete_logs', 'daily_report_labor_camp',
    'weather_logs', 'labor_camp_reports', 'equipment_logs',
    'msp_import_jobs', 'p6_import_jobs', 'notifications',
    'project_documents', 'document_revisions', 'correspondence', 'meeting_minutes',
    'subcontractors', 'subcontractor_performance_scores', 'subcontractor_warnings',
    'overtime_requests', 'leave_requests', 'material_requests',
    'permissions', 'role_permissions', 'project_member_permission_overrides',
    'change_orders',
}


class Command(BaseCommand):
    help = 'Verify blueprint Sprint 1 tables exist in Django models.'

    def handle(self, *args, **options):
        all_tables = set()
        for model in apps.get_models():
            all_tables.add(model._meta.db_table)

        found = BLUEPRINT_TABLES & all_tables
        missing = BLUEPRINT_TABLES - found
        extensions = OPTIONAL_EXTENSION_TABLES & all_tables

        self.stdout.write(f'Found {len(found)}/{len(BLUEPRINT_TABLES)} blueprint tables.')
        if extensions:
            self.stdout.write(f'Extension tables present: {len(extensions)}')
        if missing:
            self.stderr.write(self.style.ERROR(f'Missing: {sorted(missing)}'))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS('All blueprint tables present.'))
