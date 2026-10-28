from datetime import date
from decimal import Decimal
import subprocess
import tempfile
from django.utils import timezone
import pytest
from rest_framework import status

from field_reports.models import DailyReport, ReportShift, ReportStatus
from field_reports.pdf import generate_daily_report_pdf, generate_report_audit_hash


@pytest.fixture
def draft_report(project, user):
    return DailyReport.objects.create(
        project=project,
        created_by=user,
        report_date=date(2025, 2, 2),
        shift=ReportShift.FULL,
        status=ReportStatus.DRAFT,
        prepared_by=user,
    )


@pytest.fixture
def approved_report(project, user, other_user):
    now = timezone.now()
    return DailyReport.objects.create(
        project=project,
        created_by=user,
        report_date=date(2025, 2, 2),
        shift=ReportShift.DAY,
        status=ReportStatus.APPROVED,
        prepared_by=user,
        submitted_by=user,
        submitted_at=now,
        reviewed_by=other_user,
        reviewed_at=now,
        approved_by=user,
        approved_at=now,
    )


@pytest.mark.django_db
class TestPdfSignaturesAndWatermark:

    def test_audit_hash_deterministic(self, approved_report):
        hash1 = generate_report_audit_hash(approved_report)
        hash2 = generate_report_audit_hash(approved_report)
        assert hash1 == hash2
        assert len(hash1) == 16
        assert hash1.isupper()

        # Mutating approved_at or status changes hash
        approved_report.status = ReportStatus.DRAFT
        hash_mutated = generate_report_audit_hash(approved_report)
        assert hash1 != hash_mutated

    def test_draft_pdf_filename_and_watermark(self, draft_report):
        pdf_bytes, filename = generate_daily_report_pdf(draft_report)
        assert filename.startswith('daily-report-')
        assert filename.endswith('-full.pdf')
        assert pdf_bytes.startswith(b'%PDF')

    def test_draft_watermark_is_present_on_multiple_pages(self, draft_report, monkeypatch):
        from field_reports.models import DailyReportActivity
        import field_reports.pdf as pdf_module

        watermark_calls = []
        original_make_watermark = pdf_module._make_watermark

        def counted_watermark(text, font_name):
            callback = original_make_watermark(text, font_name)

            def counted_callback(canvas, doc):
                watermark_calls.append(doc.page)
                callback(canvas, doc)

            return counted_callback

        monkeypatch.setattr(pdf_module, '_make_watermark', counted_watermark)

        for index in range(80):
            DailyReportActivity.objects.create(
                report=draft_report,
                activity_description=f'فعالیت طولانی شماره {index} ' * 8,
                shift='shift_1',
                headcount=1,
                quantity=Decimal('1'),
                unit='متر',
            )

        pdf_bytes, _ = generate_daily_report_pdf(draft_report)
        with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf_file:
            pdf_file.write(pdf_bytes)
            pdf_file.flush()
            text = subprocess.run(
                ['pdftotext', '-layout', pdf_file.name, '-'],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

        page_count = text.count('\f')
        assert page_count > 1
        assert len(watermark_calls) == page_count
        assert watermark_calls == list(range(1, page_count + 1))

    def test_direct_approval_has_explicit_reviewer_fallback(self, project, user, monkeypatch):
        report = DailyReport.objects.create(
            project=project,
            created_by=user,
            report_date=date(2025, 2, 4),
            shift='day',
            status=ReportStatus.APPROVED,
            prepared_by=user,
            approved_by=user,
            approved_at=timezone.now(),
        )
        import field_reports.pdf as pdf_module

        captured = []
        original_fa = pdf_module._fa

        def capture_fa(value):
            captured.append(str(value))
            return original_fa(value)

        monkeypatch.setattr(pdf_module, '_fa', capture_fa)
        pdf_module._signatures_block(report, pdf_module._register_font())
        assert any('بدون نیاز به بررسی دفتر فنی' in value for value in captured)

    def test_approved_pdf_signatures_and_filename(self, approved_report):
        pdf_bytes, filename = generate_daily_report_pdf(approved_report)
        assert filename.startswith('daily-report-')
        assert filename.endswith('-day.pdf')
        assert pdf_bytes.startswith(b'%PDF')

    def test_pdf_endpoint_content_disposition(self, auth_client, draft_report):
        url = f'/api/v1/projects/{draft_report.project_id}/daily-reports/{draft_report.id}/pdf/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp['Content-Type'] == 'application/pdf'
        assert 'Content-Disposition' in resp
        assert 'attachment; filename="daily-report-' in resp['Content-Disposition']
        assert resp['Content-Disposition'].endswith('-full.pdf"')
