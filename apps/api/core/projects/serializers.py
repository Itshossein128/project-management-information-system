from rest_framework import serializers
from django.utils.translation import gettext as _

from config.exceptions import CodedValidationError
from projects.models import (
    PROTECTED_PROJECT_FIELDS,
    FiscalPeriodLock,
    Project,
    ProjectCapabilitySetting,
    ProjectChangeRequest,
    ProjectKickoffCharter,
    ProjectStatus,
)


PROTECTED_WHEN_STATUSES = {
    ProjectStatus.ACTIVE,
    ProjectStatus.SUSPENDED,
    ProjectStatus.COMPLETED,
    ProjectStatus.ARCHIVED,
}


def _apply_project_contractor_ref(attrs, *, project_id):
    """Sync contractor CharField snapshot from contractor_ref when provided."""
    if 'contractor_ref' not in attrs:
        return attrs
    ref = attrs.get('contractor_ref')
    if ref is None:
        attrs['contractor'] = ''
        return attrs
    from django.core.exceptions import ValidationError as DjangoValidationError
    from projects.contractor_utils import resolve_active_contractor

    if project_id is None:
        # Create path: accept active contractor; project binding happens on save.
        from projects.contractor_utils import CONTRACTOR_ROLE
        from projects.models import Stakeholder, StakeholderStatus

        pk = getattr(ref, 'pk', ref)
        try:
            stakeholder = Stakeholder.objects.get(
                pk=pk,
                is_deleted=False,
                status=StakeholderStatus.ACTIVE,
                role=CONTRACTOR_ROLE,
            )
        except Stakeholder.DoesNotExist as exc:
            raise serializers.ValidationError(
                {'contractor_ref': _('Select a valid active contractor.')}
            ) from exc
        attrs['contractor_ref'] = stakeholder
        attrs['contractor'] = stakeholder.name
        return attrs
    try:
        stakeholder = resolve_active_contractor(
            project_id=project_id, contractor_id=getattr(ref, 'pk', ref)
        )
    except DjangoValidationError as exc:
        raise serializers.ValidationError(
            getattr(exc, 'message_dict', {'contractor_ref': list(exc.messages)})
        ) from exc
    attrs['contractor_ref'] = stakeholder
    attrs['contractor'] = stakeholder.name
    return attrs


class ProjectListSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='id', read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'project_id',
            'id',
            'project_code',
            'project_name',
            'name',
            'slug',
            'employer',
            'status',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'currency',
            'member_count',
            'purpose',
            'scope_description',
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='id', read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)

    can_restore_from_archive = serializers.SerializerMethodField()

    def get_can_restore_from_archive(self, obj):
        from permissions.project import _is_global_admin
        request = self.context.get('request')
        return bool(request and _is_global_admin(request.user) and obj.status == ProjectStatus.ARCHIVED)

    can_edit_manager_for_restore = serializers.SerializerMethodField()
    can_create_restore_remediation = serializers.SerializerMethodField()
    can_view_restore_history = serializers.SerializerMethodField()

    def _restore_admin_context(self, obj):
        return self.get_can_restore_from_archive(obj) and obj.archived_from_status == ProjectStatus.ACTIVE

    def get_can_edit_manager_for_restore(self, obj):
        return bool(self._restore_admin_context(obj) and not obj.project_manager_id)

    def get_can_create_restore_remediation(self, obj):
        return bool(self._restore_admin_context(obj) and (not (obj.scope_description or '').strip() or obj.contract_amount is None) and not obj.change_requests.filter(is_deleted=False, status__in=['draft', 'submitted']).exists())

    def get_can_view_restore_history(self, obj):
        from permissions.project import member_has_codename
        request = self.context.get('request')
        return bool(request and member_has_codename(request.user, obj.pk, 'view_project'))

    can_resume_with_confirmation = serializers.SerializerMethodField()
    can_undo_completion = serializers.SerializerMethodField()
    can_view_status_undo_history = serializers.SerializerMethodField()
    status_undo_remediation = serializers.SerializerMethodField()

    def _undo_has(self, obj, permission):
        from permissions.project import member_has_codename
        request = self.context.get('request')
        return bool(request and request.user.is_active and member_has_codename(request.user, obj.pk, permission))

    def get_can_resume_with_confirmation(self, obj):
        return obj.status == 'suspended' and self._undo_has(obj, 'edit_project')

    def get_can_undo_completion(self, obj):
        from permissions.project import _is_global_admin
        request = self.context.get('request')
        return bool(obj.status == 'completed' and request and request.user.is_active and _is_global_admin(request.user))

    def get_can_view_status_undo_history(self, obj):
        return self._undo_has(obj, 'view_project')

    def get_status_undo_remediation(self, obj):
        from projects.status_undo_service import remediation
        from projects.lifecycle_service import activation_missing
        request = self.context.get('request')
        if not request or not request.user.is_active or not (obj.status == 'suspended' or obj.status == 'completed' and obj.completed_from_status == 'active'):
            return None
        operation = 'resume' if obj.status == 'suspended' else 'undo_completion'
        rows = remediation(obj, request.user, operation, activation_missing(obj))
        return {'operation': operation, 'source_event_id': str(obj.suspension_event_id if operation == 'resume' else obj.completion_event_id),
                'can_edit_manager': any(row['field']=='project_manager' and row['can_perform'] for row in rows),
                'can_create_change_request': any(row['field']!='project_manager' and row['can_perform'] for row in rows)}

    class Meta:
        model = Project
        fields = [
            'can_restore_from_archive', 'can_edit_manager_for_restore', 'can_create_restore_remediation', 'can_view_restore_history',
            'suspension_event_id','completion_event_id','completed_from_status','can_resume_with_confirmation','can_undo_completion','can_view_status_undo_history','status_undo_remediation',
            'archived_from_status', 'archive_cycle_id', 'lifecycle_version',
            'project_id',
            'id',
            'project_code',
            'project_name',
            'name',
            'slug',
            'purpose',
            'scope_description',
            'main_deliverables',
            'employer',
            'contractor',
            'contractor_ref',
            'consultant',
            'project_manager',
            'location',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'contract_number',
            'currency',
            'status',
            'budget_approved_at',
            'budget_approved_by',
            'cut_off_date',
            'max_depth',
            'owning_unit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'project_id',
            'id',
            'name',
            'slug',
            'budget_approved_at',
            'budget_approved_by',
            'created_at',
            'updated_at',
            'status',
        ]


