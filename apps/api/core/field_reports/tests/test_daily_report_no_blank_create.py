import pytest
from rest_framework import status


@pytest.fixture
def reports_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
def test_blank_create_rejected(auth_client, reports_url):
    response = auth_client.post(
        reports_url,
        {'report_date': '1403/03/21', 'site_status': 'active'},
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    detail = response.data.get('detail') or response.data
    text = detail if isinstance(detail, str) else str(detail)
    assert 'خودکار' in text or 'auto_summary' in str(response.data)
