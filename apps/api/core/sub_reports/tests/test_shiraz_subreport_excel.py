import io
from datetime import date
from decimal import Decimal
from uuid import uuid4
import openpyxl
import pytest
from rest_framework import status

from common.reporting_units import SpecialtyUnit
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    SubReportStatus,
)
from sub_reports.shiraz_subreport_excel import ShirazSubReportExcelBuilder


@pytest.fixture
def civil_sub_report(project, user):
    lid = uuid4()
    sr = DisciplineSubReport.objects.create(
        project=project,
        created_by=user,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        report_date=date(2025, 2, 2),
        status=SubReportStatus.DRAFT,
        lineage_id=lid,
        version_number=1,
        is_current=True,
        weather_condition='clear',
    )
    DisciplineSubReportActivity.objects.create(
        sub_report=sr,
        row_number=1,
        shift='1',
        crew_name='پیمانکاری خنکا',
        foreman_count=2,
        worker_count=10,
        parcel='۱۰',
        block='۳۲',
        floor='۳',
        activity_description='اجرای سازه 3D پنل و دیوار داخلی',
        unit='متر مربع',
        quantity=Decimal('150.00'),
        execution_percentage=Decimal('65.50'),
    )
    DisciplineSubReportActivity.objects.create(
        sub_report=sr,
        row_number=2,
        shift='1',
        crew_name='نفر شرکت',
        foreman_count=1,
        worker_count=4,
        parcel='۱۰',
        block='۳۳',
        floor='۲',
        activity_description='نصب وال‌پست جان‌پناه بام',
        unit='شاخه',
        quantity=Decimal('24.00'),
        execution_percentage=Decimal('100.00'),
    )
    return sr


@pytest.fixture
def electrical_sub_report(project, user):
    lid = uuid4()
    sr = DisciplineSubReport.objects.create(
        project=project,
        created_by=user,
        unit=SpecialtyUnit.ELECTRICAL,
        discipline='electrical',
        report_date=date(2025, 2, 2),
        status=SubReportStatus.DRAFT,
        lineage_id=lid,
        version_number=1,
        is_current=True,
        weather_condition='clear',
    )
    DisciplineSubReportActivity.objects.create(
        sub_report=sr,
        row_number=1,
        shift='1',
        crew_name='اکیپ رضایی',
        foreman_count=1,
        worker_count=3,
        block='۳۲',
        floor='۴',
        activity_description='لوله‌گذاری روشنایی سقف و نصب قوطی کلید',
        unit='متر طول',
        quantity=Decimal('280.00'),
    )
    return sr


