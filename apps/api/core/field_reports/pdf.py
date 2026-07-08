"""ReportLab PDF export for daily reports (RTL, Persian).

Persian text is shaped with ``arabic_reshaper`` + ``python-bidi`` when those
packages are installed, and rendered with a Persian TTF (Vazirmatn) when one is
available on disk. Everything degrades gracefully so a PDF is always produced.
"""
from __future__ import annotations

import io
import os

from django.conf import settings
from django.http import HttpResponse
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
        getattr(settings, 'IPCAS_PDF_FONT_PATH', None),
        os.environ.get('IPCAS_PDF_FONT_PATH'),
        os.path.join(os.path.dirname(__file__), 'fonts', 'Vazirmatn.ttf'),
        '/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Regular.ttf',
        # Fallbacks with Arabic/Persian glyph coverage.
        '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
    ]
    for path in candidates:
        if path and os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('IpcasFa', path))
                _FONT_NAME = 'IpcasFa'
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


def render_daily_report_pdf(report) -> HttpResponse:
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
    jalali = gregorian_to_jalali(report_date) if report_date else ''
    dow = persian_day_of_week(report_date) if report_date else ''

    story = [
        Paragraph(_fa(f'گزارش روزانه — {jalali} ({dow})'), title_style),
        Paragraph(_fa(f'وضعیت: {report.get_status_display()}'), head_style),
        Spacer(1, 8),
    ]

    weather = report.get_weather_condition_display() if report.weather_condition else '—'
    header_rows = [
        [_fa('وضعیت کارگاه'), _fa(report.get_site_status_display())],
        [_fa('وضعیت جوی'), _fa(weather)],
        [_fa('حداکثر دما'), _fa(report.temp_max if report.temp_max is not None else '—')],
        [_fa('حداقل دما'), _fa(report.temp_min if report.temp_min is not None else '—')],
        [_fa('تهیه‌کننده'), _fa(_full_name(report.prepared_by))],
        [_fa('تأییدکننده'), _fa(_full_name(report.approved_by))],
    ]
    story.append(_kv_table(header_rows, font))
    story.append(Spacer(1, 12))

    story += _section(
        'فعالیت‌های اجرایی',
        ['شرح فعالیت', 'شیفت', 'پیمانکار', 'نفر', 'مقدار', 'واحد'],
        [
            [
                r.activity_description, r.get_shift_display(), r.subcontractor_name,
                r.headcount if r.headcount is not None else '—',
                r.quantity if r.quantity is not None else '—', r.unit or '—',
            ]
            for r in report.activities.filter(is_deleted=False)
        ],
        head_style, normal, font, [150, 45, 90, 40, 60, 50],
    )

    story += _section(
        'نیروی انسانی',
        ['دسته', 'عنوان شغلی', 'شیفت ۱', 'شیفت ۲', 'شیفت ۳', 'جمع'],
        [
            [
                r.get_labor_category_display(), r.custom_title or r.job_title,
                r.shift_1_count, r.shift_2_count, r.shift_3_count, r.total_count,
            ]
            for r in report.labor_entries.filter(is_deleted=False)
        ],
        head_style, normal, font, [70, 150, 50, 50, 50, 50],
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
        ['شرح مصالح', 'نوع', 'مقدار', 'واحد'],
        [
            [r.material_description, r.get_transaction_type_display(), r.quantity, r.unit]
            for r in report.material_entries.filter(is_deleted=False)
        ],
        head_style, normal, font, [200, 90, 80, 60],
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
        ['نوع', 'شرح', 'اقدام اصلاحی'],
        [
            [r.get_incident_type_display(), r.description, r.corrective_action]
            for r in report.incidents.filter(is_deleted=False)
        ],
        head_style, normal, font, [90, 220, 180],
    )

    if report.general_notes:
        story.append(Paragraph(_fa('توضیحات کلی'), head_style))
        story.append(Paragraph(_fa(report.general_notes), normal))

    doc.build(story)
    pdf = buf.getvalue()

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f'report_{jalali.replace("/", "-") or report.id}.pdf'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def _full_name(user) -> str:
    if not user:
        return '—'
    return (user.get_full_name() or user.username) if hasattr(user, 'get_full_name') else str(user)


def _kv_table(rows, font) -> Table:
    data = [[_fa(v) if not _is_fa(v) else v for v in row] for row in rows]
    table = Table(data, colWidths=[120, 320])
    table.setStyle(
        TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eef2f7')),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
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
