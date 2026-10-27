from django.db import migrations


def seed_catalogs(apps, schema_editor):
    from project_templates.labor_catalog_seeds import seed_default_catalogs_for_template

    ProjectTemplate = apps.get_model('project_templates', 'ProjectTemplate')
    ProjectReportingConfiguration = apps.get_model('project_templates', 'ProjectReportingConfiguration')
    ProjectReportingConfigurationLaborTitle = apps.get_model('project_templates', 'ProjectReportingConfigurationLaborTitle')

    catalogs = []
    for template in ProjectTemplate.objects.all():
        cat = seed_default_catalogs_for_template(template)
        if cat:
            catalogs.append(cat)

    default_cat = catalogs[0] if catalogs else None
    if default_cat is not None:
        for config in ProjectReportingConfiguration.objects.all():
            if not ProjectReportingConfigurationLaborTitle.objects.filter(configuration_id=config.id).exists():
                cat = None
                if config.source_template_id:
                    cat = default_cat.__class__.objects.filter(template_id=config.source_template_id).order_by('-created_at').first()
                cat = cat or default_cat
                for title in cat.titles.filter(active=True).order_by('display_order', 'id'):
                    ProjectReportingConfigurationLaborTitle.objects.create(
                        configuration_id=config.id,
                        title_code=title.title_code,
                        title_label=title.title_label,
                        title_label_fa=title.title_label_fa,
                        category=title.category,
                        display_order=title.display_order,
                        legacy_alias=title.legacy_alias,
                        source_catalog_version=cat.version_name,
                    )


def unseed_catalogs(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('project_templates', '0004_labor_catalog_and_rules'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_catalogs, unseed_catalogs),
    ]
