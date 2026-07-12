from django.db import migrations

# NOTE: placeholder title lists. Replace with the exact 34 + 32 titles from the
# official Excel forms when available (counts intentionally match the spec).
INDIRECT_TITLES = [
    'مدیر پروژه', 'رئیس کارگاه', 'سرپرست کارگاه', 'مهندس عمران', 'مهندس معمار',
    'مهندس مکانیک', 'مهندس برق', 'مهندس ایمنی (HSE)', 'مهندس نقشه‌بردار',
    'مهندس کنترل پروژه', 'مهندس دفتر فنی', 'مهندس متره و برآورد', 'مهندس کیفیت (QC)',
    'کارشناس تدارکات', 'کارپرداز', 'انباردار', 'حسابدار', 'امور اداری',
    'مسئول کارگزینی', 'منشی', 'اپراتور کامپیوتر', 'راننده سبک', 'نگهبان', 'سرایدار',
    'آبدارچی', 'نظافتچی', 'آشپز', 'کمک آشپز', 'تدارکات‌چی', 'مسئول نقلیه',
    'تکنسین ایمنی', 'بهیار/امدادگر', 'مسئول انبار مرکزی', 'کنترل کیفیت مصالح',
]

DIRECT_TITLES = [
    'استادکار بنا', 'بنا', 'کمک بنا', 'آرماتوربند', 'کمک آرماتوربند', 'قالب‌بند',
    'کمک قالب‌بند', 'بتن‌ریز', 'ویبراتورچی', 'جوشکار', 'کمک جوشکار', 'لوله‌کش',
    'کمک لوله‌کش', 'برقکار', 'کمک برقکار', 'کاشی‌کار', 'سنگ‌کار', 'گچ‌کار', 'نقاش',
    'عایق‌کار', 'ایزوگام‌کار', 'داربست‌بند', 'کارگر ساده', 'کارگر ماهر',
    'راننده ماشین‌آلات سنگین', 'اپراتور جرثقیل', 'اپراتور لودر', 'اپراتور بیل مکانیکی',
    'راننده کامیون', 'مکانیک ماشین‌آلات', 'تاسیسات‌کار', 'اپراتور بچینگ',
]


def seed_titles(apps, schema_editor):
    LaborJobTitle = apps.get_model('field_reports', 'LaborJobTitle')
    for order, title in enumerate(INDIRECT_TITLES, start=1):
        LaborJobTitle.objects.get_or_create(
            category='indirect', title=title, defaults={'display_order': order},
        )
    for order, title in enumerate(DIRECT_TITLES, start=1):
        LaborJobTitle.objects.get_or_create(
            category='direct', title=title, defaults={'display_order': order},
        )


def unseed_titles(apps, schema_editor):
    LaborJobTitle = apps.get_model('field_reports', 'LaborJobTitle')
    LaborJobTitle.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_titles, unseed_titles),
    ]
