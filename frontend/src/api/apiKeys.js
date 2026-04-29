import { apiClient } from "./client";

export async function listApiKeys(limit = 200) {
  const { data } = await apiClient.get("/api-keys", {
    params: { limit },
  });
  return data;
}

export async function createApiKey(payload) {
  const { data } = await apiClient.post("/api-keys", {
    name: payload.name,
    scopes: payload.scopes || [],
    expires_in_days: payload.expiresInDays ?? null,
  });
  return data;
}

export async function revokeApiKey(apiKeyId) {
  const { data } = await apiClient.patch(`/api-keys/${apiKeyId}/revoke`);
  return data;
}