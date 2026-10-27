"""Transactional receipts and v2 operation dispatch for targeted offline sync.

The dispatcher must also lock and validate its domain target before mutation.
This module alone is not an offline-sync endpoint or a workflow decision.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from master_data.models import ProjectMember
from permissions.project import member_has_codename
from projects.models import Project
from sub_reports.models import OfflineOperationReceipt


def _fingerprint(operation: dict) -> str:
    """Canonical JSON includes the complete immutable operation envelope."""
    encoded = json.dumps(operation, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


@transaction.atomic
def apply_idempotent_operation(*, project, actor, operation: dict, mutate):
    """Return a receipt or atomically run a domain mutation and save its outcome.

    The scoped project lock serializes identical first deliveries. Domain writers
    still need their own shared target locking and lifecycle checks. Permission
    is checked under the transaction before accessing any previous receipt.
    """
    project = Project.objects.select_for_update().get(pk=project.pk)
    # Concurrent membership status updates wait until this transaction finishes.
    list(ProjectMember.objects.select_for_update().filter(project=project, user=actor))
    if not member_has_codename(actor, project.id, 'edit_reports'):
        raise PermissionDenied('Current project edit permission is required')
    operation_id = UUID(str(operation['operation_id']))
    fingerprint = _fingerprint(operation)
    receipt = OfflineOperationReceipt.objects.filter(
        project=project, actor=actor, operation_id=operation_id,
    ).first()
    if receipt is not None:
        if receipt.fingerprint != fingerprint:
            return {'operation_id': str(operation_id), 'outcome': 'validation_error',
                    'error': {'code': 'operation_id_reused'}}
        return receipt.result

    with transaction.atomic():
        result = mutate()
        # A rejected operation must not leave any business writes behind.
        if result.get('outcome') != 'success':
            transaction.set_rollback(True)
    if result.get('outcome') in {'success', 'validation_error', 'conflict'}:
        OfflineOperationReceipt.objects.create(
            project=project, actor=actor, operation_id=operation_id,
            fingerprint=fingerprint, outcome=result['outcome'], result=result,
        )
    return result


@transaction.atomic
def match_or_create_unit_draft(*, project, actor, unit, report_date, header_payload=None):
    """Scoped unit report create-or-match service (Feature 037, US1).

    Validates header atomically, respects current report, and returns conflict on divergence.
    """
    from common.reporting_units import is_canonical_unit
    from sub_reports.models import DisciplineSubReport, SubReportStatus
    from sub_reports.unit_report_services import (
        UNIT_TO_LEGACY_DISCIPLINE,
        _record_event,
        current_report_queryset,
        open_unit_report,
    )
    from sub_reports.models import UnitReportEventType
    import uuid

    if not is_canonical_unit(unit):
        return {
            'outcome': 'validation_error',
            'error': {'code': 'invalid_specialty_unit', 'message': 'واحد تخصصی نامعتبر است'},
        }

    header_payload = header_payload or {}

    existing = (
        current_report_queryset(project.id, unit, report_date)
        .select_for_update()
        .first()
    )

    if existing is not None:
        if existing.status == SubReportStatus.APPROVED:
            return {
                'outcome': 'conflict',
                'error': {
                    'code': 'conflict_report_approved',
                    'message': 'گزارش تأیید شده است و قابل ویرایش نیست',
                },
            }

        # Check for divergence between local header payload and server state
        divergent = False
        for key in ('form_code', 'weather_condition', 'site_status', 'inactivity_reason'):
            if key in header_payload and header_payload[key] is not None:
                val = getattr(existing, key, None)
                if val != header_payload[key]:
                    divergent = True
                    break

        if divergent:
            return {
                'outcome': 'conflict',
                'error': {
                    'code': 'draft_divergence_conflict',
                    'message': 'پیش‌نویس سرور با داده‌های محلی متفاوت است',
                },
            }

        return {
            'outcome': 'success',
            'report_id': str(existing.id),
            'created': False,
            'status': existing.status,
            'revision': str(existing.sync_revision),
        }

    # No existing report, create a new draft
    report, created = open_unit_report(project=project, unit=unit, report_date=report_date, user=actor)
    update_fields = []
    if 'form_code' in header_payload and header_payload['form_code']:
        report.form_code = header_payload['form_code']
        update_fields.append('form_code')
    if 'weather_condition' in header_payload and header_payload['weather_condition']:
        report.weather_condition = header_payload['weather_condition']
        update_fields.append('weather_condition')
    if 'site_status' in header_payload and header_payload['site_status']:
        report.site_status = header_payload['site_status']
        update_fields.append('site_status')

    if update_fields:
        report.save(update_fields=update_fields)

    return {
        'outcome': 'success',
        'report_id': str(report.id),
        'created': created,
        'status': report.status,
        'revision': str(report.sync_revision),
    }


def _as_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _operation_result(operation, outcome, **extra):
    body = {'operation_id': str(operation.get('operation_id')), 'outcome': outcome}
    body.update(extra)
    return body


def _error_result(operation, code, field=None, message=None):
    error = {'code': code}
    if field:
        error['field'] = field
    if message:
        error['message'] = message
    return _operation_result(operation, 'validation_error', error=error)


def _section_error(operation, exc):
    item = exc.errors[0] if getattr(exc, 'errors', None) else {}
    target = operation.get('target') or {}
    result = _error_result(
        operation,
        item.get('code') or 'invalid_row_payload',
        field=item.get('field'),
        message=str(item.get('message') or ''),
    )
    result['target'] = {
        'client_id': target.get('client_id'),
        'server_id': target.get('server_id'),
    }
    return result


def _allows_failed_predecessor(operation, dependency_id, recorded):
    return (
        str(operation.get('supersedes_operation_id') or '') == str(dependency_id)
        and (recorded or {}).get('outcome') == 'validation_error'
    )


def _receipt_result(operation_id, project, actor):
    receipt = OfflineOperationReceipt.objects.filter(
        project=project, actor=actor, operation_id=operation_id,
    ).first()
    return receipt.result if receipt is not None else None


def dispatch_operations(*, project, actor, body):
    """Run each operation in its own transaction and return the v2 envelope."""
    if not member_has_codename(actor, project.id, 'edit_reports'):
        raise PermissionDenied('Current project edit permission is required')
    operations = body.get('operations') if isinstance(body, dict) else None
    if not isinstance(operations, list) or body.get('contract_version') != 2:
        return {'contract_version': 2, 'synced_ids': [], 'results': []}

    pending = {}
    results = []
    for operation in operations:
        try:
            operation_id = UUID(str(operation.get('operation_id')))
        except (TypeError, ValueError, AttributeError):
            results.append(_error_result(operation if isinstance(operation, dict) else {}, 'malformed_operation'))
            continue
        if not isinstance(operation, dict):
            results.append(_error_result({}, 'malformed_operation'))
            continue
        pending[operation_id] = operation

    completed = {}
    while pending:
        progressed = False
        for operation_id, operation in list(pending.items()):
            dependency_state = _dependency_state(operation, pending, completed, project, actor)
            if dependency_state == 'waiting':
                continue
            if dependency_state == 'blocked':
                completed[operation_id] = _error_result(operation, 'blocked_dependency')
                _store_terminal(project, actor, operation, completed[operation_id])
            else:
                completed[operation_id] = apply_idempotent_operation(
                    project=project, actor=actor, operation=operation,
                    mutate=lambda operation=operation: _execute_operation(
                        project, actor, operation, completed,
                    ),
                )
            pending.pop(operation_id)
            progressed = True
        if not progressed:
            for operation_id, operation in list(pending.items()):
                completed[operation_id] = _error_result(operation, 'blocked_dependency')
                _store_terminal(project, actor, operation, completed[operation_id])
                pending.pop(operation_id)

    ordered = []
    synced_ids = []
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        try:
            operation_id = UUID(str(operation.get('operation_id')))
        except (TypeError, ValueError):
            continue
        result = completed.get(operation_id)
        if result is None:
            continue
        ordered.append(result)
        if result.get('outcome') == 'success':
            synced_ids.append(str(operation_id))
    return {'contract_version': 2, 'synced_ids': synced_ids, 'results': results + ordered}


def _store_terminal(project, actor, operation, result):
    """Record a deterministic non-success that never ran a mutation."""
    if result.get('outcome') not in {'validation_error', 'conflict'}:
        return
    operation_id = UUID(str(operation['operation_id']))
    if OfflineOperationReceipt.objects.filter(
        project=project, actor=actor, operation_id=operation_id,
    ).exists():
        return
    OfflineOperationReceipt.objects.create(
        project=project, actor=actor, operation_id=operation_id,
        fingerprint=_fingerprint(operation), outcome=result['outcome'], result=result,
    )


def _dependency_state(operation, pending, completed, project, actor):
    depends_on = operation.get('depends_on') or []
    if not isinstance(depends_on, list):
        return 'blocked'
    for raw_id in depends_on:
        try:
            dependency_id = UUID(str(raw_id))
        except (TypeError, ValueError):
            return 'blocked'
        if dependency_id in completed:
            recorded = completed[dependency_id]
            if recorded.get('outcome') != 'success' and not _allows_failed_predecessor(operation, dependency_id, recorded):
                return 'blocked'
            continue
        if dependency_id in pending:
            return 'waiting'
        recorded = _receipt_result(dependency_id, project, actor)
        if recorded is None:
            return 'blocked'
        if recorded.get('outcome') != 'success' and not _allows_failed_predecessor(operation, dependency_id, recorded):
            return 'blocked'
        completed[dependency_id] = recorded
    return 'ready'


def _resolve_report_id(operation, completed):
    scope = operation.get('scope') or {}
    if scope.get('report_id'):
        return scope['report_id']
    local_report_id = operation.get('local_report_id')
    for result in completed.values():
        if result.get('outcome') == 'success' and result.get('local_report_id') == local_report_id:
            target = result.get('target') or {}
            if target.get('report_id'):
                return target['report_id']
    return None


def _resolve_row_dependency(operation, completed, report):
    """Resolve a local row through an explicitly named, scoped receipt."""
    target = operation.get('target') or {}
    client_id = target.get('client_id')
    if not client_id or operation.get('action') not in {'update', 'delete'}:
        return operation, target
    # Only a predecessor for this report, local row and section can supply the
    # mapping and revision. Keep the original operation intact for its receipt.
    for dependency in reversed(operation.get('depends_on') or []):
        try:
            result = completed.get(UUID(str(dependency)))
        except (TypeError, ValueError):
            continue
        previous = (result or {}).get('target') or {}
        if ((result or {}).get('outcome') != 'success'
                or (result or {}).get('local_report_id') != operation.get('local_report_id')
                or previous.get('client_id') != client_id
                or previous.get('kind') != target.get('kind')
                or str(previous.get('report_id')) != str(report.id)):
            continue
        resolved = dict(target)
        if not resolved.get('server_id') or resolved['server_id'] == client_id:
            resolved['server_id'] = previous.get('server_id')
        if str(resolved.get('server_id')) != str(previous.get('server_id')):
            return operation, target
        effective = dict(operation)
        if not effective.get('base_revision'):
            effective['base_revision'] = previous.get('revision')
        return effective, resolved
    return operation, target


def _load_project_report(project, report_id):
    from sub_reports.models import DisciplineSubReport

    if not report_id:
        return None
    try:
        report_uuid = UUID(str(report_id))
    except (TypeError, ValueError):
        return None
    return (
        DisciplineSubReport.objects.select_for_update()
        .filter(pk=report_uuid, project=project, is_deleted=False)
        .first()
    )


def _execute_operation(project, actor, operation, completed):
    action = operation.get('action')
    scope = operation.get('scope') or {}
    target = operation.get('target') or {}
    payload = operation.get('payload')
    if payload is None:
        payload = {}
    if scope.get('kind') == 'project_metadata':
        return _error_result(operation, 'derived_readonly')
    if action == 'create_report':
        matched = match_or_create_unit_draft(
            project=project,
            actor=actor,
            unit=scope.get('unit'),
            report_date=_as_date(scope.get('report_date')),
            header_payload=payload,
        )
        if matched.get('outcome') != 'success':
            body = _operation_result(operation, matched.get('outcome') or 'validation_error')
            if matched.get('error'):
                body['error'] = matched['error']
            if matched.get('outcome') == 'conflict':
                body['status'] = 'sync_conflict'
            return body
        return _operation_result(
            operation, 'success', local_report_id=operation.get('local_report_id'),
            target={
                'client_id': None,
                'server_id': matched['report_id'],
                'report_id': matched['report_id'],
                'revision': matched['revision'],
            },
        )
    report = _load_project_report(project, _resolve_report_id(operation, completed))
    if report is None:
        return _error_result(operation, 'report_not_in_project')
    if action == 'correct_transfer':
        return _correction_transfer(operation, report, actor)
    locked = _guard_locked_report(operation, report)
    if locked is not None:
        return locked
    kind = target.get('kind')
    if isinstance(payload, list):
        return _error_result(operation, 'snapshot_replacement_forbidden')
    if action == 'update' and kind == 'header':
        return _update_header(operation, report, payload)
    if kind in _SECTION_RELATED and action in {'create', 'update', 'delete'}:
        effective, resolved_target = _resolve_row_dependency(operation, completed, report)
        return _mutate_section_row(effective, report, payload, resolved_target, action, kind)
    return _error_result(operation, 'unsupported_target')


def _guard_locked_report(operation, report):
    """Re-check the locked parent. A sync write never approves or retargets it."""
    if not report.is_current or report.is_deleted:
        return _operation_result(
            operation, 'conflict', status='sync_conflict',
            error={'code': 'non_current_report', 'message': 'نسخه هدف جاری نیست'},
        )
    if report.status == 'approved':
        return _operation_result(
            operation, 'conflict', status='sync_conflict',
            error={'code': 'conflict_report_approved', 'message': 'گزارش تأیید شده است و قابل ویرایش نیست'},
        )
    if report.status not in {'draft', 'rejected'}:
        return _operation_result(
            operation, 'conflict', status='sync_conflict',
            error={'code': 'report_not_editable', 'message': 'وضعیت گزارش اجازه ویرایش نمی‌دهد'},
        )
    return None


def _correction_transfer(operation, report, actor):
    """Official correction only. Replay returns the same destination version."""
    from sub_reports.unit_report_services import UnitReportError, correct_unit_report

    if not report.is_current or report.status != 'approved':
        return _operation_result(
            operation, 'conflict', status='sync_conflict',
            error={'code': 'conflict_report_approved', 'message': 'اصلاح فقط برای نسخه جاری تأییدشده است'},
        )
    reason = (operation.get('payload') or {}).get('reason') or ''
    try:
        destination = correct_unit_report(report, user=actor, enforce_permission=True)
    except UnitReportError as exc:
        return _error_result(operation, getattr(exc, 'code', None) or 'invalid_unit_report_transition', message=str(exc))
    return _operation_result(
        operation, 'success', local_report_id=operation.get('local_report_id'),
        target={
            'report_id': str(destination.id),
            'server_id': str(destination.id),
            'revision': str(destination.sync_revision),
            'lineage_id': str(destination.lineage_id),
            'supersedes': str(report.id),
            'reason': reason,
        },
    )


def _revision_conflict(operation, current):
    base = operation.get('base_revision')
    if base and str(base) != str(current):
        return _operation_result(
            operation, 'conflict', status='sync_conflict',
            error={'code': 'stale_target_revision', 'message': 'نسخه هدف تغییر کرده است'},
        )
    return None


def _update_header(operation, report, payload):
    conflict = _revision_conflict(operation, report.sync_revision)
    if conflict:
        return conflict
    fields = []
    for key in ('form_code', 'weather_condition', 'site_status', 'inactivity_reason'):
        if key in payload and payload[key] is not None:
            setattr(report, key, payload[key])
            fields.append(key)
    if fields:
        report.save(update_fields=fields)
    return _operation_result(
        operation, 'success', local_report_id=operation.get('local_report_id'),
        target={'report_id': str(report.id), 'server_id': str(report.id), 'revision': str(report.sync_revision)},
    )


_SECTION_RELATED = {
    'activity': 'activities',
    'labor': 'labor_entries',
    'material': 'material_entries',
    'materials': 'material_entries',
    'machinery': 'machinery_rows',
    'concrete': 'concrete_entries',
    'general': 'general_activities',
    'general_activity': 'general_activities',
    'issue': 'issues',
    'visit': 'visits',
    'incident': 'hse_incidents',
    'hse': 'hse_incidents',
    'note': 'notes',
}

_NARRATIVE_KIND = {
    'general': 'general_activity',
    'general_activity': 'general_activity',
    'issue': 'issue',
    'visit': 'visit',
    'incident': 'hse',
    'hse': 'hse',
    'note': 'note',
}

_SECTION_VALIDATORS = {
    'activity': 'validate_activity_rows',
    'labor': 'validate_labor_rows',
    'material': 'validate_material_rows',
    'materials': 'validate_material_rows',
    'machinery': 'validate_machinery_rows',
    'concrete': 'validate_concrete_rows',
}

_SECTION_UPDATERS = {
    'activity': 'update_activity_row',
    'labor': 'update_labor_row',
    'material': 'update_material_row',
    'materials': 'update_material_row',
    'machinery': 'update_machinery_row',
}


def _saved_rows(result):
    if isinstance(result, list):
        return result
    return [result]


def _section_row(report, kind, target):
    server_id = target.get('server_id')
    if not server_id:
        return None
    try:
        row_id = UUID(str(server_id))
    except (TypeError, ValueError):
        return None
    related = getattr(report, _SECTION_RELATED[kind])
    return related.select_for_update().filter(pk=row_id, is_deleted=False).first()


def _success_row(operation, report, row, target):
    return _operation_result(
        operation, 'success', local_report_id=operation.get('local_report_id'),
        target={
            'client_id': target.get('client_id'),
            'kind': target.get('kind'),
            'server_id': str(row.id),
            'report_id': str(report.id),
            'revision': str(getattr(row, 'sync_revision', '')),
        },
    )


def _mutate_section_row(operation, report, payload, target, action, kind):
    from sub_reports.services import section_validation
    from sub_reports.services.section_validation import SectionContractError

    if action == 'delete':
        row = _section_row(report, kind, target)
        if row is None:
            return _error_result(operation, 'target_not_found')
        conflict = _revision_conflict(operation, getattr(row, 'sync_revision', None))
        if conflict:
            return conflict
        row.is_deleted = True
        row.deleted_at = timezone.now()
        row.save(update_fields=['is_deleted', 'deleted_at'])
        return _success_row(operation, report, row, target)

    if action == 'update':
        row = _section_row(report, kind, target)
        if row is None:
            return _error_result(operation, 'target_not_found')
        conflict = _revision_conflict(operation, getattr(row, 'sync_revision', None))
        if conflict:
            return conflict
        updater_name = _SECTION_UPDATERS.get(kind)
        try:
            if updater_name:
                updated = getattr(section_validation, updater_name)(report, row, payload)
            else:
                for key, value in payload.items():
                    if key in {'id', 'sub_report', 'sub_report_id'}:
                        continue
                    if hasattr(row, key):
                        setattr(row, key, value)
                row.save()
                updated = row
        except SectionContractError as exc:
            return _section_error(operation, exc)
        return _success_row(operation, report, updated, target)

    try:
        if kind in _NARRATIVE_KIND:
            narrative_payload = {**payload, 'kind': _NARRATIVE_KIND[kind]}
            saved = section_validation.validate_narrative_rows(report, [narrative_payload])
        else:
            saved = _saved_rows(getattr(section_validation, _SECTION_VALIDATORS[kind])(report, [payload]))
    except SectionContractError as exc:
        return _section_error(operation, exc)
    if not saved:
        return _error_result(operation, 'invalid_row_payload')
    return _success_row(operation, report, saved[0], target)

