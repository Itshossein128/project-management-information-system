"""Daily PDF must preserve the key rows in the project summary."""
from datetime import date
from decimal import Decimal
import pytest
from field_reports.models import DailyReport, DailyReportActivity, DailyReportGeneralActivity, DailyReportMachineryRow, DailyReportVisit
from field_reports.pdf import generate_daily_report_pdf

def test_long_rtl_table_cell_wraps_before_bidi_shaping(monkeypatch):
    import field_reports.pdf as pdf
    from reportlab.lib.styles import ParagraphStyle
    logical = 'آغاز گزارش اول ادامه گزارش دوم پایان گزارش سوم'
    shaped_inputs = []
    def capture(text):
        shaped_inputs.append(text)
        return text
    monkeypatch.setattr(pdf, '_fa', capture)
    style = ParagraphStyle('rtl-wrap-test', fontName='Helvetica', fontSize=8, leading=10)
    lines = pdf._wrap_logical_lines(logical, style, 80)
    shaped_inputs.clear()
    pdf._text_paragraph(logical, style, max_width=80)
    result = shaped_inputs[-len(lines):]
    assert len(lines) > 1
    assert ' '.join(result) == logical
    assert result[0].startswith('آغاز')
    assert result[-1].endswith('سوم')

@pytest.mark.django_db
def test_pdf_preserves_structured_issue_owner_due_and_hse_severity(project, user, monkeypatch):
    import field_reports.pdf as pdf
    from field_reports.services.daily_report_aggregation import rebuild_daily_report_summary
    from sub_reports.models import DisciplineSubReport, DisciplineSubReportIssue, DisciplineSubReportHseIncident, SubReportStatus

    day = date(2025, 2, 3)
    unit = DisciplineSubReport.objects.create(
        project=project, report_date=day, unit='buildings', discipline='civil',
        status=SubReportStatus.SUBMITTED, created_by=user,
    )
    DisciplineSubReportIssue.objects.create(
        sub_report=unit, row_number=1, kind='barrier', text='مانع تأمین مصالح',
        owner_user=user, due_date=date(2025, 2, 8),
    )
    DisciplineSubReportHseIncident.objects.create(
        sub_report=unit, row_number=2, text='حادثه در کارگاه',
        severity='major', immediate_action='توقف و ایمن‌سازی',
    )
    report = rebuild_daily_report_summary(project.id, day, user=user)
    captured = {}
    original = pdf._section
    def capture(title, headers, rows, *args):
        captured[title] = (headers, rows)
        return original(title, headers, rows, *args)
    monkeypatch.setattr(pdf, '_section', capture)
    data, _ = generate_daily_report_pdf(report)
    assert data.startswith(b'%PDF')
    headers, rows = captured['حوادث و موانع']
    issue = dict(zip(headers, next(row for row in rows if 'مانع تأمین مصالح' in row)))
    incident = dict(zip(headers, next(row for row in rows if 'حادثه در کارگاه' in row)))
    assert issue['مسئول پیگیری'] == 'Test User'
    assert issue['موعد'] == '1403/11/20'
    assert issue['نوع'] == 'مانع'
    assert incident['نوع'] == 'ایمنی'
    assert incident['شدت'] == 'شدید'
    assert incident['اقدام اصلاحی'] == 'توقف و ایمن‌سازی'

@pytest.mark.django_db
def test_pdf_localizes_all_incident_types_and_severity_values(project, user, monkeypatch):
    import field_reports.pdf as pdf
    from field_reports.models import DailyReportIncident
    report = DailyReport.objects.create(project=project, report_date=date(2025, 2, 4), created_by=user)
    expected_types = {'safety': 'ایمنی', 'quality': 'کیفیت', 'environmental': 'محیط زیست',
                      'stoppage': 'توقف کار', 'visitor': 'بازدیدکننده', 'site_instruction': 'دستور کارگاهی',
                      'barrier': 'مانع', 'issue': 'مسئله'}
    expected_severities = {'minor': 'جزئی', 'moderate': 'متوسط', 'major': 'شدید'}
    for index, kind in enumerate(expected_types):
        DailyReportIncident.objects.create(report=report, row_number=index + 1, incident_type=kind, description=kind)
    for index, severity in enumerate(expected_severities):
        DailyReportIncident.objects.create(report=report, row_number=index + 20, incident_type='safety', description=severity, severity=severity)
    captured = {}
    original = pdf._section
    def capture(title, headers, rows, *args):
        captured[title] = (headers, rows)
        return original(title, headers, rows, *args)
    monkeypatch.setattr(pdf, '_section', capture)
    generate_daily_report_pdf(report)
    headers, rows = captured['حوادث و موانع']
    by_description = {row[1]: dict(zip(headers, row)) for row in rows}
    for code, label in expected_types.items():
        assert by_description[code]['نوع'] == label
    for code, label in expected_severities.items():
        assert by_description[code]['شدت'] == label

