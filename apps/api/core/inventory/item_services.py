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

def _read_and_validate_excel(file) -> pd.DataFrame:
    try:
        df = pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        logger.exception('Failed to read Excel file')
        raise ValueError('Error processing file. Please check the file format and try again.')

    required_columns = ['name', 'quantity', 'category']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f'Missing required columns: {", ".join(missing_columns)}')

    return df

def _get_or_create_categories(category_names: List[str]) -> dict:
    existing_categories = Category.objects.filter(name__in=category_names)
    category_map = {c.name: c for c in existing_categories}

    missing_categories = [
        Category(name=name)
        for name in category_names
        if name not in category_map
    ]
    if missing_categories:
        created_categories = Category.objects.bulk_create(missing_categories)
        for category in created_categories:
            category_map[category.name] = category

    return category_map

def _parse_items_from_dataframe(df: pd.DataFrame, category_map: dict) -> Tuple[List[Item], List[str]]:
    items_to_create: list[Item] = []
    errors: list[str] = []

    for row in df.itertuples(index=True):
        index = row.Index
        try:
            category_name = row.category
            if pd.isna(category_name):
                errors.append(f'Row {index + 2}: Invalid data format (e.g., missing category).')
                continue

            category = category_map.get(category_name)
            if category is None:
                errors.append(f'Row {index + 2}: Invalid data format (e.g., missing category).')
                continue

            quantity = int(row.quantity)
            items_to_create.append(
                Item(
                    name=row.name,
                    quantity=quantity,
                    category=category,
                )
            )
        except ValueError:
            errors.append(f'Row {index + 2}: Invalid data format (e.g., non-numeric quantity).')
        except Exception:
            logger.exception('Failed to import row %s', index + 2)
            errors.append(f'Row {index + 2}: An unexpected error occurred.')

    return items_to_create, errors

def _bulk_save_items(items_to_create: List[Item]) -> int:
    if not items_to_create:
        return 0
    try:
        created = Item.objects.bulk_create(items_to_create)
        return len(created)
    except Exception:
        logger.exception('Failed to bulk create items')
        raise ValueError(
            'A database error occurred while saving the imported items. '
            'Please check the data and try again.'
        )

def import_items_from_excel(file) -> Tuple[int, List[str]]:
    """
    Import items from an Excel file.
    Returns a tuple of (imported_count, list of errors).
    Raises ValueError if missing required columns or file is invalid.
    """
    df = _read_and_validate_excel(file)

    unique_category_names = df['category'].dropna().unique().tolist()
    category_map = _get_or_create_categories(unique_category_names)

    items_to_create, errors = _parse_items_from_dataframe(df, category_map)

    imported_count = _bulk_save_items(items_to_create)

    return imported_count, errors
