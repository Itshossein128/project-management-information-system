"""ReportLab PDF export for daily reports (RTL, Persian).

Persian text is shaped with ``arabic_reshaper`` + ``python-bidi`` when those
packages are installed, and rendered with a Persian TTF (Vazirmatn) when one is
available on disk. Everything degrades gracefully so a PDF is always produced.
"""
from __future__ import annotations

import io
import os
from xml.sax.saxutils import escape

from django.conf import settings
from typing import Tuple
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from common.jalali import gregorian_to_jalali, gregorian_to_jalali_datetime, persian_day_of_week

try:  # optional shaping
    import arabic_reshaper
    from bidi.algorithm import get_display

    _SHAPING = True
except Exception:  # noqa: BLE001
    _SHAPING = False

_FONT_NAME = 'Helvetica'
_FONT_READY = False
_INCIDENT_LABELS = {
    'safety': 'ایمنی', 'quality': 'کیفیت', 'environmental': 'محیط زیست',
    'stoppage': 'توقف کار', 'visitor': 'بازدیدکننده', 'site_instruction': 'دستور کارگاهی',
    'barrier': 'مانع', 'issue': 'مسئله',
}
_SEVERITY_LABELS = {'minor': 'جزئی', 'moderate': 'متوسط', 'major': 'شدید'}


