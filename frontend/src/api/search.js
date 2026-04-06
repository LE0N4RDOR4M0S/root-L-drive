import { apiClient } from "./client";

export async function semanticSearch(query, limit = 5) {
  const { data } = await apiClient.post("/search/semantic", {
    query,
    limit,
  });
  return data;
}
