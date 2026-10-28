"""ReportLab PDF export for daily reports (RTL, Persian).

Persian text is shaped with ``arabic_reshaper`` + ``python-bidi`` when those
packages are installed, and rendered with a Persian TTF (Vazirmatn) when one is
available on disk. Everything degrades gracefully so a PDF is always produced.
"""
from __future__ import annotations

import io
import os

from django.conf import settings
from typing import Tuple
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from common.jalali import gregorian_to_jalali, persian_day_of_week

try:  # optional shaping
    import arabic_reshaper
    from bidi.algorithm import get_display

    _SHAPING = True
except Exception:  # noqa: BLE001
    _SHAPING = False

_FONT_NAME = 'Helvetica'
_FONT_READY = False


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
    story.append(_kv_table(header_rows, font))
    story.append(Spacer(1, 12))

    story += _section(
        'فعالیت‌های اجرایی',
        ['شرح فعالیت', 'شیفت', 'مسئول', 'نفر', 'مقدار', 'واحد'],
        [
            [
                r.activity_description, r.get_shift_display(),
                r.responsible_name or '—',
                r.headcount if r.headcount is not None else '—',
                r.quantity if r.quantity is not None else '—', r.unit or '—',
            ]
            for r in report.activities.filter(is_deleted=False)
        ],
        head_style, normal, font, [140, 45, 80, 40, 60, 50],
    )

    story += _section(
        'نیروی انسانی',
        ['دسته', 'عنوان شغلی', 'شیفت ۱', 'شیفت ۲', 'شیفت ۳', 'غیبت', 'جمع'],
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
        'مصالح',
        ['شرح مصالح', 'نوع', 'مقدار', 'واحد', 'محل مصرف'],
        [
            [
                r.material_description,
                r.get_transaction_type_display(),
                r.quantity,
                r.unit,
                r.consumption_location or '—',
            ]
            for r in report.material_entries.filter(is_deleted=False)
        ],
        head_style, normal, font, [150, 70, 55, 45, 90],
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
        'حوادث و موانع',
        ['نوع', 'شرح', 'مسئول پیگیری', 'موعد', 'اقدام اصلاحی'],
        [
            [
                r.get_incident_type_display(),
                r.description,
                r.follow_up_owner_name or '—',
                r.due_date.isoformat() if r.due_date else '—',
                r.corrective_action or '—',
            ]
            for r in report.incidents.filter(is_deleted=False)
        ],
        head_style, normal, font, [70, 140, 80, 55, 100],
    )

    if report.general_notes:
        story.append(Paragraph(_fa('توضیحات کلی'), head_style))
        story.append(Paragraph(_fa(report.general_notes), normal))

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
        Paragraph(_fa('<b>تنظیم‌کننده (سرپرست کارگاه)</b>'), title_style),
        Spacer(1, 3),
        Paragraph(_fa(f'نام: {prep_name}'), box_style),
        Paragraph(_fa('سمت: سرپرست کارگاه'), box_style),
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
            Paragraph(_fa('<b>بررسی‌کننده (دفتر فنی)</b>'), title_style),
            Spacer(1, 3),
            Paragraph(_fa(f'نام: {rev_name}'), box_style),
            Paragraph(_fa('سمت: مسئول دفتر فنی'), box_style),
            Paragraph(_fa(f'زمان بررسی: {rev_time or "—"}'), box_style),
        ]
    else:
        b2_content = [
            Paragraph(_fa('<b>بررسی‌کننده (دفتر فنی)</b>'), title_style),
            Spacer(1, 3),
            Paragraph(_fa('بدون نیاز به بررسی دفتر فنی / تأیید مستقیم'), box_style),
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
        Paragraph(_fa('<b>تأییدکننده (مدیر پروژه / ناظر مقیم)</b>'), title_style),
        Spacer(1, 3),
        Paragraph(_fa(f'نام: {app_name}'), box_style),
        Paragraph(_fa('سمت: مدیر پروژه / دستگاه نظارت'), box_style),
        Paragraph(_fa(f'زمان تأیید: {app_time or "—"}'), box_style),
        Spacer(1, 3),
        Paragraph(_fa(f'کد رهگیری امنیتی: {audit_hash}'), box_style),
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
            escaped = (
                str(val)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
            )
            paragraphs_text = '<br/>'.join(_fa(line) for line in escaped.splitlines())
            val_cell = Paragraph(paragraphs_text, val_style)
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


def _section(title, headers, rows, head_style, normal, font, col_widths):
    story = [Spacer(1, 8), Paragraph(_fa(title), head_style)]
    if not rows:
        story.append(Paragraph(_fa('موردی ثبت نشده است.'), normal))
        return story
    data = [[_fa(h) for h in headers]]
    for row in rows:
        data.append([_fa(cell) for cell in row])
    table = Table(data, repeatRows=1, colWidths=col_widths)
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
    story.append(table)
    return story