def _register_font() -> str:
    global _FONT_NAME, _FONT_READY
    if _FONT_READY:
        return _FONT_NAME
    _FONT_READY = True
    candidates = [
        getattr(settings, 'VELORA_PDF_FONT_PATH', None),
        getattr(settings, 'IPCAS_PDF_FONT_PATH', None),
        os.environ.get('VELORA_PDF_FONT_PATH'),
        os.environ.get('IPCAS_PDF_FONT_PATH'),
        os.path.join(os.path.dirname(__file__), 'fonts', 'Vazirmatn.ttf'),
        '/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        # Fallbacks with Arabic/Persian glyph coverage.
        '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('VeloraFa', path))
                _FONT_NAME = 'VeloraFa'
                break
            except Exception:  # noqa: BLE001
                continue
    return _FONT_NAME


def _fa(text) -> str:
    if text is None:
        return ''
    text = str(text)
    if _SHAPING and text:
        try:
            return get_display(arabic_reshaper.reshape(text))
        except Exception:  # noqa: BLE001
            return text
    return text


def generate_daily_report_pdf(report) -> Tuple[bytes, str]:
    font = _register_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28,
    )

    base = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'FaTitle', parent=base['Title'], fontName=font, alignment=TA_RIGHT,
    )
    head_style = ParagraphStyle(
        'FaHead', parent=base['Heading3'], fontName=font, alignment=TA_RIGHT,
        keepWithNext=True,
    )
    normal = ParagraphStyle('FaNormal', parent=base['Normal'], fontName=font, alignment=TA_RIGHT)

    report_date = report.report_date
    if isinstance(report_date, str):
        from datetime import date
        try:
            report_date = date.fromisoformat(report_date)
        except ValueError:
            pass
    jalali = gregorian_to_jalali(report_date) if report_date else ''
    dow = persian_day_of_week(report_date) if report_date else ''

    story = [
        Paragraph(_fa(f'گزارش روزانه — {jalali} ({dow})'), title_style),
        Paragraph(_fa(f'وضعیت: {report.get_status_display()}'), head_style),
        Spacer(1, 8),
    ]

    weather = report.get_weather_condition_display() if report.weather_condition else '—'
    status_label = 'قفل‌شده' if report.status == 'approved' else report.get_status_display()
    site_status_label = report.get_site_status_display()
    if report.site_status == 'inactive' and report.inactivity_reason:
        reason_label = report.get_inactivity_reason_display()
        site_status_label = f'{site_status_label} ({reason_label})'

    header_rows = [
        ['پروژه', report.project.project_name],
        ['شماره قرارداد', report.project.contract_number or '—'],
        ['کارفرما', report.project.employer or '—'],
        ['مشاور', report.project.consultant or '—'],
        ['شیفت گزارش', report.get_shift_display()],
        ['وضعیت گزارش', status_label],
        ['محل / جبهه', report.work_front or '—'],
        ['وضعیت کارگاه', site_status_label],
        ['وضعیت جوی', weather],
        ['حداکثر دما', str(report.temp_max) if report.temp_max is not None else '—'],
        ['حداقل دما', str(report.temp_min) if report.temp_min is not None else '—'],
        ['تهیه‌کننده', _full_name(report.prepared_by)],
        ['تأییدکننده', _full_name(report.approved_by)],
        ['توضیحات و اثرات شرایط جوی', report.weather_impact_notes or ''],
    ]
    if report.is_auto_summary:
        from field_reports.services.daily_report_aggregation import build_aggregation_meta

        aggregation = build_aggregation_meta(report.project_id, report_date, report)
        completeness = aggregation['completeness']
        state = completeness['state']
        if state == 'complete':
            completeness_text = 'کامل: همه واحدهای مورد انتظار گزارش دارند.'
        elif state == 'configuration_incomplete':
            completeness_text = 'نامشخص: پیکربندی واحدهای مورد انتظار ثبت نشده است.'
        else:
            labels = {
                'buildings': 'ابنیه', 'electrical': 'تأسیسات برقی',
                'mechanical': 'تأسیسات مکانیکی', 'machinery': 'ماشین‌آلات',
                'warehouse': 'انبار', 'security': 'حراست و ایمنی',
            }
            missing = '، '.join(labels.get(unit, unit) for unit in completeness['missing_units']) or 'نامشخص'
            completeness_text = f'ناقص: واحدهای فاقد گزارش: {missing}.\nبخش‌های خالی لزوماً به معنای عدم وقوع نیست.'
        completeness_text += '\nاین وضعیت فعلی واحدهاست و ممکن است با داده‌های آخرین تجمیع متفاوت باشد.'
        comparison = aggregation.get('snapshot_source_comparison', 'unknown')
        if comparison == 'changed':
            source_text = 'منابع پس از آخرین تجمیع تغییر کرده‌اند.\nارقام این خروجی مربوط به نسخه ذخیره‌شده‌اند.'
        elif comparison == 'matching_fingerprint':
            source_text = 'منابع تحت پوشش اثرانگشت تغییر نکرده‌اند.\nوابستگی‌های بیرونی جداگانه بررسی نشده‌اند.'
        else:
            source_text = 'وضعیت تغییر منابع نسبت به آخرین تجمیع نامشخص است.'
        header_rows.insert(0, ['مقایسه منابع', source_text])
        header_rows.insert(0, ['زمان آخرین تجمیع', gregorian_to_jalali_datetime(report.aggregated_at) or 'ثبت نشده'])
        header_rows.insert(0, ['وضعیت فعلی واحدها', completeness_text])
    story.append(_kv_table(header_rows, font))
    story.append(Spacer(1, 12))

    story += _section(
        'فعالیت‌های اجرایی',
        ['شرح فعالیت و توضیحات', 'شیفت', 'پیمانکار / اکیپ', 'نفر', 'موقعیت', 'مقدار', 'واحد'],
        [
            [
                '\n'.join(filter(None, [r.activity_description, r.notes])), r.get_shift_display(),
                ' / '.join(filter(None, [
                    r.subcontractor_name or (r.contractor_ref.name if r.contractor_ref else ''),
                    r.crew_name,
                ])) or '—',
                r.headcount if r.headcount is not None else '—',
                ' / '.join(filter(None, [r.parcel, r.zone, r.block, r.floor, r.location_detail])) or '—',
                r.quantity if r.quantity_measured and r.quantity is not None else '—', r.unit or '—',
            ]
            for r in report.activities.filter(is_deleted=False).select_related('contractor_ref')
        ],
        head_style, normal, font, [115, 44, 100, 35, 115, 55, 45],
    )

    story += _section(
        'نیروی انسانی',
        ['دسته', 'عنوان شغلی', 'شیفت ۱', 'شیفت ۲', 'شیفت ۳', 'مرخصی' if report.is_auto_summary else 'مرخصی / غیبت', 'جمع'],
        [
            [
                r.get_labor_category_display(), r.custom_title or r.job_title,
                r.shift_1_count, r.shift_2_count, r.shift_3_count,
                r.absence_count if r.absence_count is not None else '—',
                r.total_count,
            ]
            for r in report.labor_entries.filter(is_deleted=False)
        ],
        head_style, normal, font, [60, 120, 40, 40, 40, 40, 40],
    )

    story += _section(
        'ماشین‌آلات',
        ['دستگاه', 'شیفت', 'وضعیت', 'مالکیت', 'کارکرد'],
        [
            [
                r.equipment_name, r.get_shift_display(), r.get_status_display(),
                r.get_ownership_type_display(),
                r.productive_hours if r.productive_hours is not None else '—',
            ]
            for r in report.equipment_entries.filter(is_deleted=False)
        ],
        head_style, normal, font, [140, 60, 70, 70, 60],
    )

    story += _section(
        'وضعیت ماشین‌آلات تجمیعی',
        ['نوع دستگاه', 'کل', 'فعال', 'آماده', 'غیرفعال', 'در تعمیر', 'کارکرد'],
        [
            [r.equipment_type, r.status_total, r.status_active, r.status_ready,
             r.status_inactive, r.status_under_repair,
             r.operating_hours if r.operating_hours is not None else '—']
            for r in report.machinery_rows.filter(is_deleted=False)
        ],
        head_style, normal, font, [150, 45, 50, 50, 60, 60, 65],
    )

    story += _section(
        'مصالح',
        ['شرح مصالح', 'نوع و وضعیت سند', 'مقدار', 'واحد', 'محل مصرف'],
        [
            [
                r.material_description,
                _material_status_label(r),
                r.quantity,
                r.unit,
                r.consumption_location or '—',
            ]
            for r in report.material_entries.filter(is_deleted=False)
        ],
        head_style, normal, font, [135, 145, 55, 45, 100],
    )

    story += _section(
        'بتن‌ریزی',
        ['شرح', 'حجم (م³)', 'قطعه', 'بلوک', 'طبقه'],
        [
            [r.concrete_description, r.volume_m3, r.zone or '—', r.block or '—', r.floor or '—']
            for r in report.concrete_logs.filter(is_deleted=False)
        ],
        head_style, normal, font, [160, 70, 60, 60, 60],
    )

    story += _section(
        'فعالیت‌های عمومی کارگاه',
        ['شرح فعالیت', 'محل', 'مقدار', 'واحد', 'توضیحات'],
        [[r.activity_description, r.location or '—',
          r.quantity if r.quantity is not None else '—', r.unit or '—', r.notes or '—']
         for r in report.general_activities.filter(is_deleted=False)],
        head_style, normal, font, [140, 95, 50, 50, 150],
    )

    story += _section(
        'بازدیدها', ['شرح'],
        [[r.text] for r in report.visits.filter(is_deleted=False)],
        head_style, normal, font, [480],
    )

    story += _section(
        'حوادث و موانع',
        ['نوع', 'شرح', 'مسئول پیگیری', 'موعد', 'اقدام اصلاحی', 'شدت'],
        [
            [
                _INCIDENT_LABELS.get(r.incident_type, r.get_incident_type_display()),
                r.description,
                r.follow_up_owner_name or _full_name(r.follow_up_owner_user),
                gregorian_to_jalali(r.due_date) if r.due_date else '—',
                r.corrective_action or '—',
                _SEVERITY_LABELS.get(r.severity, r.get_severity_display()) if r.severity else '—',
            ]
            for r in report.incidents.filter(is_deleted=False).select_related('follow_up_owner_user')
        ],
        head_style, normal, font, [50, 110, 75, 70, 105, 55],
    )

    if report.general_notes:
        story.append(Paragraph(_fa('توضیحات کلی'), head_style))
        story.append(_text_paragraph(report.general_notes, normal))
    if report.management_opinion:
        story.append(Paragraph(_fa('نظر مدیریت'), head_style))
        story.append(_text_paragraph(report.management_opinion, normal))

    # Concluding 3-tier digital signatures block
    story.append(Spacer(1, 14))
    story.append(_signatures_block(report, font))

    # Watermark for unapproved / draft reports
    is_approved = getattr(report, 'status', '') == 'approved'
    if not is_approved:
        watermark_fn = _make_watermark('پیش‌نویس — غیرقابل استناد رسمی (DRAFT)', font)
        doc.build(story, onFirstPage=watermark_fn, onLaterPages=watermark_fn)
    else:
        doc.build(story)

    pdf_bytes = buf.getvalue()

    shift_str = report.shift or 'full'
    date_str = jalali.replace('/', '-') if jalali else str(report.report_date)
    filename = f'daily-report-{date_str}-{shift_str}.pdf'
    return pdf_bytes, filename


