"""Procurement workflow API tests."""

import pytest
from django.urls import reverse

from resources.models import Material, MaterialRequest, MaterialRequestStatus, PurchaseOrder


@pytest.fixture
def material(db, project):
    return Material.objects.create(
        project=project,
        material_code='STL-01',
        material_name='فولاد',
        estimated_total_qty=500,
    )


@pytest.fixture
def supplier(db, project, user):
    from resources.models import Supplier

    return Supplier.objects.create(
        project=project,
        supplier_name='تأمین‌کننده آزمون',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def material_request(db, project, material, user):
    return MaterialRequest.objects.create(
        project=project,
        material=material,
        request_number=1,
        requested_qty=100,
        unit='kg',
        status=MaterialRequestStatus.PENDING,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestProcurementWorkflow:
    def test_create_material_request(self, auth_client, project, material):
        url = reverse('material-request-list', kwargs={'project_pk': project.id})
        resp = auth_client.post(
            url,
            {'material': str(material.id), 'requested_qty': '50', 'notes': 'E2E PR'},
            format='json',
        )
        assert resp.status_code == 201
        assert resp.data['status'] == 'pending'
        assert resp.data['request_number'] == 1

    def test_approve_request(self, auth_client, project, material_request):
        url = reverse('material-request-approve', kwargs={'project_pk': project.id, 'pk': material_request.id})
        resp = auth_client.post(url, {}, format='json')
        assert resp.status_code == 200
        material_request.refresh_from_db()
        assert material_request.status == MaterialRequestStatus.APPROVED

    def test_place_order(self, auth_client, project, material_request, supplier, user):
        material_request.status = MaterialRequestStatus.APPROVED
        material_request.save()
        url = reverse('material-request-place-order', kwargs={'project_pk': project.id, 'pk': material_request.id})
        resp = auth_client.post(
            url,
            {'supplier': str(supplier.id), 'order_date': '1403/01/15'},
            format='json',
        )
        assert resp.status_code == 200
        assert PurchaseOrder.objects.filter(material_request=material_request).exists()
        material_request.refresh_from_db()
        assert material_request.status == MaterialRequestStatus.ORDERED

    def test_deliver_creates_inventory_tx(self, auth_client, project, material_request, supplier, user):
        material_request.status = MaterialRequestStatus.APPROVED
        material_request.save()
        po = PurchaseOrder.objects.create(
            project=project,
            material_request=material_request,
            supplier=supplier,
            po_number=1,
            order_date='2024-06-01',
            ordered_qty=100,
            created_by=user,
            updated_by=user,
        )
        material_request.status = MaterialRequestStatus.ORDERED
        material_request.save()
        url = reverse('material-request-deliver', kwargs={'project_pk': project.id, 'pk': material_request.id})
        resp = auth_client.post(url, {'actual_delivery_date': '1403/02/01'}, format='json')
        assert resp.status_code == 200
        material_request.refresh_from_db()
        assert material_request.status == MaterialRequestStatus.DELIVERED
        from resources.models import InventoryTransaction

        assert InventoryTransaction.objects.filter(material=material_request.material, document_ref=f'PO-{po.po_number}').exists()

    def test_cancel_pending(self, auth_client, project, material_request):
        url = reverse('material-request-cancel', kwargs={'project_pk': project.id, 'pk': material_request.id})
        resp = auth_client.post(url, {}, format='json')
        assert resp.status_code == 200
        material_request.refresh_from_db()
        assert material_request.status == MaterialRequestStatus.CANCELLED

    def test_viewer_cannot_approve(self, api_client, project, material_request, other_user, viewer_role):
        from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole

        member = ProjectMember.objects.create(project=project, user=other_user, status=MemberStatus.ACTIVE)
        ProjectMemberRole.objects.create(member=member, role=viewer_role)
        api_client.force_authenticate(user=other_user)
        url = reverse('material-request-approve', kwargs={'project_pk': project.id, 'pk': material_request.id})
        resp = api_client.post(url, {}, format='json')
        assert resp.status_code == 403
