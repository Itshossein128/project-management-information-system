import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface EconomicSnapshot {
  id: string;
  snapshot_date: string;
  actual_cost: number;
  inflation_adj_cost: number;
  financing_cost: number;
  revenue_to_date: number;
  accounting_profit: number;
  real_profit: number;
  economic_profit: number;
  working_capital: number;
  avg_payment_delay_days: number;
  inflation_detail?: Array<{
    cost_category: string;
    nominal_cost: number;
    adjusted_cost: number;
    inflation_factor: number;
    difference: number;
  }>;
}

export interface SimulationResult {
  p10_profit: number;
  p50_profit: number;
  p90_profit: number;
  prob_of_loss: number;
  sensitivity_json: Array<{
    variable: string;
    low_profit: number;
    high_profit: number;
    impact: number;
  }>;
}

export function fetchEconomicSnapshot(projectId: string) {
  return apiJson<EconomicSnapshot>(`${base(projectId)}/economic/snapshot/`);
}

export function fetchEconomicHistory(projectId: string) {
  return apiJson<{ results: EconomicSnapshot[] }>(`${base(projectId)}/economic/history/`);
}

export function fetchFinancingCost(projectId: string) {
  return apiJson<{
    total_financing_cost: number;
    avg_payment_delay_days: number;
    details: Array<{
      ipc_number: number;
      net_amount: number;
      delay_days: number;
      financing_cost: number;
    }>;
  }>(`${base(projectId)}/economic/financing-cost/`);
}

export function runSimulation(projectId: string, body: Record<string, unknown>) {
  return apiJson<{ task_id: string }>(`${base(projectId)}/economic/simulate/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchSimulationStatus(projectId: string, taskId: string) {
  return apiJson<{ status: string; result?: Record<string, unknown> }>(
    `${base(projectId)}/economic/simulate/status/${taskId}/`,
  );
}

export function fetchLatestSimulation(projectId: string) {
  return apiJson<{ result: SimulationResult | null }>(`${base(projectId)}/economic/simulate/latest/`);
}

export function formatFaAmount(v: number) {
  return new Intl.NumberFormat("fa-IR").format(Math.round(v));
}