def generate_report_audit_hash(report) -> str:
    import hashlib
    raw = (
        f"{report.id}:{getattr(report, 'lineage_id', '')}:{report.report_date}:"
        f"{report.shift}:{report.status}:{getattr(report, 'approved_at', '')}:"
        f"{getattr(report, 'approved_by_id', '')}"
    )
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16].upper()


def _make_watermark(text: str, font_name: str):
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFont(font_name, 28)
        canvas.setFillColor(colors.Color(0.75, 0.75, 0.75, alpha=0.25))
        canvas.translate(A4[0] / 2.0, A4[1] / 2.0)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, _fa(text))
        canvas.restoreState()
    return _draw


def _signatures_block(report, font: str) -> Table:
    audit_hash = generate_report_audit_hash(report)
    box_style = ParagraphStyle('SigBox', fontName=font, fontSize=8, alignment=TA_RIGHT, leading=11)
    title_style = ParagraphStyle('SigTitle', fontName=font, fontSize=8, fontBold=True, alignment=TA_RIGHT, leading=12)

    # Box 1: Preparer / Submitter
    prep_user = getattr(report, 'submitted_by', None) or getattr(report, 'prepared_by', None)
    prep_name = _full_name(prep_user)
    prep_time = ''
    sub_at = getattr(report, 'submitted_at', None)
    if sub_at:
        j_d = gregorian_to_jalali(sub_at.date())
        prep_time = f'{j_d} {sub_at.strftime("%H:%M")}'
    elif getattr(report, 'created_at', None):
        c_at = report.created_at
        j_d = gregorian_to_jalali(c_at.date())
        prep_time = f'{j_d} {c_at.strftime("%H:%M")}'

    b1_content = [
        Paragraph(_fa('<b>تنظیم‌کننده</b>'), title_style),
        Spacer(1, 3),
        _text_paragraph(f'نام: {prep_name}', box_style),
        Paragraph(_fa(f'زمان ثبت: {prep_time or "—"}'), box_style),
    ]

    # Box 2: Reviewer
    rev_by = getattr(report, 'reviewed_by', None)
    rev_at = getattr(report, 'reviewed_at', None)
    if rev_by or rev_at:
        rev_name = _full_name(rev_by)
        rev_time = ''
        if rev_at:
            j_d = gregorian_to_jalali(rev_at.date())
            rev_time = f'{j_d} {rev_at.strftime("%H:%M")}'
        b2_content = [
            Paragraph(_fa('<b>بررسی‌کننده</b>'), title_style),
            Spacer(1, 3),
            _text_paragraph(f'نام: {rev_name}', box_style),
            Paragraph(_fa(f'زمان بررسی: {rev_time or "—"}'), box_style),
        ]
    elif getattr(report, 'status', '') == 'approved':
        b2_content = [
            Paragraph(_fa('<b>بررسی‌کننده</b>'), title_style),
            Spacer(1, 3),
            Paragraph(_fa('بدون نیاز به بررسی دفتر فنی / تأیید مستقیم'), box_style),
        ]
    else:
        b2_content = [
            Paragraph(_fa('<b>بررسی‌کننده</b>'), title_style),
            Spacer(1, 3),
            Paragraph(_fa('هنوز بررسی نشده است'), box_style),
        ]

    # Box 3: Approver
    app_by = getattr(report, 'approved_by', None)
    app_at = getattr(report, 'approved_at', None)
    app_name = _full_name(app_by)
    app_time = ''
    if app_at:
        j_d = gregorian_to_jalali(app_at.date())
        app_time = f'{j_d} {app_at.strftime("%H:%M")}'
    b3_content = [
        Paragraph(_fa('<b>تأییدکننده</b>'), title_style),
        Spacer(1, 3),
        _text_paragraph(f'نام: {app_name}', box_style),
        Paragraph(_fa(f'زمان تأیید: {app_time or "—"}'), box_style),
        Spacer(1, 3),
        Paragraph(_fa(f'شناسه رهگیری: {audit_hash}'), box_style),
    ]

    data = [[b1_content, b2_content, b3_content]]
    table = Table(data, colWidths=[175, 175, 189])
    table.setStyle(
        TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2F5597')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ])
    )
    return table


