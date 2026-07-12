"""Discipline sub-report tests."""

import pytest
from rest_framework import status

from sub_reports.models import Discipline, SubReportStatus


@pytest.fixture
def sub_reports_base(project):
    return f'/api/v1/projects/{project.id}/sub-reports/'


@pytest.mark.django_db
class TestSubReportsAPI:
    def test_create_submit_approve(self, auth_client, sub_reports_base, user):
        create = auth_client.post(
            sub_reports_base,
            {
                'report_date': '2024-08-15',
                'discipline': Discipline.CIVIL,
                'activities': [
                    {
                        'row_number': 1,
                        'activity_description': 'دیوار',
                        'shift': 'shift_1',
                        'crew_name': 'نفر شرکت',
                        'quantity': '10',
                        'unit': 'm2',
                    }
                ],
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        report_id = create.data['id']

        submit = auth_client.post(f'{sub_reports_base}{report_id}/submit/')
        assert submit.status_code == status.HTTP_200_OK
        assert submit.data['status'] == SubReportStatus.SUBMITTED

        approve = auth_client.post(f'{sub_reports_base}{report_id}/approve/')
        assert approve.status_code == status.HTTP_200_OK
        assert approve.data['status'] == SubReportStatus.APPROVED
