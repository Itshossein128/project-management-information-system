import pytest
import io
import pandas as pd
from inventory.models import Item, Category
from inventory.item_services import export_items_to_excel, import_items_from_excel

@pytest.mark.django_db
def test_export_items_to_excel():
    category = Category.objects.create(name='Test Category')
    Item.objects.create(name='Item 1', quantity=10, category=category)
    Item.objects.create(name='Item 2', quantity=20, category=category)

    excel_bytes = export_items_to_excel()
    assert isinstance(excel_bytes, bytes)

    df = pd.read_excel(io.BytesIO(excel_bytes), engine='openpyxl')
    assert len(df) == 2
    assert list(df.columns) == ['id', 'name', 'quantity', 'category']
    assert df.iloc[0]['name'] == 'Item 1'
    assert df.iloc[1]['name'] == 'Item 2'

@pytest.mark.django_db
def test_import_items_from_excel():
    df = pd.DataFrame({
        'name': ['Item A', 'Item B'],
        'quantity': [100, 200],
        'category': ['Cat 1', 'Cat 1']
    })
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)

    imported_count, errors = import_items_from_excel(buf)

    assert imported_count == 2
    assert len(errors) == 0
    assert Item.objects.count() == 2
    assert Category.objects.count() == 1
    assert Category.objects.first().name == 'Cat 1'