@pytest.mark.django_db
class TestShirazSubReportExcel:

    def test_header_uses_project_data_and_does_not_invent_missing_values(self, civil_sub_report):
        civil_sub_report.project.contractor = 'پیمانکار نمونه'
        civil_sub_report.weather_condition = ''
        civil_sub_report.form_code = ''
        civil_sub_report.revision_number = ''
        ws = openpyxl.load_workbook(io.BytesIO(ShirazSubReportExcelBuilder(civil_sub_report).build()[0])).active
        assert 'پیمانکار نمونه' in ws['A1'].value
        assert 'پی‌چین' not in ws['A1'].value
        assert 'نامشخص' in ws['D3'].value
        assert 'ثبت نشده' in ws['G3'].value and 'ثبت نشده' in ws['J3'].value

    def test_null_values_one_percent_and_formula_text_are_preserved(self, civil_sub_report):
        DisciplineSubReportActivity.objects.create(
            sub_report=civil_sub_report, row_number=3, shift='1', crew_name='=1+1',
            foreman_count=None, worker_count=None, activity_description='=2+2',
            unit='متر', quantity=None, execution_percentage=None,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=civil_sub_report, row_number=4, shift='1', crew_name='One percent',
            foreman_count=0, worker_count=0, activity_description='One percent',
            unit='متر', quantity=0, execution_percentage=Decimal('1'),
        )
        ws = openpyxl.load_workbook(io.BytesIO(ShirazSubReportExcelBuilder(civil_sub_report).build()[0]), data_only=False).active
        rows = {row[8].value: row for row in ws.iter_rows() if len(row) > 11 and row[8].value in ('=2+2', 'One percent')}
        unknown, one = rows['=2+2'], rows['One percent']
        assert unknown[2].data_type == 's' and unknown[8].data_type == 's'
        assert unknown[3].value is None and unknown[4].value is None
        assert unknown[10].value == '*' and unknown[11].value is None
        assert one[10].value == 0 and one[11].value == 0.01
        assert any(cell.data_type == 'f' and str(cell.value).startswith('=SUM(') for row in ws for cell in row)

    def test_contractor_and_crew_are_both_kept(self, civil_sub_report, user):
        from projects.models import Stakeholder
        contractor = Stakeholder.objects.create(project=civil_sub_report.project, name='پیمانکار نمونه', role='contractor', created_by=user)
        activity = civil_sub_report.activities.first()
        activity.contractor_ref = contractor
        activity.crew_name = 'اکیپ مستقل'
        activity.save()
        ws = openpyxl.load_workbook(io.BytesIO(ShirazSubReportExcelBuilder(civil_sub_report).build()[0])).active
        row = next(row for row in ws.iter_rows() if len(row) > 8 and row[8].value == activity.activity_description)
        assert 'پیمانکار نمونه' in row[2].value and 'اکیپ مستقل' in row[2].value

    def test_canonical_shift_is_readable_in_export(self, civil_sub_report):
        activity = civil_sub_report.activities.first()
        activity.shift = 'shift_1'
        activity.save(update_fields=['shift'])
        ws = openpyxl.load_workbook(io.BytesIO(ShirazSubReportExcelBuilder(civil_sub_report).build()[0])).active
        row = next(row for row in ws.iter_rows() if len(row) > 8 and row[8].value == activity.activity_description)
        assert row[1].value == 'شیفت ۱'

    def test_civil_subreport_file5_format(self, civil_sub_report):
        builder = ShirazSubReportExcelBuilder(civil_sub_report)
        excel_bytes, filename = builder.build()

        assert filename.startswith('civil-subreport-')
        assert filename.endswith('.xlsx')

        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), data_only=False)
        ws = wb.active

        # RTL orientation
        assert ws.sheet_view.rightToLeft is True

        # Header contains company and civil discipline
        title_val = str(ws['A1'].value)
        assert 'پی‌چین' not in title_val
        assert 'اجرای ابنیه' in title_val

        # Scan all cell contents
        cell_values = [cell.value for row in ws.iter_rows() for cell in row if cell.value is not None]
        all_text = ' '.join(str(v) for v in cell_values)

        # FILE 5 specific columns
        assert 'قطعه' in all_text
        assert 'درصد اجرا' in all_text

        # Activity data
        assert 'اجرای سازه 3D پنل و دیوار داخلی' in all_text
        assert 'پیمانکاری خنکا' in all_text

        # Number format for percentage column
        pct_cells = [cell for row in ws.iter_rows() for cell in row if cell.number_format == '0.0%']
        assert len(pct_cells) >= 2
        # 65.5% represented as 0.655
        assert any(abs(float(c.value) - 0.655) < 0.001 for c in pct_cells)

        # Worker subtotal formulas
        formula_cells = [str(v) for v in cell_values if str(v).startswith('=SUM')]
        assert len(formula_cells) >= 2

    def test_electrical_subreport_file6_format(self, electrical_sub_report):
        builder = ShirazSubReportExcelBuilder(electrical_sub_report)
        excel_bytes, filename = builder.build()

        assert filename.startswith('electrical-subreport-')
        assert filename.endswith('.xlsx')

        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), data_only=False)
        ws = wb.active

        # Header contains electrical discipline
        title_val = str(ws['A1'].value)
        assert 'اجرای تأسیسات برقی' in title_val

        # Scan text
        cell_values = [cell.value for row in ws.iter_rows() for cell in row if cell.value is not None]
        all_text = ' '.join(str(v) for v in cell_values)

        # FILE 6 strictly omits parcel (قطعه) and execution percentage (درصد اجرا)
        assert 'درصد اجرا' not in all_text
        # Ensure column header for parcel is not present
        header_row_values = [cell.value for cell in ws[8]]
        assert 'قطعه' not in header_row_values
        assert 'درصد اجرا' not in header_row_values

        assert 'اکیپ رضایی' in all_text
        assert 'لوله‌گذاری روشنایی سقف و نصب قوطی کلید' in all_text

    def test_civil_null_and_zero_percentages_keep_native_format(self, civil_sub_report):
        DisciplineSubReportActivity.objects.create(
            sub_report=civil_sub_report,
            row_number=3,
            shift='1',
            crew_name='اکیپ بدون درصد',
            foreman_count=0,
            worker_count=0,
            activity_description='فعالیت بدون درصد ثبت‌شده',
            unit='مورد',
            quantity=Decimal('0'),
            execution_percentage=None,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=civil_sub_report,
            row_number=4,
            shift='1',
            crew_name='اکیپ با درصد صفر',
            foreman_count=0,
            worker_count=0,
            activity_description='فعالیت با درصد صفر',
            unit='مورد',
            quantity=Decimal('0'),
            execution_percentage=Decimal('0'),
        )

        ws = openpyxl.load_workbook(
            io.BytesIO(ShirazSubReportExcelBuilder(civil_sub_report).build()[0]),
            data_only=False,
        ).active
        percentage_cells = [
            cell for row in ws.iter_rows() for cell in row if cell.number_format == '0.0%'
        ]
        assert any(cell.value is None for cell in percentage_cells)
        assert any(cell.value == 0 for cell in percentage_cells)

    def test_subreport_excel_endpoint_authorized(self, auth_client, civil_sub_report):
        url = f'/api/v1/projects/{civil_sub_report.project_id}/units/buildings/daily-reports/{civil_sub_report.id}/excel/'
        resp = auth_client.get(url)

        assert resp.status_code == status.HTTP_200_OK
        assert resp['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'attachment; filename="civil-subreport-' in resp['Content-Disposition']

    def test_subreport_excel_endpoint_unauthenticated(self, api_client, civil_sub_report):
        url = f'/api/v1/projects/{civil_sub_report.project_id}/units/buildings/daily-reports/{civil_sub_report.id}/excel/'
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
