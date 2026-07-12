import { apiJson } from "@/app/lib/api-client";

export interface UploadUrlResponse {
  file_id: string;
  upload_url: string;
  s3_key: string;
}

export async function requestUploadUrl(
  projectId: string,
  filename: string,
  contentType: string,
): Promise<UploadUrlResponse> {
  return apiJson<UploadUrlResponse>(
    `/api/v1/projects/${projectId}/files/upload-url/`,
    {
      method: "POST",
      body: JSON.stringify({ filename, content_type: contentType }),
    },
  );
}

export async function confirmUpload(
  fileId: string,
  sizeBytes: number,
): Promise<{ id: string; confirmed: boolean }> {
  return apiJson(`/api/v1/files/${fileId}/confirm/`, {
    method: "POST",
    body: JSON.stringify({ size_bytes: sizeBytes }),
  });
}

export async function uploadProjectFile(
  projectId: string,
  file: File,
): Promise<string> {
  const { file_id, upload_url } = await requestUploadUrl(
    projectId,
    file.name,
    file.type || "application/octet-stream",
  );
  const put = await fetch(upload_url, {
    method: "PUT",
    body: file,
    headers: { "Content-Type": file.type || "application/octet-stream" },
  });
  if (!put.ok) {
    throw new Error("Upload to storage failed");
  }
  await confirmUpload(file_id, file.size);
  return file_id;
}

export async function getDownloadUrl(
  fileId: string,
): Promise<{ download_url: string; filename: string }> {
  return apiJson(`/api/v1/files/${fileId}/download-url/`);
}
