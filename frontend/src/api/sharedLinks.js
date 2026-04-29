import { apiClient } from "./client";

export async function listSharedLinks(limit = 200) {
  const { data } = await apiClient.get("/shares", {
    params: { limit },
  });
  return data;
}