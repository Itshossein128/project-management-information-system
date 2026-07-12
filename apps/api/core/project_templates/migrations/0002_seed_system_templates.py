from django.db import migrations


def _create_wbs(template, nodes_spec, parent=None, level=1):
    ProjectTemplateWBS = nodes_spec['model']
    created = {}
    for order, item in enumerate(nodes_spec['items']):
        if len(item) == 3:
            code, name, children = item
        else:
            code, name = item[0], item[1]
            children = []
        node = ProjectTemplateWBS.objects.create(
            template=template,
            parent=parent,
            wbs_code=code,
            wbs_name=name,
            level=level,
            order=order,
        )
        created[code] = node
        if children:
            _create_wbs(template, {'model': ProjectTemplateWBS, 'items': children}, parent=node, level=level + 1)
    return created


RESIDENTIAL_WBS = [
    ('1', 'کارهای ابتدایی', [
        ('1.1', 'تسطیح و خاکبرداری', []),
        ('1.2', 'جانمایی و نقشه‌برداری', []),
    ]),
    ('2', 'سازه', [
        ('2.1', 'فونداسیون', []),
        ('2.2', 'اسکلت بتنی', []),
        ('2.3', 'سقف', []),
    ]),
    ('3', 'معماری', [
        ('3.1', 'دیوارچینی', []),
        ('3.2', 'نازک‌کاری', []),
        ('3.3', 'نماسازی', []),
    ]),
    ('4', 'تأسیسات مکانیکی', []),
    ('5', 'تأسیسات برقی', []),
    ('6', 'محوطه‌سازی', []),
]

ROAD_WBS = [
    ('1', 'مطالعات و برداشت', []),
    ('2', 'عملیات خاکی', [
        ('2.1', 'کانال‌کنی', []),
        ('2.2', 'خاکریزی', []),
        ('2.3', 'تراکم', []),
    ]),
    ('3', 'روسازی', [
        ('3.1', 'زیراساس', []),
        ('3.2', 'اساس', []),
        ('3.3', 'آسفالت', []),
    ]),
    ('4', 'ابنیه فنی', []),
    ('5', 'ایمنی و علائم', []),
]

EPC_WBS = [
    ('1', 'مهندسی (Engineering)', [
        ('1.1', 'طراحی پایه', []),
        ('1.2', 'طراحی تفصیلی', []),
        ('1.3', 'مدارک فروشنده', []),
    ]),
    ('2', 'تدارکات (Procurement)', [
        ('2.1', 'استعلام و ارزیابی', []),
        ('2.2', 'سفارش‌گذاری', []),
        ('2.3', 'حمل و نقل', []),
    ]),
    ('3', 'ساخت (Construction)', [
        ('3.1', 'سیویل و ساختمان', []),
        ('3.2', 'مکانیکال', []),
        ('3.3', 'الکتریکال', []),
        ('3.4', 'ابزار دقیق', []),
    ]),
    ('4', 'راه‌اندازی (Commissioning)', []),
]


def seed_templates(apps, schema_editor):
    ProjectTemplate = apps.get_model('project_templates', 'ProjectTemplate')
    ProjectTemplateWBS = apps.get_model('project_templates', 'ProjectTemplateWBS')

    specs = [
        ('پروژه مسکونی', 'residential', 'قالب استاندارد پروژه مسکونی و آپارتمانی', RESIDENTIAL_WBS),
        ('پروژه راهسازی', 'road', 'قالب استاندارد پروژه راهسازی', ROAD_WBS),
        ('پروژه EPC', 'epc', 'قالب پروژه EPC', EPC_WBS),
    ]
    for name, ptype, desc, wbs_items in specs:
        template, _ = ProjectTemplate.objects.get_or_create(
            template_name=name,
            defaults={
                'description': desc,
                'project_type': ptype,
                'is_system': True,
            },
        )
        if ProjectTemplateWBS.objects.filter(template=template).exists():
            continue
        _create_wbs(template, {'model': ProjectTemplateWBS, 'items': wbs_items})


def unseed(apps, schema_editor):
    ProjectTemplate = apps.get_model('project_templates', 'ProjectTemplate')
    ProjectTemplate.objects.filter(is_system=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('project_templates', '0001_customer_decisions'),
    ]

    operations = [
        migrations.RunPython(seed_templates, unseed),
    ]
