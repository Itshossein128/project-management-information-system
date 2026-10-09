from collections import defaultdict

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.viewsets import ProjectScopedViewSet
from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from projects.models import CommunicationPlan, Stakeholder


def _user_may_view_sensitive_contacts(user, project_id) -> bool:
    return member_has_codename(user, project_id, 'view_sensitive_contacts') or member_has_codename(
        user, project_id, 'edit_project'
    )


class StakeholderSerializer(serializers.ModelSerializer):
    contacts_redacted = serializers.BooleanField(read_only=True, required=False)

    class Meta:
        model = Stakeholder
        fields = [
            'id',
            'name',
            'organization_name',
            'role',
            'email',
            'phone',
            'influence',
            'interest',
            'communication_need',
            'relationship_owner',
            'status',
            'contacts_redacted',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'contacts_redacted']

    def validate_influence(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('Must be between 1 and 5')
        return value

    def validate_interest(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('Must be between 1 and 5')
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        project_id = instance.project_id
        if request and request.user.is_authenticated:
            if not _user_may_view_sensitive_contacts(request.user, project_id):
                data['email'] = None
                data['phone'] = None
                data['contacts_redacted'] = True
            else:
                data['contacts_redacted'] = False
        return data


class StakeholderViewSet(ProjectScopedViewSet):
    queryset = Stakeholder.objects.all()
    serializer_class = StakeholderSerializer
    view_permission = 'view_project'
    edit_permission = 'edit_project'

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response({'results': serializer.data})


class StakeholderMatrixView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_project'

    def get(self, request, project_pk=None):
        stakeholders = Stakeholder.objects.filter(
            project_id=project_pk,
            is_deleted=False,
            influence__isnull=False,
            interest__isnull=False,
        )
        buckets = defaultdict(list)
        for s in stakeholders:
            key = (s.influence, s.interest)
            buckets[key].append({'id': str(s.id), 'name': s.name})
        cells = [
            {'influence': inf, 'interest': intr, 'stakeholders': buckets[(inf, intr)]}
            for (inf, intr) in sorted(buckets.keys())
        ]
        return Response({'cells': cells})


class CommunicationPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationPlan
        fields = [
            'id',
            'audience',
            'message',
            'channel_type',
            'frequency',
            'owner',
            'stakeholder',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CommunicationPlanViewSet(ProjectScopedViewSet):
    queryset = CommunicationPlan.objects.all()
    serializer_class = CommunicationPlanSerializer
    view_permission = 'view_project'
    edit_permission = 'edit_project'

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response({'results': serializer.data})
