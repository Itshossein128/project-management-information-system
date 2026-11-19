"""Independent audit probes; strict XFAIL means a reproduced missing invariant."""
import io
import json
from datetime import date
from pathlib import Path
from decimal import Decimal

import openpyxl
import pytest

from field_reports.models import DailyReport, DailyReportActivity, DailyReportEquipment
from field_reports.shiraz_file4_excel import ShirazFile4ExcelBuilder
from field_reports.pdf import generate_daily_report_pdf, generate_report_audit_hash
from field_reports.services.activity_log import activity_log_queryset

OUT = Path('/tmp/velora-a1-audit-20261118')

def report(project, user, **kw):
    return DailyReport.objects.create(project=project, created_by=user,
        report_date=date(2026, 11, 1), **kw)

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,raises=AssertionError, reason='legacy equipment null is emitted as numeric zero')
def test_unknown_equipment_hour_must_not_be_zero(project, user):
    r = report(project, user)
    DailyReportEquipment.objects.create(report=r, equipment_name='Unknown-hour machine',
        shift='day', status='active', ownership_type='owned', productive_hours=None)
    raw, _ = ShirazFile4ExcelBuilder(r).build()
    ws = openpyxl.load_workbook(io.BytesIO(raw)).active
    row = next(row for row in ws if row[1].value == 'Unknown-hour machine')
    assert row[5].value is None

@pytest.mark.django_db
def test_explicit_equipment_zero_stays_numeric_zero(project, user):
    r = report(project, user)
    DailyReportEquipment.objects.create(report=r, equipment_name='Zero-hour machine',
        shift='day', status='active', ownership_type='owned', productive_hours=0)
    raw, _ = ShirazFile4ExcelBuilder(r).build()
    ws = openpyxl.load_workbook(io.BytesIO(raw)).active
    row = next(row for row in ws if row[1].value == 'Zero-hour machine')
    assert row[5].value == 0

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,raises=AssertionError, reason='master activity log includes superseded approved versions')
def test_log_counts_only_current_approved_version(project, user):
    old = report(project, user, status='approved', is_current=False, version_number=1)
    new = report(project, user, status='approved', is_current=True, version_number=2, supersedes=old)
    for r in (old, new):
        DailyReportActivity.objects.create(report=r, shift='shift_1',
            activity_description='same logical corrected activity', headcount=4, quantity=5, unit='m2')
    rows = list(activity_log_queryset(project.id, {}))
    (OUT/'historical-version-probe.json').write_text(json.dumps({
        'actual_rows':len(rows), 'expected_rows':1,
        'actual_quantity':sum(float(x.quantity) for x in rows), 'expected_quantity':5,
        'actual_headcount':sum(x.headcount for x in rows), 'expected_headcount':4}, indent=2))
    assert len(rows) == 1

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,raises=AssertionError, reason='API has no whole-filter aggregates; UI sums current page')
def test_activity_api_provides_whole_filter_totals(auth_client, project, user):
    r = report(project, user, status='approved')
    for n in range(51):
        DailyReportActivity.objects.create(report=r, shift='shift_1',
            activity_description=f'activity {n}', headcount=1, quantity=1, unit='m2')
    response = auth_client.get(f'/api/v1/projects/{project.id}/activity-log/?page_size=50')
    assert response.status_code == 200
    d=response.data
    (OUT/'pagination-probe.json').write_text(json.dumps({
        'count':d['count'], 'page_rows':len(d['results']),
        'page_headcount_sum':sum(x['headcount'] for x in d['results']),
        'whole_filter_expected_sum':51, 'response_keys':list(d)},indent=2))
    assert d.get('summary',{}).get('headcount') == 51

