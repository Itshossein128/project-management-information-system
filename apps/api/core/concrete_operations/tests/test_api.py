from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from concrete_operations.models import ConcreteBatch, ReadyMixDelivery
from field_reports.models import DailyReport, DailyReportConcreteLog
from master_data.models import ProjectMember, ProjectMemberPermissionOverride
from projects.models import Project
from resources.models import Supplier


@pytest.fixture
def urls(project):
    base = f'/api/v1/projects/{project.id}'
    return base + '/concrete-batches/', base + '/ready-mix-deliveries/', base + '/concrete-operations/'


@pytest.fixture
def supplier(project, user):
    return Supplier.objects.create(project=project, supplier_name='Concrete Co', created_by=user)


@pytest.fixture
def batch_payload():
    return {'date': '2024-06-01', 'volume_m3': '12.500', 'cement_kg': '100', 'sand_kg': '200',
            'aggregate_kg': '300', 'water_l': '50', 'plasticizer_l': '2'}


@pytest.mark.django_db
class TestConcreteOperations:
    def test_quantities_dates_and_project_are_validated(self, auth_client, urls, batch_payload, project):
        batches, _, _ = urls
        for field, value in [('volume_m3', '0'), ('cement_kg', '-1'), ('water_l', '-0.1'), ('date', '2024-02-30')]:
            response = auth_client.post(batches, {**batch_payload, field: value}, format='json')
            assert response.status_code == 400, (field, response.data)
        other = Project.objects.create(project_code='OTHER', project_name='Other')
        response = auth_client.post(batches, {**batch_payload, 'project': str(other.id)}, format='json')
        assert response.status_code == 201
        assert ConcreteBatch.objects.get(id=response.data['id']).project_id == project.id
        assert 'project' not in response.data

    def test_supplier_and_record_cannot_cross_project(self, auth_client, urls, batch_payload, project, user, supplier):
        batches, deliveries, _ = urls
        other = Project.objects.create(project_code='OTHER', project_name='Other')
        foreign = Supplier.objects.create(project=other, supplier_name='Foreign', created_by=user)
        data = {'date': '2024-06-01', 'volume_m3': '3', 'supplier': str(foreign.id)}
        assert auth_client.post(deliveries, data, format='json').status_code == 400
        assert auth_client.post(deliveries, {**data, 'supplier': str(supplier.id)}, format='json').status_code == 201
        foreign_batch = ConcreteBatch.objects.create(project=other, created_by=user, **batch_payload)
        detail = batches + f'{foreign_batch.id}/'
        assert auth_client.get(detail).status_code == 404
        assert auth_client.patch(detail, {'volume_m3': '5'}, format='json').status_code == 404
        assert auth_client.delete(detail).status_code == 404
        assert auth_client.get(batches).data['count'] == 0

    def test_summary_export_date_range_and_active_pours(self, auth_client, urls, batch_payload, project, user, supplier):
        batches, deliveries, report = urls
        batch = auth_client.post(batches, batch_payload, format='json')
        assert batch.status_code == 201
        delivery = auth_client.post(deliveries, {'date': '2024-06-01', 'volume_m3': '4', 'supplier': str(supplier.id)}, format='json')
        assert delivery.status_code == 201
        daily = DailyReport.objects.create(project=project, report_date='2024-06-01', created_by=user)
        DailyReportConcreteLog.objects.create(report=daily, concrete_description='Poured', volume_m3=Decimal('3.5'))
        DailyReportConcreteLog.objects.create(report=daily, concrete_description='Deleted', volume_m3=Decimal('99'), is_deleted=True)
        deleted_report = DailyReport.objects.create(project=project, report_date='2024-06-02', created_by=user, is_deleted=True)
        DailyReportConcreteLog.objects.create(report=deleted_report, concrete_description='Hidden', volume_m3=Decimal('99'))
        summary = auth_client.get(report + 'summary/?date_from=2024-06-01&date_to=2024-06-01')
        assert summary.status_code == 200
        assert summary.data == {'produced_m3': '12.500', 'delivered_m3': '4.000', 'poured_m3': '3.500'}
        exported = auth_client.get(report + 'export/?date_from=2024-06-01&date_to=2024-06-01')
        assert exported.status_code == 200
        csv = exported.content.decode('utf-8-sig')
        assert 'batch,2024-06-01,12.500' in csv
        assert 'delivery,2024-06-01,4.000' in csv
        assert 'poured_m3,,3.500' in csv
        assert auth_client.get(report + 'summary/?date_from=bad').status_code == 400
        assert auth_client.get(report + 'export/?date_from=2024-06-02&date_to=2024-06-01').status_code == 400
        assert auth_client.get(report + 'summary/?date_from=2024-07-01').data == {
            'produced_m3': '0', 'delivered_m3': '0', 'poured_m3': '0'}

    def test_permissions_for_read_only_and_nonmember(self, api_client, auth_client, urls, batch_payload, other_user, viewer_member, project):
        batches, _, report = urls
        created = auth_client.post(batches, batch_payload, format='json').data
        ProjectMemberPermissionOverride.objects.update_or_create(member=viewer_member, permission_codename='edit_reports', defaults={'is_granted': False})
        api_client.force_authenticate(user=other_user)
        assert api_client.get(batches).status_code == 200
        assert api_client.get(batches + created['id'] + '/').status_code == 200
        assert api_client.get(report + 'summary/').status_code == 200
        assert api_client.get(report + 'export/').status_code == 200
        assert api_client.post(batches, batch_payload, format='json').status_code == 403
        assert api_client.patch(batches + created['id'] + '/', {'volume_m3': '6'}, format='json').status_code == 403
        viewer_member.status = 'inactive'
        viewer_member.save(update_fields=['status'])
        assert api_client.get(batches).status_code == 403
        assert api_client.get(report + 'export/').status_code == 403
        outsider = get_user_model().objects.create_user(username='outsider', mobile='+989121234569', password='testpass123')
        api_client.force_authenticate(user=outsider)
        assert api_client.get(report + 'summary/').status_code == 403
