from rest_framework import serializers

from common.serializers import JalaliDateField
from documents.models import Correspondence, DocumentRevision, MeetingMinutes, ProjectDocument
from documents.services.upload_service import presign_get_url


class DocumentRevisionSerializer(serializers.ModelSerializer):
    revision_date = JalaliDateField()

    class Meta:
        model = DocumentRevision
        fields = [
            'id', 'revision_label', 'revision_date', 'file_url',
            'change_description', 'uploaded_by', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_url'] = presign_get_url(instance.file_url)
        return data


class ProjectDocumentSerializer(serializers.ModelSerializer):
    revision_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'doc_code', 'title', 'doc_type', 'discipline', 'revision',
            'revision_date', 'file_url', 'file_name', 'file_size_kb',
            'access_level', 'tags', 'related_activity', 'related_wbs', 'uploaded_by',
        ]
        read_only_fields = ['id', 'file_url', 'file_name', 'file_size_kb', 'uploaded_by']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_url'] = presign_get_url(instance.file_url)
        return data


class ProjectDocumentDetailSerializer(ProjectDocumentSerializer):
    revisions = DocumentRevisionSerializer(many=True, read_only=True)

    class Meta(ProjectDocumentSerializer.Meta):
        fields = ProjectDocumentSerializer.Meta.fields + ['revisions']


class CorrespondenceSerializer(serializers.ModelSerializer):
    corr_date = JalaliDateField()
    received_date = JalaliDateField(required=False, allow_null=True)
    response_due_date = JalaliDateField(required=False, allow_null=True)
    response_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = Correspondence
        fields = [
            'id', 'corr_number', 'corr_type', 'subject', 'from_party', 'to_party',
            'corr_date', 'received_date', 'response_due_date', 'response_date',
            'status', 'summary', 'file_url', 'related_document', 'related_activity', 'tags',
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_url'] = presign_get_url(instance.file_url) if instance.file_url else ''
        return data


class MeetingMinutesSerializer(serializers.ModelSerializer):
    meeting_date = JalaliDateField()

    class Meta:
        model = MeetingMinutes
        fields = [
            'id', 'meeting_date', 'meeting_type', 'location', 'chairperson',
            'attendees', 'external_attendees', 'agenda', 'decisions',
            'action_items', 'file_url',
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_url'] = presign_get_url(instance.file_url) if instance.file_url else ''
        return data