@pytest.mark.django_db
def test_audit_hash_scope_and_samples(project, user):
    """Characterize metadata hash scope; content signing is not this contract."""
    r = report(project, user, status='approved', work_front='A')
    a=DailyReportActivity.objects.create(report=r,shift='shift_1',activity_description='Work',quantity=1,unit='m2')
    before=generate_report_audit_hash(r)
    a.quantity=2; a.save(update_fields=['quantity'])
    after=generate_report_audit_hash(r)
    assert before == after
    r.version_number=2
    assert generate_report_audit_hash(r)==before
    r.status='draft'
    assert generate_report_audit_hash(r)!=before
    xlsx, name=ShirazFile4ExcelBuilder(r).build()
    (OUT/'generated-sample.xlsx').write_bytes(xlsx)
    pdf, pdfname=generate_daily_report_pdf(r)
    (OUT/'generated-sample.pdf').write_bytes(pdf)
    ws=openpyxl.load_workbook(io.BytesIO(xlsx), data_only=False).active
    (OUT/'generated-structure.json').write_text(json.dumps({
        'metadata_hash_excludes_activity_quantity':before==after,
        'sheet_count':1,'shift_hours_header':ws['G4'].value,
        'print_area':str(ws.print_area),'orientation':ws.page_setup.orientation,
        'filename':name,'pdf_filename':pdfname,'rtl':ws.sheet_view.rightToLeft},ensure_ascii=False,indent=2))

def make_derived_correction(project, user, auth_client):
    from field_reports.tests.daily_report_summary_helpers import make_sub_report, add_activity, add_labor, SUMMARY_DATE
    from field_reports.services.daily_report_aggregation import rebuild_daily_report_summary
    from field_reports.services import approve_report
    from field_reports.models import DailyReportDerivedSource
    first=make_sub_report(project,user,discipline='civil',status='submitted')
    add_activity(first)
    add_labor(first,title='کارگر ساده',present=3,leave=0)
    summary=rebuild_daily_report_summary(project.id,SUMMARY_DATE,user=user)
    summary.management_opinion='Preserve this management note'
    summary.weather_override=True
    summary.save(update_fields=['management_opinion','weather_override'])
    approve_report(summary,user)
    original_count=DailyReportDerivedSource.objects.filter(daily_report=summary).count()
    response=auth_client.post(f'/api/v1/projects/{project.id}/daily-reports/{summary.id}/correction-requests/',
        {'reason':'Correct this approved summary safely'},format='json')
    assert response.status_code==201
    result=DailyReport.objects.get(pk=response.data['result_report_id'])
    data={'source_is_auto_summary':summary.is_auto_summary,'result_is_auto_summary':result.is_auto_summary,
          'source_provenance_count':original_count,'result_provenance_count':DailyReportDerivedSource.objects.filter(daily_report=result).count(),
          'source_management_opinion':summary.management_opinion,'result_management_opinion':result.management_opinion,
          'source_weather_override':summary.weather_override,'result_weather_override':result.weather_override}
    (OUT/'correction-probe.json').write_text(json.dumps(data,indent=2))
    return summary,result,original_count

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,raises=AssertionError,reason='correction drops auto-summary identity and permits derived child edits')
def test_summary_correction_must_not_enable_direct_child_writes(project,user,auth_client):
    summary,result,count=make_derived_correction(project,user,auth_client)
    row=result.activities.get()
    response=auth_client.patch(f'/api/v1/projects/{project.id}/daily-reports/{result.id}/activities/{row.id}/',
        {'activity_description':'Direct mutation bypass'},format='json')
    row.refresh_from_db()
    (OUT/'correction-write-probe.json').write_text(json.dumps({'response_status':response.status_code,'persisted_description':row.activity_description,'derived_flag':row.is_derived,'summary_flag':result.is_auto_summary},indent=2))
    assert response.status_code==400

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,raises=AssertionError,reason='correction copies children but omits complete derived source records')
def test_summary_correction_preserves_complete_provenance(project,user,auth_client):
    from field_reports.models import DailyReportDerivedSource
    summary,result,count=make_derived_correction(project,user,auth_client)
    assert count>0
    assert DailyReportDerivedSource.objects.filter(daily_report=result).count()==count

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,raises=AssertionError,reason='correction drops management opinion and explicit override marker')
def test_summary_correction_preserves_owned_metadata(project,user,auth_client):
    summary,result,count=make_derived_correction(project,user,auth_client)
    assert result.management_opinion==summary.management_opinion
    assert result.weather_override is True

