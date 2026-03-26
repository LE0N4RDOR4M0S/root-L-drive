import axios from "axios";

import { apiClient } from "./client";

function extractFilename(contentDisposition) {
  if (!contentDisposition) return "";

  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1]);
  }

  const plainMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
  return plainMatch?.[1] || "";
}

export async function listFiles(folderId = null) {
  const { data } = await apiClient.get("/files", {
    params: { folder_id: folderId },
  });
  return data;
}

export async function requestUploadUrl(filename, folderId, mimeType) {
  const { data } = await apiClient.post("/files/upload-url", {
    filename,
    folder_id: folderId,
    mime_type: mimeType,
  });
  return data;
}

export async function uploadToPresignedUrl(uploadUrl, file) {
  await axios.put(uploadUrl, file, {
    headers: {
      "Content-Type": file.type || "application/octet-stream",
    },
  });
}

export async function completeUpload({ name, folderId, minioKey, size, mimeType }) {
  const { data } = await apiClient.post("/files/complete", {
    name,
    folder_id: folderId,
    minio_key: minioKey,
    size,
    mime_type: mimeType,
  });
  return data;
}

export async function deleteFile(fileId) {
  await apiClient.delete(`/files/${fileId}`);
}

export async function requestDownloadUrl(fileId) {
  const { data } = await apiClient.get(`/files/${fileId}/download-url`);
  return data;
}

export async function downloadFile(fileId) {
  const response = await apiClient.get(`/files/${fileId}/download`, {
    responseType: "blob",
  });

  return {
    blob: response.data,
    filename: extractFilename(response.headers["content-disposition"]),
  };
}
