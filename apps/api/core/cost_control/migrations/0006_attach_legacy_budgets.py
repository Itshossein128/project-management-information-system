"""Attach orphan Budget rows to a synthetic BudgetVersion per project."""

from django.conf import settings
from django.db import migrations


def attach_legacy_budgets(apps, schema_editor):
    Budget = apps.get_model('cost_control', 'Budget')
    BudgetVersion = apps.get_model('cost_control', 'BudgetVersion')
    Project = apps.get_model('projects', 'Project')
    User = apps.get_model(settings.AUTH_USER_MODEL)

    project_ids = (
        Budget.objects.filter(version__isnull=True, is_deleted=False)
        .values_list('project_id', flat=True)
        .distinct()
    )
    fallback_user = User.objects.order_by('pk').first()
    for project_id in project_ids:
        project = Project.objects.filter(pk=project_id).first()
        if not project:
            continue
        sample = Budget.objects.filter(project_id=project_id).order_by('created_at').first()
        creator = getattr(sample, 'created_by_id', None) or (fallback_user.pk if fallback_user else None)
        if not creator:
            continue
        approved = bool(getattr(project, 'budget_approved_at', None))
        version = BudgetVersion.objects.create(
            project_id=project_id,
            kind='approved' if approved else 'initial',
            status='approved' if approved else 'draft',
            version_number=1,
            name='Migrated legacy budget',
            currency=getattr(project, 'currency', None) or 'IRR',
            notes='Auto-created during multi-level budget migration',
            is_control=approved,
            created_by_id=creator,
            updated_by_id=creator,
        )
        Budget.objects.filter(project_id=project_id, version__isnull=True).update(
            version_id=version.id,
            level='wbs',
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cost_control', '0005_multi_level_budget'),
    ]

    operations = [
        migrations.RunPython(attach_legacy_budgets, noop_reverse),
    ]
