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
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from common.jalali import gregorian_to_jalali, gregorian_to_jalali_datetime
from field_reports.services.data_contract import (
    INCIDENT_LABELS_FA, SEVERITY_LABELS_FA, concrete_details_url, format_forecast, format_worked_shift, project_report_header,
    sampling_label,
)

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


def generate_daily_report_pdf(report, *, language='fa') -> Tuple[bytes, str]:
    header = project_report_header(report)
    english = language.startswith('en')
    def labels(en, fa):
        return en if english else fa
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
    normal = ParagraphStyle('ReportNormal', parent=base['Normal'], fontName=font,
                            alignment=TA_LEFT if english else TA_RIGHT)

    report_date = report.report_date
    if isinstance(report_date, str):
        from datetime import date
        try:
            report_date = date.fromisoformat(report_date)
        except ValueError:
            pass
    jalali, dow = header['report_date'], header['day_of_week']
    statuses_fa = {'draft': 'پیش‌نویس', 'submitted': 'ارسال‌شده', 'under_review': 'در حال بررسی',
                   'approved': 'تأییدشده', 'rejected': 'ردشده'}
    status_label = report.get_status_display() if english else statuses_fa.get(report.status, 'نامشخص')
    day_shift = report.get_shift_display()

    story = [
        Paragraph(_fa(f"{labels('Daily report', 'گزارش روزانه')} — {jalali} ({dow})"), title_style),
        Paragraph(_fa(f"{labels('Status', 'وضعیت')}: {status_label}"), head_style),
        Spacer(1, 8),
    ]

    weather = (report.weather_condition.capitalize() if english else report.get_weather_condition_display()) if report.weather_condition else '—'
    site_status_label = report.site_status.capitalize() if english else report.get_site_status_display()
    if report.site_status == 'inactive' and report.inactivity_reason:
        reason_label = report.inactivity_reason.replace('_', ' ').capitalize() if english else report.get_inactivity_reason_display()
        site_status_label = f'{site_status_label} ({reason_label})'

    header_rows = [
        ['Project' if english else 'پروژه', header['project_name']],
        ['Contract' if english else 'شماره قرارداد', header['contract_number'] or '—'],
        [labels('Employer', 'کارفرما'), report.project.employer or '—'],
        [labels('Consultant', 'مشاور'), report.project.consultant or '—'],
        [labels('Report shift', 'شیفت گزارش'), day_shift],
        [labels('Report status', 'وضعیت گزارش'), status_label],
        [labels('Work front', 'محل / جبهه'), report.work_front or '—'],
        [labels('Site status', 'وضعیت کارگاه'), site_status_label],
        [labels('Weather', 'وضعیت جوی'), weather],
        [labels('High temperature', 'حداکثر دما'), str(report.temp_max) if report.temp_max is not None else '—'],
        [labels('Low temperature', 'حداقل دما'), str(report.temp_min) if report.temp_min is not None else '—'],
        ['Preparer' if english else 'تهیه‌کننده', header['prepared_by_name'] or '—'],
        [labels('Approver', 'تأییدکننده'), _full_name(report.approved_by)],
        ['Weather impact' if english else 'توضیحات و اثرات شرایط جوی', header['weather_impact_notes'] or ''],
        ['Official report' if english else 'شماره گزارش', header['official_numbering']['official_report_number'] or '—'],
        ['Project day' if english else 'روز پروژه', str(header['official_numbering']['project_day'] or '—')],
        ['Worked shifts' if english else 'شیفت‌های کارکرد', '\n'.join(
            format_worked_shift(shift, english=english) for shift in header['worked_shifts']
        ) or '—'],
        ['Wind' if english else 'باد', header['weather']['wind_speed'] or '—'],
        ['Ground conditions' if english else 'وضعیت زمین', header['weather']['soil_condition'] or '—'],
        ['Forecast' if english else 'پیش‌بینی',
         f"{header['weather']['forecast_provider']}\n{format_forecast(header['weather'])}"],
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
            unit_labels = {
                'buildings': 'ابنیه', 'electrical': 'تأسیسات برقی',
                'mechanical': 'تأسیسات مکانیکی', 'machinery': 'ماشین‌آلات',
                'warehouse': 'انبار', 'security': 'حراست و ایمنی',
            }
            missing = '، '.join(unit_labels.get(unit, unit) for unit in completeness['missing_units']) or 'نامشخص'
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
        labels('Executed activities', 'فعالیت‌های اجرایی'),
        labels(['Activity and notes', 'Shift', 'Contractor / Crew', 'Count', 'Location', 'Quantity', 'Unit'],
               ['شرح فعالیت و توضیحات', 'شیفت', 'پیمانکار / اکیپ', 'نفر', 'موقعیت', 'مقدار', 'واحد']),
        [
            [
                '\n'.join(filter(None, [r.activity_ref.activity_code if r.activity_ref else '', r.activity_description, r.notes])),
                r.get_shift_display(),
                ' / '.join(filter(None, [
                    r.subcontractor_name or (r.contractor_ref.name if r.contractor_ref else ''),
                    r.crew_name,
                ])) or '—',
                r.headcount if r.headcount is not None else '—',
                ' / '.join(filter(None, [r.parcel, r.zone, r.block, r.floor, r.location_detail])) or '—',
                r.quantity if r.quantity_measured and r.quantity is not None else '—', r.unit or '—',
            ]
            for r in report.activities.filter(is_deleted=False).select_related('contractor_ref', 'activity_ref')
        ],
        head_style, normal, font, [115, 44, 100, 35, 115, 55, 45],
    )

    labor_rows = [
        [row.get_labor_category_display(), row.custom_title or row.job_title,
         row.shift_1_count, row.shift_2_count, row.shift_3_count,
         row.absence_count if row.absence_count is not None else '—', row.total_count]
        for row in report.labor_entries.filter(is_deleted=False)
    ]
    if labor_rows:
        labor_rows.append([
            '', labels('Total person-shifts', 'جمع کل نفر-شیفت'),
            *(sum(row[index] for row in labor_rows) for index in (2, 3, 4)),
            '—', sum(row[6] for row in labor_rows),
        ])
    story += _section(
        labels('Labor', 'نیروی انسانی'),
        labels(['Category', 'Position', 'Shift 1', 'Shift 2', 'Shift 3', 'Leave / Absence', 'Total'],
               ['دسته', 'عنوان شغلی', 'شیفت ۱', 'شیفت ۲', 'شیفت ۳', 'مرخصی' if report.is_auto_summary else 'مرخصی / غیبت', 'جمع']),
        labor_rows,
        head_style, normal, font, [60, 120, 40, 40, 40, 40, 40],
    )

    story += _section(
        labels('Equipment', 'ماشین‌آلات'),
        labels(['Equipment', 'Shift', 'Status', 'Ownership', 'Work h'], ['دستگاه', 'شیفت', 'وضعیت', 'مالکیت', 'کارکرد']),
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
        labels('Machinery summary', 'وضعیت ماشین‌آلات تجمیعی'),
        labels(['Machine', 'Total', 'Active', 'Ready', 'Inactive', 'Under repair', 'Work h'],
               ['نوع دستگاه', 'کل', 'فعال', 'آماده', 'غیرفعال', 'در تعمیر', 'کارکرد']),
        [
            [r.equipment_type, r.status_total, r.status_active, r.status_ready,
             r.status_inactive, r.status_under_repair,
             r.operating_hours if r.operating_hours is not None else '—']
            for r in report.machinery_rows.filter(is_deleted=False)
        ],
        head_style, normal, font, [150, 45, 50, 50, 60, 60, 65],
    )

    receipts, other_materials = [], []
    for row in report.material_entries.filter(is_deleted=False):
        collection = receipts if row.transaction_type == 'receipt' and (
            not report.is_auto_summary or row.receipt_resolved is True
        ) else other_materials
        collection.append([
            row.material_description, _material_status_label(row, english=english), row.quantity, row.unit,
            row.consumption_location or '—', row.warehouse_document_reference or '—',
        ])
    material_headers = labels(
        ['Material', 'Transaction and reconciliation', 'Quantity', 'Unit', 'Location', 'Warehouse document'],
        ['شرح مصالح', 'نوع و وضعیت سند', 'مقدار', 'واحد', 'محل مصرف', 'سند انبار'],
    )
    for title, rows in (
        ('Material receipts' if english else 'مصالح وارده', receipts),
        ('Other material movements' if english else 'سایر گردش‌ها و رسیدهای تأییدنشده', other_materials),
    ):
        story += _section(title, material_headers, rows, head_style, normal, font, [105, 135, 45, 35, 85, 75])

    concrete_rows = list(report.concrete_logs.filter(is_deleted=False))
    story += _section(
        'Concrete pours' if english else 'بتن‌ریزی',
        (['Description', 'Volume (m³)', 'Parcel', 'Block', 'Floor', 'Element', 'Delivery note', 'Lab sample', 'Sampling']
         if english else ['شرح', 'حجم (م³)', 'قطعه', 'بلوک', 'طبقه', 'عضو سازه‌ای', 'شماره حواله', 'کد نمونه', 'نمونه‌گیری']),
        [
            [r.concrete_description, r.volume_m3, r.parcel or r.zone or '—', r.block or '—', r.floor or '—',
             r.structural_element or '—', r.truck_delivery_note_number or '—', r.lab_sample_code or '—',
             sampling_label(r.sampling_state, english=english)]
            for r in concrete_rows
        ],
        head_style, normal, font, [87, 45, 39, 36, 32, 59, 60, 59, 63],
    )
    if concrete_rows:
        total_label = labels('Total concrete volume', 'جمع کل حجم بتن‌ریزی')
        total = sum(row.volume_m3 for row in concrete_rows)
        story.append(_text_paragraph(f'{total_label}: {total} m³', normal))
        detail_label = labels('Open concrete details for this version', 'مشاهده جزئیات بتن‌ریزی همین نسخه')
        detail_url = escape(concrete_details_url(report), {'"': '&quot;'})
        story.append(Paragraph(f'<link href="{detail_url}">{escape(_fa(detail_label))}</link>', normal))

    story += _section(
        labels('General activities', 'فعالیت‌های عمومی کارگاه'),
        labels(['Activity', 'Location', 'Quantity', 'Unit', 'Notes', 'Source unit'],
               ['شرح فعالیت', 'محل', 'مقدار', 'واحد', 'توضیحات', 'واحد مبدأ']),
        [[r.activity_description, r.location or '—',
          r.quantity if r.quantity is not None else '—', r.unit or '—', r.notes or '—', r.source_discipline or '—']
         for r in report.general_activities.filter(is_deleted=False).order_by('row_number', 'id')],
        head_style, normal, font, [125, 85, 50, 45, 120, 55],
    )

    story += _section(
        labels('Visits', 'بازدیدها'), labels(['Description', 'Source unit'], ['شرح', 'واحد مبدأ']),
        [[r.text, r.source_discipline or '—'] for r in report.visits.filter(is_deleted=False).order_by('row_number', 'id')],
        head_style, normal, font, [385, 95],
    )

    story += _section(
        labels('Incidents and issues', 'حوادث و موانع'),
        labels(['Type', 'Description', 'Owner', 'Due date', 'Immediate action', 'Severity', 'Source unit'],
               ['نوع', 'شرح', 'مسئول پیگیری', 'موعد', 'اقدام اصلاحی', 'شدت', 'واحد مبدأ']),
        [
            [
                r.get_incident_type_display() if english else INCIDENT_LABELS_FA.get(r.incident_type, r.get_incident_type_display()),
                r.description,
                r.follow_up_owner_name or _full_name(r.follow_up_owner_user),
                gregorian_to_jalali(r.due_date) if r.due_date else '—',
                r.corrective_action or '—',
                (r.get_severity_display() if english else SEVERITY_LABELS_FA.get(r.severity, r.get_severity_display()))
                if r.severity else '—',
                (r.source_report.unit or r.source_report.discipline) if r.source_report else '—',
            ]
            for r in report.incidents.filter(is_deleted=False)
            .select_related('follow_up_owner_user', 'source_report').order_by('row_number', 'id')
        ],
        head_style, normal, font, [50, 105, 75, 65, 100, 45, 55],
    )

    if report.general_notes:
        story.append(Paragraph(_fa(labels('General notes', 'توضیحات کلی')), head_style))
        story.append(_text_paragraph(report.general_notes, normal))
    if report.management_opinion:
        story.append(Paragraph(_fa(labels('Management opinion', 'نظر مدیریت')), head_style))
        story.append(_text_paragraph(report.management_opinion, normal))

    # Put version attribution after the report sections.
    story.append(Spacer(1, 14))
    story.append(_signatures_block(report, font, language=language))

    _build_with_watermark(doc, story, font, approved=report.status == 'approved', language=language)
    filename = f"daily-report-{jalali.replace('/', '-')}-{report.shift or 'full'}.pdf"
    return buf.getvalue(), filename


