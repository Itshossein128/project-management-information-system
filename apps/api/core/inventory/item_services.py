import logging
import io
import pandas as pd
from .models import Item, Category

logger = logging.getLogger(__name__)


def generate_items_excel() -> bytes:
    """
    Generate an Excel file containing all items.
    Returns the Excel file as bytes.
    """
    items = Item.objects.all().values('id', 'name', 'quantity', 'category__name')
    df = pd.DataFrame(list(items))
    df.rename(columns={'category__name': 'category'}, inplace=True)

    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False, engine='openpyxl')
    return excel_file.getvalue()


def process_items_import(file) -> dict:
    """
    Process an uploaded Excel file to import items into the database.
    Returns a dictionary with status, message, and imported count/errors.
    """
    try:
        df = pd.read_excel(file, engine='openpyxl')

        # Validate required columns
        required_columns = ['name', 'quantity', 'category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }

        imported_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                category_name = row['category']
                category, created = Category.objects.get_or_create(name=category_name)

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
                errors.append(f'Row {index + 2}: An unexpected error occurred.')  # +2 because Excel rows start at 1 and header is row 1

        return {
            'success': True,
            'message': f'Successfully imported {imported_count} items',
            'imported_count': imported_count,
            'errors': errors if errors else None
        }

    except Exception as e:
        logger.exception('Failed to process Excel file')
        return {
            'success': False,
            'error': 'Error processing file. Please check the file format and try again.'
        }
