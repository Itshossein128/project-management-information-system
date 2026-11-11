import pytest

from master_data.models import Unit


@pytest.mark.django_db
def test_steward_can_create_measurement_unit(hr_client):
    resp = hr_client.post(
        '/api/v1/measurement-units/',
        {'unit_name': 'Square meter', 'unit_symbol': 'm2'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body['unit_name'] == 'Square meter'
    assert body['unit_symbol'] == 'm2'
    assert Unit.objects.filter(unit_name='Square meter').exists()


@pytest.mark.django_db
def test_staff_cannot_create_measurement_unit(staff_client):
    resp = staff_client.post(
        '/api/v1/measurement-units/',
        {'unit_name': 'Staff unit', 'unit_symbol': 'su'},
        format='json',
    )
    assert resp.status_code == 403, resp.content
    assert not Unit.objects.filter(unit_name='Staff unit').exists()


@pytest.mark.django_db
def test_blank_measurement_unit_name_rejected(hr_client):
    resp = hr_client.post(
        '/api/v1/measurement-units/',
        {'unit_name': '   ', 'unit_symbol': ''},
        format='json',
    )
    assert resp.status_code == 400, resp.content
    assert Unit.objects.count() == 0


@pytest.mark.django_db
def test_duplicate_measurement_unit_name_rejected(hr_client):
    first = hr_client.post(
        '/api/v1/measurement-units/',
        {'unit_name': 'Meter', 'unit_symbol': 'm'},
        format='json',
    )
    assert first.status_code == 201, first.content
    second = hr_client.post(
        '/api/v1/measurement-units/',
        {'unit_name': 'meter', 'unit_symbol': 'M'},
        format='json',
    )
    assert second.status_code == 400, second.content
    assert Unit.objects.filter(unit_name__iexact='meter').count() == 1
