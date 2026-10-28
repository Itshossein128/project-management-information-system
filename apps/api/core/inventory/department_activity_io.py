"""
Excel export/import, multi-sheet workbooks with native =SUM formulas, and PDF reports for department activity records.
"""
from __future__ import annotations

import io
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from business_meta.models import Project
from common.jalali import gregorian_to_jalali, parse_jalali_or_gregorian
from projects.contractor_utils import parse_contractor_id, resolve_active_contractor

from .department_activity_services import normalize_department
from .models import (
    Department,
    DepartmentActivityRecord,
    department_uses_unit,
    is_warehouse_department,
)

# Typography and palette for official Excel output
FONT_FAMILY = 'Tahoma'
THIN_SIDE = Side(border_style='thin', color='CBD5E1')
BORDER_ALL = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)

FILL_TITLE = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
FILL_HEADER = PatternFill(start_color='2563EB', end_color='2563EB', fill_type='solid')
FILL_ZEBRA = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
FILL_TOTAL = PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid')

FONT_TITLE = Font(name=FONT_FAMILY, size=13, bold=True, color='FFFFFF')
FONT_SUBTITLE = Font(name=FONT_FAMILY, size=10, bold=False, color='334155')
FONT_HEADER = Font(name=FONT_FAMILY, size=10, bold=True, color='FFFFFF')
FONT_DATA = Font(name=FONT_FAMILY, size=9, bold=False, color='0F172A')
FONT_TOTAL = Font(name=FONT_FAMILY, size=10, bold=True, color='0F172A')

ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal='right', vertical='center', wrap_text=True)

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

EXPORT_HEADERS = EXPORT_HEADERS_WITH_UNIT

