import client from "./client";
import type {
  Application,
  ApplicationCreate,
  ApplicationUpdate,
  PaginatedResponse,
} from "@/types";

export async function createApplication(
  data: ApplicationCreate,
): Promise<Application> {
  const resp = await client.post("/applications", data);
  return resp.data;
}

export async function listMyApplications(params: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<PaginatedResponse<Application>> {
  const resp = await client.get("/applications", { params });
  return resp.data;
}

export async function listPendingApprovals(params: {
  limit?: number;
  offset?: number;
}): Promise<PaginatedResponse<Application>> {
  const resp = await client.get("/applications/pending", { params });
  return resp.data;
}

export async function getApplication(id: number): Promise<Application> {
  const resp = await client.get(`/applications/${id}`);
  return resp.data;
}

export async function updateApplication(
  id: number,
  data: ApplicationUpdate,
): Promise<Application> {
  const resp = await client.put(`/applications/${id}`, data);
  return resp.data;
}

export async function approveApplication(id: number): Promise<Application> {
  const resp = await client.post(`/applications/${id}/approve`);
  return resp.data;
}

export async function rejectApplication(
  id: number,
  reason: string,
): Promise<Application> {
  const resp = await client.post(`/applications/${id}/reject`, { reason });
  return resp.data;
}

export async function voidApplication(id: number): Promise<Application> {
  const resp = await client.post(`/applications/${id}/void`);
  return resp.data;
}