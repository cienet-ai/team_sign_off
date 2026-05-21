import client from "./client";
import type { AuditLog, PaginatedResponse, AuditFilter } from "@/types";

export async function listAuditLogs(
  filter: AuditFilter,
): Promise<PaginatedResponse<AuditLog>> {
  const params: Record<string, unknown> = {};
  if (filter.status) params.status = filter.status;
  if (filter.action) params.action = filter.action;
  if (filter.start_date) params.start_date = filter.start_date;
  if (filter.end_date) params.end_date = filter.end_date;
  if (filter.applicant_id) params.applicant_id = filter.applicant_id;
  if (filter.approver_id) params.approver_id = filter.approver_id;
  if (filter.limit) params.limit = filter.limit;
  if (filter.offset) params.offset = filter.offset;

  const resp = await client.get("/audit", { params });
  return resp.data;
}