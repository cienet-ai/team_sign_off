export interface User {
  id: number;
  username: string;
  email: string | null;
  display_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Application {
  id: number;
  title: string;
  reason: string;
  content: string;
  status: "pending" | "approved" | "rejected" | "voided";
  applicant_id: number;
  approver_id: number;
  reject_reason: string | null;
  previous_id: number | null;
  created_at: string;
  updated_at: string;
  applicant: User | null;
  approver: User | null;
}

export interface ApplicationCreate {
  title: string;
  reason: string;
  content: string;
  approver_id: number;
}

export interface ApplicationUpdate {
  title?: string;
  reason?: string;
  content?: string;
  approver_id?: number;
}

export interface AuditLog {
  id: number;
  application_id: number;
  action: string;
  performed_by_id: number;
  comment: string | null;
  created_at: string;
  performed_by: User | null;
  application: Application | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditFilter {
  status?: string;
  action?: string;
  start_date?: string;
  end_date?: string;
  applicant_id?: number;
  approver_id?: number;
  limit?: number;
  offset?: number;
}

export const STATUS_OPTIONS = [
  { label: "待审批", value: "pending" },
  { label: "已通过", value: "approved" },
  { label: "已驳回", value: "rejected" },
  { label: "已作废", value: "voided" },
];

export const ACTION_OPTIONS = [
  { label: "创建", value: "created" },
  { label: "提交", value: "submitted" },
  { label: "通过", value: "approved" },
  { label: "驳回", value: "rejected" },
  { label: "重新提交", value: "resubmitted" },
  { label: "作废", value: "voided" },
];

export const STATUS_TAG_MAP: Record<
  string,
  "info" | "success" | "danger" | "warning"
> = {
  pending: "warning",
  approved: "success",
  rejected: "danger",
  voided: "info",
};

export const STATUS_LABEL_MAP: Record<string, string> = {
  pending: "待审批",
  approved: "已通过",
  rejected: "已驳回",
  voided: "已作废",
};

export const ACTION_LABEL_MAP: Record<string, string> = {
  created: "创建",
  submitted: "提交",
  approved: "通过",
  rejected: "驳回",
  resubmitted: "修改重提交",
  voided: "作废",
};