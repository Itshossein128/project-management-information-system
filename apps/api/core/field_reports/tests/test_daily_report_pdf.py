"""Tests for daily report PDF export formatting, weather impact notes, and unconditional table rows."""
import subprocess
import unicodedata
import pytest
from field_reports.models import DailyReport, ReportStatus, SiteStatus, WeatherCondition
from field_reports.pdf import generate_daily_report_pdf


@pytest.mark.django_db
def test_pdf_export_contains_unconditional_weather_impact_row_with_empty_notes(project, user):
    """Verify that when weather_impact_notes is empty, the labeled row still appears with an empty cell."""
    report = DailyReport.objects.create(
        project=project,
        report_date='2026-09-20',
        shift='full',
        status=ReportStatus.APPROVED,
        site_status=SiteStatus.ACTIVE,
        weather_condition=WeatherCondition.CLEAR,
        weather_impact_notes='',
        created_by=user,
        updated_by=user,
    )
    pdf_bytes, filename = generate_daily_report_pdf(report)
    assert pdf_bytes.startswith(b'%PDF')
    assert filename.endswith('.pdf')

    # Run pdftotext to extract text
    proc = subprocess.run(['pdftotext', '-', '-'], input=pdf_bytes, capture_output=True)
    text = unicodedata.normalize('NFKD', proc.stdout.decode('utf-8', errors='ignore'))
    # Label «توضیحات و اثرات شرایط جوی» or its shaped form should appear in the generated document
    assert 'توضیحات و اثرات شرایط جوی' in text or 'شرایط جوی' in text


@pytest.mark.django_db
def test_pdf_export_renders_multiline_mixed_language_and_escaped_characters(project, user):
    """Verify multiline notes with XML-significant characters (& and <) render without crashing and preserve content."""
    notes = "بارش باران شدید & وزش باد < 50km/h\nکاهش دید افقی در جبهه کاری شمالی.\nHeavy rain & wind."
    report = DailyReport.objects.create(
        project=project,
        report_date='2026-09-21',
        shift='full',
        status=ReportStatus.APPROVED,
        site_status=SiteStatus.ACTIVE,
        weather_condition=WeatherCondition.RAINY,
        weather_impact_notes=notes,
        created_by=user,
        updated_by=user,
    )
    pdf_bytes, filename = generate_daily_report_pdf(report)
    assert pdf_bytes.startswith(b'%PDF')

    proc = subprocess.run(['pdftotext', '-', '-'], input=pdf_bytes, capture_output=True)
    text = unicodedata.normalize('NFKD', proc.stdout.decode('utf-8', errors='ignore'))
    assert 'Heavy rain' in text or 'wind' in text
