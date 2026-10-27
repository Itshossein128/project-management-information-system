"""Default labor title catalog seeds from legacy migration evidence (feature 033, T072).

Evidence sources:
- 0002_seed_labor_titles.py: 34 indirect + 32 direct (v1 standard)
- 0010_shiraz_labor_titles.py: 33 indirect + 32 direct (v2 shiraz)
"""
from __future__ import annotations

import re


INDIRECT_TITLES_0002 = [
    'مدیر پروژه', 'رئیس کارگاه', 'سرپرست کارگاه', 'مهندس عمران', 'مهندس معمار',
    'مهندس مکانیک', 'مهندس برق', 'مهندس ایمنی (HSE)', 'مهندس نقشه‌بردار',
    'مهندس کنترل پروژه', 'مهندس دفتر فنی', 'مهندس متره و برآورد', 'مهندس کیفیت (QC)',
    'کارشناس تدارکات', 'کارپرداز', 'انباردار', 'حسابدار', 'امور اداری',
    'مسئول کارگزینی', 'منشی', 'اپراتور کامپیوتر', 'راننده سبک', 'نگهبان', 'سرایدار',
    'آبدارچی', 'نظافتچی', 'آشپز', 'کمک آشپز', 'تدارکات‌چی', 'مسئول نقلیه',
    'تکنسین ایمنی', 'بهیار/امدادگر', 'مسئول انبار مرکزی', 'کنترل کیفیت مصالح',
]

DIRECT_TITLES_0002 = [
    'استادکار بنا', 'بنا', 'کمک بنا', 'آرماتوربند', 'کمک آرماتوربند', 'قالب‌بند',
    'کمک قالب‌بند', 'بتن‌ریز', 'ویبراتورچی', 'جوشکار', 'کمک جوشکار', 'لوله‌کش',
    'کمک لوله‌کش', 'برقکار', 'کمک برقکار', 'کاشی‌کار', 'سنگ‌کار', 'گچ‌کار', 'نقاش',
    'عایق‌کار', 'ایزوگام‌کار', 'داربست‌بند', 'کارگر ساده', 'کارگر ماهر',
    'راننده ماشین‌آلات سنگین', 'اپراتور جرثقیل', 'اپراتور لودر', 'اپراتور بیل مکانیکی',
    'راننده کامیون', 'مکانیک ماشین‌آلات', 'تاسیسات‌کار', 'اپراتور بچینگ',
]

INDIRECT_TITLES_0010 = [
    'مدیرشعبه', 'معاونت فنی شعبه', 'سرپرست کنترل پروژه', 'کنترل کیفیت شعبه',
    'مدیر مالی', 'تدارکات', 'مدیر پروژه', 'سرپرست کارگاه', 'معاونت کارگاه',
    'سرپرست دفتر فنی', 'برنامه‌ریزی و کنترل پروژه', 'کارشناس دفتر فنی',
    'سرپرست اجرا', 'کارشناس اجرا', 'حسابداری', 'واحد مکانیک', 'واحد برق',
    'اداری و مالی', 'کارمند اداری', 'کنترل کیفیت', 'سرپرست ایمنی',
    'کارشناس ایمنی', 'انباردار', 'نقشه‌بردار', 'نگهبان روز و شب', 'خدمات',
    'تأسیسات', 'مسئول ماشین‌آلات', 'تکنسین اجرا', 'فناوری اطلاعات',
    'سرپرست بچینگ', 'آزمایشگاه', 'مهمان',
]

DIRECT_TITLES_0010 = [
    'کارگر ساده', 'کارگر ماهر', 'بنا', 'آرماتور بند و قالب بند', 'اکیپ بتن‌ریزی',
    'جوشکار', 'اکیپ حفاری', 'سرویس‌کار', 'متفرقه (تعمیرکار-برق‌کار)',
    'پیمانکار برق و تأسیسات', 'پلاستر کار', 'لوله‌کش تأسیسات', 'نصاب تاور',
    'داربست‌بند', 'نیروی انسانی ماشین‌آلات', 'راننده بابکت', 'راننده کامیون',
    'راننده لودر', 'راننده بیل مکانیکی', 'راننده تراک میکسر', 'راننده غلتک',
    'راننده بیل بکهو', 'راننده جرثقیل', 'راننده تانکر آب', 'راننده گریدر',
    'اپراتور پمپ بتن', 'اپراتور بچینگ', 'اپراتور باسکول', 'کنترل‌چی عملیات خاکی',
    'راننده سواری', 'اپراتور دستگاه حفاری', 'اپراتور تاور',
]


