import io
import logging
from typing import Tuple, List
import pandas as pd

from .models import Item, Category

logger = logging.getLogger(__name__)

def export_items_to_excel() -> bytes:
    """
    Export all items to an Excel file and return as bytes.
    """
    items = Item.objects.all().values('id', 'name', 'quantity', 'category__name')
    df = pd.DataFrame(list(items))
    if not df.empty:
        df.rename(columns={'category__name': 'category'}, inplace=True)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return buf.getvalue()

def import_items_from_excel(file) -> Tuple[int, List[str]]:
    """
    Import items from an Excel file.
    Returns a tuple of (imported_count, list of errors).
    Raises ValueError if missing required columns or file is invalid.
    """
    try:
        df = pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        logger.exception('Failed to read Excel file')
        raise ValueError('Error processing file. Please check the file format and try again.')

    required_columns = ['name', 'quantity', 'category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f'Missing required columns: {", ".join(missing_columns)}')

    imported_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            category_name = row['category']
            category, _ = Category.objects.get_or_create(name=category_name)

            Item.objects.create(
                name=row['name'],
                quantity=int(row['quantity']),
                category=category
            )
            imported_count += 1
        except ValueError:
            errors.append(f'Row {index + 2}: Invalid data format (e.g., non-numeric quantity).')
        except Exception:
            logger.exception('Failed to import row %s', index + 2)
            errors.append(f'Row {index + 2}: An unexpected error occurred.')

    return imported_count, errors
