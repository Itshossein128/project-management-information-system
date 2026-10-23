"""Receipt/consumption transaction typing, document references, and positive quantities (feature 033, task T033)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
import pytest

from common.reporting_units import SpecialtyUnit
from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
from project_templates.models import ProjectTemplate
from project_templates.services import activate_project_reporting_configuration
from projects.models import Project, Stakeholder, WBS
from resources.models import InventoryTransaction, Material, TransactionType
from sub_reports.models import DisciplineSubReport, SubReportStatus
from sub_reports.serializers import (
    SubReportMaterialSerializer,
    UnitReportMaterialSectionSerializer,
)
from sub_reports.services.section_validation import (
    SectionContractError,
    validate_material_rows,
)

User = get_user_model()

REPORT_DATE = date(2024, 6, 10)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def unit_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.WAREHOUSE,
        discipline='civil',
        lineage_id=None,
        status=SubReportStatus.DRAFT,
        created_by=user,
    )


@pytest.fixture
def project_with_material_catalog(db, project, user):
    template = ProjectTemplate.objects.create(
        template_name='Material Contract Template',
        project_type='warehouse',
        is_system=False,
        created_by=user,
    )
    activate_project_reporting_configuration(
        project=project,
        template=template,
        effective_from=date(2024, 6, 1),
        user=user,
    )
    return project


@pytest.fixture
def foreign_project(db, user):
    other = Project.objects.create(
        project_code='PRJ-001-F',
        project_name='Other Project',
        employer='Employer Co',
    )
    WBS.add_root(project=other, wbs_code='1', wbs_name='Root')
    stakeholder = Stakeholder.objects.create(
        project=other,
        name='Foreign Contractor Co',
        role='contractor',
        created_by=user,
    )
    other_material = Material.objects.create(
        project=other,
        material_code='MAT-FOREIGN-01',
        material_name='Foreign Steel Beams',
    )
    return {
        'project': other,
        'stakeholder': stakeholder,
        'material': other_material,
    }


@pytest.fixture
def material(db, project):
    """A project-scoped material."""
    return Material.objects.create(
        project=project,
        material_code='MAT-STEEL-01',
        material_name='Steel Beams',
    )


@pytest.fixture
def contractor(db, project, user):
    stakeholder = Stakeholder.objects.create(
        project=project,
        name='Test Contractor Co',
        role='contractor',
        created_by=user,
    )
    stakeholder.refresh_from_db()
    return stakeholder


@pytest.fixture
def section_material_payload(material):
    return {
        'material_description': 'Steel Beams',
        'quantity': '12.5000',
        'unit': 'kg',
        'transaction_type': 'receipt',
        'material_ref': str(material.id),
        'consumption_location': '',
        'supplier': 'Supplier Co',
        'warehouse_document_reference': 'WD-2024-001',
        'notes': 'Delivered at gate 2',
    }


# ---------------------------------------------------------------------------
# §2.4 / Contract §4: material transaction typing and document references
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestMaterialReceiptContract:
    def test_transaction_type_required(self, db, unit_report, section_material_payload):
        """Serializer and section validation require transaction_type on material rows."""
        payload = dict(section_material_payload)
        payload['transaction_type'] = ''
        with pytest.raises(SectionContractError) as exc_info:
            validate_material_rows(unit_report, [payload])
        assert 'transaction_type_required' in exc_info.value.codes
        assert 'transaction_type_required' in exc_info.value.field_errors('transaction_type')

        ser = SubReportMaterialSerializer(data=payload, context={'report': unit_report})
        assert not ser.is_valid()
        assert 'transaction_type' in ser.errors

    def test_receipt_requires_document_reference(self, db, unit_report, section_material_payload):
        """A receipt row must have a non-blank warehouse_document_reference."""
        payload = dict(section_material_payload)
        payload['transaction_type'] = 'receipt'
        payload['warehouse_document_reference'] = '   '
        with pytest.raises(SectionContractError) as exc_info:
            validate_material_rows(unit_report, [payload])
        assert 'receipt_requires_document_reference' in exc_info.value.codes
        assert 'receipt_requires_document_reference' in exc_info.value.field_errors(
            'warehouse_document_reference'
        )

    def test_consumption_location_required_for_consumption(
        self, db, unit_report, section_material_payload
    ):
        """Consumption rows must have consumption_location filled in."""
        payload = dict(section_material_payload)
        payload['transaction_type'] = 'consumption'
        payload['warehouse_document_reference'] = ''
        payload['consumption_location'] = ''
        with pytest.raises(SectionContractError) as exc_info:
            validate_material_rows(unit_report, [payload])
        assert 'consumption_location_required_for_consumption' in exc_info.value.codes
        assert 'consumption_location_required_for_consumption' in exc_info.value.field_errors(
            'consumption_location'
        )

    def test_quantity_must_be_positive(self, db, unit_report, section_material_payload):
        """Quantity on material rows must be strictly positive (> 0)."""
        for invalid_qty in ('0', '0.0000', '-5.0000'):
            payload = dict(section_material_payload)
            payload['quantity'] = invalid_qty
            with pytest.raises(SectionContractError) as exc_info:
                validate_material_rows(unit_report, [payload])
            assert 'quantity_must_be_positive' in exc_info.value.codes
            assert 'quantity_must_be_positive' in exc_info.value.field_errors('quantity')

    def test_supplier_preserved_independently(
        self, db, unit_report, section_material_payload, material
    ):
        """Supplier field is stored and returned verbatim and independently of material_ref."""
        payload = dict(section_material_payload)
        payload['material_ref'] = str(material.id)
        payload['supplier'] = 'Foolad Mobarakeh Co.'
        rows = validate_material_rows(unit_report, [payload])
        assert len(rows) == 1
        row = rows[0]
        assert row.supplier == 'Foolad Mobarakeh Co.'
        assert row.material_ref_id == material.id

        serialized = UnitReportMaterialSectionSerializer(
            row, context={'report': unit_report}
        ).data
        assert serialized['supplier'] == 'Foolad Mobarakeh Co.'
        assert serialized['material_ref'] == str(material.id)

    def test_warehouse_document_reference_preserved_independently(
        self, db, unit_report, section_material_payload, material, user
    ):
        """Warehouse document reference is stored verbatim and receipt_evidence is computed read-only."""
        payload = dict(section_material_payload)
        payload['material_ref'] = str(material.id)
        payload['warehouse_document_reference'] = 'WD-2024-001'
        rows = validate_material_rows(unit_report, [payload])
        row = rows[0]
        assert row.warehouse_document_reference == 'WD-2024-001'

        # Without a matching InventoryTransaction, receipt_evidence is 'unresolved_reference'
        serialized_unresolved = UnitReportMaterialSectionSerializer(
            row, context={'report': unit_report}
        ).data
        assert serialized_unresolved['warehouse_document_reference'] == 'WD-2024-001'
        assert serialized_unresolved['receipt_evidence'] == 'unresolved_reference'
        assert serialized_unresolved['receipt_resolved'] is False

        # Once a matching project warehouse document exists, receipt_evidence becomes 'resolved'
        InventoryTransaction.objects.create(
            project=unit_report.project,
            material=material,
            tx_date=REPORT_DATE,
            tx_type=TransactionType.IN,
            quantity=Decimal('12.5000'),
            document_ref='WD-2024-001',
            created_by=user,
        )
        serialized_resolved = UnitReportMaterialSectionSerializer(
            row, context={'report': unit_report}
        ).data
        assert serialized_resolved['receipt_evidence'] == 'resolved'
        assert serialized_resolved['receipt_resolved'] is True

    def test_cross_project_material_ref_refused(
        self, db, unit_report, section_material_payload, foreign_project
    ):
        """A material_ref belonging to a different project is rejected with reference_not_in_project_scope."""
        payload = dict(section_material_payload)
        payload['material_ref'] = str(foreign_project['material'].id)
        with pytest.raises(SectionContractError) as exc_info:
            validate_material_rows(unit_report, [payload])
        assert 'reference_not_in_project_scope' in exc_info.value.codes
        assert 'reference_not_in_project_scope' in exc_info.value.field_errors('material_ref')

    def test_materials_section_api_crud(
        self, db, auth_client, project, user, unit_report, section_material_payload
    ):
        """GET/POST/PATCH/DELETE on /units/warehouse/daily-reports/{id}/materials/ enforces §4 contract."""
        member, _ = ProjectMember.objects.get_or_create(
            project=project, user=user, defaults={'status': 'active'}
        )
        role, _ = Role.objects.get_or_create(role_name='WarehouseEditor033')
        for codename in ('view_reports', 'edit_reports'):
            RolePermission.objects.get_or_create(role=role, permission_codename=codename)
        ProjectMemberRole.objects.get_or_create(member=member, role=role)

        base_url = (
            f'/api/v1/projects/{project.id}/units/warehouse/'
            f'daily-reports/{unit_report.id}/materials/'
        )

        # Invalid POST (receipt without document ref) -> 422
        bad_payload = dict(section_material_payload, warehouse_document_reference='')
        res_bad = auth_client.post(base_url, bad_payload, format='json')
        assert res_bad.status_code == 422
        assert res_bad.data['error']['code'] == 'receipt_requires_document_reference'

        # Valid POST -> 201
        res_create = auth_client.post(base_url, section_material_payload, format='json')
        assert res_create.status_code == 201
        assert len(res_create.data) == 1
        row_id = res_create.data[0]['id']
        assert res_create.data[0]['supplier'] == 'Supplier Co'
        assert res_create.data[0]['warehouse_document_reference'] == 'WD-2024-001'

        # PATCH -> 200
        res_patch = auth_client.patch(
            f'{base_url}{row_id}/',
            {'quantity': '20.0000', 'supplier': 'Updated Supplier'},
            format='json',
        )
        assert res_patch.status_code == 200
        assert res_patch.data['quantity'] == '20.0000'
        assert res_patch.data['supplier'] == 'Updated Supplier'

        # DELETE -> 204
        res_del = auth_client.delete(f'{base_url}{row_id}/')
        assert res_del.status_code == 204
