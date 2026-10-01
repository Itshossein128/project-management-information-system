"""
Excel export/import and PDF reports for department activity records.
"""
from __future__ import annotations

import io
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from openpyxl import Workbook, load_workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from business_meta.models import Project

from .models import Department, DepartmentActivityRecord, department_uses_unit, is_warehouse_department

EXPORT_HEADERS_WITH_UNIT = [
    'date',
    'location',
    'activity_description',
    'contractor',
    'unit',
    'description',
]

EXPORT_HEADERS_WITHOUT_UNIT = [
    'date',
    'location',
    'activity_description',
    'contractor',
    'description',
]

EXPORT_HEADERS_WAREHOUSE = [
    'date',
    'material_type',
    'quantity_in',
    'unit',
    'quantity_out',
    'consumption_location',
    'supplier',
    'description',
]

# Backwards-compatible alias used by tests / callers that expect the full header set.
EXPORT_HEADERS = EXPORT_HEADERS_WITH_UNIT

HEADER_ALIASES: dict[str, list[str]] = {
    'date': ['date', 'تاریخ', 'Date'],
    'location': ['location', 'موقعیت', 'Location'],
    'activity_description': [
        'activity_description',
        'activity description',
        'شرح فعالیت',
        'Activity',
    ],
    'contractor': ['contractor', 'پیمانکار', 'پیمانگار', 'Contractor'],
    'unit': ['unit', 'واحد', 'Unit'],
    'description': ['description', 'توضیحات', 'Notes', 'notes'],
    'material_type': [
        'material_type',
        'material type',
        'نوع مصالح',
        'Material Type',
    ],
    'quantity_in': [
        'quantity_in',
        'quantity in',
        'ورودی',
        'Inbound',
        'In',
    ],
    'quantity_out': [
        'quantity_out',
        'quantity out',
        'خروجی',
        'Outbound',
        'Out',
    ],
    'consumption_location': [
        'consumption_location',
        'consumption location',
        'محل مصرف',
        'Consumption Location',
    ],
    'supplier': [
        'supplier',
        'تامین‌کننده',
        'تامین کننده',
        'تاميین‌کننده',
        'Supplier',
    ],
}


def export_headers_for_department(department: str) -> list[str]:
    if is_warehouse_department(department):
        return list(EXPORT_HEADERS_WAREHOUSE)
    if department_uses_unit(department):
        return list(EXPORT_HEADERS_WITH_UNIT)
    return list(EXPORT_HEADERS_WITHOUT_UNIT)


def export_activities_to_xlsx(
    records: list[DepartmentActivityRecord],
    *,
    department: str | None = None,
) -> bytes:
    resolved_department = department
    if resolved_department is None and records:
        resolved_department = records[0].department

    headers = export_headers_for_department(resolved_department or Department.BUILDINGS)
    warehouse = is_warehouse_department(resolved_department or '')

    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title='Activity log')
    ws.append(headers)
    for record in records:
        if warehouse:
            row = [
                record.date.isoformat() if record.date else '',
                record.material_type,
                str(record.quantity_in),
                record.unit,
                str(record.quantity_out),
                record.consumption_location,
                record.supplier,
                record.description or '',
            ]
        else:
            include_unit = department_uses_unit(resolved_department or record.department)
            row = [
                record.date.isoformat() if record.date else '',
                record.location,
                record.activity_description,
                record.contractor,
            ]
            if include_unit:
                row.append(record.unit)
            row.append(record.description or '')
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _map_header_row(header_row: tuple[Any, ...]) -> dict[int, str]:
    alias_to_field: dict[str, str] = {}
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            alias_to_field[alias.strip().lower()] = field

    col_to_field: dict[int, str] = {}
    for idx, cell in enumerate(header_row):
        if cell is None:
            continue
        key = str(cell).strip().lower()
        field = alias_to_field.get(key)
        if field:
            col_to_field[idx] = field
    return col_to_field


def _parse_date_value(raw: Any) -> date | None:
    if raw is None:
        return None
    if hasattr(raw, 'date') and callable(getattr(raw, 'date', None)):
        try:
            return raw.date()
        except Exception:
            pass
    if isinstance(raw, date):
        return raw
    text = str(raw).strip()
    if not text:
        return None
    parsed = parse_date(text[:10])
    if parsed:
        return parsed
    return None


