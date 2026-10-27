"""Feature 037: exercise the expand migration on real pre-feature data.

The pre-feature boundary is deliberately fixed.  The tests discover the new
migration/model instead of requiring a particular filename.  A missing
migration or receipt/revision capability is a behavioral assertion, not an
import failure. Run only against a disposable, isolated PostgreSQL test DB.
"""
from datetime import date
from uuid import uuid4

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


BASE = ('sub_reports', '0011_general_activity_row_number')


def _executor():
    return MigrationExecutor(connection)


def _snapshot(apps, report_ids, activity_id, labor_id, material_id, attachment_id):
    report = apps.get_model('sub_reports', 'DisciplineSubReport')
    activity = apps.get_model('sub_reports', 'DisciplineSubReportActivity')
    labor = apps.get_model('sub_reports', 'DisciplineSubReportLabor')
    material = apps.get_model('sub_reports', 'DisciplineSubReportMaterial')
    attachment = apps.get_model('sub_reports', 'UnitReportAttachment')
    return {
        'reports': list(report.objects.filter(pk__in=report_ids).order_by('version_number').values(
            'id', 'project_id', 'report_date', 'unit', 'status', 'lineage_id',
            'version_number', 'is_current', 'supersedes_id', 'linked_daily_report_id', 'form_code',
        )),
        'activity': activity.objects.filter(pk=activity_id).values(
            'id', 'sub_report_id', 'row_number', 'activity_description', 'quantity', 'notes',
        ).get(),
        'labor': labor.objects.filter(pk=labor_id).values(
            'id', 'sub_report_id', 'job_title', 'present_count',
        ).get(),
        'material': material.objects.filter(pk=material_id).values(
            'id', 'sub_report_id', 'material_description', 'quantity', 'unit',
        ).get(),
        'attachment': attachment.objects.filter(pk=attachment_id).values(
            'id', 'sub_report_id', 'row_id', 'storage_key', 'checksum',
        ).get(),
    }


@pytest.mark.django_db(transaction=True)
def test_expand_preserves_historical_data_and_backfills_tokens(project, user):
    executor = _executor()
    leaves = executor.loader.graph.leaf_nodes()
    try:
        executor.migrate([BASE])
        old = executor.loader.project_state([BASE]).apps
        Report = old.get_model('sub_reports', 'DisciplineSubReport')
        Daily = old.get_model('field_reports', 'DailyReport')
        Activity = old.get_model('sub_reports', 'DisciplineSubReportActivity')
        Labor = old.get_model('sub_reports', 'DisciplineSubReportLabor')
        Material = old.get_model('sub_reports', 'DisciplineSubReportMaterial')
        Attachment = old.get_model('sub_reports', 'UnitReportAttachment')
        day = date(2026, 10, 17)
        daily = Daily.objects.create(project_id=project.pk, report_date=day, status='draft', created_by_id=user.pk)
        lineage = uuid4()
        prior = Report.objects.create(project_id=project.pk, report_date=day, unit='buildings',
                                      status='approved', lineage_id=lineage, version_number=1,
                                      is_current=False, linked_daily_report_id=daily.pk,
                                      form_code='historic', created_by_id=user.pk)
        current = Report.objects.create(project_id=project.pk, report_date=day, unit='buildings',
                                        status='draft', lineage_id=lineage, version_number=2,
                                        is_current=True, supersedes_id=prior.pk,
                                        linked_daily_report_id=daily.pk, form_code='correction',
                                        created_by_id=user.pk)
        activity = Activity.objects.create(sub_report_id=current.pk, row_number=1, shift='day',
                                           crew_name='Crew', activity_description='Existing work',
                                           quantity='1.2500', notes='preserve note')
        labor = Labor.objects.create(sub_report_id=current.pk, labor_category='worker',
                                     job_title='Mason', present_count=3)
        material = Material.objects.create(sub_report_id=current.pk, material_description='Cement',
                                           quantity='2.5000', unit='kg')
        attachment = Attachment.objects.create(sub_report_id=current.pk, row_kind='activity',
                                               row_id=str(activity.pk), storage_key='existing/image.jpg',
                                               checksum='abc123')
        ids = ([prior.pk, current.pk], activity.pk, labor.pk, material.pk, attachment.pk)
        before = _snapshot(old, *ids)

        executor = _executor()
        steps = [m for m, backwards in executor.migration_plan(leaves)
                 if m.app_label == 'sub_reports' and not backwards]
        assert steps, 'Feature 037 needs an additive migration after 0011 for receipts and revision backfill'
        executor.migrate(leaves)
        new = _executor().loader.project_state(leaves).apps
        assert _snapshot(new, *ids) == before, 'expand/backfill must preserve legacy values, lineage and references'
        for model_name, pk in [('DisciplineSubReport', current.pk),
                               ('DisciplineSubReportActivity', activity.pk),
                               ('DisciplineSubReportLabor', labor.pk),
                               ('DisciplineSubReportMaterial', material.pk)]:
            model = new.get_model('sub_reports', model_name)
            fields = {field.name for field in model._meta.fields}
            tokens = fields & {'sync_revision', 'sync_version', 'revision_token'}
            assert tokens, f'{model_name} needs a backfilled synchronization concurrency token'
            assert getattr(model.objects.get(pk=pk), sorted(tokens)[0]) is not None

        # An older application reads its historical model against the expanded
        # schema; this is the supported application rollback, not schema deletion.
        assert _snapshot(old, *ids) == before

        # Rehearse schema rollback only before any receipt exists, then restore.
        # Once receipts exist, supported rollback is application-only and must
        # retain the expanded journal; destructive schema reversal is unsafe.
        _executor().migrate([BASE])
        assert _snapshot(old, *ids) == before, 'pre-receipt schema rollback lost legacy data'
        _executor().migrate(leaves)
        restored = _executor().loader.project_state(leaves).apps
        assert _snapshot(restored, *ids) == before, 'reapplying migration lost legacy data'
    finally:
        _executor().migrate(leaves)