@pytest.mark.django_db
@pytest.mark.parametrize(('is_summary', 'expected'), [(True, 'مرخصی'), (False, 'مرخصی / غیبت')])
def test_pdf_labor_absence_label_respects_source_semantics(project, user, monkeypatch, is_summary, expected):
    import field_reports.pdf as pdf
    report = DailyReport.objects.create(project=project, report_date=date(2026, 3, 20), created_by=user, is_auto_summary=is_summary)
    captured = {}
    original = pdf._section
    def capture(title, headers, rows, *args):
        captured[title] = headers
        return original(title, headers, rows, *args)
    monkeypatch.setattr(pdf, '_section', capture)
    generate_daily_report_pdf(report)
    assert expected in captured['نیروی انسانی']

@pytest.mark.django_db
def test_pdf_includes_project_and_derived_summary_details(project, user, monkeypatch):
    import field_reports.pdf as pdf
    project.project_name = 'Project Omega'
    project.contract_number = 'CN-234'
    project.employer = 'Employer Omega'
    project.consultant = 'Consultant Omega'
    project.save()
    report = DailyReport.objects.create(project=project, report_date=date(2026, 3, 21), created_by=user, management_opinion='Management note Omega')
    DailyReportActivity.objects.create(report=report, activity_description='Activity Omega', shift='shift_1', subcontractor_name='Contractor Omega', crew_name='Crew Omega', headcount=4, parcel='Parcel Omega', block='Block Omega', floor='Floor Omega', location_detail='Location Omega', quantity=None, quantity_measured=False, notes='Activity note Omega')
    DailyReportMachineryRow.objects.create(report=report, equipment_type='Machinery Omega', status_total=4, status_active=2, status_ready=1, status_inactive=1)
    DailyReportGeneralActivity.objects.create(report=report, row_number=1, activity_description='General Omega', location='Yard Omega', quantity=Decimal('3'), unit='unit', notes='General note Omega')
    DailyReportVisit.objects.create(report=report, row_number=1, text='Visit Omega')
    captured = []
    original = pdf._fa
    def capture(value):
        captured.append(str(value))
        return original(value)
    monkeypatch.setattr(pdf, '_fa', capture)
    result, _ = generate_daily_report_pdf(report)
    assert result.startswith(b'%PDF')
    for expected in ('Project Omega', 'CN-234', 'Employer Omega', 'Consultant Omega', 'Contractor Omega', 'Crew Omega', 'Parcel Omega', 'Block Omega', 'Floor Omega', 'Location Omega', 'Activity note Omega', 'Machinery Omega', 'General Omega', 'Yard Omega', 'General note Omega', 'Visit Omega', 'Management note Omega'):
        assert any(expected in value for value in captured), expected


@pytest.mark.django_db
def test_draft_does_not_claim_direct_approval(project, user, monkeypatch):
    import field_reports.pdf as pdf
    report = DailyReport.objects.create(project=project, report_date=date(2026, 3, 22), created_by=user)
    captured = []
    original = pdf._fa

    def capture(value):
        captured.append(str(value))
        return original(value)

    monkeypatch.setattr(pdf, '_fa', capture)
    generate_daily_report_pdf(report)
    assert any('هنوز بررسی نشده است' in value for value in captured)
    assert not any('تأیید مستقیم' in value for value in captured)


@pytest.mark.django_db
def test_pdf_does_not_invent_user_job_titles(project, user, monkeypatch):
    import field_reports.pdf as pdf
    report = DailyReport.objects.create(
        project=project, report_date=date(2026, 3, 25), created_by=user,
        prepared_by=user, reviewed_by=user, approved_by=user,
    )
    captured = []
    original = pdf._fa

    def capture(value):
        captured.append(str(value))
        return original(value)

    monkeypatch.setattr(pdf, '_fa', capture)
    pdf._signatures_block(report, pdf._register_font())
    assert not any(value.startswith('سمت:') for value in captured)


