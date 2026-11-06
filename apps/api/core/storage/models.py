from django.conf import settings
from django.db import models

from common.models import UUIDModel


class StoredFileSource(models.TextChoices):
    """Which product area minted the file; drives view_documents vs view_reports."""

    DOCUMENTS = 'documents', 'documents'
    REPORTS = 'reports', 'reports'


class StoredFile(UUIDModel):
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='stored_files',
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_files',
    )
    s3_key = models.CharField(max_length=512)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True, default='')
    size_bytes = models.BigIntegerField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(
        max_length=20,
        choices=StoredFileSource.choices,
        blank=True,
        default='',
        help_text='Area that created the upload; used for permission checks.',
    )
    restricted_allowlist = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='allowed_stored_files',
    )

    class Meta:
        db_table = 'stored_files'
