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

export async function uploadFileViaBackend(file, folderId = null, onProgress) {
  const formData = new FormData();
  formData.append("file", file);
  if (folderId) {
    formData.append("folder_id", folderId);
  }

  const { data } = await apiClient.post("/files/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (event) => {
      if (typeof onProgress === "function") {
        onProgress(event);
      }
    },
  });

  return data;
}

export async function uploadToPresignedUrl(uploadUrl, file, onProgress) {
  await axios.put(uploadUrl, file, {
    headers: {
      "Content-Type": file.type || "application/octet-stream",
    },
    onUploadProgress: (event) => {
      if (typeof onProgress === "function") {
        onProgress(event);
      }
    },
  });
}

export async function completeUpload({
  name,
  folderId,
  minioKey,
  size,
  mimeType,
}) {
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

export async function listTrashFiles(limit = 200) {
  const { data } = await apiClient.get("/files/trash", {
    params: { limit },
  });
  return data;
}

export async function restoreFile(fileId) {
  await apiClient.patch(`/files/${fileId}/restore`);
}

export async function hardDeleteFile(fileId) {
  await apiClient.delete(`/files/${fileId}/hard`);
}

export async function createFileShareLink(fileId, payload = {}) {
  const { data } = await apiClient.post(`/shares/files/${fileId}`, {
    expires_in_days: payload.expiresInDays ?? null,
    password: payload.password || null,
  });
  return data;
}

export async function getSharedFileInfo(token) {
  const { data } = await apiClient.get(`/public/shares/${token}`);
  return data;
}

export async function downloadSharedFile(token, password = null) {
  const response = await apiClient.post(
    `/public/shares/${token}/download`,
    { password },
    { responseType: "blob" }
  );

  return {
    blob: response.data,
    filename: extractFilename(response.headers["content-disposition"]),
  };
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
