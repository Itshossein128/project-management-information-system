"""Documents module tests."""

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from documents.models import AccessLevel, Correspondence, CorrStatus, CorrType, ProjectDocument
from master_data.models import ProjectMember


@pytest.mark.django_db
class TestDocumentsAPI:
    @patch('documents.services.document_service.upload_file_to_s3')
    def test_upload_document_and_revision(self, mock_upload, auth_client, project):
        mock_upload.return_value = ('documents/x/file.pdf', 'file.pdf', 12)
        url = f'/api/v1/projects/{project.id}/documents/'
        upload = auth_client.post(
            url,
            {
                'title': 'Foundation plan',
                'doc_type': 'drawing',
                'file': SimpleUploadedFile('file.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
            format='multipart',
        )
        assert upload.status_code == status.HTTP_201_CREATED, upload.data
        doc_id = upload.data['id']
        assert upload.data['file_url']

        rev = auth_client.post(
            f'/api/v1/projects/{project.id}/documents/{doc_id}/revisions/',
            {
                'revision_label': 'A',
                'file': SimpleUploadedFile('file2.pdf', b'%PDF-1.4', content_type='application/pdf'),
            },
            format='multipart',
        )
        assert rev.status_code == status.HTTP_200_OK

    def test_list_documents_search_filter(self, auth_client, project, user):
        ProjectDocument.objects.create(
            project=project,
            title='Foundation plan',
            doc_code='DRW-01',
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        ProjectDocument.objects.create(
            project=project,
            title='Other',
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        url = f'/api/v1/projects/{project.id}/documents/?search=Foundation'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1

    def test_restricted_document_hidden_from_other_member(self, auth_client, project, user, other_user):
        from master_data.models import MemberStatus, ProjectMemberRole, Role

        ProjectDocument.objects.create(
            project=project,
            title='Secret',
            access_level=AccessLevel.RESTRICTED,
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        ProjectDocument.objects.create(
            project=project,
            title='Public plan',
            access_level=AccessLevel.PROJECT,
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        role = Role.objects.get(role_name='document_controller')
        member, _ = ProjectMember.objects.get_or_create(
            project=project,
            user=other_user,
            defaults={'status': MemberStatus.ACTIVE},
        )
        ProjectMemberRole.objects.get_or_create(member=member, role=role)
        auth_client.force_authenticate(user=other_user)
        resp = auth_client.get(f'/api/v1/projects/{project.id}/documents/')
        assert resp.status_code == status.HTTP_200_OK, resp.data
        titles = [r['title'] for r in resp.data['results']]
        assert 'Secret' not in titles
        assert 'Public plan' in titles

    def test_soft_delete_document(self, auth_client, project, user):
        doc = ProjectDocument.objects.create(
            project=project,
            title='To delete',
            uploaded_by=user,
            created_by=user,
            updated_by=user,
        )
        resp = auth_client.delete(f'/api/v1/projects/{project.id}/documents/{doc.id}/')
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not ProjectDocument.objects.filter(id=doc.id).exists()

    def test_correspondence_overdue_filter(self, auth_client, project, user):
        Correspondence.objects.create(
            project=project,
            corr_number='C-1',
            corr_type=CorrType.INCOMING,
            subject='Late',
            from_party='A',
            to_party='B',
            corr_date=date.today() - timedelta(days=10),
            response_due_date=date.today() - timedelta(days=1),
            status=CorrStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        Correspondence.objects.create(
            project=project,
            corr_number='C-2',
            corr_type=CorrType.OUTGOING,
            subject='Ok',
            from_party='A',
            to_party='B',
            corr_date=date.today(),
            response_due_date=date.today() + timedelta(days=5),
            status=CorrStatus.OPEN,
            created_by=user,
            updated_by=user,
        )
        resp = auth_client.get(f'/api/v1/projects/{project.id}/correspondence/?overdue=true')
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data['results']) == 1
        assert resp.data['results'][0]['corr_number'] == 'C-1'