class ProjectLifecycleWriteGuard:
    @staticmethod
    def assert_writable(data):
        if set(data) & {'status', 'archived_from_status', 'archive_cycle_id', 'lifecycle_version', 'budget_approved_at', 'budget_approved_by', 'restore_archive_cycle_id', 'restore_archive_cycle_id_id', 'restore_completion_event', 'restore_completion_event_id', 'suspension_event', 'suspension_event_id', 'completion_event', 'completion_event_id', 'completed_from_status'}:
            raise CodedValidationError({'detail': _('Project lifecycle fields are read-only. Use the project actions.')}, code='invalid_status_transition')

    def to_internal_value(self, data):
        self.assert_writable(data)
        return super().to_internal_value(data)


class ProjectCreateSerializer(ProjectLifecycleWriteGuard, serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_code',
            'project_name',
            'purpose',
            'scope_description',
            'main_deliverables',
            'employer',
            'contractor',
            'contractor_ref',
            'consultant',
            'project_manager',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'contract_number',
            'currency',
            'location',
            'start_date',
            'owning_unit',
        ]

    def validate_project_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_('Project code is required.'))
        return value

    def validate(self, attrs):
        if not attrs.get('project_name'):
            raise serializers.ValidationError({'project_name': 'This field is required.'})
        if not attrs.get('employer'):
            raise serializers.ValidationError({'employer': 'This field is required.'})
        if not attrs.get('start_date'):
            raise serializers.ValidationError({'start_date': 'This field is required.'})
        attrs = _apply_project_contractor_ref(attrs, project_id=None)
        return attrs

    def create(self, validated_data):
        validated_data['status'] = ProjectStatus.DRAFT
        validated_data['budget_approved_at'] = None
        validated_data['budget_approved_by'] = None
        return super().create(validated_data)


class ProjectUpdateSerializer(ProjectLifecycleWriteGuard, serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_code',
            'project_name',
            'purpose',
            'scope_description',
            'main_deliverables',
            'employer',
            'contractor',
            'contractor_ref',
            'consultant',
            'project_manager',
            'location',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'contract_number',
            'currency',
            'cut_off_date',
            'owning_unit',
        ]

    def validate(self, attrs):
        instance: Project = self.instance
        if instance and instance.status in PROTECTED_WHEN_STATUSES:
            blocked = [k for k in attrs if k in PROTECTED_PROJECT_FIELDS]
            if blocked:
                raise CodedValidationError(
                    {
                        'code': 'protected_field_requires_change_request',
                        'detail': 'Protected fields require a project change request.',
                        'fields': blocked,
                    },
                    code='protected_field_requires_change_request',
                )
        project_id = getattr(instance, 'id', None)
        return _apply_project_contractor_ref(attrs, project_id=project_id)

    def update(self, instance, validated_data):
        from django.db import transaction
        from projects.lifecycle_service import lock_project, save_project, assert_not_archived_mutable
        with transaction.atomic():
            fresh = lock_project(instance)
            request = self.context.get('request')
            if request:
                assert_not_archived_mutable(fresh, request.user)
            self.instance = fresh
            validated_data = self.validate(validated_data)
            changed = [key for key, value in validated_data.items() if getattr(fresh, key) != value]
            for key, value in validated_data.items():
                setattr(fresh, key, value)
            if changed:
                save_project(fresh, changed)
            return fresh