def _build_with_watermark(doc, story, font, *, approved, language):
    if approved:
        doc.build(story)
        return
    text = 'DRAFT' if language.startswith('en') else 'پیش‌نویس — غیرقابل استناد رسمی (DRAFT)'
    watermark = _make_watermark(text, font)
    # Filled table cells cover a background watermark. Draw it after the
    # page's content so the mark remains visible on densely filled pages.
    doc.afterPage = lambda: watermark(doc.canv, doc)
    doc.build(story)


def _metadata_fingerprint(metadata):
    import hashlib
    import json

    raw = json.dumps(metadata, default=str, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16].upper()


def generate_report_audit_hash(report) -> str:
    return _metadata_fingerprint({
        'id': report.pk,
        'lineage_id': report.lineage_id,
        'report_date': report.report_date,
        'shift': report.shift,
        'status': report.status,
        **{
            key: getattr(report, key) for key in (
                'prepared_by_id', 'submitted_by_id', 'submitted_at', 'reviewed_by_id',
                'reviewed_at', 'approved_by_id', 'approved_at', 'export_action_attribution',
            )
        },
    })


def _make_watermark(text: str, font_name: str):
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFont(font_name, 28)
        canvas.setFillColor(colors.Color(0.47, 0.47, 0.47, alpha=0.28))
        canvas.translate(A4[0] / 2.0, A4[1] / 2.0)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, _fa(text))
        canvas.restoreState()
    return _draw


