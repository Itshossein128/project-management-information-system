import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface AlertRule {
  id: string;
  alert_type: string;
  name: string;
  threshold_value: number | null;
  notify_roles: string;
  cooldown_hours: number;
  is_active: boolean;
  is_system: boolean;
}

export interface AlertLogEntry {
  id: string;
  alert_type: string;
  rule_name: string;
  fired_at: string;
  trigger_reference: string;
  message: string;
  notifications_sent: number;
  acknowledged_at: string | null;
}

export const ALERT_TYPE_LABELS: Record<string, string> = {
  ipc_payment_overdue: "تأخیر پرداخت IPC",
  guarantee_expiring: "انقضای ضمانت‌نامه",
  budget_overrun: "تجاوز از بودجه",
  cash_gap_detected: "کمبود نقدینگی",
  low_stock: "موجودی کم",
  activity_behind_schedule: "تأخیر فعالیت",
  missing_daily_report: "گزارش روزانه ارسال نشده",
  daily_report_not_approved: "گزارش تأیید نشده",
  subcontractor_at_risk: "ریسک پیمانکار",
  correspondence_response_due: "سررسید مکاتبه",
  baseline_not_set: "خط مبنا تعریف نشده",
  sync_conflict_unresolved: "تعارض همگام‌سازی",
};

export function fetchAlertRules(projectId: string) {
  return apiJson<{ results: AlertRule[] }>(`${base(projectId)}/alert-rules/`);
}

export function createAlertRule(projectId: string, body: Record<string, unknown>) {
  return apiJson<AlertRule>(`${base(projectId)}/alert-rules/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateAlertRule(projectId: string, ruleId: string, body: Record<string, unknown>) {
  return apiJson<AlertRule>(`${base(projectId)}/alert-rules/${ruleId}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteAlertRule(projectId: string, ruleId: string) {
  return apiJson<void>(`${base(projectId)}/alert-rules/${ruleId}/`, { method: "DELETE" });
}

export function fetchAlerts(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: AlertLogEntry[] }>(`${base(projectId)}/alerts/${qs ? `?${qs}` : ""}`);
}

export function fetchActiveAlertCounts(projectId: string) {
  return apiJson<{ counts: Record<string, number>; total: number }>(`${base(projectId)}/alerts/active/`);
}

export function acknowledgeAlert(projectId: string, logId: string) {
  return apiJson<AlertLogEntry>(`${base(projectId)}/alerts/${logId}/acknowledge/`, { method: "POST" });
}
