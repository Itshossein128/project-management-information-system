# Generated manually for FR-CON gap closure (011-contracts-ipc)

from django.db import migrations, models


def backfill_ipc_amounts(apps, schema_editor):
    IPC = apps.get_model('contracts', 'IPC')
    for ipc in IPC.objects.all().iterator():
        gross = ipc.gross_amount or 0
        updates = []
        if ipc.status in ('submitted', 'under_review', 'approved', 'paid'):
            if ipc.submitted_amount is None:
                ipc.submitted_amount = gross
                updates.append('submitted_amount')
        if ipc.status in ('approved', 'paid'):
            if ipc.approved_amount is None:
                ipc.approved_amount = gross
                updates.append('approved_amount')
        if updates:
            ipc.save(update_fields=updates)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0005_central_data_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='payment_terms',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='ipc',
            name='submitted_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='ipc',
            name='approved_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='ipc',
            name='approval_variance_note',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.RunPython(backfill_ipc_amounts, noop_reverse),
    ]
