"""Seed live fast-track procurement alert and extend AlertType choices."""

from django.db import migrations, models


def seed_fast_track_rule(apps, schema_editor):
    AlertRule = apps.get_model('alerts', 'AlertRule')
    AlertRule.objects.get_or_create(
        project_id=None,
        alert_type='procurement_fast_track',
        defaults={
            'name': 'درخواست خرید فورس‌ماژور',
            'threshold': 0,
            'notify_roles': 'project_manager,hq_project_controller',
            'cooldown_hours': 24,
            'is_active': True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0006_alter_alertrule_alert_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertrule',
            name='alert_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('ipc_payment_overdue', 'IPC payment overdue'),
                    ('guarantee_expiring', 'Guarantee expiring'),
                    ('budget_overrun', 'Budget overrun'),
                    ('cash_gap_detected', 'Cash gap detected'),
                    ('low_stock', 'Low stock'),
                    ('activity_behind_schedule', 'Activity behind schedule'),
                    ('missing_daily_report', 'Missing daily report'),
                    ('daily_report_not_approved', 'Daily report not approved'),
                    ('baseline_not_set', 'Baseline not set'),
                    ('subcontractor_at_risk', 'Subcontractor at risk'),
                    ('subcontractor_score_low', 'Subcontractor score low'),
                    ('correspondence_response_due', 'Correspondence response due'),
                    ('sync_conflict_unresolved', 'Sync conflict unresolved'),
                    ('critical_path_delay', 'Critical path delay'),
                    ('ipc_approval_delayed', 'IPC approval delayed'),
                    ('procurement_overdue', 'Procurement overdue'),
                    ('procurement_fast_track', 'Procurement fast-track'),
                ],
                default='',
                max_length=60,
            ),
        ),
        migrations.RunPython(seed_fast_track_rule, migrations.RunPython.noop),
    ]