def _full_name(user) -> str:
    if not user:
        return '—'
    return (user.get_full_name() or user.username) if hasattr(user, 'get_full_name') else str(user)


def _kv_table(rows, font) -> Table:
    val_style = ParagraphStyle('KVVal', fontName=font, fontSize=9, alignment=TA_RIGHT, leading=12)
    data = []
    for row in rows:
        label = row[0]
        val = row[1] if len(row) > 1 else ''
        shaped_label = _fa(label)
        if isinstance(val, str) and (len(str(val)) > 30 or '\n' in str(val)):
            val_cell = _text_paragraph(val, val_style, max_width=308)
        else:
            val_cell = _fa(val) if val else ''
        data.append([shaped_label, val_cell])
    table = Table(data, colWidths=[120, 320])
    table.setStyle(
        TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eef2f7')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
    )
    return table


def _is_fa(value) -> bool:
    # header_rows are already passed through _fa; guard against double-shaping.
    return False


def _material_status_label(row) -> str:
    """Document resolution does not itself mean the reported quantity matches."""
    if row.transaction_type == 'receipt':
        if row.receipt_resolved is not True:
            return 'رسید بدون سند قابل تطبیق'
        label = 'رسید؛ سند انبار یافت شد'
        if row.reconciliation_status == 'match':
            return f'{label}؛ مقدار مطابق'
        if row.reconciliation_status == 'mismatch':
            return f'{label}؛ مقدار مغایر'
        return label
    if row.transaction_type == 'issue':
        return 'مصرف / خروج'
    return row.get_transaction_type_display() or 'نوع نامشخص'


