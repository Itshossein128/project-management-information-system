from datetime import date

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.jalali import parse_jalali_or_gregorian
from common.viewsets import ProjectScopedViewSet
from documents.models import Correspondence, CorrStatus, DocumentRevision, MeetingMinutes, ProjectDocument
from documents.serializers import (
    CorrespondenceSerializer,
    DocumentRevisionSerializer,
    MeetingMinutesSerializer,
    ProjectDocumentDetailSerializer,
    ProjectDocumentSerializer,
)
from documents.services.correspondence_service import generate_corr_number
from documents.services.document_service import create_project_document, create_document_revision
from permissions.project import HasProjectPermission, IsProjectMember


class DocScopedViewSet(ProjectScopedViewSet):
    view_permission = 'view_documents'
    edit_permission = 'upload_documents'


class ProjectDocumentViewSet(DocScopedViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = ProjectDocument.objects.filter(
            project_id=self.kwargs['project_pk'], is_deleted=False
        )
        params = self.request.query_params
        for key in ('doc_type', 'discipline', 'access_level', 'related_activity', 'related_wbs'):
            if params.get(key):
                qs = qs.filter(**{key: params[key]})
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
        doc = create_project_document(
            project_id=self.kwargs['project_pk'],
            user=request.user,
            data=request.data,
            file_obj=request.FILES.get('file'),
        )
        return Response(ProjectDocumentDetailSerializer(doc).data, status=201)


class DocumentRevisionUploadView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'upload_documents'
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, project_pk=None, pk=None):
        doc = ProjectDocument.objects.get(pk=pk, project_id=project_pk, is_deleted=False)
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

    def list(self, request, *args, **kwargs):
        return Response({'results': CorrespondenceSerializer(self.get_queryset(), many=True).data})

    def perform_create(self, serializer):
        corr_number = self.request.data.get('corr_number') or generate_corr_number(
            self.kwargs['project_pk'], serializer.validated_data['corr_type']
        )
        serializer.save(
            project_id=self.kwargs['project_pk'],
            corr_number=corr_number,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


class CorrespondenceRespondView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_correspondence'

    def post(self, request, project_pk=None, pk=None):
        corr = Correspondence.objects.get(pk=pk, project_id=project_pk, is_deleted=False)
        corr.response_date = parse_jalali_or_gregorian(request.data.get('response_date')) or date.today()
        corr.status = CorrStatus.RESPONDED
        if request.data.get('file_url'):
            corr.file_url = request.data['file_url']
        corr.updated_by = request.user
        corr.save()
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
