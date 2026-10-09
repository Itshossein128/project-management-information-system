from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.serializers import JalaliDateField
from documents.models import (
    Correspondence,
    DocumentRevision,
    MeetingAction,
    MeetingMinutes,
    ProjectDocument,
)
from documents.services.upload_service import presign_get_url

User = get_user_model()


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
    approver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'doc_code', 'title', 'doc_type', 'discipline', 'revision',
            'revision_date', 'file_url', 'file_name', 'file_size_kb',
            'access_level', 'tags', 'related_activity', 'related_wbs', 'uploaded_by',
            'status', 'approver',
        ]
        read_only_fields = ['id', 'file_url', 'file_name', 'file_size_kb', 'uploaded_by']

    def validate(self, attrs):
        doc_code = attrs.get('doc_code')
        if doc_code is None and self.instance is not None:
            doc_code = self.instance.doc_code
        if doc_code:
            project_id = self.context.get('project_id')
            if project_id is None and self.instance is not None:
                project_id = self.instance.project_id
            if project_id is not None:
                qs = ProjectDocument.objects.filter(
                    project_id=project_id,
                    doc_code=doc_code,
                    is_deleted=False,
                )
                if self.instance is not None:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    raise serializers.ValidationError(
                        {'doc_code': 'Document code must be unique within the project.'}
                    )
        return attrs

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
            'status', 'summary', 'file_url', 'related_document', 'related_activity',
            'related_contract', 'tags',
        ]
        read_only_fields = ['id']

    def validate_related_contract(self, contract):
        if contract is None:
            return contract
        project_pk = self.context.get('project_pk')
        if project_pk is not None and str(contract.project_id) != str(project_pk):
            raise serializers.ValidationError('Contract must belong to the same project.')
        return contract

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_url'] = presign_get_url(instance.file_url) if instance.file_url else ''
        return data


class MeetingMinutesSerializer(serializers.ModelSerializer):
    meeting_date = JalaliDateField()

    class Meta:
        model = MeetingMinutes
        fields = [
            'id', 'meeting_date', 'meeting_type', 'topic', 'location', 'chairperson',
            'attendees', 'external_attendees', 'agenda', 'decisions',
            'action_items', 'file_url',
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file_url'] = presign_get_url(instance.file_url) if instance.file_url else ''
        return data


class MeetingActionSerializer(serializers.ModelSerializer):
    due_date = JalaliDateField(required=False, allow_null=True)
    is_overdue = serializers.BooleanField(read_only=True, required=False)

    class Meta:
        model = MeetingAction
        fields = [
            'id',
            'meeting',
            'description',
            'owner',
            'due_date',
            'status',
            'completed_at',
            'is_overdue',
        ]
        read_only_fields = ['id', 'meeting', 'completed_at', 'is_overdue']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.due_date and instance.status == 'open':
            data['is_overdue'] = instance.due_date < date.today()
        else:
            data['is_overdue'] = False
        return data
