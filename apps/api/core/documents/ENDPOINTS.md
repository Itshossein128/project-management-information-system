# Documents Endpoints

This document outlines the API endpoints available in the `documents` app, mapping out the routes, their corresponding views, and the operations they support. Note that these endpoints are typically nested under a project URL (e.g., `/api/projects/{project_pk}/...`).

## Documents

Endpoints related to managing project documents.

*   **`GET /documents/`**
    *   **Purpose:** Lists all documents associated with a specific project.
    *   **Behavior:** Supports filtering by `doc_type`, `discipline`, `access_level`, `related_activity`, `related_wbs`, and searching by `title`, `doc_code`, or `tags`. Only returns documents that are not marked as deleted (`is_deleted=False`).

*   **`POST /documents/`**
    *   **Purpose:** Creates and uploads a new project document.
    *   **Behavior:** Accepts multipart form data containing the file and metadata. Validates the upload, uploads the file to S3, and saves the document metadata to the database. Supports linking to related activities or WBS nodes.

*   **`GET /documents/<uuid:pk>/`**
    *   **Purpose:** Retrieves the details of a specific project document.
    *   **Behavior:** Returns detailed information using the `ProjectDocumentDetailSerializer`.

*   **`DELETE /documents/<uuid:pk>/`**
    *   **Purpose:** Deletes a specific project document.
    *   **Behavior:** Performs a soft delete by setting `is_deleted = True`, `deleted_at = timezone.now()`, and updating the `updated_by` field. Returns a `204 No Content` status.

*   **`POST /documents/<uuid:pk>/revisions/`**
    *   **Purpose:** Uploads a new revision for an existing document.
    *   **Behavior:** Handled by `DocumentRevisionUploadView`. Accepts a new file, validates it, uploads to S3, creates a `DocumentRevision` record, and updates the primary `ProjectDocument` record with the new revision details and file URL.

## Correspondence

Endpoints related to managing project correspondences (e.g., RFIs, Transmittals, Letters).

*   **`GET /correspondence/`**
    *   **Purpose:** Lists all correspondences for a project.
    *   **Behavior:** Supports filtering by `corr_type`, `status`, date ranges (`date_from`, `date_to`), overdue status (`overdue=true`), and searching by `subject`, `from_party`, or `to_party`. Only returns non-deleted items.

*   **`POST /correspondence/`**
    *   **Purpose:** Creates a new correspondence record.
    *   **Behavior:** Automatically generates a correspondence number (`corr_number`) if not provided, based on the project and correspondence type using `generate_corr_number`.

*   **`PATCH /correspondence/<uuid:pk>/`**
    *   **Purpose:** Partially updates an existing correspondence.
    *   **Behavior:** Updates specific fields of a correspondence record.

*   **`DELETE /correspondence/<uuid:pk>/`**
    *   **Purpose:** Deletes a specific correspondence.
    *   **Behavior:** Soft deletes the correspondence.

*   **`POST /correspondence/<uuid:pk>/respond/`**
    *   **Purpose:** Marks a correspondence as responded to.
    *   **Behavior:** Handled by `CorrespondenceRespondView`. Updates the `response_date`, sets the status to `RESPONDED` (`CorrStatus.RESPONDED`), and optionally updates the `file_url`.

## Meeting Minutes

Endpoints related to managing meeting minutes for a project.

*   **`GET /meetings/`**
    *   **Purpose:** Lists meeting minutes for a project.
    *   **Behavior:** Ordered by `meeting_date` descending. Supports filtering by `meeting_type`. Only returns non-deleted items.

*   **`POST /meetings/`**
    *   **Purpose:** Creates a new meeting minutes record.
    *   **Behavior:** Saves a new meeting minute entry linked to the project.

*   **`GET /meetings/<uuid:pk>/`**
    *   **Purpose:** Retrieves details of a specific meeting minutes record.
    *   **Behavior:** Returns the full details of the meeting minutes.

*   **`PATCH /meetings/<uuid:pk>/`**
    *   **Purpose:** Partially updates a specific meeting minutes record.
    *   **Behavior:** Updates specific fields.

*   **`DELETE /meetings/<uuid:pk>/`**
    *   **Purpose:** Deletes a specific meeting minutes record.
    *   **Behavior:** Soft deletes the meeting minutes entry.

## Upload security

Document and revision uploads pass through two layers of validation:

1. **`common.validators.validate_document_upload`** — enforces extension whitelist, 50 MB max size, and MIME sniffing (via `python-magic` when available).
2. **`documents.services.upload_service.upload_file_to_s3`** — rejects filenames containing `..`, `/`, or `\`; stores objects under `{prefix}/{project_id}/{uuid}.{ext}` using only the basename.

Clients must send the file as multipart form data with a plain filename (no directory components). Path traversal in the original filename returns `400` with `Invalid filename: Path traversal attempts are not allowed.`
