"""Tests for dynamic table row CRUD and Excel import/export."""

import io

import pytest
from django.contrib.auth.models import Group
from openpyxl import Workbook
from rest_framework import status

from business_meta.models import DynamicTableRow, FieldDefinition, TableDefinition


@pytest.fixture
def dynamic_table(db, project):
    table = TableDefinition.objects.create(
        project=project,
        name='Items',
        slug='items',
        ordering=0,
    )
    FieldDefinition.objects.create(
        table=table,
        name='Name',
        slug='name',
        field_type='string',
        required=True,
        ordering=0,
    )
    FieldDefinition.objects.create(
        table=table,
        name='Quantity',
        slug='quantity',
        field_type='number',
        required=False,
        ordering=1,
    )
    return table


def rows_url(project, table_slug):
    return f'/api/v1/projects/{project.id}/tables/{table_slug}/rows/'


def row_detail_url(project, table_slug, row_id):
    return f'/api/v1/projects/{project.id}/tables/{table_slug}/rows/{row_id}/'


@pytest.mark.django_db
class TestDynamicRowCrud:
    def test_unauthenticated_cannot_list(self, api_client, project, dynamic_table):
        response = api_client.get(rows_url(project, dynamic_table.slug))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_member_cannot_list(self, api_client, other_user, project, dynamic_table):
        api_client.force_authenticate(user=other_user)
        response = api_client.get(rows_url(project, dynamic_table.slug))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_list_get_update_delete_row(self, auth_client, project, dynamic_table):
        base = rows_url(project, dynamic_table.slug)

        create_resp = auth_client.post(
            base,
            {'name': 'Bolt', 'quantity': 10},
            format='json',
        )
        assert create_resp.status_code == status.HTTP_201_CREATED
        row_id = create_resp.data['id']

        list_resp = auth_client.get(base)
        assert list_resp.status_code == status.HTTP_200_OK
        assert list_resp.data['count'] == 1
        assert list_resp.data['results'][0]['name'] == 'Bolt'

        detail_url = row_detail_url(project, dynamic_table.slug, row_id)
        get_resp = auth_client.get(detail_url)
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.data['quantity'] == 10

        patch_resp = auth_client.patch(
            detail_url,
            {'quantity': 25},
            format='json',
        )
        assert patch_resp.status_code == status.HTTP_200_OK
        assert patch_resp.data['quantity'] == 25

        delete_resp = auth_client.delete(detail_url)
        assert delete_resp.status_code == status.HTTP_204_NO_CONTENT
        assert not DynamicTableRow.objects.filter(pk=row_id).exists()

    def test_create_row_validation_error(self, auth_client, project, dynamic_table):
        response = auth_client.post(
            rows_url(project, dynamic_table.slug),
            {'quantity': 5},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_filter_rows_by_field(self, auth_client, project, dynamic_table):
        DynamicTableRow.objects.create(table=dynamic_table, data={'name': 'Alpha', 'quantity': 1})
        DynamicTableRow.objects.create(table=dynamic_table, data={'name': 'Beta', 'quantity': 2})

        response = auth_client.get(
            rows_url(project, dynamic_table.slug) + '?name=Alpha',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Alpha'

    def test_unknown_table_returns_404(self, auth_client, project):
        response = auth_client.get(rows_url(project, 'missing'))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDynamicRowExcel:
    def test_export_import_round_trip(self, auth_client, project, dynamic_table):
        DynamicTableRow.objects.create(
            table=dynamic_table,
            data={'name': 'Widget', 'quantity': 3},
        )

        export_url = rows_url(project, dynamic_table.slug) + 'export/'
        export_resp = auth_client.get(export_url)
        assert export_resp.status_code == status.HTTP_200_OK
        assert (
            export_resp['Content-Type']
            == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        import_url = rows_url(project, dynamic_table.slug) + 'import/'
        import_resp = auth_client.post(
            import_url,
            {'file': io.BytesIO(export_resp.content)},
            format='multipart',
        )
        assert import_resp.status_code == status.HTTP_200_OK
        assert import_resp.data['created'] >= 1
        assert DynamicTableRow.objects.filter(table=dynamic_table).count() >= 2

    def test_import_from_minimal_workbook(self, auth_client, project, dynamic_table):
        wb = Workbook()
        ws = wb.active
        ws.title = 'Items'
        ws.append(['Name', 'Quantity'])
        ws.append(['Screw', 42])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        import_url = rows_url(project, dynamic_table.slug) + 'import/'
        response = auth_client.post(
            import_url,
            {'file': buf},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 1
        row = DynamicTableRow.objects.get(table=dynamic_table)
        assert row.data['name'] == 'Screw'
        assert row.data['quantity'] == 42

    def test_import_without_file_returns_400(self, auth_client, project, dynamic_table):
        import_url = rows_url(project, dynamic_table.slug) + 'import/'
        response = auth_client.post(import_url, {}, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTableDefinitionApi:
    @pytest.fixture
    def business_setup_client(self, api_client, user):
        Group.objects.get_or_create(name='business-setup')
        user.groups.add(Group.objects.get(name='business-setup'))
        api_client.force_authenticate(user=user)
        return api_client

    def test_business_setup_can_create_table(self, business_setup_client, project):
        response = business_setup_client.post(
            f'/api/v1/projects/{project.id}/tables/',
            {'name': 'Vendors', 'slug': 'vendors', 'ordering': 0},
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert TableDefinition.objects.filter(project=project, slug='vendors').exists()

    def test_regular_member_cannot_create_table(self, auth_client, project):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/tables/',
            {'name': 'Blocked', 'slug': 'blocked', 'ordering': 0},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
