import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from field_reports.models import (
    DailyReport,
    ReportShift,
    ReportStatus,
    DailyActivity,
    DailyLabor,
    DailyEquipment,
    DailyMaterialUsage,
    DailyIncident,
    IncidentType,
)
from projects.models import Project, Activity, WBS
from resources.models import Material

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='tester', password='pwd')

@pytest.fixture
def project(db, user):
    return Project.objects.create(
        project_code='PRJ-001',
        project_name='Test Project',
        employer='Test Employer',
        start_date='2024-01-01',
        project_manager=user,
    )

@pytest.fixture
def wbs(project):
    return WBS.objects.create(
        project=project,
        wbs_code='W-1',
        wbs_name='WBS 1',
        weight_physical=1.0,
        weight_financial=1.0,
        depth=1,
    )

@pytest.fixture
def activity(project, wbs):
    return Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='ACT-1',
        activity_name='Activity 1',
        weight=1.0,
    )

@pytest.fixture
def daily_report(project, user):
    return DailyReport.objects.create(
        project=project,
        report_date='2024-01-01',
        shift=ReportShift.DAY,
        weather='Sunny',
        prepared_by=user,
    )

@pytest.fixture
def material(db):
    return Material.objects.create(
        material_code='MAT-1',
        material_name='Cement',
    )


@pytest.mark.django_db
class TestDailyReportModel:
    def test_create_daily_report(self, project):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-01-01',
            shift=ReportShift.DAY,
            weather='Sunny'
        )
        assert report.id is not None
        assert report.status == ReportStatus.DRAFT
        assert report.synced_from_offline is False

    def test_unique_together_constraint(self, project):
        DailyReport.objects.create(
            project=project,
            report_date='2024-01-01',
            shift=ReportShift.DAY
        )
        with pytest.raises(IntegrityError):
            DailyReport.objects.create(
                project=project,
                report_date='2024-01-01',
                shift=ReportShift.DAY
            )


@pytest.mark.django_db
class TestDailyActivityModel:
    def test_create_daily_activity(self, daily_report, activity):
        da = DailyActivity.objects.create(
            report=daily_report,
            activity=activity,
            work_front='Block A',
            executed_quantity=15.5,
            notes='All good'
        )
        assert da.id is not None
        assert da.report == daily_report
        assert da.activity == activity
        assert da.work_front == 'Block A'
        assert float(da.executed_quantity) == 15.5


@pytest.mark.django_db
class TestDailyLaborModel:
    def test_create_daily_labor(self, daily_report, activity):
        dl = DailyLabor.objects.create(
            report=daily_report,
            labor_type='Skilled',
            discipline='Civil',
            headcount=10,
            work_hours=8,
            overtime_hours=2,
            daily_rate=150.0,
            activity=activity,
        )
        assert dl.id is not None
        assert dl.report == daily_report
        assert dl.headcount == 10
        assert float(dl.work_hours) == 8.0


@pytest.mark.django_db
class TestDailyEquipmentModel:
    def test_create_daily_equipment(self, daily_report, user, activity):
        de = DailyEquipment.objects.create(
            report=daily_report,
            equipment_type='Excavator',
            equipment_code='EXC-01',
            work_hours=6.5,
            idle_hours=1.5,
            idle_reason='Waiting for trucks',
            operator=user,
            activity=activity,
            hourly_rate=50.0,
            fuel_cost=20.0,
        )
        assert de.id is not None
        assert de.report == daily_report
        assert de.equipment_type == 'Excavator'
        assert float(de.work_hours) == 6.5


@pytest.mark.django_db
class TestDailyMaterialUsageModel:
    def test_create_daily_material_usage(self, daily_report, material, activity):
        dmu = DailyMaterialUsage.objects.create(
            report=daily_report,
            material=material,
            quantity_used=100.5,
            activity=activity,
            notes='Used in foundation',
        )
        assert dmu.id is not None
        assert dmu.report == daily_report
        assert dmu.material == material
        assert float(dmu.quantity_used) == 100.5


@pytest.mark.django_db
class TestDailyIncidentModel:
    def test_create_daily_incident(self, daily_report):
        di = DailyIncident.objects.create(
            report=daily_report,
            incident_type=IncidentType.SAFETY,
            description='Worker tripped over wire',
            corrective_action='Cleaned up site',
        )
        assert di.id is not None
        assert di.report == daily_report
        assert di.incident_type == IncidentType.SAFETY
