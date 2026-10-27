"""Section writers used by v2 sync (feature 037, T036)."""
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from projects.models import Activity, Stakeholder, WBS
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportHseIncident,
    DisciplineSubReportIssue,
    DisciplineSubReportLabor,
    DisciplineSubReportMachinery,
    DisciplineSubReportMaterial,
    DisciplineSubReportNote,
    DisciplineSubReportVisit,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def endpoint(project):
    return f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/'


def op(local_report_id, kind, payload, depends_on, report_id=None):
    return {
        'operation_id': str(uuid4()),
        'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': report_id},
        'action': 'create',
        'target': {'kind': kind, 'client_id': str(uuid4()), 'server_id': None},
        'base_revision': None,
        'depends_on': depends_on,
        'payload': payload,
    }


def test_each_section_create_is_targeted_and_empty_payload_does_not_replace(project, user):
    node = WBS.add_root(project=project, wbs_code='1', wbs_name='Root')
    activity = Activity.objects.create(
        project=project, wbs=node, activity_code='A1', activity_name='Pour', status='in_progress', created_by=user,
    )
    contractor = Stakeholder.objects.create(project=project, name='Crew Co', role='contractor', created_by=user)
    client = APIClient()
    client.force_authenticate(user)
    local_report_id = str(uuid4())
    header = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': 'SECTIONS'},
    }
    rows = [
        op(local_report_id, 'activity', {
            'row_number': 1, 'shift': 'shift_1', 'activity_ref': str(activity.id),
            'activity_description': 'kept activity', 'contractor_ref': str(contractor.id), 'crew_name': 'Crew A',
        }, [header['operation_id']]),
        op(local_report_id, 'labor', {
            'labor_category': 'direct', 'job_title': 'Mason', 'present_count': 2,
        }, [header['operation_id']]),
        op(local_report_id, 'material', {
            'transaction_type': 'consumption', 'material_description': 'Cement', 'quantity': '1.5',
            'unit': 'ton', 'consumption_location': 'Slab',
        }, [header['operation_id']]),
        op(local_report_id, 'machinery', {
            'row_number': 1, 'equipment_type': 'Crane',
            'status_total': 0, 'status_active': 0, 'status_ready': 0, 'status_inactive': 0, 'status_under_repair': 0,
            'operating_hours': '1.00', 'stoppage_hours': '0.00', 'repair_hours': '0.00',
        }, [header['operation_id']]),
        op(local_report_id, 'concrete', {
            'concrete_description': 'Slab pour', 'volume_m3': '2.5',
        }, [header['operation_id']]),
        op(local_report_id, 'general', {'activity_description': 'Site cleanup'}, [header['operation_id']]),
        op(local_report_id, 'issue', {'text': 'Blocked access'}, [header['operation_id']]),
        op(local_report_id, 'visit', {'text': 'Consultant visit'}, [header['operation_id']]),
        op(local_report_id, 'incident', {
            'text': 'Minor cut', 'severity': 'minor', 'immediate_action': 'First aid',
        }, [header['operation_id']]),
        op(local_report_id, 'note', {'text': 'End of shift'}, [header['operation_id']]),
    ]
    response = client.post(endpoint(project), {'contract_version': 2, 'operations': [header, *rows]}, format='json')
    assert response.status_code == 200, response.content
    failed = [item for item in response.data['results'] if item['outcome'] != 'success']
    assert failed == [], failed
    report = DisciplineSubReport.objects.get(project=project, form_code='SECTIONS')
    assert report.activities.filter(is_deleted=False).count() == 1
    assert DisciplineSubReportLabor.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportMaterial.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportMachinery.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportConcrete.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportGeneralActivity.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportIssue.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportVisit.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportHseIncident.objects.filter(sub_report=report, is_deleted=False).count() == 1
    assert DisciplineSubReportNote.objects.filter(sub_report=report, is_deleted=False).count() == 1

    replacement = {
        'operation_id': str(uuid4()), 'local_report_id': local_report_id,
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-27', 'report_id': str(report.id)},
        'action': 'create', 'target': {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': None},
        'base_revision': None, 'depends_on': [], 'payload': [],
    }
    rejected = client.post(endpoint(project), {'contract_version': 2, 'operations': [replacement]}, format='json')
    assert rejected.data['results'][0]['error']['code'] == 'snapshot_replacement_forbidden'
    assert DisciplineSubReportActivity.objects.filter(sub_report=report, is_deleted=False, activity_description='kept activity').count() == 1
