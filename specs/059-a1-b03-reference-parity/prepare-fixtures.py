"""Populate the B03 cases after seeding B01 in a disposable B03 database."""
from datetime import timedelta
from os import environ
from uuid import uuid5

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils import timezone

from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportDerivedSource,
    DailyReportEquipment,
    DailyReportWorkedShift,
    EquipmentStatus,
    InactivityReason,
    OwnershipType,
    ReportShift,
    ReportStatus,
    SiteStatus,
)
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity
from master_data.models import ProjectMember, ProjectMemberPermissionOverride


@transaction.atomic
def prepare():
    if not connection.settings_dict['NAME'].startswith('velora_b03_'):
        raise RuntimeError('Use an isolated velora_b03_ database.')

    reference = DailyReport.objects.get(
        project__project_code='SIM-A1-001', is_synthetic_reference=True,
        pk='fb9bcd42-a786-4b19-ba7b-1548c9526393',
    )
    if password := environ.get('B03_TEST_PASSWORD'):
        prepare_browser_membership(reference, password)
    print(f'normal {reference.report_date} {reference.pk}')
    for offset, case in enumerate(('inactive', 'measured-zero', 'unknown', 'three-shift', 'long-bilingual'), 1):
        report, _ = DailyReport.objects.get_or_create(
            pk=uuid5(reference.pk, f'b03-{case}'),
            project=reference.project,
            is_synthetic_reference=True,
            defaults={
                'created_by': reference.created_by,
                'report_date': reference.report_date + timedelta(days=offset),
                'contract_version': reference.contract_version,
                'presentation_profile_code': reference.presentation_profile_code,
                'shift': ReportShift.FULL,
                'weather_condition': 'clear',
                'site_status': SiteStatus.INACTIVE if case == 'inactive' else SiteStatus.ACTIVE,
                'inactivity_reason': InactivityReason.HOLIDAY if case == 'inactive' else '',
            },
        )
        if case in ('measured-zero', 'unknown'):
            measured = case == 'measured-zero'
            value = 0 if measured else None
            DailyReportEquipment.objects.get_or_create(
                pk=uuid5(report.pk, 'equipment'), report=report,
                defaults={
                    'equipment_name': f'Synthetic equipment ({case})',
                    'status': EquipmentStatus.ACTIVE,
                    'shift': ReportShift.DAY,
                    'ownership_type': OwnershipType.OWNED,
                    'productive_hours': value, 'idle_hours': value,
                },
            )
            unit_report, _ = DisciplineSubReport.objects.get_or_create(
                pk=uuid5(report.pk, 'buildings'),
                project=report.project, unit='buildings', report_date=report.report_date,
                defaults={'created_by': report.created_by, 'discipline': 'civil'},
            )
            DisciplineSubReportActivity.objects.get_or_create(
                pk=uuid5(unit_report.pk, 'activity'), sub_report=unit_report,
                defaults={
                    'row_number': 1, 'shift': 'shift_1', 'activity_description': case,
                    'quantity': value, 'execution_percentage': value, 'unit': 'm³',
                },
            )
        if case == 'three-shift':
            for shift_id, hours in enumerate(('8.50', '7.25', '6.00'), 1):
                DailyReportWorkedShift.objects.get_or_create(
                    report=report, shift_id=shift_id, defaults={'actual_duration_hours': hours},
                )
        if case == 'long-bilingual':
            for row in range(1, 57):
                DailyReportActivity.objects.get_or_create(
                    pk=uuid5(report.pk, str(row)), report=report,
                    defaults={
                        'activity_description': (
                            f'ردیف {row}، بتن‌ریزی و کنترل محل اجرای کار در بلوک آزمایشی\n'
                            'Synthetic bilingual activity with a long note for printed layout verification.'
                        ),
                        'shift': 'shift_1', 'quantity': row, 'quantity_measured': True, 'unit': 'm³',
                    },
                )
        print(f'{case} {report.report_date} {report.pk}')


def prepare_browser_membership(reference, password):
    from common.reporting_units import CANONICAL_SPECIALTY_UNITS
    from field_reports.services.weather_forecast import capture_report_weather

    actor, _ = get_user_model().objects.get_or_create(
        username='b03-browser-viewer', defaults={'full_name': 'Synthetic B03 Viewer', 'is_active': True},
    )
    actor.set_password(password)
    actor.save(update_fields=['password'])
    member, _ = ProjectMember.objects.get_or_create(project=reference.project, user=actor)
    for permission in ('view_project', 'view_reports', 'view_activities'):
        ProjectMemberPermissionOverride.objects.update_or_create(
            member=member, permission_codename=permission, defaults={'is_granted': True},
        )
    reference.prepared_by = actor
    reference.status = ReportStatus.APPROVED
    reference.approved_at = timezone.now()
    reference.export_weather_snapshot = capture_report_weather(reference, cache_only=True)
    reference.save(update_fields=['prepared_by', 'status', 'approved_at', 'export_weather_snapshot'])
    for unit in CANONICAL_SPECIALTY_UNITS:
        report, _ = DisciplineSubReport.objects.get_or_create(
            pk=uuid5(reference.pk, f'browser-{unit}'), project=reference.project, unit=unit,
            report_date=reference.report_date, defaults={'created_by': actor},
        )
        activity, _ = DisciplineSubReportActivity.objects.get_or_create(
            pk=uuid5(report.pk, 'activity'), sub_report=report,
            defaults={
                'row_number': 1, 'shift': 'shift_1', 'activity_description': f'{unit} B03 browser evidence',
                'quantity': 8, 'unit': 'm', 'execution_percentage': '45.5',
            },
        )
        if unit == 'buildings' and environ.get('B03_TEST_ATTACHMENTS') == '1':
            derived = reference.activities.order_by('pk').first()
            DailyReportDerivedSource.objects.get_or_create(
                daily_report=reference, derived_kind='activity', derived_row_id=str(derived.pk),
                source_report_id_snapshot=report.pk, source_row_kind='activity', source_row_id=str(activity.pk),
                defaults={'source_report': report, 'source_report_version': 1, 'source_unit': unit, 'ordinal': 0},
            )
            editor, _ = get_user_model().objects.get_or_create(
                username='b03-browser-editor', defaults={'full_name': 'Synthetic B03 Editor', 'is_active': True},
            )
            editor.set_password(password)
            editor.save(update_fields=['password'])
            editing_member, _ = ProjectMember.objects.get_or_create(project=reference.project, user=editor)
            for permission in ('view_project', 'view_reports', 'edit_reports'):
                ProjectMemberPermissionOverride.objects.update_or_create(
                    member=editing_member, permission_codename=permission, defaults={'is_granted': True},
                )


prepare()
