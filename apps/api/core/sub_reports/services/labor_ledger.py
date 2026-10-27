"""Subcontractor labor ledger rollup service (feature 038, US6).

Aggregates crew person-hours from activity rows for referenced contractors
upon sub-report approval.
"""
from decimal import Decimal

from sub_reports.models import SubcontractorLaborLedgerEntry


def rollup_subcontractor_labor(report, user=None):
    """
    Computes (foreman_count + worker_count) * shift_hours for each contractor-associated
    activity row in an approved sub-report and records to the SubcontractorLaborLedgerEntry.
    """
    entries = []
    for row in report.activities.filter(is_deleted=False, contractor_ref__isnull=False).select_related('contractor_ref'):
        foreman = row.foreman_count or 0
        worker = row.worker_count or 0
        shift_h = row.shift_hours or Decimal('8.00')
        total_hours = Decimal(foreman + worker) * shift_h

        entry, _created = SubcontractorLaborLedgerEntry.objects.update_or_create(
            activity_row=row,
            defaults={
                'project_id': report.project_id,
                'contractor': row.contractor_ref,
                'sub_report': report,
                'report_date': report.report_date,
                'discipline': report.unit or report.discipline or '',
                'foreman_count': foreman,
                'worker_count': worker,
                'shift_hours': shift_h,
                'total_person_hours': total_hours,
                'status': 'APPROVED',
            },
        )
        entries.append(entry)
    return entries
