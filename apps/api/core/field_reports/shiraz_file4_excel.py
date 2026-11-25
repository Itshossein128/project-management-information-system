"""Shiraz FILE 4 Master Daily Report Excel Builder.

Replicates the physical and digital layout of Shiraz National Housing
FILE 4 daily reports (RTL layout, Tahoma font, 34 staff labor roles,
32 direct labor worker roles, native Excel `=SUM(...)` subtotal and grand total
formulas, incoming materials, concrete pours, machinery, and daily activities).
"""
from __future__ import annotations

import io
from datetime import timezone
from typing import Tuple
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.writer.excel import ExcelWriter

from common.jalali import gregorian_to_jalali
from field_reports.models import DailyReport
from field_reports.excel_safety import configure_report_print, literalize_cell
from field_reports.services.data_contract import (
    INCIDENT_LABELS_FA, SEVERITY_LABELS_FA, concrete_details_url, format_forecast, format_worked_shift, project_report_header,
    sampling_label,
)
from field_reports.services.form_profiles import (
    SHIRAZ_PROFILE,
    load_form_presentation_profile,
    resolve_labor_rows_for_profile,
)

# Public constants used by existing export callers.
_shiraz_profile = load_form_presentation_profile()
SHIRAZ_INDIRECT_ROLES = list(_shiraz_profile.indirect_slots)
SHIRAZ_DIRECT_ROLES = list(_shiraz_profile.direct_slots)

FONT_FAMILY = 'Tahoma'

STYLE_HEADER_FILL = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
STYLE_HEADER_FONT = Font(name=FONT_FAMILY, size=11, bold=True, color='FFFFFF')

STYLE_SECTION_FILL = PatternFill(start_color='2F5597', end_color='2F5597', fill_type='solid')
STYLE_SECTION_FONT = Font(name=FONT_FAMILY, size=10, bold=True, color='FFFFFF')

STYLE_SUBHEADER_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
STYLE_SUBHEADER_FONT = Font(name=FONT_FAMILY, size=9, bold=True, color='1F4E79')

STYLE_TOTAL_FILL = PatternFill(start_color='B4C6E7', end_color='B4C6E7', fill_type='solid')
STYLE_TOTAL_FONT = Font(name=FONT_FAMILY, size=9, bold=True, color='000000')

STYLE_DATA_FONT = Font(name=FONT_FAMILY, size=9)
STYLE_BOLD_FONT = Font(name=FONT_FAMILY, size=9, bold=True)

THIN_BORDER = Border(
    left=Side(style='thin', color='B0C4DE'),
    right=Side(style='thin', color='B0C4DE'),
    top=Side(style='thin', color='B0C4DE'),
    bottom=Side(style='thin', color='B0C4DE'),
)

ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal='right', vertical='center', wrap_text=True)
ALIGN_LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)


class _ReportWorkbookArchive(ZipFile):
    def open(self, name, mode='r', pwd=None, *, force_zip64=False):
        if mode == 'w' and isinstance(name, ZipInfo):
            # XLSX member timestamps must not depend on when the workbook was downloaded.
            name.date_time = (1980, 1, 1, 0, 0, 0)
        return super().open(name, mode, pwd, force_zip64=force_zip64)