HEADER_ALIASES: dict[str, list[str]] = {
    'date': ['date', 'تاریخ', 'Date'],
    'location': [
        'location',
        'موقعیت',
        'جبهه کاری',
        'جبهه کاری / موقعیت',
        'موقعیت / جبهه کاری',
        'Location',
    ],
    'activity_description': [
        'activity_description',
        'activity description',
        'شرح فعالیت',
        'فعالیت',
        'Activity',
    ],
    'contractor': ['contractor', 'پیمانکار', 'پیمانگار', 'Contractor'],
    'executed_quantity': [
        'executed_quantity',
        'executed quantity',
        'مقدار اجرا',
        'مقدار',
        'حجم',
        'حجم اجرا',
        'Quantity',
        'quantity',
    ],
    'unit': ['unit', 'واحد', 'Unit'],
    'description': ['description', 'توضیحات', 'Notes', 'notes', 'یادداشت'],
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
        'مقدار ورودی',
        'Inbound',
        'In',
    ],
    'quantity_out': [
        'quantity_out',
        'quantity out',
        'خروجی',
        'مقدار خروجی',
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


def normalize_persian_numbers(raw: Any) -> str:
    """Normalize Persian/Arabic digits to standard ASCII numerals."""
    if raw is None:
        return ''
    text = str(raw).strip()
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    for p, e in zip(persian_digits, '0123456789'):
        text = text.replace(p, e)
    for a, e in zip(arabic_digits, '0123456789'):
        text = text.replace(a, e)
    return text


def export_headers_for_department(department: str) -> list[str]:
    dept_norm = normalize_department(department)
    if is_warehouse_department(dept_norm or ''):
        return list(EXPORT_HEADERS_WAREHOUSE)
    if department_uses_unit(dept_norm or ''):
        return list(EXPORT_HEADERS_WITH_UNIT)
    return list(EXPORT_HEADERS_WITHOUT_UNIT)


def _adjust_column_widths(ws, max_cols: int, min_width: int = 12, max_width: int = 40):
    for col_idx in range(1, max_cols + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for row in range(1, ws.max_row + 1):
            cell_val = ws.cell(row=row, column=col_idx).value
            if cell_val is not None:
                val_str = str(cell_val)
                if not val_str.startswith('='):
                    max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(min_width, min(max_len + 4, max_width))


def export_activities_to_xlsx(
    records: list[DepartmentActivityRecord],
    *,
    department: str | None = None,
    persian_headers: bool = True,
) -> bytes:
    resolved_department = normalize_department(department)
    if resolved_department is None and records:
        resolved_department = normalize_department(records[0].department)
    resolved_department = resolved_department or Department.BUILDINGS

    warehouse = is_warehouse_department(resolved_department)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Activity log'

    if persian_headers:
        ws.sheet_view.rightToLeft = True
        if warehouse:
            headers = [
                'تاریخ',
                'نوع مصالح',
                'مقدار ورودی',
                'واحد',
                'مقدار خروجی',
                'محل مصرف',
                'تامین‌کننده',
                'توضیحات',
            ]
        elif not department_uses_unit(resolved_department):
            headers = [
                'تاریخ',
                'موقعیت / جبهه کاری',
                'شرح فعالیت',
                'پیمانکار',
                'مقدار اجرا',
                'توضیحات',
            ]
        else:
            headers = [
                'تاریخ',
                'موقعیت / جبهه کاری',
                'شرح فعالیت',
                'پیمانکار',
                'مقدار اجرا',
                'واحد',
                'توضیحات',
            ]
        ws.append(headers)
        ws.row_dimensions[1].height = 24
        for col_idx in range(1, len(headers) + 1):
            c = ws.cell(row=1, column=col_idx)
            c.font = FONT_HEADER
            c.fill = FILL_HEADER
            c.alignment = ALIGN_CENTER
            c.border = BORDER_ALL

        for row_idx, record in enumerate(records, start=2):
            ws.row_dimensions[row_idx].height = 20
            row_fill = FILL_ZEBRA if row_idx % 2 == 0 else PatternFill(fill_type=None)
            if warehouse:
                vals = [
                    record.date.isoformat() if record.date else '',
                    record.material_type,
                    float(record.quantity_in or 0),
                    record.unit,
                    float(record.quantity_out or 0),
                    record.consumption_location,
                    record.supplier,
                    record.description or '',
                ]
            elif not department_uses_unit(resolved_department):
                vals = [
                    record.date.isoformat() if record.date else '',
                    record.location,
                    record.activity_description,
                    record.contractor,
                    float(record.executed_quantity or 0),
                    record.description or '',
                ]
            else:
                vals = [
                    record.date.isoformat() if record.date else '',
                    record.location,
                    record.activity_description,
                    record.contractor,
                    float(record.executed_quantity or 0),
                    record.unit,
                    record.description or '',
                ]
            for col_idx, val in enumerate(vals, start=1):
                c = ws.cell(row=row_idx, column=col_idx, value=val)
                c.font = FONT_DATA
                c.border = BORDER_ALL
                if row_fill.fill_type:
                    c.fill = row_fill
                if col_idx in (1, 4 if warehouse else 6):
                    c.alignment = ALIGN_CENTER
                else:
                    c.alignment = ALIGN_RIGHT
        _adjust_column_widths(ws, len(headers))
    else:
        # Legacy raw headers for compatibility
        headers = export_headers_for_department(resolved_department)
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
                include_unit = department_uses_unit(resolved_department)
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


def generate_daily_activity_report_xlsx(
    *,
    business: Project,
    department: str,
    report_date: date,
    records: list[DepartmentActivityRecord],
) -> bytes:
    resolved_dept = normalize_department(department) or department
    dept_label = department_display_label(department)
    warehouse = is_warehouse_department(resolved_dept)

    wb = Workbook()
    ws = wb.active
    ws.title = f'گزارش {dept_label}'[:31]
    ws.sheet_view.rightToLeft = True

    date_fa = gregorian_to_jalali(report_date)
    proj_name = getattr(business, 'name', '') or getattr(business, 'project_name', '')
    proj_code = getattr(business, 'project_code', '')

    if warehouse:
        headers = ['ردیف', 'تاریخ', 'نوع مصالح', 'مقدار ورودی', 'واحد', 'مقدار خروجی', 'محل مصرف', 'تامین‌کننده', 'توضیحات']
    else:
        headers = ['ردیف', 'تاریخ', 'شرح فعالیت', 'پیمانکار', 'جبهه کاری / موقعیت', 'مقدار اجرا', 'واحد', 'توضیحات']

    num_cols = len(headers)

    # Row 1: Merged Title
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
    title_cell = ws.cell(row=1, column=1)
    if warehouse:
        title_cell.value = f'گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}'
    else:
        title_cell.value = f'گزارش روزانه فعالیت دپارتمان {dept_label} — {proj_name}'
    title_cell.font = FONT_TITLE
    title_cell.fill = FILL_TITLE
    title_cell.alignment = ALIGN_CENTER
    ws.row_dimensions[1].height = 32

    # Row 2: Subtitle
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=num_cols)
    sub_cell = ws.cell(row=2, column=1)
    sub_cell.value = f'تاریخ گزارش: {date_fa} ({report_date.isoformat()}) | کد کارگاه: {proj_code}'
    sub_cell.font = FONT_SUBTITLE
    sub_cell.alignment = ALIGN_RIGHT
    ws.row_dimensions[2].height = 20

    # Row 3: Blank
    ws.row_dimensions[3].height = 8

    # Row 4: Column Headers
    ws.row_dimensions[4].height = 24
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = BORDER_ALL

    current_row = 5
    if not records:
        ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=num_cols)
        empty_cell = ws.cell(row=5, column=1, value='رکوردی در این روز ثبت نشده است')
        empty_cell.font = FONT_DATA
        empty_cell.alignment = ALIGN_CENTER
        empty_cell.border = BORDER_ALL
        for c in range(1, num_cols + 1):
            ws.cell(row=5, column=c).border = BORDER_ALL
        current_row = 6
    else:
        for idx, rec in enumerate(records, start=1):
            ws.row_dimensions[current_row].height = 20
            row_fill = FILL_ZEBRA if idx % 2 == 0 else PatternFill(fill_type=None)
            if warehouse:
                vals = [
                    idx,
                    rec.date.isoformat() if rec.date else '',
                    rec.material_type,
                    float(rec.quantity_in or 0),
                    rec.unit,
                    float(rec.quantity_out or 0),
                    rec.consumption_location,
                    rec.supplier,
                    rec.description or '',
                ]
            else:
                vals = [
                    idx,
                    rec.date.isoformat() if rec.date else '',
                    rec.activity_description,
                    rec.contractor,
                    rec.location,
                    float(rec.executed_quantity or 0),
                    rec.unit,
                    rec.description or '',
                ]
            for col_idx, val in enumerate(vals, start=1):
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = FONT_DATA
                if row_fill.fill_type:
                    cell.fill = row_fill
                cell.border = BORDER_ALL
                if col_idx in (1, 2, 5 if not warehouse else 4, 6, 7):
                    cell.alignment = ALIGN_CENTER
                else:
                    cell.alignment = ALIGN_RIGHT
            current_row += 1

    # Total Row (Tier 1)
    ws.row_dimensions[current_row].height = 24
    if warehouse:
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        lbl_in = ws.cell(row=current_row, column=1, value='مجموع ورودی روز:')
        lbl_in.font = FONT_TOTAL
        lbl_in.alignment = ALIGN_RIGHT
        lbl_in.fill = FILL_TOTAL

        sum_in = ws.cell(row=current_row, column=4)
        sum_in.value = f'=SUM(D5:D{current_row - 1})' if records else 0
        sum_in.font = FONT_TOTAL
        sum_in.fill = FILL_TOTAL
        sum_in.alignment = ALIGN_CENTER

        lbl_out = ws.cell(row=current_row, column=5, value='مجموع خروجی روز:')
        lbl_out.font = FONT_TOTAL
        lbl_out.alignment = ALIGN_RIGHT
        lbl_out.fill = FILL_TOTAL

        sum_out = ws.cell(row=current_row, column=6)
        sum_out.value = f'=SUM(F5:F{current_row - 1})' if records else 0
        sum_out.font = FONT_TOTAL
        sum_out.fill = FILL_TOTAL
        sum_out.alignment = ALIGN_CENTER

        for c in range(1, num_cols + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.border = BORDER_ALL
            cell.fill = FILL_TOTAL

        # Tier 2: Net Daily Balance
        net_row = current_row + 1
        ws.row_dimensions[net_row].height = 24
        ws.merge_cells(start_row=net_row, start_column=1, end_row=net_row, end_column=5)
        net_lbl = ws.cell(row=net_row, column=1, value='تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):')
        net_lbl.font = FONT_TOTAL
        net_lbl.alignment = ALIGN_RIGHT
        net_lbl.fill = FILL_TOTAL

        net_val = ws.cell(row=net_row, column=6)
        net_val.value = f'=D{current_row}-F{current_row}' if records else 0
        net_val.font = FONT_TOTAL
        net_val.fill = FILL_TOTAL
        net_val.alignment = ALIGN_CENTER

        for c in range(1, num_cols + 1):
            cell = ws.cell(row=net_row, column=c)
            cell.border = BORDER_ALL
            cell.fill = FILL_TOTAL
    else:
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=5)
        lbl = ws.cell(row=current_row, column=1, value='مجموع احجام اجرایی روز:')
        lbl.font = FONT_TOTAL
        lbl.alignment = ALIGN_RIGHT
        lbl.fill = FILL_TOTAL

        sum_cell = ws.cell(row=current_row, column=6)
        sum_cell.value = f'=SUM(F5:F{current_row - 1})' if records else 0
        sum_cell.font = FONT_TOTAL
        sum_cell.fill = FILL_TOTAL
        sum_cell.alignment = ALIGN_CENTER

        for c in range(1, num_cols + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.border = BORDER_ALL
            cell.fill = FILL_TOTAL

    _adjust_column_widths(ws, num_cols)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def generate_weekly_activity_report_xlsx(
    *,
    business: Project,
    department: str,
    week_start: date,
    records: list[DepartmentActivityRecord],
    opening_balances: dict[tuple[str, str], float | Decimal] | None = None,
) -> bytes:
    resolved_dept = normalize_department(department) or department
    dept_label = department_display_label(department)
    warehouse = is_warehouse_department(resolved_dept)

    wb = Workbook()
    day_names = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
    day_dates = [week_start + timedelta(days=i) for i in range(7)]

    proj_name = getattr(business, 'name', '') or getattr(business, 'project_name', '')
    proj_code = getattr(business, 'project_code', '')

    if warehouse:
        headers = ['ردیف', 'تاریخ', 'نوع مصالح', 'مقدار ورودی', 'واحد', 'مقدار خروجی', 'محل مصرف', 'تامین‌کننده', 'توضیحات']
    else:
        headers = ['ردیف', 'تاریخ', 'شرح فعالیت', 'پیمانکار', 'جبهه کاری / موقعیت', 'مقدار اجرا', 'واحد', 'توضیحات']
    num_cols = len(headers)

    # 1-7: Daily Sheets
    for i, (day_name, day_date) in enumerate(zip(day_names, day_dates)):
        if i == 0:
            ws = wb.active
            ws.title = day_name
        else:
            ws = wb.create_sheet(title=day_name)
        ws.sheet_view.rightToLeft = True

        day_fa = gregorian_to_jalali(day_date)
        day_records = [r for r in records if r.date == day_date]

        # Title
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
        t_cell = ws.cell(row=1, column=1)
        t_cell.value = f'گزارش روزانه {day_name} ({day_fa}) — دپارتمان {dept_label} — {proj_name}'
        t_cell.font = FONT_TITLE
        t_cell.fill = FILL_TITLE
        t_cell.alignment = ALIGN_CENTER
        ws.row_dimensions[1].height = 32

        # Subtitle
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=num_cols)
        s_cell = ws.cell(row=2, column=1)
        s_cell.value = f'کد پروژه: {proj_code} | تاریخ میلادی: {day_date.isoformat()}'
        s_cell.font = FONT_SUBTITLE
        s_cell.alignment = ALIGN_RIGHT
        ws.row_dimensions[2].height = 20
        ws.row_dimensions[3].height = 8

        # Headers
        ws.row_dimensions[4].height = 24
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=col_idx, value=h)
            cell.font = FONT_HEADER
            cell.fill = FILL_HEADER
            cell.alignment = ALIGN_CENTER
            cell.border = BORDER_ALL

        current_row = 5
        if not day_records:
            ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=num_cols)
            empty_cell = ws.cell(row=5, column=1, value='رکوردی در این روز ثبت نشده است')
            empty_cell.font = FONT_DATA
            empty_cell.alignment = ALIGN_CENTER
            for c in range(1, num_cols + 1):
                ws.cell(row=5, column=c).border = BORDER_ALL
            current_row = 6
        else:
            for idx, rec in enumerate(day_records, start=1):
                ws.row_dimensions[current_row].height = 20
                row_fill = FILL_ZEBRA if idx % 2 == 0 else PatternFill(fill_type=None)
                if warehouse:
                    vals = [
                        idx,
                        rec.date.isoformat() if rec.date else '',
                        rec.material_type,
                        float(rec.quantity_in or 0),
                        rec.unit,
                        float(rec.quantity_out or 0),
                        rec.consumption_location,
                        rec.supplier,
                        rec.description or '',
                    ]
                else:
                    vals = [
                        idx,
                        rec.date.isoformat() if rec.date else '',
                        rec.activity_description,
                        rec.contractor,
                        rec.location,
                        float(rec.executed_quantity or 0),
                        rec.unit,
                        rec.description or '',
                    ]
                for col_idx, val in enumerate(vals, start=1):
                    cell = ws.cell(row=current_row, column=col_idx, value=val)
                    cell.font = FONT_DATA
                    if row_fill.fill_type:
                        cell.fill = row_fill
                    cell.border = BORDER_ALL
                    if col_idx in (1, 2, 5 if not warehouse else 4, 6, 7):
                        cell.alignment = ALIGN_CENTER
                    else:
                        cell.alignment = ALIGN_RIGHT
                current_row += 1

        # Total Row
        ws.row_dimensions[current_row].height = 24
        if warehouse:
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
            lbl_in = ws.cell(row=current_row, column=1, value='مجموع ورودی:')
            lbl_in.font = FONT_TOTAL
            lbl_in.alignment = ALIGN_RIGHT
            lbl_in.fill = FILL_TOTAL

            sum_in = ws.cell(row=current_row, column=4)
            sum_in.value = f'=SUM(D5:D{current_row - 1})'
            sum_in.font = FONT_TOTAL
            sum_in.fill = FILL_TOTAL
            sum_in.alignment = ALIGN_CENTER

            lbl_out = ws.cell(row=current_row, column=5, value='مجموع خروجی:')
            lbl_out.font = FONT_TOTAL
            lbl_out.alignment = ALIGN_RIGHT
            lbl_out.fill = FILL_TOTAL

            sum_out = ws.cell(row=current_row, column=6)
            sum_out.value = f'=SUM(F5:F{current_row - 1})'
            sum_out.font = FONT_TOTAL
            sum_out.fill = FILL_TOTAL
            sum_out.alignment = ALIGN_CENTER

            for c in range(1, num_cols + 1):
                cell = ws.cell(row=current_row, column=c)
                cell.border = BORDER_ALL
                cell.fill = FILL_TOTAL
        else:
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=5)
            lbl = ws.cell(row=current_row, column=1, value='مجموع احجام اجرایی روز:')
            lbl.font = FONT_TOTAL
            lbl.alignment = ALIGN_RIGHT
            lbl.fill = FILL_TOTAL

            sum_cell = ws.cell(row=current_row, column=6)
            sum_cell.value = f'=SUM(F5:F{current_row - 1})'
            sum_cell.font = FONT_TOTAL
            sum_cell.fill = FILL_TOTAL
            sum_cell.alignment = ALIGN_CENTER

            for c in range(1, num_cols + 1):
                cell = ws.cell(row=current_row, column=c)
                cell.border = BORDER_ALL
                cell.fill = FILL_TOTAL

        _adjust_column_widths(ws, num_cols)

    # 8th Sheet: Summary Sheet (خلاصه هفتگی یا بالانس تجمعی مصالح)
    if warehouse:
        summary_ws = wb.create_sheet(title='بالانس تجمعی مصالح')
        summary_ws.sheet_view.rightToLeft = True

        sum_headers = [
            'ردیف',
            'نوع مصالح',
            'واحد',
            'موجودی اول دوره',
            'کل ورودی دوره',
            'کل خروجی دوره',
            'مانده پای کار / موجودی پایان دوره',
            'توضیحات و وضعیت اقلام',
        ]
        s_cols = len(sum_headers)

        summary_ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=s_cols)
        s_title = summary_ws.cell(row=1, column=1)
        s_title.value = f'گزارش بالانس تجمعی مصالح کارگاه — {proj_name}'
        s_title.font = FONT_TITLE
        s_title.fill = FILL_TITLE
        s_title.alignment = ALIGN_CENTER
        summary_ws.row_dimensions[1].height = 32

        week_end_date = week_start + timedelta(days=6)
        summary_ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=s_cols)
        s_sub = summary_ws.cell(row=2, column=1)
        s_sub.value = f'هفته کاری از {gregorian_to_jalali(week_start)} تا {gregorian_to_jalali(week_end_date)} | کد کارگاه: {proj_code}'
        s_sub.font = FONT_SUBTITLE
        s_sub.alignment = ALIGN_RIGHT
        summary_ws.row_dimensions[2].height = 20
        summary_ws.row_dimensions[3].height = 8

        # Summary table header
        summary_ws.row_dimensions[4].height = 24
        for col_idx, h in enumerate(sum_headers, start=1):
            cell = summary_ws.cell(row=4, column=col_idx, value=h)
            cell.font = FONT_HEADER
            cell.fill = FILL_HEADER
            cell.alignment = ALIGN_CENTER
            cell.border = BORDER_ALL

        # Collect unique (material_type, unit) keys from both opening_balances and records
        all_keys: set[tuple[str, str]] = set()
        if opening_balances:
            for k in opening_balances.keys():
                all_keys.add((k[0].strip(), k[1].strip()))

        weekly_in: dict[tuple[str, str], float] = {}
        weekly_out: dict[tuple[str, str], float] = {}
        material_notes: dict[tuple[str, str], list[str]] = {}

        for rec in records:
            k = ((rec.material_type or '').strip(), (rec.unit or '').strip())
            all_keys.add(k)
            weekly_in[k] = weekly_in.get(k, 0.0) + float(rec.quantity_in or 0)
            weekly_out[k] = weekly_out.get(k, 0.0) + float(rec.quantity_out or 0)
            if rec.description:
                desc = rec.description.strip()
                if desc and desc not in material_notes.setdefault(k, []):
                    material_notes[k].append(desc)

        sorted_keys = sorted(all_keys, key=lambda x: (x[0], x[1]))

        s_row = 5
        if not sorted_keys:
            summary_ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=s_cols)
            empty_c = summary_ws.cell(row=5, column=1, value='رکوردی در این هفته ثبت نشده است')
            empty_c.font = FONT_DATA
            empty_c.alignment = ALIGN_CENTER
            for c in range(1, s_cols + 1):
                summary_ws.cell(row=5, column=c).border = BORDER_ALL
            s_row = 6
        else:
            for idx, key in enumerate(sorted_keys, start=1):
                summary_ws.row_dimensions[s_row].height = 20
                row_fill = FILL_ZEBRA if idx % 2 == 0 else PatternFill(fill_type=None)

                op_balance = float(opening_balances.get(key, 0.0)) if opening_balances else 0.0
                tot_in = weekly_in.get(key, 0.0)
                tot_out = weekly_out.get(key, 0.0)
                notes_str = '؛ '.join(material_notes.get(key, []))

                row_data = [
                    idx,
                    key[0],
                    key[1],
                    op_balance,
                    tot_in,
                    tot_out,
                    f'=D{s_row}+E{s_row}-F{s_row}',
                    notes_str,
                ]

                for col_idx, val in enumerate(row_data, start=1):
                    cell = summary_ws.cell(row=s_row, column=col_idx, value=val)
                    cell.font = FONT_DATA
                    if row_fill.fill_type:
                        cell.fill = row_fill
                    cell.border = BORDER_ALL
                    if col_idx in (1, 3):
                        cell.alignment = ALIGN_CENTER
                    elif col_idx in (4, 5, 6, 7):
                        cell.alignment = ALIGN_CENTER
                    else:
                        cell.alignment = ALIGN_RIGHT
                s_row += 1

        # Warehouse Summary Total Row
        summary_ws.row_dimensions[s_row].height = 24
        summary_ws.merge_cells(start_row=s_row, start_column=1, end_row=s_row, end_column=3)
        tot_lbl = summary_ws.cell(row=s_row, column=1, value='مجموع کل بالانس مصالح انبار:')
        tot_lbl.font = FONT_TOTAL
        tot_lbl.alignment = ALIGN_RIGHT
        tot_lbl.fill = FILL_TOTAL

        for c_idx, c_letter in enumerate(['D', 'E', 'F', 'G'], start=4):
            sum_c = summary_ws.cell(row=s_row, column=c_idx)
            # Keep native formulas even when the week has no material rows.  The
            # placeholder row is intentionally included so Excel evaluates a
            # valid zero total without producing an invalid/empty range.
            sum_c.value = f'=SUM({c_letter}5:{c_letter}{s_row - 1})'
            sum_c.font = FONT_TOTAL
            sum_c.fill = FILL_TOTAL
            sum_c.alignment = ALIGN_CENTER

        for c in range(1, s_cols + 1):
            summary_ws.cell(row=s_row, column=c).border = BORDER_ALL
            summary_ws.cell(row=s_row, column=c).fill = FILL_TOTAL

        _adjust_column_widths(summary_ws, s_cols)
    else:
        summary_ws = wb.create_sheet(title='خلاصه هفتگی')
        summary_ws.sheet_view.rightToLeft = True

        sum_headers = [
            'ردیف',
            'شرح فعالیت / آیتم',
            'پیمانکار',
            'واحد',
            'شنبه',
            'یکشنبه',
            'دوشنبه',
            'سه‌شنبه',
            'چهارشنبه',
            'پنجشنبه',
            'جمعه',
            'مجموع کل هفته',
        ]
        s_cols = len(sum_headers)

        summary_ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=s_cols)
        s_title = summary_ws.cell(row=1, column=1)
        s_title.value = f'گزارش جمع‌بندی هفتگی دپارتمان {dept_label} — {proj_name}'
        s_title.font = FONT_TITLE
        s_title.fill = FILL_TITLE
        s_title.alignment = ALIGN_CENTER
        summary_ws.row_dimensions[1].height = 32

        week_end_date = week_start + timedelta(days=6)
        summary_ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=s_cols)
        s_sub = summary_ws.cell(row=2, column=1)
        s_sub.value = f'هفته کاری از {gregorian_to_jalali(week_start)} تا {gregorian_to_jalali(week_end_date)} | کد کارگاه: {proj_code}'
        s_sub.font = FONT_SUBTITLE
        s_sub.alignment = ALIGN_RIGHT
        summary_ws.row_dimensions[2].height = 20
        summary_ws.row_dimensions[3].height = 8

        # Summary table header
        summary_ws.row_dimensions[4].height = 24
        for col_idx, h in enumerate(sum_headers, start=1):
            cell = summary_ws.cell(row=4, column=col_idx, value=h)
            cell.font = FONT_HEADER
            cell.fill = FILL_HEADER
            cell.alignment = ALIGN_CENTER
            cell.border = BORDER_ALL

        # Group records by (item_desc, entity_name, unit)
        grouped: dict[tuple[str, str, str], dict[int, float]] = {}
        for rec in records:
            key = (rec.activity_description, rec.contractor, rec.unit)
            qty = float(rec.executed_quantity or 0)

            if key not in grouped:
                grouped[key] = {d_idx: 0.0 for d_idx in range(7)}

            for d_idx, day_d in enumerate(day_dates):
                if rec.date == day_d:
                    grouped[key][d_idx] += qty

        s_row = 5
        if not grouped:
            summary_ws.merge_cells(start_row=5, start_column=1, end_row=5, end_column=s_cols)
            empty_c = summary_ws.cell(row=5, column=1, value='رکوردی در این هفته ثبت نشده است')
            empty_c.font = FONT_DATA
            empty_c.alignment = ALIGN_CENTER
            for c in range(1, s_cols + 1):
                summary_ws.cell(row=5, column=c).border = BORDER_ALL
            s_row = 6
        else:
            for idx, (key, days_dict) in enumerate(grouped.items(), start=1):
                summary_ws.row_dimensions[s_row].height = 20
                row_fill = FILL_ZEBRA if idx % 2 == 0 else PatternFill(fill_type=None)

                row_data = [
                    idx,
                    key[0],
                    key[1],
                    key[2],
                    days_dict[0],
                    days_dict[1],
                    days_dict[2],
                    days_dict[3],
                    days_dict[4],
                    days_dict[5],
                    days_dict[6],
                    f'=SUM(E{s_row}:K{s_row})',
                ]

                for col_idx, val in enumerate(row_data, start=1):
                    cell = summary_ws.cell(row=s_row, column=col_idx, value=val)
                    cell.font = FONT_DATA
                    if row_fill.fill_type:
                        cell.fill = row_fill
                    cell.border = BORDER_ALL
                    if col_idx in (1, 4):
                        cell.alignment = ALIGN_CENTER
                    elif col_idx in range(5, 13):
                        cell.alignment = ALIGN_CENTER
                    else:
                        cell.alignment = ALIGN_RIGHT
                s_row += 1

        # Weekly Summary Total Row
        summary_ws.row_dimensions[s_row].height = 24
        summary_ws.merge_cells(start_row=s_row, start_column=1, end_row=s_row, end_column=4)
        tot_lbl = summary_ws.cell(row=s_row, column=1, value='مجموع احجام کل روزانه:')
        tot_lbl.font = FONT_TOTAL
        tot_lbl.alignment = ALIGN_RIGHT
        tot_lbl.fill = FILL_TOTAL

        # Daily columns E through K and grand total L
        for c_idx, c_letter in enumerate(['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'], start=5):
            sum_c = summary_ws.cell(row=s_row, column=c_idx)
            sum_c.value = f'=SUM({c_letter}5:{c_letter}{s_row - 1})'
            sum_c.font = FONT_TOTAL
            sum_c.fill = FILL_TOTAL
            sum_c.alignment = ALIGN_CENTER

        for c in range(1, s_cols + 1):
            summary_ws.cell(row=s_row, column=c).border = BORDER_ALL
            summary_ws.cell(row=s_row, column=c).fill = FILL_TOTAL

        _adjust_column_widths(summary_ws, s_cols)

    _adjust_column_widths(summary_ws, s_cols)

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
    text = normalize_persian_numbers(raw)
    if not text:
        return None
    try:
        return parse_jalali_or_gregorian(text[:10])
    except Exception:
        pass
    parsed = parse_date(text[:10])
    if parsed:
        return parsed
    return None


