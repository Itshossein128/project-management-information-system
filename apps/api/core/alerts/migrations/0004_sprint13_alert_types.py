"""Seed Sprint 13 alert rule types (critical path, IPC approval, procurement)."""

from django.db import migrations


NEW_RULES = [
    {
        'alert_type': 'critical_path_delay',
        'name': 'تأخیر مسیر بحرانی',
        'threshold': 5,
        'notify_roles': 'project_manager,planning_engineer',
        'cooldown_hours': 48,
    },
    {
        'alert_type': 'ipc_approval_delayed',
        'name': 'تأخیر تأیید صدور موقت',
        'threshold': 7,
        'notify_roles': 'project_manager,finance_manager',
        'cooldown_hours': 48,
    },
    {
        'alert_type': 'procurement_overdue',
        'name': 'تأخیر تأمین و خرید',
        'threshold': 0,
        'notify_roles': 'project_manager',
        'cooldown_hours': 24,
    },
]


def seed_sprint13_rules(apps, schema_editor):
    AlertRule = apps.get_model('alerts', 'AlertRule')
    for rule in NEW_RULES:
        AlertRule.objects.get_or_create(
            project_id=None,
            alert_type=rule['alert_type'],
            defaults={
                'name': rule['name'],
                'threshold': rule['threshold'],
                'notify_roles': rule['notify_roles'],
                'cooldown_hours': rule['cooldown_hours'],
                'is_active': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0003_alert_engine_fields'),
    ]

    operations = [
        migrations.RunPython(seed_sprint13_rules, migrations.RunPython.noop),
    ]
