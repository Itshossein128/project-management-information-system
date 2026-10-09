"""TDD: HSE events and quality/safety period report."""

from datetime import date

import pytest
from rest_framework import status

from projects.models import WBS
from risk.models import (
    HseEvent,
    HseEventKind,
    Inspection,
    InspectionResult,
    Nonconformity,
    SafetyTraining,
    WorkPermit,
)


HSE = '/api/v1/projects/{project_id}/hse-events/'
REPORT = '/api/v1/projects/{project_id}/quality-safety/report/'
PERMIT = '/api/v1/projects/{project_id}/work-permits/'
TRAIN = '/api/v1/projects/{project_id}/safety-trainings/'


@pytest.fixture
def wbs_node(db, project, user):
    return WBS.add_root(
        project_id=project.id,
        wbs_code='H1',
        wbs_name='HSE area',
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestHseAndPeriodReport:
    def test_create_incident_and_near_miss_without_wbs(self, auth_client, project):
        url = HSE.format(project_id=project.id)
        for kind in ('incident', 'near_miss'):
            resp = auth_client.post(
                url,
                {
                    'kind': kind,
                    'event_date': '2026-10-08',
                    'description': f'{kind} sample',
                },
                format='json',
            )
            assert resp.status_code == status.HTTP_201_CREATED, resp.data
            assert resp.data['kind'] == kind
            assert resp.data.get('wbs') in (None, '')

    def test_period_report_lists_hse_events(self, auth_client, project, user):
        HseEvent.objects.create(
            project=project,
            kind=HseEventKind.INCIDENT,
            event_date=date(2026, 10, 5),
            description='Incident A',
            created_by=user,
            updated_by=user,
        )
        HseEvent.objects.create(
            project=project,
            kind=HseEventKind.NEAR_MISS,
            event_date=date(2026, 10, 12),
            description='Near miss B',
            created_by=user,
            updated_by=user,
        )
        url = REPORT.format(project_id=project.id)
        resp = auth_client.get(url, {'date_from': '2026-10-01', 'date_to': '2026-10-31'})
        assert resp.status_code == status.HTTP_200_OK, resp.data
        assert resp.data['counts']['incidents'] == 1
        assert resp.data['counts']['near_misses'] == 1
        assert len(resp.data['incidents']) == 1
        assert len(resp.data['near_misses']) == 1

    def test_empty_period_returns_empty_arrays(self, auth_client, project):
        url = REPORT.format(project_id=project.id)
        resp = auth_client.get(url, {'date_from': '2020-01-01', 'date_to': '2020-01-31'})
        assert resp.status_code == status.HTTP_200_OK, resp.data
        for key in (
            'inspections',
            'nonconformities',
            'corrective_actions',
            'incidents',
            'near_misses',
            'work_permits',
            'trainings',
        ):
            assert resp.data[key] == []
            assert resp.data['counts'][key] == 0

    def test_period_report_includes_inspections_and_ncrs(
        self, auth_client, project, user, wbs_node,
    ):
        insp = Inspection.objects.create(
            project=project,
            wbs=wbs_node,
            responsible_user=user,
            inspection_date=date(2026, 10, 10),
            result=InspectionResult.FAIL,
            description='Check',
            created_by=user,
            updated_by=user,
        )
        Nonconformity.objects.create(
            project=project,
            inspection=insp,
            wbs=wbs_node,
            description='NCR',
            raised_date=date(2026, 10, 10),
            created_by=user,
            updated_by=user,
        )
        url = REPORT.format(project_id=project.id)
        resp = auth_client.get(url, {'date_from': '2026-10-01', 'date_to': '2026-10-31'})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['counts']['inspections'] == 1
        assert resp.data['counts']['nonconformities'] == 1

    def test_work_permit_and_training_in_report(self, auth_client, project, user):
        permit = auth_client.post(
            PERMIT.format(project_id=project.id),
            {
                'permit_date': '2026-10-15',
                'permit_type': 'hot_work',
                'description': 'Welding',
            },
            format='json',
        )
        assert permit.status_code == status.HTTP_201_CREATED, permit.data
        train = auth_client.post(
            TRAIN.format(project_id=project.id),
            {
                'training_date': '2026-10-16',
                'topic': 'Scaffold safety',
            },
            format='json',
        )
        assert train.status_code == status.HTTP_201_CREATED, train.data
        report = auth_client.get(
            REPORT.format(project_id=project.id),
            {'date_from': '2026-10-01', 'date_to': '2026-10-31'},
        )
        assert report.status_code == status.HTTP_200_OK
        assert report.data['counts']['work_permits'] == 1
        assert report.data['counts']['trainings'] == 1
