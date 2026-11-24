"""Keep user-controlled spreadsheet values as text, not Excel formulas."""
from copy import copy
from math import ceil

from openpyxl.cell.cell import MergedCell
from openpyxl.utils import get_column_letter


def literalize_cell(cell):
    # openpyxl infers a formula from any text beginning with '='. The data
    # rows below never intentionally contain formulas; preserve the exact
    # string while forcing its OOXML type to text.
    if isinstance(cell.value, str):
        cell.data_type = 's'
    return cell


def configure_report_print(sheet, *, title_rows, landscape=False):
    sheet.page_setup.paperSize = sheet.PAPERSIZE_A4
    sheet.page_setup.orientation = sheet.ORIENTATION_LANDSCAPE if landscape else sheet.ORIENTATION_PORTRAIT
    sheet.sheet_properties.pageSetUpPr.fitToPage = True
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 0
    sheet.print_area = sheet.dimensions
    sheet.print_title_rows = title_rows

    merged_widths = {
        (region.min_row, region.min_col): sum(
            sheet.column_dimensions[get_column_letter(col)].width
            for col in range(region.min_col, region.max_col + 1)
        )
        for region in sheet.merged_cells.ranges
    }
    for row in sheet.iter_rows():
        lines = 1
        for cell in row:
            if isinstance(cell, MergedCell) or not isinstance(cell.value, str) or cell.data_type == 'f':
                continue
            if not cell.alignment.wrap_text:
                alignment = copy(cell.alignment)
                alignment.wrap_text = True
                cell.alignment = alignment
            width = merged_widths.get((cell.row, cell.column), sheet.column_dimensions[cell.column_letter].width)
            available = max(width - 2, 1)
            lines = max(lines, sum(max(1, ceil(len(line) / available)) for line in cell.value.split('\n')))
        dimension = sheet.row_dimensions[row[0].row]
        dimension.height = min(409, max(dimension.height or 0, 14 * lines + 3))
