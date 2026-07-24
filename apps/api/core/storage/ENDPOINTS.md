# Storage Endpoints

Routes are nested under `/api/v1/`

## Permissions

| Action | Permission |
|--------|------------|
| Get presigned upload URL | `IsAuthenticated` + `IsProjectMember` |
| Confirm file upload | `IsAuthenticated` + `CanAccessStoredFile` (requires to be the uploader) |
| Get presigned download URL | `IsAuthenticated` + `CanAccessStoredFile` |

## Endpoints

### 1. File Upload

The file upload flow involves getting a presigned URL directly to S3 and then confirming the upload on completion.

*   **URL:** `/projects/{project_pk}/files/upload-url/`
*   **Method:** `POST`
*   **Description:** Validates a request to upload a file and creates a new `StoredFile` object in the DB. Returns a presigned URL that allows securely uploading the file to S3.
    *   **Body:** `filename` (name of the file), `content_type` (MIME type of the file).

*   **URL:** `/files/{file_id}/confirm/`
*   **Method:** `POST`
*   **Description:** Confirms that a file has been successfully uploaded to S3. Validates the size and updates the status of the file record in the DB.
    *   **Body:** `size_bytes` (integer size of the file).

### 2. File Download

*   **URL:** `/files/{file_id}/download-url/`
*   **Method:** `GET`
*   **Description:** Generates a short-lived presigned URL to securely download an S3 file.
