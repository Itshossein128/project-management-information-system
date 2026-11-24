"""Verify saved browser FILE1 workbooks against the independent B04 manifest."""
from collections import defaultdict
from decimal import Decimal
from sys import argv

from openpyxl import load_workbook


def verify(path):
    sheet = load_workbook(path, read_only=True, data_only=False)['ACTIVITY']
    rows = list(sheet.values)
    data = rows[1:-1]
    assert len(data) == 51
    assert {row[2] for row in data} == {f'B04 row {number:02}' for number in range(51)}
    assert {row[4] for row in data} == {'آرماتوربند الف'}
    assert sum(row[5] for row in data) == 51
    assert rows[-1][5] == '=SUM(F2:F52)'
    assert {row[2]: row[10] for row in data if row[2] in {f'B04 row {i:02}' for i in range(5)}} == {
        'B04 row 00': 0,
        'B04 row 01': '*',
        'B04 row 02': '*',
        'B04 row 03': '*',
        'B04 row 04': '*',
    }
    quantities = defaultdict(Decimal)
    for row in data:
        if isinstance(row[10], (float, int)):
            quantities[row[11]] += Decimal(str(row[10]))
    assert dict(quantities) == {'m²': Decimal('45'), 'm³': Decimal('25')}
    return data


assert verify(argv[1]) == verify(argv[2])