def _signatures_block(report, font: str, *, language='fa') -> Table:
    recorded = report.export_action_attribution or {}
    submission = (report.submitted_by, report.submitted_at, recorded.get('submitted', {}))
    if report.submitted_by_id is None and report.submitted_at is None:
        prep_at = report.created_at if report.prepared_by_id == report.created_by_id else None
        submission = (report.prepared_by, prep_at if report.prepared_by_id else None, {})
    review = (report.reviewed_by, report.reviewed_at, recorded.get('reviewed', {}))
    if report.submitted_at and report.reviewed_at and report.reviewed_at < report.submitted_at:
        review = (None, None, {})
    approval = (report.approved_by, report.approved_at, recorded.get('approved', {}))
    slots = [
        (data.get('actor_name') or (_full_name(actor) if actor else None), at, data.get('position'))
        for actor, at, data in (submission, review, approval)
    ]
    return _signature_table(
        slots, generate_report_audit_hash(report), font, language=language, approved=report.status == 'approved',
    )


def _signature_table(slots, fingerprint, font, *, language, approved):
    from field_reports.services.weather_forecast import PROJECT_TIME_ZONE

    english = language.startswith('en')
    labels = ('Preparer', 'Reviewer', 'Approver') if english else ('تنظیم‌کننده', 'بررسی‌کننده', 'تأییدکننده')
    name_label, time_label, position_label = ('Name', 'Local time', 'Position') if english else ('نام', 'زمان محلی', 'سمت')
    unknown = 'Unknown' if english else 'نامشخص'
    box_style = ParagraphStyle('SigBox', fontName=font, fontSize=8, alignment=TA_RIGHT, leading=11)
    title_style = ParagraphStyle('SigTitle', fontName=font, fontSize=8, alignment=TA_RIGHT, leading=12)

    boxes = []
    for index, (title, (name, at, position)) in enumerate(zip(labels, slots)):
        content = [_text_paragraph(title, title_style), Spacer(1, 3)]
        if name is not None or at is not None:
            local_time = at.astimezone(PROJECT_TIME_ZONE) if at is not None else None
            timestamp = f"{gregorian_to_jalali(local_time.date())} {local_time:%H:%M}" if local_time else unknown
            content.extend(_text_paragraph(value, box_style, max_width=150) for value in (
                f'{name_label}: {name or unknown}', f'{position_label}: {position or unknown}',
                f'{time_label}: {timestamp}',
            ))
        elif index == 1 and approved:
            content.append(_text_paragraph(
                'Direct approval; no review recorded' if english else 'بدون نیاز به بررسی دفتر فنی / تأیید مستقیم',
                box_style,
            ))
        elif index == 1:
            content.append(_text_paragraph('Pending review' if english else 'هنوز بررسی نشده است', box_style))
        if index == 2:
            caption = 'Metadata fingerprint' if english else 'اثرانگشت فراداده'
            content.extend([Spacer(1, 3), _text_paragraph(f'{caption}: {fingerprint}', box_style)])
        boxes.append(content)

    table = Table([boxes], colWidths=[175, 175, 175])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2F5597')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
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