LEGACY_0002_TO_0010 = {
    'کارشناس اجرا': ['مهندس عمران'],
    'کارشناس دفتر فنی': ['مهندس معمار', 'مهندس متره و برآورد'],
    'واحد مکانیک': ['مهندس مکانیک'],
    'واحد برق': ['مهندس برق'],
    'کارشناس ایمنی': ['مهندس ایمنی (HSE)', 'تکنسین ایمنی'],
    'نقشه‌بردار': ['مهندس نقشه‌بردار'],
    'برنامه‌ریزی و کنترل پروژه': ['مهندس کنترل پروژه'],
    'سرپرست دفتر فنی': ['مهندس دفتر فنی'],
    'کنترل کیفیت': ['مهندس کیفیت (QC)', 'کنترل کیفیت مصالح'],
    'تدارکات': ['کارشناس تدارکات', 'کارپرداز'],
    'مسئول ماشین‌آلات': ['مسئول نقلیه'],
    'انباردار': ['مسئول انبار مرکزی'],
    'آرماتور بند و قالب بند': ['آرماتوربند', 'قالب‌بند', 'کمک آرماتوربند', 'کمک قالب‌بند'],
    'اکیپ بتن‌ریزی': ['بتن‌ریز', 'ویبراتورچی'],
    'لوله‌کش تأسیسات': ['لوله‌کش', 'کمک لوله‌کش'],
    'پیمانکار برق و تأسیسات': ['برقکار', 'کمک برقکار'],
    'تأسیسات': ['تاسیسات‌کار'],
    'نیروی انسانی ماشین‌آلات': ['راننده ماشین‌آلات سنگین'],
}


def _slugify_code(prefix: str, idx: int) -> str:
    return f"{prefix}_{idx:02d}"


def build_titles_spec(
    indirect_list: list[str],
    direct_list: list[str],
    alias_map: dict[str, list[str]] | None = None,
) -> list[dict]:
    titles = []
    for idx, title_fa in enumerate(indirect_list, start=1):
        extra = alias_map.get(title_fa, []) if alias_map else []
        aliases = [title_fa] + [a for a in extra if a != title_fa]
        titles.append({
            'title_code': _slugify_code('ind', idx),
            'title_label': title_fa,
            'title_label_fa': title_fa,
            'category': 'indirect',
            'display_order': idx,
            'active': True,
            'legacy_alias': ', '.join(aliases),
            'project_specific': False,
        })
    for idx, title_fa in enumerate(direct_list, start=1):
        extra = alias_map.get(title_fa, []) if alias_map else []
        aliases = [title_fa] + [a for a in extra if a != title_fa]
        titles.append({
            'title_code': _slugify_code('dir', idx),
            'title_label': title_fa,
            'title_label_fa': title_fa,
            'category': 'direct',
            'display_order': idx,
            'active': True,
            'legacy_alias': ', '.join(aliases),
            'project_specific': False,
        })
    return titles


def seed_default_catalogs_for_template(template):
    """Seed both v1 (34/32) and v2 (33/32) catalogs for a project template."""
    from project_templates.models import LaborTitleCatalog, LaborTitleCatalogTitle

    template_id = getattr(template, 'id', template)

    # 1. Version 1: 34/32 standard
    v1_catalog, created1 = LaborTitleCatalog.objects.get_or_create(
        template_id=template_id,
        version_name='v1-standard',
        defaults={'notes': '34/32 shape from 0002_seed_labor_titles.py'},
    )
    v1_titles = build_titles_spec(INDIRECT_TITLES_0002, DIRECT_TITLES_0002)
    for t in v1_titles:
        LaborTitleCatalogTitle.objects.update_or_create(
            catalog=v1_catalog,
            title_code=t['title_code'],
            defaults=t,
        )

    # 2. Version 2: 33/32 shiraz (with legacy aliases to 0002 titles)
    v2_catalog, created2 = LaborTitleCatalog.objects.get_or_create(
        template_id=template_id,
        version_name='v2-shiraz',
        defaults={'notes': '33/32 shape from 0010_shiraz_labor_titles.py'},
    )
    v2_titles = build_titles_spec(
        INDIRECT_TITLES_0010, DIRECT_TITLES_0010, alias_map=LEGACY_0002_TO_0010,
    )
    for t in v2_titles:
        LaborTitleCatalogTitle.objects.update_or_create(
            catalog=v2_catalog,
            title_code=t['title_code'],
            defaults=t,
        )

    return v2_catalog


def seed_default_catalogs_for_owner(*, template=None, project=None):
    if template is not None:
        return seed_default_catalogs_for_template(template)
    from project_templates.models import ProjectTemplate
    sys_tmpl = ProjectTemplate.objects.filter(is_system=True).first()
    if sys_tmpl is None:
        sys_tmpl = ProjectTemplate.objects.first()
    if sys_tmpl is not None:
        return seed_default_catalogs_for_template(sys_tmpl)
    return None