@pytest.mark.django_db
def test_pdf_distinguishes_resolved_receipts_from_unresolved_and_consumption(project, user, monkeypatch):
    import field_reports.pdf as pdf
    from field_reports.models import DailyReportMaterial

    report = DailyReport.objects.create(project=project, report_date=date(2026, 3, 24), created_by=user, is_auto_summary=True)
    for description, kind, resolved in [
        ('Resolved receipt', 'receipt', True),
        ('Unresolved receipt', 'receipt', False),
        ('Material consumption', 'issue', False),
    ]:
        DailyReportMaterial.objects.create(
            report=report, material_description=description, transaction_type=kind,
            quantity=Decimal('5'), unit='kg', receipt_resolved=resolved,
        )
    DailyReportMaterial.objects.create(
        report=report, material_description='Mismatch receipt', transaction_type='receipt',
        quantity=Decimal('7'), unit='kg', receipt_resolved=True, reconciliation_status='mismatch',
    )
    captured = []
    original = pdf._fa

    def capture(value):
        captured.append(str(value))
        return original(value)

    monkeypatch.setattr(pdf, '_fa', capture)
    generate_daily_report_pdf(report)
    assert 'رسید؛ سند انبار یافت شد' in captured
    assert 'رسید بدون سند قابل تطبیق' in captured
    assert 'مصرف / خروج' in captured
    assert 'رسید؛ سند انبار یافت شد؛ مقدار مغایر' in captured
    assert any('وضعیت تغییر منابع نسبت به آخرین تجمیع نامشخص است' in text for text in captured)


@pytest.mark.django_db
@pytest.mark.parametrize('state', ['configuration_incomplete', 'partial', 'complete'])
def test_summary_pdf_displays_real_completeness(project, user, monkeypatch, state):
    import field_reports.pdf as pdf
    from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
    from project_templates.models import ProjectTemplate, ProjectTemplateRequiredUnit
    from project_templates.services import activate_project_reporting_configuration
    from sub_reports.models import DisciplineSubReport, SubReportStatus

    report_date = date(2026, 3, 23)
    if state != 'configuration_incomplete':
        template = ProjectTemplate.objects.create(template_name='PDF completeness', created_by=user)
        for index, unit in enumerate(['buildings', 'warehouse']):
            ProjectTemplateRequiredUnit.objects.create(template=template, unit=unit, display_order=index)
        activate_project_reporting_configuration(project=project, template=template, effective_from=report_date, user=user)
    units = ['buildings', 'warehouse'] if state == 'complete' else ['buildings']
    for unit in units:
        DisciplineSubReport.objects.create(
            project=project, report_date=report_date, unit=unit, legacy_discipline=unit,
            discipline='civil', status=SubReportStatus.SUBMITTED, created_by=user, updated_by=user,
        )
    report = ensure_daily_report_summary(project.id, report_date, user=user)
    captured = []
    original = pdf._fa

    def capture(value):
        captured.append(str(value))
        return original(value)

    monkeypatch.setattr(pdf, '_fa', capture)
    data, _ = generate_daily_report_pdf(report)
    assert data.startswith(b'%PDF')
    expected = {'configuration_incomplete': 'پیکربندی واحدهای مورد انتظار',
                'partial': 'واحدهای فاقد گزارش', 'complete': 'همه واحدهای مورد انتظار'}[state]
    assert any(expected in text for text in captured)
    assert any('وضعیت فعلی واحدها' in text for text in captured)
    assert any('زمان آخرین تجمیع' in text for text in captured)
    assert any('منابع تحت پوشش اثرانگشت تغییر نکرده‌اند' in text for text in captured)
    assert any('وابستگی‌های بیرونی جداگانه بررسی نشده‌اند' in text for text in captured)
    assert any('ممکن است با داده‌های آخرین تجمیع متفاوت باشد' in text for text in captured)
    if state == 'partial':
        assert any('انبار' in text for text in captured)
        assert any('عدم وقوع' in text for text in captured)


@pytest.mark.django_db
def test_summary_pdf_warns_when_current_sources_changed_since_aggregation(project, user, monkeypatch):
    import field_reports.pdf as pdf
    from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
    from sub_reports.models import DisciplineSubReport, SubReportStatus

    report_date = date(2026, 3, 26)
    unit = DisciplineSubReport.objects.create(
        project=project, report_date=report_date, unit='buildings', legacy_discipline='buildings',
        discipline='civil', status=SubReportStatus.SUBMITTED, weather_condition='clear',
        created_by=user, updated_by=user,
    )
    report = ensure_daily_report_summary(project.id, report_date, user=user)
    report.status = 'approved'
    report.save(update_fields=['status'])
    original_fingerprint = report.aggregation_fingerprint
    unit.weather_condition = 'rainy'
    unit.save(update_fields=['weather_condition'])
    captured = []
    original = pdf._fa

    def capture(value):
        captured.append(str(value))
        return original(value)

    monkeypatch.setattr(pdf, '_fa', capture)
    generate_daily_report_pdf(report)
    assert any('منابع پس از آخرین تجمیع تغییر کرده‌اند' in text for text in captured)
    report.refresh_from_db()
    assert report.status == 'approved'
    assert report.aggregation_fingerprint == original_fingerprint
