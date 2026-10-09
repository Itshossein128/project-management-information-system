from datetime import date

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.viewsets import ProjectScopedViewSet
from common.jalali import parse_date_optional, parse_jalali_or_gregorian
from documents.models import (
    AccessLevel,
    Correspondence,
    CorrStatus,
    MeetingAction,
    MeetingActionStatus,
    MeetingMinutes,
    ProjectDocument,
)
from documents.serializers import (
    CorrespondenceSerializer,
    MeetingActionSerializer,
    MeetingMinutesSerializer,
    ProjectDocumentDetailSerializer,
    ProjectDocumentSerializer,
)
from documents.services.correspondence_service import generate_corr_number, respond_to_correspondence
from documents.services.document_service import create_project_document, create_document_revision
from documents.services.meeting_action_service import list_open_meeting_actions, mark_meeting_action_done
from permissions.project import HasProjectPermission


class DocScopedViewSet(ProjectScopedViewSet):
    view_permission = 'view_documents'
    edit_permission = 'upload_documents'


def _visible_documents_qs(project_id, user):
    """Enforce access_level: public/project for members; restricted to allowlist/uploader."""
    qs = ProjectDocument.objects.filter(project_id=project_id, is_deleted=False)
    return qs.filter(
        Q(access_level__in=[AccessLevel.PUBLIC, AccessLevel.PROJECT])
        | Q(access_level=AccessLevel.RESTRICTED, restricted_to=user)
        | Q(uploaded_by=user)
    ).distinct()


class ProjectDocumentViewSet(DocScopedViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = _visible_documents_qs(self.kwargs['project_pk'], self.request.user)
        params = self.request.query_params
        for key in ('doc_type', 'discipline', 'access_level', 'related_activity', 'related_wbs', 'status'):
            if params.get(key):
                qs = qs.filter(**{key: params[key]})
        if params.get('date_from'):
            qs = qs.filter(revision_date__gte=parse_jalali_or_gregorian(params['date_from']))
        if params.get('date_to'):
            qs = qs.filter(revision_date__lte=parse_jalali_or_gregorian(params['date_to']))
        if params.get('search'):
            q = params['search']
            qs = qs.filter(Q(title__icontains=q) | Q(doc_code__icontains=q) | Q(tags__icontains=q))
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDocumentDetailSerializer
        return ProjectDocumentSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return Response({'results': ProjectDocumentSerializer(qs, many=True).data})

    @extend_schema(summary='Upload project document', tags=['Documents'])
    def create(self, request, *args, **kwargs):
        serializer = ProjectDocumentSerializer(
            data=request.data,
            context={'project_id': self.kwargs['project_pk']},
        )
        serializer.is_valid(raise_exception=True)
        doc = create_project_document(
            project_id=self.kwargs['project_pk'],
            user=request.user,
            data=serializer.validated_data,
            file_obj=request.FILES.get('file'),
        )
        return Response(ProjectDocumentDetailSerializer(doc).data, status=201)


class DocumentRevisionUploadView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'upload_documents'
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, project_pk=None, pk=None):
        doc = get_object_or_404(
            _visible_documents_qs(project_pk, request.user),
            pk=pk,
        )
        create_document_revision(
            doc=doc,
            user=request.user,
            data=request.data,
            file_obj=request.FILES.get('file'),
        )
        return Response(ProjectDocumentDetailSerializer(doc).data)


