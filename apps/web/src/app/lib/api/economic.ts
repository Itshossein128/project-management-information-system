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
  p10_profit?: number;
  p50_profit?: number;
  p90_profit?: number;
  p10?: number;
  p50?: number;
  p90?: number;
  prob_of_loss: number;
  max_working_capital?: number;
  sensitivity_json?: SensitivityRow[];
}

export interface SensitivityRow {
  variable: string;
  low_profit: number;
  high_profit: number;
  impact: number;
}

export interface EconomicForecast {
  as_of_date: string;
  bac: number;
  ev: number;
  pv: number;
  ac: number;
  sv: number;
  cv: number;
  spi: number | null;
  cpi: number | null;
  eac_nominal: number | null;
  eac_inflation_adjusted: number | null;
  etc_to_complete: number | null;
  vac: number | null;
  inflation_factor: number;
}

export interface InflationMapping {
  id: string;
  cost_category: string;
  index_name: string;
  weight: number;
  project: string | null;
  is_global: boolean;
}

export function simPercentile(sim: SimulationResult | Record<string, unknown> | null | undefined, key: "p10" | "p50" | "p90") {
  if (!sim) return 0;
  const profitKey = `${key}_profit` as const;
  const v = (sim as Record<string, unknown>)[profitKey] ?? (sim as Record<string, unknown>)[key];
  return Number(v ?? 0);
}

export function fetchEconomicSnapshot(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  return apiJson<EconomicSnapshot>(`${base(projectId)}/economic/snapshot/${qs}`);
}

export function fetchEconomicHistory(projectId: string) {
  return apiJson<{ results: EconomicSnapshot[] }>(`${base(projectId)}/economic/history/`);
}

export function fetchEconomicForecast(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  return apiJson<EconomicForecast>(`${base(projectId)}/economic/forecast/${qs}`);
}

export function fetchWorkingCapital(projectId: string) {
  return apiJson<{
    points: Array<{
      month: string;
      cumulative_cost: number;
      cumulative_payment: number;
      working_capital: number;
    }>;
    peak_working_capital: number;
  }>(`${base(projectId)}/economic/working-capital/`);
}

export function fetchCashFlowReal(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  return apiJson<{
    as_of_date: string;
    points: Array<{
      month: string;
      nominal_outflow: number;
      real_outflow: number;
      inflow: number;
      net_nominal: number;
      net_real: number;
    }>;
  }>(`${base(projectId)}/economic/cash-flow-real/${qs}`);
}

export function fetchFinancingCost(projectId: string) {
  return apiJson<{
    total_financing_cost: number;
    avg_payment_delay_days: number;
    annual_financing_rate?: number;
    details: Array<{
      ipc_number: number;
      net_amount: number;
      delay_days: number;
      financing_cost: number;
    }>;
  }>(`${base(projectId)}/economic/financing-cost/`);
}

export function fetchInflationMappings(projectId: string) {
  return apiJson<{ results: InflationMapping[] }>(`${base(projectId)}/economic/inflation-mappings/`);
}

export function createInflationMapping(projectId: string, body: Record<string, unknown>) {
  return apiJson<InflationMapping>(`${base(projectId)}/economic/inflation-mappings/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function deleteInflationMapping(projectId: string, id: string) {
  return apiJson<void>(`${base(projectId)}/economic/inflation-mappings/${id}/`, { method: "DELETE" });
}

export function updateInflationMapping(
  projectId: string,
  id: string,
  body: Partial<{ cost_category: string; index_name: string; weight: number }>,
) {
  return apiJson<InflationMapping>(`${base(projectId)}/economic/inflation-mappings/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function fetchPaymentDelay(projectId: string) {
  return apiJson<{
    total_financing_cost: number;
    avg_payment_delay_days: number;
    annual_financing_rate: number;
    details: Array<{
      ipc_number: number;
      net_amount: number;
      delay_days: number;
      financing_cost: number;
    }>;
  }>(`${base(projectId)}/economic/payment-delay/`);
}

export function fetchSensitivity(projectId: string) {
  return apiJson<{ sensitivity: SensitivityRow[] }>(`${base(projectId)}/economic/sensitivity/`);
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

export function profitColor(v: number) {
  return v >= 0 ? "text-emerald-600" : "text-red-600";
}
