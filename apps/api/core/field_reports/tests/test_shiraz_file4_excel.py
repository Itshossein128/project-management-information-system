import io
from datetime import date
from decimal import Decimal
import openpyxl
import pytest
from rest_framework import status
from django.urls import reverse

from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportEquipment,
    DailyReportLabor,
    DailyReportMaterial,
    LaborCategory,
    ReportShift,
    ReportStatus,
)
from field_reports.shiraz_file4_excel import (
    SHIRAZ_DIRECT_ROLES,
    SHIRAZ_INDIRECT_ROLES,
    ShirazFile4ExcelBuilder,
)


@pytest.fixture
def sample_report_with_data(project, user):
    report = DailyReport.objects.create(
        project=project,
        created_by=user,
        report_date=date(2025, 2, 2),
        shift=ReportShift.FULL,
        work_front='بلوک ۳۲ و ۳۳',
        weather_condition='clear',
        temp_min=Decimal('5.0'),
        temp_max=Decimal('18.5'),
        site_status='active',
        prepared_by=user,
        status=ReportStatus.DRAFT,
    )
    # Indirect staff entries
    DailyReportLabor.objects.create(
        report=report,
        job_title='سرپرست کارگاه',
        custom_title='سرپرست کارگاه',
        labor_category=LaborCategory.INDIRECT,
        shift_1_count=1,
        shift_2_count=0,
        shift_3_count=0,
        absence_count=0,
        total_count=1,
    )
    DailyReportLabor.objects.create(
        report=report,
        job_title='کارشناس دفتر فنی',
        custom_title='کارشناس دفتر فنی',
        labor_category=LaborCategory.INDIRECT,
        shift_1_count=2,
        shift_2_count=1,
        shift_3_count=0,
        absence_count=1,
        total_count=3,
    )

    # Direct labor entries
    DailyReportLabor.objects.create(
        report=report,
        job_title='کارگر ساده',
        custom_title='کارگر ساده',
        labor_category=LaborCategory.DIRECT,
        shift_1_count=15,
        shift_2_count=5,
        shift_3_count=0,
        absence_count=2,
        total_count=20,
    )
    DailyReportLabor.objects.create(
        report=report,
        job_title='آرماتور بند و قالب بند',
        custom_title='آرماتور بند و قالب بند',
        labor_category=LaborCategory.DIRECT,
        shift_1_count=8,
        shift_2_count=0,
        shift_3_count=0,
        absence_count=0,
        total_count=8,
    )

    # Materials
    DailyReportMaterial.objects.create(
        report=report,
        material_description='سیمان فله تیپ ۲',
        transaction_type='receipt',
        quantity=Decimal('25.5'),
        unit='تن',
        supplier='سیمان فارس',
        consumption_location='سیلو شماره ۱',
    )

    # Concrete
    DailyReportConcreteLog.objects.create(
        report=report,
        concrete_description='بتن عیار ۳۵۰',
        volume_m3=Decimal('84.0'),
        zone='قطعه ۱۰',
        block='بلوک ۳۲',
        floor='سقف سوم',
        structural_element='دال سقف',
        notes='بخش شرقی',
    )

    # Equipment
    DailyReportEquipment.objects.create(
        report=report,
        equipment_name='پمپ بتن دکل ۳۶ متری',
        shift=ReportShift.DAY,
        status='active',
        ownership_type='rented',
        productive_hours=Decimal('7.5'),
        repair_hours=Decimal('0.5'),
    )

    # Activities
    DailyReportActivity.objects.create(
        report=report,
        activity_description='قالب‌بندی و بتن‌ریزی سقف بلوک ۳۲',
        shift='shift_1',
        subcontractor_name='پیمانکاری خنکا',
        headcount=12,
        zone='۱۰',
        block='۳۲',
        floor='۳',
        quantity=Decimal('84.0'),
        unit='متر مکعب',
    )

    return report


@pytest.mark.django_db
class TestShirazFile4Excel:

    def test_empty_report_keeps_sections_and_zero_formulas(self, project, user):
        report = DailyReport.objects.create(
            project=project,
            created_by=user,
            report_date=date(2025, 2, 3),
            shift=ReportShift.FULL,
            site_status='inactive',
            inactivity_reason='holiday',
            status=ReportStatus.DRAFT,
        )

        excel_bytes, _ = ShirazFile4ExcelBuilder(report).build()
        ws = openpyxl.load_workbook(io.BytesIO(excel_bytes), data_only=False).active
        values = [cell.value for row in ws.iter_rows() for cell in row]
        formulas = [str(value) for value in values if isinstance(value, str) and value.startswith('=SUM')]

        assert ws.sheet_view.rightToLeft is True
        assert any('هیچ فعالیت اجرایی' in str(value) for value in values)
        assert any('موردی برای بتن‌ریزی' in str(value) for value in values)
        assert any(formula.startswith('=SUM(C') for formula in formulas)
        assert any(formula.startswith('=SUM(E') for formula in formulas)

    def test_builder_rtl_and_sections(self, sample_report_with_data):
        builder = ShirazFile4ExcelBuilder(sample_report_with_data)
        excel_bytes, filename = builder.build()

        assert filename.startswith('daily-report-')
        assert filename.endswith('.xlsx')

        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), data_only=False)
        ws = wb.active

        # RTL orientation
        assert ws.sheet_view.rightToLeft is True

        # Header contains project and title
        header_val = ws['A1'].value
        assert 'گزارش روزانه کارگاه' in header_val

        # Scan text across all cells
        cell_values = [cell.value for row in ws.iter_rows() for cell in row if cell.value is not None]
        all_text = ' '.join(str(v) for v in cell_values)

        # 34 indirect roles checked
        for role in SHIRAZ_INDIRECT_ROLES:
            assert role in all_text, f'Role {role} missing from indirect section'

        # 32 direct roles checked
        for role in SHIRAZ_DIRECT_ROLES:
            assert role in all_text, f'Role {role} missing from direct section'

        # Native Excel formulas checked
        formula_cells = [str(v) for v in cell_values if str(v).startswith('=SUM')]
        assert len(formula_cells) >= 68, f'Expected at least 68 =SUM formulas, found {len(formula_cells)}'

        # Child tables checked
        assert 'سیمان فله تیپ ۲' in all_text
        assert 'بتن عیار ۳۵۰' in all_text
        assert 'پمپ بتن دکل ۳۶ متری' in all_text
        assert 'قالب‌بندی و بتن‌ریزی سقف بلوک ۳۲' in all_text

    def test_excel_endpoint_authorized(self, auth_client, sample_report_with_data):
        url = f'/api/v1/projects/{sample_report_with_data.project_id}/daily-reports/{sample_report_with_data.id}/excel/'
        resp = auth_client.get(url)

        assert resp.status_code == status.HTTP_200_OK
        assert resp['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'Content-Disposition' in resp
        assert 'attachment; filename="daily-report-' in resp['Content-Disposition']

        wb = openpyxl.load_workbook(io.BytesIO(resp.content))
        assert wb.active.sheet_view.rightToLeft is True

    def test_excel_endpoint_unauthenticated(self, api_client, sample_report_with_data):
        url = f'/api/v1/projects/{sample_report_with_data.project_id}/daily-reports/{sample_report_with_data.id}/excel/'
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
