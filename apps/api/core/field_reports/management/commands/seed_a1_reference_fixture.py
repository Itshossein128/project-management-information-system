"""Import the reviewable, synthetic B01 fixture without altering real projects."""
import json
from pathlib import Path
from uuid import UUID, uuid5

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from field_reports.models import (
    DailyReport, DailyReportActivity, DailyReportLabor, DailyReportWorkedShift, ReportShift, WeatherLog,
)
from field_reports.services.data_contract import load_daily_report_contract
from projects.models import Project

FIXTURE_PATH = Path(__file__).resolve().parents[2] / 'fixtures' / 'sim_a1_001_1406_03_01.json'
PROJECT_CODE = 'SIM-A1-001'
PROJECT_LABEL = '[SYNTHETIC A.1 REFERENCE]'
ACTOR_USERNAME = 'sim-a1-001-fixture'


class Command(BaseCommand):
    help = 'Import the labeled SIM-A1-001 synthetic daily report and related reference rows.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Restore fixture-owned rows to their published values.')

    @transaction.atomic
    def handle(self, *args, reset, **options):
        with FIXTURE_PATH.open(encoding='utf-8') as source:
            fixture = json.load(source)
        project_data = fixture['project']
        report_data = fixture['report']
        project_id = UUID(project_data['id'])
        report_id = UUID(report_data['id'])
        contract = load_daily_report_contract(report_data['contract_version'])
        reference = contract['reference_day_fixture']
        if (fixture['is_synthetic_reference'] is not True
                or project_data['project_code'] != PROJECT_CODE
                or not project_data['project_name'].startswith(PROJECT_LABEL)
                or project_data['start_date'] != reference['gregorian_actual_start_date']
                or report_data['report_date'] != reference['gregorian_date']):
            raise CommandError('The fixture does not match the published synthetic reference.')

        project_values = {key: value for key, value in project_data.items() if key not in ('id', 'project_code')}
        project, _ = Project.objects.get_or_create(project_code=PROJECT_CODE, defaults={
            'id': project_id, **project_values,
        })
        project = Project.objects.select_for_update().get(pk=project.pk)
        if project.pk != project_id or not project.project_name.startswith(PROJECT_LABEL):
            raise CommandError(f'{PROJECT_CODE} is already used by a project outside this fixture.')
        if reset:
            for key, value in project_values.items():
                setattr(project, key, value)
            project.save(update_fields=[*project_values, 'updated_at'])

        report_defaults = {key: value for key, value in report_data.items() if key not in ('id', 'report_date')}
        report_date = report_data['report_date']
        conflict = DailyReport.objects.filter(project=project, report_date=report_date, is_current=True)
        existing = DailyReport.all_objects.filter(pk=report_id).first()
        if conflict.exclude(pk=report_id).exists() or (
            existing and (existing.project_id != project.pk or existing.report_date.isoformat() != report_date
                          or not existing.is_synthetic_reference)
        ):
            raise CommandError('The reference report conflicts with a report outside this fixture.')

        actor = self._fixture_actor(uuid5(project_id, 'fixture-actor'))
        save = 'update_or_create' if reset else 'get_or_create'
        report, _ = getattr(DailyReport.all_objects, save)(
            pk=report_id, project=project, report_date=report_date,
            defaults={
                **report_defaults, 'created_by': actor, 'shift': ReportShift.FULL,
                'is_synthetic_reference': True, 'is_deleted': False, 'deleted_at': None, 'is_current': True,
            },
        )
        if report.is_deleted or not report.is_current:
            raise CommandError('The synthetic report is inactive. Use --reset to restore it.')
        for shift in fixture['worked_shifts']:
            getattr(DailyReportWorkedShift.objects, save)(
                report=report, shift_id=shift['shift_id'],
                defaults={'actual_duration_hours': shift['actual_duration_hours']},
            )

        for section, model in (('activities', DailyReportActivity), ('labor', DailyReportLabor)):
            for index, row in enumerate(fixture[section], start=1):
                getattr(model.objects, save)(
                    report=report, pk=uuid5(report_id, f'{section}-{index}'),
                    defaults={**row, 'is_derived': True, 'is_deleted': False, 'deleted_at': None},
                )

        weather_id = uuid5(report_id, 'weather')
        if WeatherLog.objects.filter(project=project, log_date=report_date).exclude(pk=weather_id).exists():
            raise CommandError('The reference weather log conflicts with a log outside this fixture.')
        getattr(WeatherLog.all_objects, save)(
            pk=weather_id, project=project, log_date=report_date,
            defaults={**fixture['weather'], 'created_by': actor, 'is_deleted': False, 'deleted_at': None},
        )
        self.stdout.write(self.style.SUCCESS(f'Imported synthetic reference {reference["official_report_number"]}'))

    def _fixture_actor(self, actor_id):
        user_model = get_user_model()
        actor = user_model.objects.filter(username=ACTOR_USERNAME).first()
        if actor is None:
            actor = user_model.objects.create_user(
                pk=actor_id, username=ACTOR_USERNAME, full_name='Synthetic A.1 Fixture',
                is_active=False, status='inactive',
            )
        if actor.pk != actor_id or actor.is_active or actor.has_usable_password():
            raise CommandError('The synthetic fixture actor conflicts with an existing user.')
        return actor
