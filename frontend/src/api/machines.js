import { apiClient } from "./client";

export async function listMachines(limit = 200) {
  const { data } = await apiClient.get("/machines", { params: { limit } });
  return data;
}

export async function createMachine(payload) {
  const { data } = await apiClient.post("/machines", payload);
  return data;
}

export async function downloadInstaller(machineId, payload) {
  const { data } = await apiClient.post(`/machines/${machineId}/installer`, payload);
  return data;
}

export async function revokeMachine(id) {
  const { data } = await apiClient.patch(`/machines/${id}/revoke`);
  return data;
}

export async function sendMachineCommand(id, command) {
  const { data } = await apiClient.post(`/machines/${id}/command`, command);
  return data;
}
