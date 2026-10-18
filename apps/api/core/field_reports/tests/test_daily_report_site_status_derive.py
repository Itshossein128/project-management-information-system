"""T070 — site_status derivation from specialty contributions (Decision 7)."""
import pytest

from field_reports.models import SiteStatus
from field_reports.services.daily_report_aggregation import (
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import Discipline, SubReportStatus


@pytest.mark.django_db
def test_site_status_inactive_when_any_specialty_inactive(project, user):
    civil = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(civil)
    electrical = make_sub_report(
        project,
        user,
        discipline=Discipline.ELECTRICAL,
        status=SubReportStatus.SUBMITTED,
    )
    electrical.site_status = SiteStatus.INACTIVE
    electrical.save(update_fields=['site_status', 'updated_at'])
    add_activity(electrical, description='Elec')

    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert report.site_status == SiteStatus.INACTIVE


@pytest.mark.django_db
def test_site_status_active_when_all_specialty_active(project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    sr.site_status = SiteStatus.ACTIVE
    sr.save(update_fields=['site_status', 'updated_at'])
    add_activity(sr)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    assert report.site_status == SiteStatus.ACTIVE


@pytest.mark.django_db
def test_site_status_override_survives_rebuild(project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    sr.site_status = SiteStatus.INACTIVE
    sr.save(update_fields=['site_status', 'updated_at'])
    add_activity(sr)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    report.site_status_override = True
    report.site_status = SiteStatus.ACTIVE
    report.save(update_fields=['site_status_override', 'site_status', 'updated_at'])

    rebuild_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    report.refresh_from_db()
    assert report.site_status == SiteStatus.ACTIVE
    assert report.site_status_override is True
