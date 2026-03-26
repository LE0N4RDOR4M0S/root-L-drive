import { apiClient } from "./client";

export async function login(email, password) {
  const { data } = await apiClient.post("/auth/login", { email, password });
  localStorage.setItem("auth_token", data.access_token);
  return data;
}

export async function register(email, password) {
  const { data } = await apiClient.post("/auth/register", { email, password });
  return data;
}
