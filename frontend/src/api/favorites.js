import { apiClient } from "./client";

export async function listFavorites(limit = 200) {
  const { data } = await apiClient.get("/favorites", {
    params: { limit },
  });
  return data;
}

export async function setFileFavorite(fileId, isFavorite) {
  const { data } = await apiClient.patch(`/favorites/files/${fileId}`, {
    is_favorite: isFavorite,
  });
  return data;
}

export async function setFolderFavorite(folderId, isFavorite) {
  const { data } = await apiClient.patch(`/favorites/folders/${folderId}`, {
    is_favorite: isFavorite,
  });
  return data;
}