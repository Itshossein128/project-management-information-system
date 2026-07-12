import { apiJson } from "@/app/lib/api-client";
import type { ListResponse } from "@/app/lib/api-types";

const BASE = "/v1/notifications";

export type NotificationType =
  | "report_submitted"
  | "report_approved"
  | "report_rejected"
  | "generic";

export interface AppNotification {
  id: string;
  project: string | null;
  notification_type: NotificationType;
  notification_type_label: string;
  title: string;
  message: string;
  link: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export function fetchNotifications(params?: {
  is_read?: boolean;
  project?: string;
  page_size?: number;
}): Promise<ListResponse<AppNotification>> {
  const q = new URLSearchParams();
  if (params?.is_read !== undefined) q.set("is_read", String(params.is_read));
  if (params?.project) q.set("project", params.project);
  if (params?.page_size) q.set("page_size", String(params.page_size));
  const suffix = q.toString() ? `?${q.toString()}` : "";
  return apiJson<ListResponse<AppNotification>>(`${BASE}/${suffix}`);
}

export function fetchUnreadCount(): Promise<{ unread: number }> {
  return apiJson<{ unread: number }>(`${BASE}/unread-count/`);
}

export function markNotificationRead(id: string): Promise<AppNotification> {
  return apiJson<AppNotification>(`${BASE}/${id}/mark-read/`, { method: "POST" });
}

export function markAllNotificationsRead(): Promise<{ updated: number }> {
  return apiJson<{ updated: number }>(`${BASE}/mark-all-read/`, { method: "POST" });
}