def _material_status_label(row, *, english=False) -> str:
    """Document resolution does not itself mean the reported quantity matches."""
    if english:
        status = {'receipt': 'Receipt', 'issue': 'Issue', 'waste': 'Waste', 'return': 'Return'}.get(
            row.transaction_type, 'Unknown transaction',
        )
        if row.transaction_type == 'receipt':
            status = 'Receipt with warehouse document' if row.receipt_resolved is True else 'Unresolved receipt'
        if row.reconciliation_status:
            status = f'{status} ({row.get_reconciliation_status_display()})'
        return status
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
        'DailyPdfCell', fontName=font, fontSize=8, leading=10, alignment=normal.alignment,
        splitLongWords=True,
    )
    data = [[_text_paragraph(h, cell_style, max_width=width - 12) for h, width in zip(headers, col_widths)]]
    for row in rows:
        data.append([_text_paragraph(cell, cell_style, max_width=width - 12) for cell, width in zip(row, col_widths)])
    if not rows:
        empty = 'No entries recorded.' if normal.alignment == TA_LEFT else 'موردی ثبت نشده است.'
        data.append([_text_paragraph(empty, cell_style)] + [''] * (len(headers) - 1))
    # Ordinary rows stay intact. Rows taller than a fresh page may split so
    # unusually long multiline notes remain printable.
    split_tall_row = any(
        cell.wrap(width - 12, 760)[1] > 720
        for row in data[1:] for cell, width in zip(row, col_widths) if isinstance(cell, Paragraph)
    )
    table = Table(data, repeatRows=1, colWidths=col_widths, splitInRow=int(split_tall_row))
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
