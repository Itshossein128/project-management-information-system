import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

export type RiskEventType =
  | "delay"
  | "barrier"
  | "risk"
  | "issue"
  | "claim"
  | "change_order";
export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type RiskStatus =
  | "open"
  | "under_review"
  | "mitigated"
  | "closed"
  | "residual"
  | "in_progress"
  | "resolved";

export type ImpactDimension =
  | "schedule"
  | "cost"
  | "quality"
  | "safety"
  | "contract"
  | "liquidity";

export interface RiskEvent {
  id: string;
  event_date: string | null;
  event_type: RiskEventType;
  event_type_label?: string;
  description: string;
  cause?: string;
  consequence?: string;
  response?: string;
  category: string;
  probability: number | null;
  probability_level?: number | null;
  severity: RiskSeverity | "";
  severity_label?: string;
  impact_severity_level?: number | null;
  composite_score?: number | null;
  status: RiskStatus;
  status_label?: string;
  time_impact_days: number | null;
  cost_impact: number | null;
  responsible_party: string;
  owner?: string | null;
  corrective_action: string;
  due_date?: string | null;
  impact_on_schedule?: boolean;
  impact_on_cost?: boolean;
  impact_on_quality?: boolean;
  impact_on_safety?: boolean;
  impact_on_contract?: boolean;
  impact_on_liquidity?: boolean;
  activity?: string | null;
  cost_item?: string | null;
  contract?: string | null;
  related_decision_ref?: string;
  related_decision_note?: string;
  related_daily_report: string | null;
  related_correspondence: string | null;
  open_actions_count?: number;
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

export function createRiskEvent(
  projectId: string,
  body: Partial<RiskEvent> & { acknowledge_open_actions?: boolean },
) {
  return apiJson<RiskEvent>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateRiskEvent(
  projectId: string,
  id: string,
  body: Partial<RiskEvent> & { acknowledge_open_actions?: boolean },
) {
  return apiJson<RiskEvent>(`${base(projectId)}/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteRiskEvent(projectId: string, id: string) {
  return apiJson<void>(`${base(projectId)}/${id}/`, { method: "DELETE" });
}

export interface RiskAction {
  id: string;
  risk_event: string;
  description: string;
  due_date: string | null;
  owner: string | null;
  status: "open" | "done";
}

export function createRiskAction(
  projectId: string,
  body: Partial<RiskAction> & { risk_event: string; description: string },
) {
  return apiJson<RiskAction>(`/${PATHS.API_PROJECTS}/${projectId}/risk-actions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export const EVENT_TYPE_LABELS: Record<RiskEventType, string> = {
  delay: "تأخیر",
  barrier: "مانع",
  risk: "ریسک",
  issue: "مسئله",
  claim: "ادعا",
  change_order: "دستور تغییر",
};

export const SEVERITY_LABELS: Record<RiskSeverity, string> = {
  low: "کم",
  medium: "متوسط",
  high: "زیاد",
  critical: "بحرانی",
};

export const RISK_STATUS_LABELS: Record<string, string> = {
  open: "باز",
  under_review: "در بررسی",
  mitigated: "کاهش‌یافته",
  closed: "بسته",
  residual: "باقیمانده",
  in_progress: "در حال پیگیری",
  resolved: "رفع شده",
};