def _wrap_logical_lines(value, style, max_width):
    """Wrap logical text before bidi reordering so lines retain reading order."""
    result = []
    for paragraph in str(value if value is not None else '').split('\n'):
        current = ''
        for word in paragraph.split():
            candidate = f'{current} {word}' if current else word
            if current and pdfmetrics.stringWidth(_fa(candidate), style.fontName, style.fontSize) > max_width:
                result.append(current)
                current = word
            else:
                current = candidate
        result.append(current)
    return result


def _text_paragraph(value, style, max_width=None):
    # User content is plain text, not ReportLab markup. Break logical lines
    # before shaping, otherwise bidi-reordered prose wraps in reverse order.
    lines = (_wrap_logical_lines(value, style, max_width) if max_width else
             str(value if value is not None else '').splitlines() or [''])
    return Paragraph('<br/>'.join(escape(_fa(line)) for line in lines), style)


def _section(title, headers, rows, head_style, normal, font, col_widths):
    story = [Spacer(1, 8), Paragraph(_fa(title), head_style)]
    cell_style = ParagraphStyle(
        'DailyPdfCell', fontName=font, fontSize=8, leading=10, alignment=TA_RIGHT,
        splitLongWords=True,
    )
    data = [[_text_paragraph(h, cell_style, max_width=width - 12) for h, width in zip(headers, col_widths)]]
    for row in rows:
        data.append([_text_paragraph(cell, cell_style, max_width=width - 12) for cell, width in zip(row, col_widths)])
    if not rows:
        data.append([_text_paragraph('موردی ثبت نشده است.', cell_style)] + [''] * (len(headers) - 1))
    table = Table(data, repeatRows=1, colWidths=col_widths, splitInRow=1)
    table.setStyle(
        TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef5')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ])
    )
    if not rows and len(headers) > 1:
        table.setStyle(TableStyle([('SPAN', (0, 1), (-1, 1))]))
    story.append(table)
    return story
