"""Discipline sub-report tests."""

import pytest
from rest_framework import status

from sub_reports.models import Discipline, SubReportStatus


@pytest.fixture
def sub_reports_base(project):
    return f'/api/v1/projects/{project.id}/sub-reports/'


def _create_sub_report(auth_client, sub_reports_base):
    return auth_client.post(
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


@pytest.mark.django_db
class TestSubReportsAPI:
    def test_create_submit_approve(self, auth_client, sub_reports_base, user):
        create = _create_sub_report(auth_client, sub_reports_base)
        assert create.status_code == status.HTTP_201_CREATED
        report_id = create.data['id']

        submit = auth_client.post(f'{sub_reports_base}{report_id}/submit/')
        assert submit.status_code == status.HTTP_200_OK
        assert submit.data['status'] == SubReportStatus.SUBMITTED

        approve = auth_client.post(f'{sub_reports_base}{report_id}/approve/')
        assert approve.status_code == status.HTTP_200_OK
        assert approve.data['status'] == SubReportStatus.APPROVED

    def test_reject_flow(self, auth_client, sub_reports_base):
        report_id = _create_sub_report(auth_client, sub_reports_base).data['id']
        auth_client.post(f'{sub_reports_base}{report_id}/submit/')
        reject = auth_client.post(
            f'{sub_reports_base}{report_id}/reject/',
            {'rejection_reason': 'اطلاعات ناقص است و نیاز به تکمیل دارد'},
            format='json',
        )
        assert reject.status_code == status.HTTP_200_OK
        assert reject.data['status'] == SubReportStatus.REJECTED

    def test_approve_from_draft_fails(self, auth_client, sub_reports_base):
        report_id = _create_sub_report(auth_client, sub_reports_base).data['id']
        approve = auth_client.post(f'{sub_reports_base}{report_id}/approve/')
        assert approve.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_from_submitted_fails(self, auth_client, sub_reports_base):
        report_id = _create_sub_report(auth_client, sub_reports_base).data['id']
        auth_client.post(f'{sub_reports_base}{report_id}/submit/')
        again = auth_client.post(f'{sub_reports_base}{report_id}/submit/')
        assert again.status_code == status.HTTP_400_BAD_REQUEST

    def test_viewer_cannot_approve(self, auth_client, api_client, sub_reports_base, member):
        report_id = _create_sub_report(auth_client, sub_reports_base).data['id']
        auth_client.post(f'{sub_reports_base}{report_id}/submit/')
        api_client.force_authenticate(user=member.user)
        approve = api_client.post(f'{sub_reports_base}{report_id}/approve/')
        assert approve.status_code == status.HTTP_403_FORBIDDEN
