"""Keep user-controlled spreadsheet values as text, not Excel formulas."""


def literalize_cell(cell):
    # openpyxl infers a formula from any text beginning with '='. The data
    # rows below never intentionally contain formulas; preserve the exact
    # string while forcing its OOXML type to text.
    if cell.data_type == 'f':
        cell.data_type = 's'
    return cell