# Backward-compatible alias
ProjectSerializer = ProjectDetailSerializer


class ProjectCapabilitySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCapabilitySetting
        fields = [
            'capability_key',
            'enabled',
            'mode',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['capability_key', 'updated_at', 'updated_by']


class FiscalPeriodLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalPeriodLock
        fields = [
            'id',
            'period_start',
            'period_end',
            'reason',
            'closed_at',
            'closed_by',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'closed_at', 'closed_by', 'is_active', 'created_at']


class ProjectKickoffCharterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectKickoffCharter
        fields = [
            'id',
            'justification',
            'success_criteria',
            'constraints',
            'assumptions',
            'key_stakeholders_summary',
            'pm_authority',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectChangeRequestSerializer(serializers.ModelSerializer):
    @staticmethod
    def assert_unbound_input(data):
        if set(data) & {'restore_archive_cycle_id','restore_completion_event','restore_completion_event_id'}:
            raise CodedValidationError({'detail': _('Project lifecycle fields are read-only. Use the project actions.')}, code='invalid_status_transition')

    def to_internal_value(self, data):
        self.assert_unbound_input(data)
        return super().to_internal_value(data)

    restore_remediation_actions = serializers.SerializerMethodField()

    def get_restore_remediation_actions(self, obj):
        from permissions.project import member_has_codename, _is_global_admin
        from django.contrib.auth import get_user_model
        from rest_framework.exceptions import APIException
        request = self.context.get('request')
        user = get_user_model().objects.filter(pk=getattr(getattr(request, 'user', None), 'pk', None), is_active=True).first()
        if not user: return []
        if obj.restore_completion_event_id or obj.project.status == ProjectStatus.COMPLETED:
            edit = member_has_codename(user, obj.project_id, 'edit_project')
            approve = member_has_codename(user, obj.project_id, 'approve_project')
            admin = _is_global_admin(user)
            valid = True
            if obj.restore_completion_event_id:
                from projects.change_request_service import _check_bound_remediation
                try: _check_bound_remediation(obj.project, obj, user)
                except APIException: valid = False
                edit = admin
            if obj.status == 'draft': return (['update','submit'] if edit and valid else []) + (['cancel'] if edit else [])
            if obj.status == 'submitted':
                actions = (['cancel'] if edit else []) + (['reject'] if approve else [])
                if approve and valid and (user.is_superuser or str(obj.requested_by_id) != str(user.pk)): actions.append('approve')
                return actions
            return []
        from permissions.project import _is_global_admin
        request = self.context.get('request')
        if not request or not _is_global_admin(request.user) or obj.project.status != ProjectStatus.ARCHIVED or obj.project.archived_from_status != ProjectStatus.ACTIVE:
            return []
        if obj.restore_archive_cycle_id:
            from projects.change_request_service import _check_bound_remediation
            from rest_framework.exceptions import APIException
            try:
                _check_bound_remediation(obj.project, obj, request.user)
            except APIException:
                return ['cancel'] if obj.status in ('draft', 'submitted') else []
        if obj.status == 'draft': return ['update', 'submit', 'cancel']
        if obj.status == 'submitted':
            actions = ['reject', 'cancel']
            if request.user.is_superuser or str(obj.requested_by_id) != str(request.user.pk): actions.append('approve')
            return actions
        return []

    class Meta:
        model = ProjectChangeRequest
        fields = [
            'restore_remediation_actions', 'restore_archive_cycle_id', 'restore_completion_event_id',
            'id',
            'reason',
            'status',
            'proposed_changes',
            'previous_values',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
            'decision_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'restore_archive_cycle_id', 'restore_completion_event_id',
            'id',
            'status',
            'previous_values',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
            'created_at',
            'updated_at',
        ]


class ProjectRestoreRequestSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    confirmation_token = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) - set(self.fields):
            raise CodedValidationError({'detail': _('Invalid restoration request. Open a new preview.')}, code='invalid_restore_request')
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            raise CodedValidationError({'detail': _('Invalid restoration request. Open a new preview.'), 'fields': exc.detail}, code='invalid_restore_request')

    def validate(self, attrs):
        if not attrs.get('reason'):
            raise CodedValidationError({'detail': _('Enter a reason for restoration.'), 'fields': {'reason': _('A reason is required.')}}, code='reason_required')
        return attrs


class ProjectStatusUndoRequestSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    confirmation_token = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def to_internal_value(self, data):
        from projects.status_undo_service import invalid
        if not isinstance(data, dict) or set(data) - set(self.fields) or ('reason' in data and not isinstance(data['reason'], str)):
            invalid()
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            invalid()

    def validate(self, attrs):
        if not attrs.get('reason'):
            raise CodedValidationError({'detail': _('Enter a reason for this status correction.'), 'fields': {'reason': _('A reason is required.')}}, code='reason_required')
        return attrs