class CorrespondenceViewSet(DocScopedViewSet):
    view_permission = 'view_correspondence'
    edit_permission = 'edit_correspondence'
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        qs = Correspondence.objects.filter(project_id=self.kwargs['project_pk'], is_deleted=False)
        params = self.request.query_params
        for key in ('corr_type', 'status'):
            if params.get(key):
                qs = qs.filter(**{key: params[key]})
        if params.get('date_from'):
            qs = qs.filter(corr_date__gte=parse_jalali_or_gregorian(params['date_from']))
        if params.get('date_to'):
            qs = qs.filter(corr_date__lte=parse_jalali_or_gregorian(params['date_to']))
        if params.get('overdue') == 'true':
            qs = qs.filter(status=CorrStatus.OPEN, response_due_date__lt=date.today())
        if params.get('search'):
            q = params['search']
            qs = qs.filter(Q(subject__icontains=q) | Q(from_party__icontains=q) | Q(to_party__icontains=q))
        return qs

    def get_serializer_class(self):
        return CorrespondenceSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['project_pk'] = self.kwargs['project_pk']
        return ctx

    def list(self, request, *args, **kwargs):
        return Response({'results': CorrespondenceSerializer(self.get_queryset(), many=True).data})

    def perform_create(self, serializer):
        corr_number = self.request.data.get('corr_number') or generate_corr_number(
            self.kwargs['project_pk'], serializer.validated_data['corr_type']
        )
        super().perform_create(serializer, corr_number=corr_number)


class CorrespondenceRespondView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_correspondence'

    def post(self, request, project_pk=None, pk=None):
        corr = get_object_or_404(
            Correspondence,
            pk=pk,
            project_id=project_pk,
            is_deleted=False,
        )
        corr = respond_to_correspondence(corr, request.data, request.user)
        return Response(CorrespondenceSerializer(corr).data)


class MeetingMinutesViewSet(DocScopedViewSet):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    def get_queryset(self):
        qs = MeetingMinutes.objects.filter(project_id=self.kwargs['project_pk'], is_deleted=False)
        if self.request.query_params.get('meeting_type'):
            qs = qs.filter(meeting_type=self.request.query_params['meeting_type'])
        return qs.order_by('-meeting_date')

    def get_serializer_class(self):
        return MeetingMinutesSerializer

    def list(self, request, *args, **kwargs):
        return Response({'results': MeetingMinutesSerializer(self.get_queryset(), many=True).data})


    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class MeetingActionNestedView(DocScopedViewSet):
    """GET|POST /meetings/{meeting_id}/actions/"""

    serializer_class = MeetingActionSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_meeting(self):
        return get_object_or_404(
            MeetingMinutes,
            pk=self.kwargs['meeting_pk'],
            project_id=self.kwargs['project_pk'],
            is_deleted=False,
        )

    def get_queryset(self):
        meeting = self.get_meeting()
        return MeetingAction.objects.filter(meeting=meeting, is_deleted=False)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return Response({'results': MeetingActionSerializer(qs, many=True).data})

    def create(self, request, *args, **kwargs):
        meeting = self.get_meeting()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.save(
            meeting=meeting,
            project_id=self.kwargs['project_pk'],
            created_by=request.user,
            updated_by=request.user,
        )
        return Response(MeetingActionSerializer(action).data, status=201)


class MeetingActionDetailView(DocScopedViewSet):
    """PATCH /meeting-actions/{id}/"""

    serializer_class = MeetingActionSerializer
    http_method_names = ['patch', 'head', 'options']

    def get_queryset(self):
        return MeetingAction.objects.filter(
            project_id=self.kwargs['project_pk'],
            is_deleted=False,
        )

    def partial_update(self, request, *args, **kwargs):
        action = self.get_object()
        new_status = request.data.get('status')
        if new_status == MeetingActionStatus.DONE:
            mark_meeting_action_done(action, request.user)
            action.refresh_from_db()
            return Response(MeetingActionSerializer(action).data)
        serializer = self.get_serializer(action, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(MeetingActionSerializer(action).data)


class OpenMeetingActionsView(DocScopedViewSet):
    """GET /meeting-actions/open/"""

    serializer_class = MeetingActionSerializer
    http_method_names = ['get', 'head', 'options']

    def list(self, request, *args, **kwargs):
        overdue = request.query_params.get('overdue') == 'true'
        qs = list_open_meeting_actions(self.kwargs['project_pk'], overdue=overdue)
        return Response({'results': MeetingActionSerializer(qs, many=True).data})
