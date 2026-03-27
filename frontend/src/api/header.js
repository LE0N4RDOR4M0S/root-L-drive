import { apiClient } from "./client";

export async function searchWorkspace(query, limit = 8) {
  const { data } = await apiClient.get("/search", {
    params: { query, limit },
  });
  return data;
}

export async function listNotifications(limit = 12) {
  const { data } = await apiClient.get("/notifications", {
    params: { limit },
  });
  return data;
}

export async function markNotificationAsRead(notificationId) {
  const { data } = await apiClient.patch(`/notifications/${notificationId}/read`);
  return data;
}

export async function markAllNotificationsAsRead() {
  const { data } = await apiClient.patch("/notifications/read-all");
  return data;
}

export async function getMyProfile() {
  const { data } = await apiClient.get("/profile/me");
  return data;
}

export async function updateMyProfile(payload) {
  const { data } = await apiClient.patch("/profile/me", payload);
  return data;
}
