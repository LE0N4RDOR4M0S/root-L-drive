import { apiClient } from "./client";

export async function listFolders(parentId = null) {
  const { data } = await apiClient.get("/folders", {
    params: { parent_id: parentId },
  });
  return data;
}

export async function createFolder(name, parentId = null) {
  const { data } = await apiClient.post("/folders", {
    name,
    parent_id: parentId,
  });
  return data;
}

export async function deleteFolder(folderId) {
  await apiClient.delete(`/folders/${folderId}`);
}