@pytest.mark.django_db(transaction=True)
def test_receipt_schema_enforces_scoped_operation_identity():
    executor = _executor()
    apps = executor.loader.project_state(executor.loader.graph.leaf_nodes()).apps
    candidates = []
    for model in apps.get_app_config('sub_reports').get_models():
        fields = {field.name for field in model._meta.fields}
        if {'project', 'actor', 'operation_id'} <= fields:
            candidates.append(model)
    assert candidates, 'A durable receipt with project, actor and operation_id is required for replay safety'
    receipt = candidates[0]
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, receipt._meta.db_table)
    expected = {receipt._meta.get_field(name).column for name in ('project', 'actor', 'operation_id')}
    assert any(c['unique'] and set(c['columns']) == expected for c in constraints.values()), (
        'Receipt operation identity must be unique per project and actor in the database'
    )


@pytest.mark.django_db(transaction=True)
def test_receipt_survives_old_application_reads_and_enforces_identity(project, user, other_user):
    """Application rollback keeps the expanded schema and its replay journal."""
    from django.db import IntegrityError, transaction

    executor = _executor()
    leaves = executor.loader.graph.leaf_nodes()
    apps = executor.loader.project_state(leaves).apps
    candidates = [model for model in apps.get_app_config('sub_reports').get_models()
                  if {'project', 'actor', 'operation_id'} <= {f.name for f in model._meta.fields}]
    assert candidates, 'A durable receipt is needed before rollback can preserve replay evidence'
    receipt = candidates[0]
    fields = {field.name: field for field in receipt._meta.fields}
    fingerprint = next((name for name in ('fingerprint', 'request_fingerprint', 'payload_hash')
                        if name in fields), None)
    outcome = next((name for name in ('outcome', 'status', 'terminal_outcome') if name in fields), None)
    assert fingerprint and outcome, 'A receipt must retain immutable request fingerprint and terminal outcome'
    values = {'project_id': project.pk, 'actor_id': user.pk, 'operation_id': uuid4(),
              fingerprint: 'a' * 64, outcome: 'success'}
    # Require an explicit fixture for extra mandatory fields instead of inventing data.
    missing = [f.name for f in fields.values() if not f.primary_key and not f.null
               and not f.has_default() and not getattr(f, 'auto_now', False)
               and not getattr(f, 'auto_now_add', False)
               and f.name not in {fingerprint, outcome, 'project', 'actor', 'operation_id'}]
    assert not missing, f'Populate additional required receipt contract fields explicitly: {missing}'
    original = receipt.objects.create(**values)
    with pytest.raises(IntegrityError), transaction.atomic():
        receipt.objects.create(**values)
    different_actor = dict(values, actor_id=other_user.pk)
    assert receipt.objects.create(**different_actor).pk != original.pk

    # Historical code may read original tables but cannot erase the new journal.
    old = executor.loader.project_state([BASE]).apps
    old.get_model('sub_reports', 'DisciplineSubReport').objects.filter(project_id=project.pk).count()
    saved = receipt.objects.get(pk=original.pk)
    assert saved.operation_id == values['operation_id']
    assert getattr(saved, fingerprint) == values[fingerprint]
    assert getattr(saved, outcome) == 'success'
