# Service Contract: IPC Auto-Population Based on Approved Progress

## Module: `apps/api/core/contracts/services/ipc_service.py`
## Routine: `auto_populate_ipc(ipc_id)`

### Preconditions
- The target IPC must be in `DRAFT` status. If already submitted/approved, raises `CodedValidationError('ipc_locked_after_submit')`.
- The parent contract contains linked `ContractItem` records with `activity_id`.
- Period is bounded by `ipc.period_start` and `ipc.period_end`.

### Progress Query Logic
```python
# Look for approved progress on or before period_end
latest_approved = (
    ActivityProgress.objects.filter(
        activity_id=item.activity_id,
        report_date__gte=ipc.period_start,
        report_date__lte=ipc.period_end,
        approved_progress__isnull=False,
    )
    .order_by('-report_date')
    .first()
)

earliest_before = (
    ActivityProgress.objects.filter(
        activity_id=item.activity_id,
        report_date__lt=ipc.period_start,
        approved_progress__isnull=False,
    )
    .order_by('-report_date')
    .first()
)
```

### Calculation Rules
1. `approved_start = float(earliest_before.approved_progress) if earliest_before else 0.0`
2. `approved_end = float(latest_approved.approved_progress) if latest_approved else 0.0`
3. `progress_delta = max(approved_end - approved_start, 0.0)`
4. `qty_current = Decimal(str(progress_delta * float(item.activity.total_quantity or 0)))`
5. `amount_current = unit_price * qty_current`

### Warning Logging
If unapproved progress records exist in the period (`actual_progress > 0` but `approved_progress` is null or zero):
- System sets `qty_current = Decimal('0')`
- System logs / issues structured warning:
  `«پیشرفت این فعالیت فاقد تأیید فنی مهندس ناظر است»`
