import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

export type RiskEventType = "delay" | "barrier" | "risk" | "claim" | "change_order";
export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type RiskStatus = "open" | "in_progress" | "resolved";

export interface RiskEvent {
  id: string;
  event_date: string | null;
  event_type: RiskEventType;
  event_type_label?: string;
  description: string;
  category: string;
  probability: number | null;
  severity: RiskSeverity | "";
  severity_label?: string;
  status: RiskStatus;
  status_label?: string;
  time_impact_days: number | null;
  cost_impact: number | null;
  responsible_party: string;
  corrective_action: string;
  related_daily_report: string | null;
  related_correspondence: string | null;
}

export interface RiskMatrixResponse {
  total_open: number;
  matrix: {
    probability_bucket: string;
    cells: { severity: RiskSeverity; count: number }[];
  }[];
}

export interface PaginatedRiskEvents {
  count: number;
  results: RiskEvent[];
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/risk-events`;

export function fetchRiskEvents(
  projectId: string,
  params: Record<string, string | undefined> = {},
) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v) search.set(k, v);
  }
  const qs = search.toString();
  return apiJson<PaginatedRiskEvents>(`${base(projectId)}/${qs ? `?${qs}` : ""}`);
}

export function fetchRiskMatrix(projectId: string) {
  return apiJson<RiskMatrixResponse>(`${base(projectId)}/matrix/`);
}

export function createRiskEvent(projectId: string, body: Partial<RiskEvent>) {
  return apiJson<RiskEvent>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateRiskEvent(projectId: string, id: string, body: Partial<RiskEvent>) {
  return apiJson<RiskEvent>(`${base(projectId)}/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteRiskEvent(projectId: string, id: string) {
  return apiJson<void>(`${base(projectId)}/${id}/`, { method: "DELETE" });
}

export const EVENT_TYPE_LABELS: Record<RiskEventType, string> = {
  delay: "تأخیر",
  barrier: "مانع",
  risk: "ریسک",
  claim: "ادعا",
  change_order: "دستور تغییر",
};

export const SEVERITY_LABELS: Record<RiskSeverity, string> = {
  low: "کم",
  medium: "متوسط",
  high: "زیاد",
  critical: "بحرانی",
};
