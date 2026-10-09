"""FR-COL US2: versioned documents — retention, status, filters, revise ACL."""

from datetime import date
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from documents.models import DocumentRevision, DocumentStatus, ProjectDocument


@pytest.mark.django_db
class TestDocumentRevisionRetention:
    @patch('documents.services.document_service.upload_file_to_s3')
    def test_prior_revision_row_kept_with_original_file_url(self, mock_upload, auth_client, project):
        mock_upload.side_effect = [
            ('documents/x/v1.pdf', 'v1.pdf', 10),
            ('documents/x/v2.pdf', 'v2.pdf', 11),
        ]
        base = f'/api/v1/projects/{project.id}/documents/'
        upload = auth_client.post(
            base,
            {
                'title': 'Foundation plan',
                'doc_type': 'drawing',
                'revision': '0',
                'file': SimpleUploadedFile('v1.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
            format='multipart',
        )
        assert upload.status_code == status.HTTP_201_CREATED, upload.data
        doc_id = upload.data['id']

        rev = auth_client.post(
            f'{base}{doc_id}/revisions/',
            {
                'revision_label': 'A',
                'file': SimpleUploadedFile('v2.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
            format='multipart',
        )
        assert rev.status_code == status.HTTP_200_OK, rev.data

        prior = DocumentRevision.objects.get(document_id=doc_id, file_url='documents/x/v1.pdf')
        assert prior.revision_label in ('0', '')
        assert prior.file_url == 'documents/x/v1.pdf'

        latest = DocumentRevision.objects.get(document_id=doc_id, file_url='documents/x/v2.pdf')
        assert latest.revision_label == 'A'


@pytest.mark.django_db
class TestDocumentStatusAndIdentity:
    def test_default_status_draft_and_null_approver(self, auth_client, project):
        resp = auth_client.post(
            f'/api/v1/projects/{project.id}/documents/',
            {'title': 'Memo', 'doc_type': 'report'},
            format='multipart',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['status'] == DocumentStatus.DRAFT
        assert resp.data['approver'] is None

    def test_create_accepts_status_and_approver(self, auth_client, project, user):
        resp = auth_client.post(
            f'/api/v1/projects/{project.id}/documents/',
            {
                'title': 'Approved drawing',
                'doc_type': 'drawing',
                'doc_code': 'DWG-001',
                'status': DocumentStatus.APPROVED,
                'approver': str(user.id),
            },
            format='multipart',
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.data
        assert resp.data['status'] == DocumentStatus.APPROVED
        assert resp.data['approver'] == user.id

    def test_doc_code_unique_per_project_when_non_empty(self, auth_client, project):
        url = f'/api/v1/projects/{project.id}/documents/'
        first = auth_client.post(
            url,
            {'title': 'One', 'doc_code': 'DWG-UNIQ'},
            format='multipart',
        )
        assert first.status_code == status.HTTP_201_CREATED, first.data
        second = auth_client.post(
            url,
            {'title': 'Two', 'doc_code': 'DWG-UNIQ'},
            format='multipart',
        )
        assert second.status_code == status.HTTP_400_BAD_REQUEST

    def test_status_enum_validation(self, auth_client, project):
        resp = auth_client.post(
            f'/api/v1/projects/{project.id}/documents/',
            {'title': 'Bad', 'status': 'not_a_status'},
            format='multipart',
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDocumentListFilters:
    def test_list_filters_by_status_and_revision_date_and_doc_type(self, auth_client, project, user):
        ProjectDocument.objects.create(
            project=project,
            title='Draft drawing',
            doc_type='drawing',
            status=DocumentStatus.DRAFT,
            revision_date=date(2026, 1, 15),
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        ProjectDocument.objects.create(
            project=project,
            title='Approved spec',
            doc_type='specification',
            status=DocumentStatus.APPROVED,
            revision_date=date(2026, 3, 1),
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        ProjectDocument.objects.create(
            project=project,
            title='Old report',
            doc_type='report',
            status=DocumentStatus.APPROVED,
            revision_date=date(2025, 6, 1),
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        base = f'/api/v1/projects/{project.id}/documents/'
        by_status = auth_client.get(f'{base}?status={DocumentStatus.APPROVED}')
        assert by_status.status_code == status.HTTP_200_OK
        titles = {r['title'] for r in by_status.data['results']}
        assert titles == {'Approved spec', 'Old report'}

        by_type = auth_client.get(f'{base}?doc_type=drawing')
        assert len(by_type.data['results']) == 1
        assert by_type.data['results'][0]['title'] == 'Draft drawing'

        by_date = auth_client.get(f'{base}?date_from=2026-01-01&date_to=2026-12-31')
        assert {r['title'] for r in by_date.data['results']} == {'Draft drawing', 'Approved spec'}


@pytest.mark.django_db
class TestDocumentRevisePermission:
    @patch('documents.services.document_service.upload_file_to_s3')
    def test_revise_without_upload_documents_returns_403(
        self, mock_upload, auth_client, api_client, project, member, other_user
    ):
        mock_upload.return_value = ('documents/x/v1.pdf', 'v1.pdf', 10)
        create = auth_client.post(
            f'/api/v1/projects/{project.id}/documents/',
            {
                'title': 'Plan',
                'file': SimpleUploadedFile('v1.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
            format='multipart',
        )
        assert create.status_code == status.HTTP_201_CREATED
        doc_id = create.data['id']
        count_before = DocumentRevision.objects.filter(document_id=doc_id).count()

        api_client.force_authenticate(user=other_user)
        denied = api_client.post(
            f'/api/v1/projects/{project.id}/documents/{doc_id}/revisions/',
            {
                'revision_label': 'A',
                'file': SimpleUploadedFile('v2.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
            format='multipart',
        )
        assert denied.status_code == status.HTTP_403_FORBIDDEN
        assert DocumentRevision.objects.filter(document_id=doc_id).count() == count_before
