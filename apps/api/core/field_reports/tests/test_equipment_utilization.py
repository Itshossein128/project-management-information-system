"""Tests for equipment registry and utilization."""

import pytest
from rest_framework import status

from field_reports.models import Equipment, EquipmentLog, EquipmentStatus, OwnershipType, ReportShift
from field_reports.services.equipment_utilization import equipment_utilization_list, equipment_utilization_summary


@pytest.fixture
def registry_equipment(db, project, user):
    return Equipment.objects.create(
        project=project,
        equipment_code='EX-01',
        equipment_name='بیل مکانیکی',
        ownership_type=OwnershipType.OWNED,
        default_hourly_rate=500,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestEquipmentUtilization:
    def test_utilization_rate_from_productive_and_idle(self, project, user, registry_equipment):
        EquipmentLog.objects.create(
            project=project,
            equipment=registry_equipment,
            log_date='2024-08-01',
            equipment_name='بیل مکانیکی',
            equipment_ref='EX-01',
            shift=ReportShift.DAY,
            status=EquipmentStatus.ACTIVE,
            ownership_type=OwnershipType.OWNED,
            productive_hours=6,
            idle_hours=2,
            hourly_rate=500,
            fuel_cost=100,
            created_by=user,
            updated_by=user,
        )
        rows = equipment_utilization_list(project.id)
        assert len(rows) == 1
        assert rows[0]['productive_hours'] == 6
        assert rows[0]['idle_hours'] == 2
        assert rows[0]['utilization_rate'] == 75.0
        assert rows[0]['total_cost'] == 3100.0

    def test_derives_productive_from_work_times(self, project, user):
        from datetime import time

        EquipmentLog.objects.create(
            project=project,
            log_date='2024-08-02',
            equipment_name='لودر',
            shift=ReportShift.DAY,
            status=EquipmentStatus.ACTIVE,
            ownership_type=OwnershipType.RENTED,
            work_start=time(8, 0),
            work_end=time(16, 0),
            repair_hours=1,
            created_by=user,
            updated_by=user,
        )
        rows = equipment_utilization_list(project.id)
        assert rows[0]['productive_hours'] == 7.0

    def test_summary_endpoint(self, auth_client, project, user, registry_equipment):
        EquipmentLog.objects.create(
            project=project,
            equipment=registry_equipment,
            log_date='2024-08-01',
            equipment_name='بیل مکانیکی',
            shift=ReportShift.DAY,
            status=EquipmentStatus.ACTIVE,
            ownership_type=OwnershipType.OWNED,
            productive_hours=8,
            idle_hours=0,
            created_by=user,
            updated_by=user,
        )
        url = f'/api/v1/projects/{project.id}/equipment-utilization/summary/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['equipment_count'] == 1
        assert resp.data['avg_utilization_rate'] == 100.0

    def test_registry_crud(self, auth_client, project):
        base = f'/api/v1/projects/{project.id}/equipment/'
        create = auth_client.post(
            base,
            {
                'equipment_code': 'CR-01',
                'equipment_name': 'جرثقیل',
                'ownership_type': 'owned',
            },
            format='json',
        )
        assert create.status_code == status.HTTP_201_CREATED
        listing = auth_client.get(base)
        assert listing.status_code == status.HTTP_200_OK
        assert len(listing.data['results']) >= 1

    def test_dedupes_daily_report_when_standalone_log_exists(
        self, project, user, registry_equipment
    ):
        from datetime import time

        from field_reports.models import (
            DailyReport,
            DailyReportEquipment,
            ReportStatus,
            ReportShift,
        )

        EquipmentLog.objects.create(
            project=project,
            equipment=registry_equipment,
            log_date='2024-08-10',
            equipment_name='بیل مکانیکی',
            equipment_ref='EX-01',
            shift=ReportShift.DAY,
            status=EquipmentStatus.ACTIVE,
            ownership_type=OwnershipType.OWNED,
            productive_hours=6,
            idle_hours=2,
            created_by=user,
            updated_by=user,
        )
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-10',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
        )
        DailyReportEquipment.objects.create(
            report=report,
            equipment=registry_equipment,
            equipment_name='بیل مکانیکی',
            equipment_ref='EX-01',
            shift=ReportShift.DAY,
            status=EquipmentStatus.ACTIVE,
            ownership_type=OwnershipType.OWNED,
            productive_hours=8,
            idle_hours=0,
            work_start=time(8, 0),
            work_end=time(16, 0),
        )

        rows = equipment_utilization_list(project.id)
        assert len(rows) == 1
        assert rows[0]['productive_hours'] == 6
        assert rows[0]['idle_hours'] == 2
        assert rows[0]['log_count'] == 1
