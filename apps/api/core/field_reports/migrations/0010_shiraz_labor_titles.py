from django.db import migrations

INDIRECT_TITLES = [
    'مدیرشعبه',
    'معاونت فنی شعبه',
    'سرپرست کنترل پروژه',
    'کنترل کیفیت شعبه',
    'مدیر مالی',
    'تدارکات',
    'مدیر پروژه',
    'سرپرست کارگاه',
    'معاونت کارگاه',
    'سرپرست دفتر فنی',
    'برنامه‌ریزی و کنترل پروژه',
    'کارشناس دفتر فنی',
    'سرپرست اجرا',
    'کارشناس اجرا',
    'حسابداری',
    'واحد مکانیک',
    'واحد برق',
    'اداری و مالی',
    'کارمند اداری',
    'کنترل کیفیت',
    'سرپرست ایمنی',
    'کارشناس ایمنی',
    'انباردار',
    'نقشه‌بردار',
    'نگهبان روز و شب',
    'خدمات',
    'تأسیسات',
    'مسئول ماشین‌آلات',
    'تکنسین اجرا',
    'فناوری اطلاعات',
    'سرپرست بچینگ',
    'آزمایشگاه',
    'مهمان',
]

DIRECT_TITLES = [
    'کارگر ساده',
    'کارگر ماهر',
    'بنا',
    'آرماتور بند و قالب بند',
    'اکیپ بتن‌ریزی',
    'جوشکار',
    'اکیپ حفاری',
    'سرویس‌کار',
    'متفرقه (تعمیرکار-برق‌کار)',
    'پیمانکار برق و تأسیسات',
    'پلاستر کار',
    'لوله‌کش تأسیسات',
    'نصاب تاور',
    'داربست‌بند',
    'نیروی انسانی ماشین‌آلات',
    'راننده بابکت',
    'راننده کامیون',
    'راننده لودر',
    'راننده بیل مکانیکی',
    'راننده تراک میکسر',
    'راننده غلتک',
    'راننده بیل بکهو',
    'راننده جرثقیل',
    'راننده تانکر آب',
    'راننده گریدر',
    'اپراتور پمپ بتن',
    'اپراتور بچینگ',
    'اپراتور باسکول',
    'کنترل‌چی عملیات خاکی',
    'راننده سواری',
    'اپراتور دستگاه حفاری',
    'اپراتور تاور',
]


def reseed_shiraz_titles(apps, schema_editor):
    LaborJobTitle = apps.get_model('field_reports', 'LaborJobTitle')
    LaborJobTitle.objects.all().delete()
    for order, title in enumerate(INDIRECT_TITLES, start=1):
        LaborJobTitle.objects.create(
            category='indirect', title=title, display_order=order,
        )
    for order, title in enumerate(DIRECT_TITLES, start=1):
        LaborJobTitle.objects.create(
            category='direct', title=title, display_order=order,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('field_reports', '0009_dailyreportactivity_photo_file'),
    ]

    operations = [
        migrations.RunPython(reseed_shiraz_titles, noop),
    ]