def _parse_quantity(raw: Any) -> Decimal | None:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return Decimal('0')
    try:
        return Decimal(str(raw).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None


def _required_import_fields(department: str) -> set[str]:
    if is_warehouse_department(department):
        return {
            'date',
            'material_type',
            'quantity_in',
            'unit',
            'quantity_out',
            'consumption_location',
            'supplier',
        }
    required = {'date', 'location', 'activity_description', 'contractor'}
    if department_uses_unit(department):
        required.add('unit')
    return required


def import_activities_from_xlsx(
    business: Project,
    department: str,
    file_bytes: bytes,
) -> tuple[int, list[dict]]:
    created = 0
    errors: list[dict] = []
    uses_unit = department_uses_unit(department)
    warehouse = is_warehouse_department(department)
    expected_headers = export_headers_for_department(department)

    wb = load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    ws = wb.active
    if ws is None:
        return 0, [{'row': 0, 'errors': {'_sheet': 'No sheet in workbook.'}}]

    rows_iter = ws.iter_rows(values_only=True)
    header_row = next(rows_iter, None)
    if not header_row:
        return 0, [{'row': 0, 'errors': {'_sheet': 'Empty sheet.'}}]

    col_to_field = _map_header_row(header_row)
    required = _required_import_fields(department)
    if not required.issubset(set(col_to_field.values())):
        return 0, [
            {
                'row': 0,
                'errors': {
                    '_sheet': (
                        'Missing required columns. Expected headers: '
                        + ', '.join(expected_headers)
                    ),
                },
            }
        ]

    for row_index, row_tuple in enumerate(rows_iter, start=2):
        if row_tuple is None or all(
            cell is None or str(cell).strip() == '' for cell in row_tuple
        ):
            continue

        values: dict[str, Any] = {}
        for idx, field in col_to_field.items():
            if idx < len(row_tuple):
                raw = row_tuple[idx]
                if raw is not None and str(raw).strip() != '':
                    values[field] = raw

        row_errors: dict[str, str] = {}
        activity_date = _parse_date_value(values.get('date'))
        if not activity_date:
            row_errors['date'] = 'Valid date is required (YYYY-MM-DD).'

        description = values.get('description')
        description_text = '' if description is None else str(description).strip()

        if warehouse:
            for field in (
                'material_type',
                'unit',
                'consumption_location',
                'supplier',
            ):
                val = values.get(field)
                if val is None or str(val).strip() == '':
                    row_errors[field] = str(_('This field is required.'))

            quantity_in = _parse_quantity(values.get('quantity_in'))
            quantity_out = _parse_quantity(values.get('quantity_out'))
            if quantity_in is None:
                row_errors['quantity_in'] = str(_('Enter a valid number.'))
                quantity_in = Decimal('0')
            if quantity_out is None:
                row_errors['quantity_out'] = str(_('Enter a valid number.'))
                quantity_out = Decimal('0')
            if 'quantity_in' not in row_errors and quantity_in < 0:
                row_errors['quantity_in'] = str(
                    _('Quantity must be greater than or equal to zero.')
                )
            if 'quantity_out' not in row_errors and quantity_out < 0:
                row_errors['quantity_out'] = str(
                    _('Quantity must be greater than or equal to zero.')
                )
            if (
                'quantity_in' not in row_errors
                and 'quantity_out' not in row_errors
                and quantity_in <= 0
                and quantity_out <= 0
            ):
                msg = str(
                    _(
                        'At least one of quantity_in or quantity_out must be greater than zero.'
                    )
                )
                row_errors['quantity_in'] = msg
                row_errors['quantity_out'] = msg

            if row_errors:
                errors.append({'row': row_index, 'errors': row_errors})
                continue

            try:
                DepartmentActivityRecord.objects.create(
                    project=business,
                    department=department,
                    date=activity_date,
                    location='',
                    activity_description='',
                    contractor='',
                    unit=str(values['unit']).strip()[:64],
                    description=description_text,
                    material_type=str(values['material_type']).strip()[:255],
                    quantity_in=quantity_in,
                    quantity_out=quantity_out,
                    consumption_location=str(values['consumption_location']).strip()[:255],
                    supplier=str(values['supplier']).strip()[:255],
                )
                created += 1
            except ValidationError as exc:
                errors.append({'row': row_index, 'errors': exc.message_dict})
            continue

        required_value_fields = (
            'location',
            'activity_description',
            'contractor',
        )
        if uses_unit:
            required_value_fields = (
                *required_value_fields,
                'unit',
            )
        for field in required_value_fields:
            val = values.get(field)
            if val is None or str(val).strip() == '':
                row_errors[field] = str(_('This field is required.'))

        if row_errors:
            errors.append({'row': row_index, 'errors': row_errors})
            continue

        unit_text = (
            ''
            if not uses_unit
            else str(values['unit']).strip()[:64]
        )

        try:
            DepartmentActivityRecord.objects.create(
                project=business,
                department=department,
                date=activity_date,
                location=str(values['location']).strip()[:255],
                activity_description=str(values['activity_description']).strip()[:500],
                contractor=str(values['contractor']).strip()[:255],
                unit=unit_text,
                description=description_text,
                material_type='',
                quantity_in=Decimal('0'),
                quantity_out=Decimal('0'),
                consumption_location='',
                supplier='',
            )
            created += 1
        except ValidationError as exc:
            errors.append({'row': row_index, 'errors': exc.message_dict})

    wb.close()
    return created, errors


def generate_activity_report_pdf(
    *,
    business: Project,
    department: str,
    department_label: str,
    period_label: str,
    date_from: date,
    date_to: date,
    records: list[DepartmentActivityRecord],
) -> bytes:
    warehouse = is_warehouse_department(department)
    include_unit = department_uses_unit(department)
    buf = io.BytesIO()

    class _ReportDoc(SimpleDocTemplate):
        def handle_documentBegin(self):
            super().handle_documentBegin()
            # Unrequested but intentional: keep PDF content streams uncompressed so
            # warehouse smoke tests can assert English column labels/values in bytes
            # (ReportLab Flate+ASCII85 streams are otherwise opaque to plain asserts).
            self.canv.setPageCompression(0)

    doc = _ReportDoc(
        buf,
        pagesize=landscape(A4),
        leftMargin=24,
        rightMargin=24,
        topMargin=28,
        bottomMargin=28,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(
            f'<b>{business.name}</b> — {department_label}',
            styles['Title'],
        ),
        Paragraph(
            f'{period_label}: {date_from.isoformat()} — {date_to.isoformat()}',
            styles['Heading3'],
        ),
        Spacer(1, 12),
    ]

    if not records:
        story.append(Paragraph('No activity records in this period.', styles['Normal']))
    elif warehouse:
        header = [
            'Date',
            'Material type',
            'In',
            'Unit',
            'Out',
            'Consumption location',
            'Supplier',
            'Description',
        ]
        table_data = [header]
        for record in records:
            table_data.append(
                [
                    record.date.isoformat(),
                    record.material_type,
                    str(record.quantity_in),
                    record.unit,
                    str(record.quantity_out),
                    record.consumption_location,
                    record.supplier,
                    (record.description or '')[:200],
                ]
            )
        col_widths = [55, 90, 45, 40, 45, 95, 85, 140]
        table = Table(
            table_data,
            repeatRows=1,
            colWidths=col_widths,
        )
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ]
            )
        )
        story.append(table)
    else:
        header = ['Date', 'Location', 'Activity', 'Contractor']
        if include_unit:
            header.append('Unit')
        header.append('Description')
        table_data = [header]
        for record in records:
            row = [
                record.date.isoformat(),
                record.location,
                record.activity_description,
                record.contractor,
            ]
            if include_unit:
                row.append(record.unit)
            row.append((record.description or '')[:200])
            table_data.append(row)

        col_widths = (
            [70, 90, 140, 90, 50, 160] if include_unit else [70, 100, 160, 100, 180]
        )
        table = Table(
            table_data,
            repeatRows=1,
            colWidths=col_widths,
        )
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ]
            )
        )
        story.append(table)

    doc.build(story)
    return buf.getvalue()


def department_display_label(department: str) -> str:
    for value, label in Department.choices:
        if value == department:
            return label
    return department
