"""Render an authorized unit-report version with its own operational sections."""
from io import BytesIO

from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer

from common.jalali import gregorian_to_jalali
from common.reporting_units import SpecialtyUnit
from field_reports.pdf import (
    _build_with_watermark, _full_name, _kv_table, _metadata_fingerprint, _register_font, _section,
    _signature_table, _text_paragraph,
)
from field_reports.services.data_contract import SEVERITY_LABELS_FA, sampling_label
from sub_reports.models import SubReportStatus, UnitReportEventType


UNIT_NAMES_FA = {
    'buildings': 'ابنیه', 'electrical': 'تأسیسات برقی', 'mechanical': 'تأسیسات مکانیکی',
    'machinery': 'ماشین‌آلات', 'warehouse': 'انبار', 'security': 'حراست و ایمنی',
}
STATUS_FA = {'draft': 'پیش‌نویس', 'submitted': 'ارسال‌شده', 'approved': 'تأییدشده', 'rejected': 'ردشده'}


def generate_unit_report_pdf(report, *, language='fa'):
    english = language.startswith('en')

    def labels(en, fa):
        return en if english else fa

    font = _register_font()
    target = BytesIO()
    doc = SimpleDocTemplate(target, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28)
    styles = getSampleStyleSheet()
    alignment = TA_LEFT if english else TA_RIGHT
    title = ParagraphStyle('UnitTitle', parent=styles['Title'], fontName=font, alignment=alignment)
    head = ParagraphStyle('UnitHead', parent=styles['Heading3'], fontName=font, alignment=alignment, keepWithNext=True)
    normal = ParagraphStyle('UnitNormal', parent=styles['Normal'], fontName=font, alignment=alignment)
    local_date = gregorian_to_jalali(report.report_date)
    unit_name = SpecialtyUnit(report.unit).label if english else UNIT_NAMES_FA[report.unit]
    approved = report.status == SubReportStatus.APPROVED
    status_text = report.get_status_display() if english else STATUS_FA.get(report.status, 'نامشخص')
    story = [
        _text_paragraph(labels(f'Daily report — {unit_name}', f'گزارش روزانه — {unit_name}'), title),
        _kv_table([
            (labels('Project', 'پروژه'), report.project.project_name),
            (labels('Date', 'تاریخ'), local_date),
            (labels('Version', 'نسخه'), str(report.version_number)),
            (labels('Status', 'وضعیت'), status_text),
            (labels('Form', 'فرم'), report.form_code or '—'),
        ], font),
    ]

    def add(name, columns, rows, widths):
        if rows:
            story.extend(_section(name, columns, rows, head, normal, font, widths))

    activities = list(report.activities.filter(is_deleted=False).select_related(
        'activity_ref', 'contractor_ref',
    ).order_by('row_number', 'pk'))
    activity_columns = labels(
        ['Activity', 'Shift', 'Contractor', 'Crew', 'Location', 'Quantity', 'Unit'],
        ['فعالیت', 'شیفت', 'پیمانکار', 'اکیپ', 'موقعیت', 'مقدار', 'واحد'],
    )
    activity_widths = [152, 42, 76, 75, 72, 59, 45]
    activity_rows = [
        ['\n'.join(filter(None, [row.activity_ref.activity_code if row.activity_ref else '',
                                  row.activity_description, row.notes])),
         row.shift or '—', row.contractor_ref.name if row.contractor_ref else '—',
         row.crew_name or '—', ' / '.join(filter(None, [row.parcel, row.zone, row.block, row.floor])) or '—',
         _number(row.quantity), row.unit or '—']
        for row in activities
    ]
    if report.unit == SpecialtyUnit.BUILDINGS:
        activity_columns.append(labels('Progress', 'درصد اجرا'))
        activity_widths[0] -= 52
        activity_widths.append(52)
        for values, activity in zip(activity_rows, activities):
            percentage = activity.execution_percentage
            values.append(f'{percentage}%' if percentage is not None else '—')
    add(
        labels('Executed activities', 'فعالیت‌های اجرایی'),
        activity_columns, activity_rows, activity_widths,
    )
    add(
        labels('Labor', 'نیروی انسانی'),
        labels(['Position', 'Contractor', 'Present', 'Leave', 'Overtime (h)'],
               ['عنوان شغلی', 'پیمانکار', 'حاضر', 'مرخصی', 'اضافه‌کاری']),
        [(r.job_title, r.contractor_ref.name if r.contractor_ref else '—', r.present_count,
          r.leave_count, r.overtime_hours)
         for r in report.labor_entries.filter(is_deleted=False).select_related('contractor_ref').order_by('job_title', 'pk')],
        [170, 120, 65, 65, 90],
    )
    add(
        labels('Machinery', 'ماشین‌آلات'),
        labels(['Machine', 'Total', 'Active', 'Ready', 'Inactive', 'Under repair', 'Work h', 'Stop h', 'Repair h', 'Reason'],
               ['دستگاه', 'کل', 'فعال', 'آماده', 'غیرفعال', 'در تعمیر', 'کارکرد', 'توقف', 'تعمیر', 'علت']),
        [(r.equipment_type, r.status_total, r.status_active, r.status_ready, r.status_inactive, r.status_under_repair,
          _number(r.operating_hours), _number(r.stoppage_hours), _number(r.repair_hours), r.stoppage_reason_code or '—')
         for r in report.machinery_rows.filter(is_deleted=False).order_by('row_number', 'pk')],
        [105, 38, 42, 40, 48, 52, 42, 42, 44, 65],
    )
    add(
        labels('Materials', 'مصالح'),
        labels(['Material', 'Transaction', 'Quantity', 'Unit', 'Warehouse document', 'Location'],
               ['مصالح', 'تراکنش', 'مقدار', 'واحد', 'سند انبار', 'موقعیت']),
        [(r.material_description, r.get_transaction_type_display() or '—', r.quantity, r.unit,
          r.warehouse_document_reference or '—', r.consumption_location or '—')
         for r in report.material_entries.filter(is_deleted=False).order_by('pk')],
        [150, 85, 55, 45, 100, 90],
    )
    add(
        labels('Concrete pours', 'بتن‌ریزی'),
        labels(['Description', 'Volume (m³)', 'Parcel / Block / Floor', 'Element', 'Delivery note', 'Sample', 'Sampling'],
               ['شرح', 'حجم (م³)', 'قطعه / بلوک / طبقه', 'عضو سازه‌ای', 'حواله', 'کد نمونه', 'نمونه‌گیری']),
        [(r.concrete_description, r.volume_m3, ' / '.join(filter(None, [r.parcel or r.zone, r.block, r.floor])) or '—',
          r.structural_element or '—', r.truck_delivery_note_number or '—', r.lab_sample_code or '—',
          sampling_label(r.sampling_state, english=english))
         for r in report.concrete_entries.filter(is_deleted=False).order_by('pk')],
        [110, 55, 85, 65, 60, 65, 85],
    )
    _add_unit_narratives(report, add, labels, english)

    slots, event_metadata = _attribution(report)
    fingerprint = _metadata_fingerprint({
        'id': report.pk, 'lineage_id': report.lineage_id, 'date': report.report_date,
        'unit': report.unit, 'status': report.status, 'actions': event_metadata,
    })
    story.extend([Spacer(1, 14), _signature_table(slots, fingerprint, font, language=language, approved=approved)])
    _build_with_watermark(doc, story, font, approved=approved, language=language)
    return target.getvalue(), f"unit-daily-report-{report.unit}-{local_date.replace('/', '-')}.pdf"