def _parse_quantity(raw: Any) -> Decimal | None:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return Decimal('0')
    cleaned = normalize_persian_numbers(raw)
    if not cleaned:
        return Decimal('0')
    try:
        return Decimal(cleaned)
    except (InvalidOperation, TypeError, ValueError):
        return None


def _required_import_fields(department: str) -> set[str]:
    dept_norm = normalize_department(department)
    if is_warehouse_department(dept_norm or ''):
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
    if department_uses_unit(dept_norm or ''):
        required.add('unit')
    return required


def import_activities_from_xlsx(
    business: Project,
    department: str,
    file_bytes: bytes,
) -> tuple[int, list[dict]]:
    dept_norm = normalize_department(department) or department
    uses_unit = department_uses_unit(dept_norm)
    warehouse = is_warehouse_department(dept_norm)
    expected_headers = export_headers_for_department(dept_norm)

    wb = load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    ws = wb.active
    if ws is None:
        return 0, [{'row': 0, 'errors': {'_sheet': 'فایلی فاقد شیت معتبر است.'}}]

    rows_iter = ws.iter_rows(values_only=True)
    header_row = next(rows_iter, None)
    if not header_row:
        return 0, [{'row': 0, 'errors': {'_sheet': 'شیت اکسل خالی است.'}}]

    col_to_field = _map_header_row(header_row)
    required = _required_import_fields(dept_norm)
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

    errors: list[dict] = []
    records_to_create: list[DepartmentActivityRecord] = []

    with transaction.atomic():
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
                row_errors['date'] = 'فرمت تاریخ نامعتبر است (الگوی معتبر: YYYY-MM-DD)'

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
                row_code = None
                if (
                    'quantity_in' not in row_errors
                    and 'quantity_out' not in row_errors
                    and quantity_in <= 0
                    and quantity_out <= 0
                ):
                    msg = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
                    row_errors['quantity_in'] = msg
                    row_errors['quantity_out'] = msg
                    row_code = 'at_least_one_quantity_must_be_positive'

                if row_errors:
                    err_entry: dict[str, Any] = {'row': row_index, 'errors': row_errors}
                    if row_code:
                        err_entry['code'] = row_code
                    errors.append(err_entry)
                    continue

                records_to_create.append(
                    DepartmentActivityRecord(
                        project=business,
                        department=dept_norm,
                        date=activity_date,
                        location='',
                        activity_description='',
                        contractor='',
                        executed_quantity=Decimal('0.000'),
                        unit=str(values.get('unit') or '').strip()[:64],
                        description=description_text,
                        material_type=str(values.get('material_type') or '').strip()[:255],
                        quantity_in=quantity_in,
                        quantity_out=quantity_out,
                        consumption_location=str(values.get('consumption_location') or '').strip()[:255],
                        supplier=str(values.get('supplier') or '').strip()[:255],
                    )
                )
                continue

            # Non-warehouse validation
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

            # Executed quantity validation
            raw_eq = values.get('executed_quantity')
            if raw_eq is not None and str(raw_eq).strip() != '':
                eq_num = _parse_quantity(raw_eq)
                if eq_num is None:
                    row_errors['executed_quantity'] = 'مقدار اجرا باید عددی باشد'
                    exec_qty = Decimal('0.000')
                elif eq_num < 0:
                    row_errors['executed_quantity'] = 'مقدار اجرا باید عددی مثبت باشد'
                    exec_qty = Decimal('0.000')
                else:
                    exec_qty = eq_num
            else:
                exec_qty = Decimal('0.000')

            contractor_raw = str(values.get('contractor') or '').strip()
            stakeholder = None
            if contractor_raw:
                contractor_uuid = parse_contractor_id(contractor_raw)
                try:
                    stakeholder = resolve_active_contractor(
                        project_id=business.id,
                        contractor_id=contractor_uuid,
                        name=None if contractor_uuid else contractor_raw,
                    )
                except Exception:
                    row_errors['contractor'] = 'پیمانکار مشخص شده در این پروژه معتبر نیست'

            if row_errors:
                errors.append({'row': row_index, 'errors': row_errors})
                continue

            unit_text = (
                ''
                if not uses_unit
                else str(values.get('unit') or '').strip()[:64]
            )

            records_to_create.append(
                DepartmentActivityRecord(
                    project=business,
                    department=dept_norm,
                    date=activity_date,
                    location=str(values.get('location') or '').strip()[:255],
                    activity_description=str(values.get('activity_description') or '').strip()[:500],
                    contractor=stakeholder.name if stakeholder else contractor_raw,
                    contractor_ref=stakeholder,
                    executed_quantity=exec_qty,
                    unit=unit_text,
                    description=description_text,
                    material_type='',
                    quantity_in=Decimal('0'),
                    quantity_out=Decimal('0'),
                    consumption_location='',
                    supplier='',
                )
            )

        wb.close()

        if errors:
            transaction.set_rollback(True)
            return 0, errors

        DepartmentActivityRecord.objects.bulk_create(records_to_create)
        return len(records_to_create), []


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
    dept_norm = normalize_department(department)
    for value, label in Department.choices:
        if value == department or value == dept_norm:
            return label
    return department
