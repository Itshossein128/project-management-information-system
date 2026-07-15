from datetime import date
from django.db import transaction
from django.utils import timezone
from common.jalali import parse_jalali_or_gregorian
from common.validators import validate_document_upload
from documents.models import DocumentRevision, ProjectDocument
from documents.services.upload_service import upload_file_to_s3

@transaction.atomic
def create_project_document(project_id, user, data, file_obj=None) -> ProjectDocument:
    if file_obj:
        validate_document_upload(file_obj)
        url, name, size_kb = upload_file_to_s3(file_obj, project_id)
    else:
        url, name, size_kb = '', '', None

    doc = ProjectDocument.objects.create(
        project_id=project_id,
        title=data.get('title', name or 'Untitled'),
        doc_type=data.get('doc_type', 'other'),
        doc_code=data.get('doc_code', ''),
        discipline=data.get('discipline', ''),
        revision=data.get('revision', ''),
        revision_date=parse_jalali_or_gregorian(data['revision_date']) if data.get('revision_date') else None,
        access_level=data.get('access_level', 'project'),
        tags=data.get('tags', ''),
        file_url=url,
        file_name=name,
        file_size_kb=size_kb,
        uploaded_by=user,
        created_by=user,
        updated_by=user,
    )

    if data.get('related_activity'):
        doc.related_activity_id = data['related_activity']
        doc.save(update_fields=['related_activity'])
    if data.get('related_wbs'):
        doc.related_wbs_id = data['related_wbs']
        doc.save(update_fields=['related_wbs'])

    return doc


@transaction.atomic
def create_document_revision(doc: ProjectDocument, user, data, file_obj) -> DocumentRevision:
    validate_document_upload(file_obj)
    url, name, size_kb = upload_file_to_s3(file_obj, doc.project_id)

    rev_label = data.get('revision_label', doc.revision or 'Rev')
    rev_date = parse_jalali_or_gregorian(data.get('revision_date')) or date.today()

    revision = DocumentRevision.objects.create(
        document=doc,
        revision_label=rev_label,
        revision_date=rev_date,
        file_url=url,
        change_description=data.get('change_description', ''),
        uploaded_by=user,
    )

    doc.revision = rev_label
    doc.revision_date = rev_date
    doc.file_url = url
    doc.file_name = name
    doc.file_size_kb = size_kb
    doc.updated_by = user
    doc.save()

    return revision
