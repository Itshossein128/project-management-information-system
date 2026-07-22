import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface ProjectKpis {
  as_of: string;
  physical_progress: {
    planned: number;
    actual: number;
    variance: number;
    spi: number | null;
  };
  cost: {
    budget: string;
    actual_cost: string;
    earned_value: string;
    cost_variance: string;
    cpi: number | null;
    budget_consumption: number;
    eac: number | null;
  };
  cash: {
    total_received: string;
    total_paid_out: string;
    net_balance: string;
    receivables: string;
    payables_to_subs: string;
    has_cash_gap: boolean;
  };
  schedule: {
    critical_activities: number;
    behind_schedule: number;
    ahead_of_schedule: number;
  };
  alerts: {
    unacknowledged_total: number;
  };
  panel: {
    spi: number | null;
    cpi: number | null;
    physical_actual_pct: number | null;
    schedule_variance_pct: number | null;
    budget_consumption_pct: number | null;
    net_cash: number;
    has_cash_gap: boolean;
    open_alerts: number;
    critical_activities: number;
    behind_schedule: number;
    eac: number | null;
  };
}

export function fetchProjectKpis(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<ProjectKpis>(`${base(projectId)}/kpis/${qs ? `?${qs}` : ""}`);
}