def _add_unit_narratives(report, add, labels, english):
    add(
        labels('General activities', 'فعالیت‌های عمومی'),
        labels(['Description', 'Location', 'Quantity', 'Unit', 'Notes'], ['شرح', 'موقعیت', 'مقدار', 'واحد', 'یادداشت']),
        [(row.activity_description, row.location or '—', _number(row.quantity), row.unit or '—', row.notes or '—')
         for row in report.general_activities.filter(is_deleted=False).order_by('row_number', 'pk')],
        [155, 85, 55, 45, 185],
    )
    add(
        labels('Issues and barriers', 'مسائل و موانع'),
        labels(['Type', 'Description', 'Owner', 'Due date'], ['نوع', 'شرح', 'پیگیر', 'موعد']),
        [(row.get_kind_display() if english else ('مانع' if row.kind == 'barrier' else 'مسئله'),
          row.text, _full_name(row.owner_user), gregorian_to_jalali(row.due_date) if row.due_date else '—')
         for row in report.issues.filter(is_deleted=False).select_related('owner_user').order_by('row_number', 'pk')],
        [65, 255, 110, 95],
    )
    add(
        labels('Visits', 'بازدیدها'), [labels('Description', 'شرح')],
        [(row.text,) for row in report.visits.filter(is_deleted=False).order_by('row_number', 'pk')], [525],
    )
    add(
        labels('HSE incidents', 'حوادث ایمنی'),
        labels(['Description', 'Severity', 'Immediate action'], ['شرح', 'شدت', 'اقدام فوری']),
        [(row.text, row.get_severity_display() if english else SEVERITY_LABELS_FA.get(row.severity, '—'),
          row.immediate_action)
         for row in report.hse_incidents.filter(is_deleted=False).order_by('row_number', 'pk')],
        [235, 70, 220],
    )
    add(
        labels('Notes', 'یادداشت‌ها'), [labels('Description', 'شرح')],
        [(row.text,) for row in report.notes.filter(is_deleted=False).order_by('row_number', 'pk')], [525],
    )
    records = report.activity_records.filter(project_id=report.project_id).order_by('pk')
    if report.unit == SpecialtyUnit.WAREHOUSE:
        add(
            labels('Warehouse records', 'گردش انبار'),
            labels(['Material', 'Received', 'Issued', 'Unit', 'Location', 'Supplier'],
                   ['مصالح', 'وارده', 'صادره', 'واحد', 'موقعیت', 'تأمین‌کننده']),
            [(r.material_type, r.quantity_in, r.quantity_out, r.unit, r.consumption_location, r.supplier) for r in records],
            [115, 60, 60, 55, 120, 115],
        )
    else:
        add(
            labels('Department records', 'عملیات واحد'),
            labels(['Activity', 'Location', 'Result', 'Unit', 'Notes'], ['فعالیت', 'موقعیت', 'مقدار', 'واحد', 'یادداشت']),
            [(r.activity_description, r.location, _number(r.executed_quantity), r.unit, r.description) for r in records],
            [155, 85, 55, 45, 185],
        )


def _number(value):
    return value if value is not None else '—'


def _attribution(report):
    events = list(report.status_events.select_related('actor').order_by('occurred_at', 'pk'))
    by_type = {event.event_type: event for event in events}
    prepare = by_type.get(UnitReportEventType.SUBMITTED) or by_type.get(UnitReportEventType.CORRECTED) or by_type.get(UnitReportEventType.CREATED)
    approve = by_type.get(UnitReportEventType.APPROVED)

    def attributed(action, actor, recorded_at):
        if action:
            return (action.actor_name or (_full_name(action.actor) if action.actor_id else None),
                    action.occurred_at, action.actor_position)
        return (_full_name(actor) if actor else None, recorded_at, None)

    slots = [
        attributed(prepare, report.submitted_by or report.created_by, report.submitted_at or report.created_at),
        (None, None, None),
        attributed(approve, report.approved_by, report.approved_at),
    ]
    metadata = [(event.event_type, event.actor_id, event.occurred_at, event.actor_position) for event in events]
    if not prepare or not approve:
        metadata.append((report.submitted_by_id, report.submitted_at, report.approved_by_id, report.approved_at))
    return slots, metadata
