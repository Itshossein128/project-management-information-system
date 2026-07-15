from django.db import migrations, models
import django.db.models.deletion


DEFAULT_RULES = [
    {
        'alert_type': 'ipc_payment_overdue',
        'name': 'تأخیر پرداخت صدور موقت',
        'threshold': 0,
        'notify_roles': 'project_manager,finance_manager',
        'cooldown_hours': 24,
    },
    {
        'alert_type': 'guarantee_expiring',
        'name': 'انقضای ضمانت‌نامه',
        'threshold': 30,
        'notify_roles': 'project_manager,finance_manager',
        'cooldown_hours': 168,
    },
    {
        'alert_type': 'budget_overrun',
        'name': 'تجاوز از بودجه',
        'threshold': 90,
        'notify_roles': 'project_manager,finance_manager',
        'cooldown_hours': 48,
    },
    {
        'alert_type': 'missing_daily_report',
        'name': 'گزارش روزانه ارسال نشده',
        'threshold': 1,
        'notify_roles': 'project_manager,site_supervisor',
        'cooldown_hours': 24,
    },
    {
        'alert_type': 'activity_behind_schedule',
        'name': 'تأخیر در فعالیت',
        'threshold': 10,
        'notify_roles': 'project_manager,planning_engineer',
        'cooldown_hours': 48,
    },
    {
        'alert_type': 'low_stock',
        'name': 'موجودی کم مصالح',
        'threshold': 0,
        'notify_roles': 'project_manager',
        'cooldown_hours': 24,
    },
    {
        'alert_type': 'subcontractor_at_risk',
        'name': 'پیمانکار در وضعیت ریسک',
        'threshold': 6,
        'notify_roles': 'project_manager',
        'cooldown_hours': 168,
    },
    {
        'alert_type': 'correspondence_response_due',
        'name': 'سررسید پاسخ مکاتبه',
        'threshold': 3,
        'notify_roles': 'project_manager,document_controller',
        'cooldown_hours': 24,
    },
]


def seed_default_rules(apps, schema_editor):
    AlertRule = apps.get_model('alerts', 'AlertRule')
    for rule in DEFAULT_RULES:
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
        ('alerts', '0002_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertrule',
            name='name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='alertrule',
            name='notify_roles',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='alertrule',
            name='cooldown_hours',
            field=models.PositiveIntegerField(default=24),
        ),
        migrations.AddField(
            model_name='alertrule',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alertrule',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alertlog',
            name='project',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='alert_logs',
                to='projects.project',
            ),
        ),
        migrations.AddField(
            model_name='alertlog',
            name='trigger_reference',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='alertlog',
            name='notifications_sent',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='alertlog',
            name='rule',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='log_entries',
                to='alerts.alertrule',
            ),
        ),
        migrations.RunPython(seed_default_rules, migrations.RunPython.noop),
    ]