class ShirazFile4ExcelBuilder:
    def __init__(self, report: DailyReport, *, language='fa', sheet=None):
        self.report = report
        self.english = language.startswith('en')
        if sheet is None:
            sheet = openpyxl.Workbook().active
            sheet.title = 'گزارش روزانه'
        self.ws = sheet
        self.ws.sheet_view.rightToLeft = True

    def build(self) -> Tuple[bytes, str]:
        self.populate()
        buf = io.BytesIO()
        workbook = self.ws.parent
        created = self.report.created_at.astimezone(timezone.utc).replace(tzinfo=None)
        workbook.properties.created = created
        workbook.properties.modified = created
        with _ReportWorkbookArchive(buf, 'w', ZIP_DEFLATED) as archive:
            ExcelWriter(workbook, archive).write_data()
        report_date = self.report.report_date
        shift = self.report.shift or 'full'
        formatted_date = gregorian_to_jalali(report_date).replace('/', '-')
        return buf.getvalue(), f'daily-report-{formatted_date}-{shift}.xlsx'

    def populate(self):
        self._write_header()
        current_row = 13
        current_row = self._write_manpower(current_row)
        current_row += 1
        current_row = self._write_materials(current_row)
        current_row += 1
        current_row = self._write_concrete(current_row)
        current_row += 1
        current_row = self._write_machinery(current_row)
        current_row += 1
        current_row = self._write_activities(current_row)
        current_row = self._write_general_activities(current_row + 1)
        current_row = self._write_visits_and_incidents(current_row + 1)
        self._write_notes(current_row + 1)

        self._auto_fit_columns()
        configure_report_print(self.ws, title_rows='1:4', landscape=True)

    def _write_header(self):
        ws = self.ws
        header = project_report_header(self.report)
        english = self.english
        project_name = header['project_name']
        contract_number = header['contract_number'] or 'ثبت نشده'
        jalali_date, dow = header['report_date'], header['day_of_week']

        # Row 1-2: Title block
        ws.merge_cells('A1:R2')
        title_cell = ws['A1']
        title_cell.value = f'گزارش روزانه کارگاه — {project_name} (شماره قرارداد: {contract_number})'
        title_cell.font = STYLE_HEADER_FONT
        title_cell.fill = STYLE_HEADER_FILL
        title_cell.alignment = ALIGN_CENTER

        # Row 3: Date, Day, Status, Weather
        ws.merge_cells('A3:B3')
        ws['A3'] = f'تاریخ: {jalali_date}'
        ws.merge_cells('C3:D3')
        ws['C3'] = f'روز: {dow}'
        ws.merge_cells('E3:F3')
        if self.report.site_status == 'active':
            status_text = 'فعال'
        elif self.report.site_status == 'inactive':
            reason = self.report.get_inactivity_reason_display()
            status_text = f'غیرفعال ({reason})' if reason else 'غیرفعال (دلیل ثبت نشده)'
        else:
            status_text = 'نامشخص'
        ws['E3'] = f'وضعیت کارگاه: {status_text}'
        ws.merge_cells('G3:H3')
        weather_text = self.report.get_weather_condition_display() if self.report.weather_condition else 'نامشخص'
        t_min = self.report.temp_min if self.report.temp_min is not None else '—'
        t_max = self.report.temp_max if self.report.temp_max is not None else '—'
        ws['G3'] = f'وضعیت جوی: {weather_text} (دما: {t_min} تا {t_max} °C)'
        ws.merge_cells('I3:J3')
        ws['I3'] = f'شیفت کاری: {self.report.get_shift_display()}'

        # Row 4: Shift hours
        ws.merge_cells('A4:C4')
        ws['A4'] = 'کارفرما: ' + (self.report.project.employer or 'ثبت نشده')
        ws.merge_cells('D4:F4')
        ws['D4'] = 'مشاور: ' + (self.report.project.consultant or 'ثبت نشده')
        ws.merge_cells('G4:J4')
        preparer = header['prepared_by_name'] or '—'
        ws['G4'] = f'تهیه‌کننده: {preparer}'

        if self.report.is_auto_summary:
            from field_reports.services.daily_report_aggregation import build_aggregation_meta

            meta = build_aggregation_meta(self.report.project_id, self.report.report_date, self.report)
            completeness = meta['completeness']
            state = completeness['state']
            if state == 'complete':
                message = 'وضعیت فعلی گزارش‌های واحدها: کامل'
            elif state == 'configuration_incomplete':
                message = 'هشدار وضعیت فعلی واحدها: پیکربندی مشخص نیست؛ کامل بودن گزارش قابل احراز نیست.'
            else:
                missing = '، '.join(completeness['missing_units']) or 'نامشخص'
                message = f'هشدار وضعیت فعلی واحدها: ناقص؛ واحدهای فاقد گزارش: {missing}'
            message += f' | آخرین تجمیع: {self.report.aggregated_at.isoformat() if self.report.aggregated_at else "ثبت نشده"}'
            ws.merge_cells('A5:L5')
            ws['A5'] = message
            ws['A5'].font = STYLE_BOLD_FONT
            ws['A5'].alignment = ALIGN_RIGHT
            ws.row_dimensions[5].height = 32
            comparison = meta['snapshot_source_comparison']
            if comparison != 'matching_fingerprint':
                ws.merge_cells('A6:L6')
                ws['A6'] = (
                    'هشدار: منابع پس از آخرین تجمیع تغییر کرده‌اند؛ این خروجی نسخه ذخیره‌شده است.'
                    if comparison == 'changed'
                    else 'هشدار: انطباق منابع با نسخه ذخیره‌شده قابل احراز نیست.'
                )
                ws['A6'].font = STYLE_BOLD_FONT
                ws['A6'].alignment = ALIGN_RIGHT
                ws.row_dimensions[6].height = 32

        official = header['official_numbering']
        weather = header['weather']
        shifts = '\n'.join(format_worked_shift(item, english=english) for item in header['worked_shifts']) or '—'
        number = official['official_report_number'] or '—'
        project_day = official['project_day'] or '—'
        wind, soil = weather['wind_speed'] or '—', weather['soil_condition'] or '—'
        forecast = format_forecast(weather)
        notes = header['weather_impact_notes'] or '—'
        rows = (
            (f'Official report: {number} | Project day: {project_day}', f'شماره گزارش: {number} | روز پروژه: {project_day}', 22),
            (f'Worked shifts\n{shifts}', f'شیفت‌های کارکرد\n{shifts}', 16 * (len(header['worked_shifts']) + 1)),
            (f'Wind: {wind} | Ground: {soil}', f'باد: {wind} | وضعیت زمین: {soil}', 22),
            (f'Weather impact:\n{notes}', f'اثرات شرایط جوی:\n{notes}', 16 * (notes.count('\n') + 2)),
            (f"{weather['forecast_provider']}\n{forecast}", f"پیش‌بینی {weather['forecast_provider']}\n{forecast}", 68),
        )
        for row_index, (en, fa, height) in enumerate(rows, 7):
            ws.merge_cells(start_row=row_index, start_column=1, end_row=row_index, end_column=12)
            cell = ws.cell(row_index, 1, en if english else fa)
            cell.font = STYLE_DATA_FONT
            cell.alignment = ALIGN_RIGHT if not english else ALIGN_LEFT
            ws.row_dimensions[row_index].height = min(height, 409)

        # Style header rows 3-4
        for r in range(3, 5):
            for col_idx in range(1, 11):
                cell = ws.cell(row=r, column=col_idx)
                cell.font = STYLE_SUBHEADER_FONT
                cell.fill = STYLE_SUBHEADER_FILL
                cell.border = THIN_BORDER
                cell.alignment = ALIGN_CENTER

    def _write_manpower(self, start_row: int) -> int:
        entries = list(
            self.report.labor_entries.filter(is_deleted=False).select_related('contractor_ref')
            .order_by('job_title', 'contractor_name', 'id')
        )
        profile = None
        if self.report.presentation_profile_code == SHIRAZ_PROFILE:
            profile = resolve_labor_rows_for_profile(entries, SHIRAZ_PROFILE)
            staff = [(slot['title'], slot['rows']) for slot in profile['standard_indirect']]
            workers = [(slot['title'], slot['rows']) for slot in profile['standard_direct']]
        else:
            staff = [(entry.custom_title or entry.job_title, [entry]) for entry in entries
                     if entry.labor_category == 'indirect']
            workers = [(entry.custom_title or entry.job_title, [entry]) for entry in entries
                       if entry.labor_category == 'direct']

        staff_end, staff_total = self._write_labor_block(
            start_row, 1, 'نیروی انسانی ستادی و غیرمستقیم', staff,
        )
        workers_end, workers_total = self._write_labor_block(
            start_row, 10, 'نیروی انسانی مستقیم و کارگری', workers,
        )
        row = max(staff_end, workers_end) + 1
        subtotals = [staff_total, workers_total]
        if profile:
            appendix = [
                (entry.custom_title or entry.job_title, [entry])
                for category in ('indirect', 'direct') for entry in profile[f'appendix_{category}']
            ]
            if appendix:
                summary, appendix_total = self._write_labor_block(
                    row, 1, profile['appendix_heading_fa'], appendix,
                )
                row = summary + 1
                subtotals.append(appendix_total)

        self.ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        self.ws.cell(row, 1, 'جمع کل نفر-شیفت کارگاه (ستادی + کارگری)')
        self.ws.cell(row, 7, f"=SUM({','.join(subtotals)})")
        for cell in self.ws[row][:7]:
            self._style_labor_cell(cell, STYLE_TOTAL_FONT, STYLE_TOTAL_FILL)
        return row + 1

    def _write_labor_block(self, start_row, start_col, title, slots):
        ws = self.ws
        ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=start_col + 8)
        self._style_labor_cell(ws.cell(start_row, start_col, title), STYLE_SECTION_FONT, STYLE_SECTION_FILL)
        headers = ('ردیف', 'عنوان شغلی', 'شیفت ۱', 'شیفت ۲', 'شیفت ۳', 'مرخصی',
                   'جمع نفر-شیفت', 'اضافه‌کاری (ساعت)', 'پیمانکار')
        for col, header in enumerate(headers, start_col):
            self._style_labor_cell(ws.cell(start_row + 1, col, header), STYLE_SUBHEADER_FONT, STYLE_SUBHEADER_FILL)
        first = start_row + 2
        shift_start, shift_end = (get_column_letter(start_col + offset) for offset in (2, 4))
        for index, (title, entries) in enumerate(slots, 1):
            row = first + index - 1
            counts = [
                sum(recorded) if (recorded := [getattr(entry, field) for entry in entries
                                                if getattr(entry, field) is not None]) else None
                for field in ('shift_1_count', 'shift_2_count', 'shift_3_count', 'absence_count', 'overtime_hours')
            ]
            contractors = dict.fromkeys(
                entry.contractor_ref.name if entry.contractor_ref else entry.contractor_name for entry in entries
            )
            total = f'=SUM({shift_start}{row}:{shift_end}{row})' if entries else None
            values = (index, title, *counts[:4], total, counts[4], '، '.join(filter(None, contractors)))
            for offset, value in enumerate(values):
                cell = ws.cell(row, start_col + offset, value=value)
                self._style_labor_cell(cell, STYLE_DATA_FONT)
                if offset != 6:
                    literalize_cell(cell)

        # Empty custom catalogs still produce a valid subtotal and print header.
        last = first + max(len(slots), 1) - 1
        subtotal = last + 1
        ws.merge_cells(start_row=subtotal, start_column=start_col,
                       end_row=subtotal, end_column=start_col + 1)
        for offset in range(8):
            col = start_col + offset
            cell = ws.cell(subtotal, col)
            if offset == 0:
                cell.value = 'جمع نفر-شیفت'
            if offset >= 2:
                letter = get_column_letter(col)
                cell.value = f'=SUM({letter}{first}:{letter}{last})'
            self._style_labor_cell(cell, STYLE_TOTAL_FONT, STYLE_TOTAL_FILL)
        return subtotal, ws.cell(subtotal, start_col + 6).coordinate

    @staticmethod
    def _style_labor_cell(cell, font, fill=None):
        cell.font = font
        if fill is not None:
            cell.fill = fill
        cell.alignment = ALIGN_CENTER
        cell.border = THIN_BORDER

    def _write_materials(self, start_row: int) -> int:
        ws = self.ws
        row = start_row

        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        c = ws.cell(row=row, column=1, value='بخش ج: مصالح وارده به کارگاه')
        c.font = STYLE_SECTION_FONT
        c.fill = STYLE_SECTION_FILL
        c.alignment = ALIGN_CENTER
        row += 1

        headers = ['ردیف', 'شرح مصالح', 'نوع تراکنش', 'مقدار', 'واحد', 'محل مصرف / دپو', 'تأمین‌کننده',
                   'سند انبار', 'تطبیق']
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col_idx, value=h)
            cell.font = STYLE_SUBHEADER_FONT
            cell.fill = STYLE_SUBHEADER_FILL
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
        row += 1

        all_items = list(self.report.material_entries.filter(is_deleted=False))
        items = [item for item in all_items if item.transaction_type == 'receipt' and (not self.report.is_auto_summary or item.receipt_resolved is True)]
        if not items:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            cell = ws.cell(row=row, column=1, value='موردی برای مصالح وارده در این روز ثبت نشده است.')
            cell.font = STYLE_DATA_FONT
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
            row += 1
        else:
            for idx, item in enumerate(items, start=1):
                ws.cell(row=row, column=1, value=idx).alignment = ALIGN_CENTER
                ws.cell(row=row, column=2, value=item.material_description).alignment = ALIGN_RIGHT
                ws.cell(row=row, column=3, value=item.get_transaction_type_display()).alignment = ALIGN_CENTER
                ws.cell(row=row, column=4, value=float(item.quantity) if item.quantity is not None else 0).alignment = ALIGN_CENTER
                ws.cell(row=row, column=5, value=item.unit).alignment = ALIGN_CENTER
                ws.cell(row=row, column=6, value=item.consumption_location or '—').alignment = ALIGN_RIGHT
                supplier_val = getattr(item, 'supplier', None) or getattr(item, 'supplier_name', None) or '—'
                ws.cell(row=row, column=7, value=supplier_val).alignment = ALIGN_RIGHT
                ws.cell(row=row, column=8, value=item.warehouse_document_reference or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=9, value=item.get_reconciliation_status_display() or '—').alignment = ALIGN_CENTER

                for c_i in range(1, 10):
                    literalize_cell(ws.cell(row=row, column=c_i)).font = STYLE_DATA_FONT
                    ws.cell(row=row, column=c_i).border = THIN_BORDER
                row += 1

        other_items = [item for item in all_items if item not in items]
        if other_items:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            cell = ws.cell(row=row, column=1, value='سایر گردش‌ها و رسیدهای تأییدنشده (خارج از مصالح وارده)')
            cell.font, cell.fill, cell.alignment = STYLE_SUBHEADER_FONT, STYLE_SUBHEADER_FILL, ALIGN_RIGHT
            row += 1
            for idx, item in enumerate(other_items, 1):
                values = [idx, item.material_description, item.get_transaction_type_display(), item.quantity,
                          item.unit, item.consumption_location or '—', item.supplier or '—',
                          item.warehouse_document_reference or '—', item.get_reconciliation_status_display() or '—']
                for col, value in enumerate(values, 1):
                    cell = literalize_cell(ws.cell(row=row, column=col, value=value))
                    cell.font, cell.border, cell.alignment = STYLE_DATA_FONT, THIN_BORDER, ALIGN_CENTER
                row += 1
        return row

    def _write_concrete(self, start_row: int) -> int:
        ws = self.ws
        row = start_row

        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        c = ws.cell(row=row, column=1, value='بخش د: احجام بتن‌ریزی')
        c.font = STYLE_SECTION_FONT
        c.fill = STYLE_SECTION_FILL
        c.alignment = ALIGN_CENTER
        row += 1

        headers = (
            ['No.', 'Concrete description', 'Volume (m³)', 'Parcel', 'Block', 'Floor', 'Element',
             'Delivery note', 'Lab sample code', 'Sampling']
            if self.english else
            ['ردیف', 'شرح بتن / عیار', 'حجم (متر مکعب)', 'قطعه', 'بلوک', 'طبقه', 'عضو سازه‌ای',
             'شماره حواله', 'کد نمونه آزمایشگاه', 'وضعیت نمونه‌گیری']
        )
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col_idx, value=h)
            cell.font = STYLE_SUBHEADER_FONT
            cell.fill = STYLE_SUBHEADER_FILL
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
        row += 1

        items = list(self.report.concrete_logs.filter(is_deleted=False))
        if not items:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            cell = ws.cell(row=row, column=1, value='موردی برای بتن‌ریزی در این روز ثبت نشده است.')
            cell.font = STYLE_DATA_FONT
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
            row += 1

            # Keep the empty section computationally valid: spreadsheet viewers
            # evaluate this as zero instead of leaving the section without a
            # numeric total/formula row.
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
            total_label = ws.cell(row=row, column=1, value='جمع کل حجم بتن‌ریزی (متر مکعب)')
            total_label.font = STYLE_TOTAL_FONT
            total_label.fill = STYLE_TOTAL_FILL
            total_label.alignment = ALIGN_RIGHT
            total_value = ws.cell(row=row, column=3, value=f'=SUM(C{row - 1}:C{row - 1})')
            total_value.font = STYLE_TOTAL_FONT
            total_value.fill = STYLE_TOTAL_FILL
            total_value.alignment = ALIGN_CENTER
            for c_i in range(1, 8):
                ws.cell(row=row, column=c_i).border = THIN_BORDER
                ws.cell(row=row, column=c_i).fill = STYLE_TOTAL_FILL
            row += 1
        else:
            concrete_start = row
            for idx, item in enumerate(items, start=1):
                ws.cell(row=row, column=1, value=idx).alignment = ALIGN_CENTER
                ws.cell(row=row, column=2, value=item.concrete_description).alignment = ALIGN_RIGHT
                ws.cell(row=row, column=3, value=item.volume_m3).alignment = ALIGN_CENTER
                ws.cell(row=row, column=4, value=item.parcel or item.zone or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=5, value=item.block or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=6, value=item.floor or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=7, value=item.structural_element or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=8, value=item.truck_delivery_note_number or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=9, value=item.lab_sample_code or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=10, value=sampling_label(item.sampling_state, english=self.english))

                for c_i in range(1, 11):
                    literalize_cell(ws.cell(row=row, column=c_i)).font = STYLE_DATA_FONT
                    ws.cell(row=row, column=c_i).border = THIN_BORDER
                row += 1

            concrete_end = row - 1
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
            c_tot = ws.cell(row=row, column=1, value='جمع کل حجم بتن‌ریزی (متر مکعب)')
            c_tot.font = STYLE_TOTAL_FONT
            c_tot.fill = STYLE_TOTAL_FILL
            c_tot.alignment = ALIGN_RIGHT

            tot_val = ws.cell(row=row, column=3, value=f'=SUM(C{concrete_start}:C{concrete_end})')
            tot_val.font = STYLE_TOTAL_FONT
            tot_val.fill = STYLE_TOTAL_FILL
            tot_val.alignment = ALIGN_CENTER

            for c_i in range(1, 8):
                ws.cell(row=row, column=c_i).border = THIN_BORDER
                ws.cell(row=row, column=c_i).fill = STYLE_TOTAL_FILL
            row += 1
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
            label = 'Open concrete details for this version' if self.english else 'مشاهده جزئیات بتن‌ریزی همین نسخه'
            link = ws.cell(row, 1, label)
            link.hyperlink = concrete_details_url(self.report)
            link.font = Font(name=FONT_FAMILY, size=9, color='1F4E79', underline='single')
            row += 1

        return row

    def _write_machinery(self, start_row: int) -> int:
        ws = self.ws
        row = start_row

        items = list(self.report.equipment_entries.filter(is_deleted=False))
        derived = list(self.report.machinery_rows.filter(is_deleted=False))
        if derived or self.report.is_auto_summary:
            headers = ['ردیف', 'نوع دستگاه', 'تعداد کل', 'فعال', 'آماده', 'غیرفعال', 'در تعمیر', 'ساعت کارکرد', 'ساعت توقف', 'ساعت تعمیر']
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
            cell = ws.cell(row=row, column=1, value='بخش هـ: ماشین‌آلات و تجهیزات کارگاه')
            cell.font, cell.fill, cell.alignment = STYLE_SECTION_FONT, STYLE_SECTION_FILL, ALIGN_CENTER
            row += 1
            for col, title in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col, value=title)
                cell.font, cell.fill, cell.alignment, cell.border = STYLE_SUBHEADER_FONT, STYLE_SUBHEADER_FILL, ALIGN_CENTER, THIN_BORDER
            row += 1
            for idx, item in enumerate(derived, 1):
                values = [idx, item.equipment_type, item.status_total, item.status_active, item.status_ready, item.status_inactive, item.status_under_repair, item.operating_hours, item.stoppage_hours, item.repair_hours]
                for col, value in enumerate(values, 1):
                    cell = literalize_cell(ws.cell(row=row, column=col, value=value))
                    cell.font, cell.border, cell.alignment = STYLE_DATA_FONT, THIN_BORDER, ALIGN_CENTER
                row += 1
            if not derived and not items:
                ws.cell(row=row, column=2, value='موردی برای ماشین‌آلات در این روز ثبت نشده است.')
                row += 1
            if not items:
                return row
            row += 1

        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        title = 'تجهیزات ثبت‌شده در فرم قدیمی' if derived or self.report.is_auto_summary else 'بخش هـ: ماشین‌آلات و تجهیزات کارگاه'
        c = ws.cell(row=row, column=1, value=title)
        c.font = STYLE_SECTION_FONT
        c.fill = STYLE_SECTION_FILL
        c.alignment = ALIGN_CENTER
        row += 1

        headers = ['ردیف', 'نام دستگاه و تجهیزات', 'شیفت', 'وضعیت', 'نوع مالکیت', 'ساعات کارکرد مفید', 'ساعات تعمیرات']
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col_idx, value=h)
            cell.font = STYLE_SUBHEADER_FONT
            cell.fill = STYLE_SUBHEADER_FILL
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
        row += 1

        if not items:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            cell = ws.cell(row=row, column=1, value='موردی برای ماشین‌آلات در این روز ثبت نشده است.')
            cell.font = STYLE_DATA_FONT
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
            row += 1
        else:
            for idx, item in enumerate(items, start=1):
                ws.cell(row=row, column=1, value=idx).alignment = ALIGN_CENTER
                ws.cell(row=row, column=2, value=item.equipment_name).alignment = ALIGN_RIGHT
                ws.cell(row=row, column=3, value=item.get_shift_display()).alignment = ALIGN_CENTER
                ws.cell(row=row, column=4, value=item.get_status_display()).alignment = ALIGN_CENTER
                ws.cell(row=row, column=5, value=item.get_ownership_type_display()).alignment = ALIGN_CENTER
                ws.cell(row=row, column=6, value=item.productive_hours).alignment = ALIGN_CENTER
                repair_h = float(getattr(item, 'repair_hours', 0) or getattr(item, 'idle_repair_hours', 0) or 0)
                ws.cell(row=row, column=7, value=repair_h).alignment = ALIGN_CENTER

                for c_i in range(1, 8):
                    literalize_cell(ws.cell(row=row, column=c_i)).font = STYLE_DATA_FONT
                    ws.cell(row=row, column=c_i).border = THIN_BORDER
                row += 1

        return row

    def _write_activities(self, start_row: int) -> int:
        ws = self.ws
        row = start_row

        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=12)
        c = ws.cell(row=row, column=1, value='بخش و: فعالیت‌های اجرایی کارگاه (منطبق بر دیتابیس فعالیت‌ها)')
        c.font = STYLE_SECTION_FONT
        c.fill = STYLE_SECTION_FILL
        c.alignment = ALIGN_CENTER
        row += 1

        headers = ['ردیف', 'شرح فعالیت', 'شیفت', 'پیمانکار / اکیپ', 'نفرات', 'قطعه', 'بلوک', 'طبقه',
                   'مقدار', 'واحد', 'موقعیت', 'توضیحات', 'کد فعالیت']
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col_idx, value=h)
            cell.font = STYLE_SUBHEADER_FONT
            cell.fill = STYLE_SUBHEADER_FILL
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
        row += 1

        items = list(self.report.activities.filter(is_deleted=False).select_related('contractor_ref', 'activity_ref'))
        if not items:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
            cell = ws.cell(row=row, column=1, value='هیچ فعالیت اجرایی در این روز ثبت نشده است.')
            cell.font = STYLE_DATA_FONT
            cell.alignment = ALIGN_CENTER
            cell.border = THIN_BORDER
            row += 1

            # Preserve a zero-valued native formula for an empty activity table.
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
            total_label = ws.cell(row=row, column=1, value='جمع کل نفرات فعالیت‌ها')
            total_label.font = STYLE_TOTAL_FONT
            total_label.fill = STYLE_TOTAL_FILL
            total_label.alignment = ALIGN_RIGHT
            total_value = ws.cell(row=row, column=5, value=f'=SUM(E{row - 1}:E{row - 1})')
            total_value.font = STYLE_TOTAL_FONT
            total_value.fill = STYLE_TOTAL_FILL
            total_value.alignment = ALIGN_CENTER
            for c_i in range(1, 11):
                ws.cell(row=row, column=c_i).border = THIN_BORDER
                ws.cell(row=row, column=c_i).fill = STYLE_TOTAL_FILL
            row += 1
        else:
            for idx, item in enumerate(items, start=1):
                qty_display = float(item.quantity) if item.quantity is not None and item.quantity_measured else '*'
                ws.cell(row=row, column=1, value=idx).alignment = ALIGN_CENTER
                ws.cell(row=row, column=2, value=item.activity_description).alignment = ALIGN_RIGHT
                ws.cell(row=row, column=3, value=item.get_shift_display()).alignment = ALIGN_CENTER
                contractor = item.contractor_ref.name if item.contractor_ref_id else item.subcontractor_name
                parties = []
                if contractor:
                    parties.append(f'پیمانکار: {contractor}')
                if item.crew_name:
                    parties.append(f'اکیپ: {item.crew_name}')
                if not parties and item.responsible_name:
                    parties.append(f'مسئول: {item.responsible_name}')
                ws.cell(row=row, column=4, value=' / '.join(parties) or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=5, value=item.headcount).alignment = ALIGN_CENTER
                ws.cell(row=row, column=6, value=item.parcel or item.zone or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=7, value=item.block or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=8, value=item.floor or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=9, value=qty_display).alignment = ALIGN_CENTER
                ws.cell(row=row, column=10, value=item.unit or '—').alignment = ALIGN_CENTER
                ws.cell(row=row, column=11, value=item.location_detail or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=12, value=item.notes or '—').alignment = ALIGN_RIGHT
                ws.cell(row=row, column=13, value=item.activity_ref.activity_code if item.activity_ref else '—')

                for c_i in range(1, 14):
                    literalize_cell(ws.cell(row=row, column=c_i)).font = STYLE_DATA_FONT
                    ws.cell(row=row, column=c_i).border = THIN_BORDER
                row += 1

        return row

    def _write_general_activities(self, row):
        ws = self.ws
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        cell = ws.cell(row=row, column=1, value='فعالیت‌های عمومی کارگاه')
        cell.font, cell.fill, cell.alignment = STYLE_SECTION_FONT, STYLE_SECTION_FILL, ALIGN_CENTER
        row += 1
        for col, label in enumerate(['ردیف', 'شرح فعالیت', 'محل', 'مقدار', 'واحد', 'توضیحات', 'واحد مبدأ'], 1):
            cell = ws.cell(row=row, column=col, value=label)
            cell.font, cell.fill, cell.border, cell.alignment = STYLE_SUBHEADER_FONT, STYLE_SUBHEADER_FILL, THIN_BORDER, ALIGN_CENTER
        row += 1
        for item in self.report.general_activities.filter(is_deleted=False).order_by('row_number', 'id'):
            for col, value in enumerate([item.row_number, item.activity_description, item.location, item.quantity,
                                         item.unit, item.notes, item.source_discipline or '—'], 1):
                cell = literalize_cell(ws.cell(row=row, column=col, value=value))
                cell.font, cell.border, cell.alignment = STYLE_DATA_FONT, THIN_BORDER, ALIGN_RIGHT
            row += 1
        return row

    def _write_notes(self, row):
        for label, value in [('توضیحات عمومی و موانع', self.report.general_notes), ('نظر مدیریت', self.report.management_opinion), ('تأثیر شرایط جوی', self.report.weather_impact_notes)]:
            self.ws.cell(row=row, column=1, value=label).font = STYLE_BOLD_FONT
            self.ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=10)
            literalize_cell(self.ws.cell(row=row, column=2, value=value or '—')).alignment = ALIGN_RIGHT
            row += 1

    def _write_visits_and_incidents(self, row):
        """Keep structured field observations separate from free-text notes."""
        ws = self.ws

        def heading(title, headers):
            nonlocal row
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(headers))
            cell = ws.cell(row=row, column=1, value=title)
            cell.font, cell.fill, cell.alignment = STYLE_SECTION_FONT, STYLE_SECTION_FILL, ALIGN_CENTER
            row += 1
            for col, label in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col, value=label)
                cell.font, cell.fill, cell.border, cell.alignment = STYLE_SUBHEADER_FONT, STYLE_SUBHEADER_FILL, THIN_BORDER, ALIGN_CENTER
            row += 1

        def data_row(values):
            nonlocal row
            for col, value in enumerate(values, 1):
                cell = literalize_cell(ws.cell(row=row, column=col, value=value))
                cell.font, cell.border, cell.alignment = STYLE_DATA_FONT, THIN_BORDER, ALIGN_RIGHT
            row += 1

        heading('بازدیدهای کارگاه', ['ردیف', 'شرح بازدید', 'واحد مبدأ'])
        for visit in self.report.visits.filter(is_deleted=False).order_by('row_number', 'id'):
            data_row([visit.row_number, visit.text, visit.source_discipline or '—'])

        heading('مسائل، موانع و حوادث ایمنی',
                ['ردیف', 'نوع', 'شرح', 'مسئول پیگیری', 'موعد', 'اقدام اصلاحی / فوری', 'شدت', 'واحد مبدأ'])
        type_labels = {} if self.english else INCIDENT_LABELS_FA
        severity_labels = {} if self.english else SEVERITY_LABELS_FA
        incidents = self.report.incidents.filter(is_deleted=False).select_related('follow_up_owner_user', 'source_report')
        for incident in incidents.order_by('row_number', 'id'):
            owner = incident.follow_up_owner_name
            if not owner and incident.follow_up_owner_user:
                owner = incident.follow_up_owner_user.get_full_name() or incident.follow_up_owner_user.username
            due = gregorian_to_jalali(incident.due_date) if incident.due_date else '—'
            data_row([
                incident.row_number, type_labels.get(incident.incident_type, incident.get_incident_type_display()),
                incident.description, owner or '—', due, incident.corrective_action or '—',
                severity_labels.get(incident.severity, incident.get_severity_display()) if incident.severity else '—',
                (incident.source_report.unit or incident.source_report.discipline) if incident.source_report else '—',
            ])
        return row

    def _auto_fit_columns(self):
        ws = self.ws
        preferred = (6, 24, 8, 11, 8, 8, 10, 10, 12, 7, 22, 10, 8, 8, 7, 10, 9, 12)
        for index, width in enumerate(preferred, 1):
            ws.column_dimensions[get_column_letter(index)].width = width
