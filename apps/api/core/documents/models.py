from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, UUIDModel, TimeStampedModel


class DocType(models.TextChoices):
    DRAWING = 'drawing', 'Drawing'
    SPECIFICATION = 'specification', 'Specification'
    CONTRACT = 'contract', 'Contract'
    REPORT = 'report', 'Report'
    CORRESPONDENCE = 'correspondence', 'Correspondence'
    MINUTES = 'minutes', 'Minutes'
    PHOTO = 'photo', 'Photo'
    OTHER = 'other', 'Other'


class AccessLevel(models.TextChoices):
    PUBLIC = 'public', 'Public'
    PROJECT = 'project', 'Project'
    RESTRICTED = 'restricted', 'Restricted'


class ProjectDocument(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='documents')
    doc_code = models.CharField(max_length=60, blank=True, default='')
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=40, choices=DocType.choices, default=DocType.OTHER)
    discipline = models.CharField(max_length=60, blank=True, default='')
    revision = models.CharField(max_length=20, blank=True, default='')
    revision_date = models.DateField(null=True, blank=True)
    file_url = models.CharField(max_length=500, blank=True, default='')
    file_name = models.CharField(max_length=200, blank=True, default='')
    file_size_kb = models.PositiveIntegerField(null=True, blank=True)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.PROJECT)
    restricted_to = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='restricted_documents')
    tags = models.CharField(max_length=200, blank=True, default='')
    related_activity = models.ForeignKey(
        'projects.Activity', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents'
    )
    related_wbs = models.ForeignKey(
        'projects.WBS', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='uploaded_documents'
    )

    class Meta:
        db_table = 'project_documents'


class DocumentRevision(UUIDModel, TimeStampedModel):
    document = models.ForeignKey(ProjectDocument, on_delete=models.CASCADE, related_name='revisions')
    revision_label = models.CharField(max_length=20)
    revision_date = models.DateField()
    file_url = models.CharField(max_length=500)
    change_description = models.TextField(blank=True, default='')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')

    class Meta:
        db_table = 'document_revisions'


class CorrType(models.TextChoices):
    OUTGOING = 'outgoing', 'Outgoing'
    INCOMING = 'incoming', 'Incoming'
    INTERNAL = 'internal', 'Internal'


class CorrStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    RESPONDED = 'responded', 'Responded'
    CLOSED = 'closed', 'Closed'
    NO_RESPONSE_NEEDED = 'no_response_needed', 'No response needed'


class Correspondence(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='correspondence')
    corr_number = models.CharField(max_length=60)
    corr_type = models.CharField(max_length=20, choices=CorrType.choices)
    subject = models.CharField(max_length=200)
    from_party = models.CharField(max_length=120)
    to_party = models.CharField(max_length=120)
    corr_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    response_due_date = models.DateField(null=True, blank=True)
    response_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=CorrStatus.choices, default=CorrStatus.OPEN)
    summary = models.TextField(blank=True, default='')
    file_url = models.CharField(max_length=500, blank=True, default='')
    related_document = models.ForeignKey(
        ProjectDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='correspondence'
    )
    related_activity = models.ForeignKey(
        'projects.Activity', on_delete=models.SET_NULL, null=True, blank=True, related_name='correspondence'
    )
    tags = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        db_table = 'correspondence'


class MeetingType(models.TextChoices):
    WEEKLY_PROGRESS = 'weekly_progress', 'Weekly progress'
    EMPLOYER_MEETING = 'employer_meeting', 'Employer meeting'
    SUBCONTRACTOR = 'subcontractor', 'Subcontractor'
    SAFETY = 'safety', 'Safety'
    OTHER = 'other', 'Other'


class MeetingMinutes(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='meetings')
    meeting_date = models.DateField()
    meeting_type = models.CharField(max_length=40, choices=MeetingType.choices)
    location = models.CharField(max_length=120, blank=True, default='')
    chairperson = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='chaired_meetings'
    )
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='meetings_attended')
    external_attendees = models.TextField(blank=True, default='')
    agenda = models.TextField(blank=True, default='')
    decisions = models.TextField()
    action_items = models.TextField(blank=True, default='')
    file_url = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'meeting_minutes'
