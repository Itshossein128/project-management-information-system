import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/cash-flow`;

export type TxType = "in" | "out";

export const INFLOW_CATEGORIES = [
  { value: "ipc_receipt", label: "دریافت صورت وضعیت" },
  { value: "advance_receipt", label: "دریافت پیش‌پرداخت" },
  { value: "guarantee_receipt", label: "دریافت ضمانت‌نامه" },
  { value: "other_income", label: "سایر درآمدها" },
] as const;

export const OUTFLOW_CATEGORIES = [
  { value: "subcontractor_payment", label: "پرداخت پیمانکار" },
  { value: "supplier_payment", label: "پرداخت تأمین‌کننده" },
  { value: "salary", label: "حقوق و دستمزد" },
  { value: "equipment_rental", label: "اجاره ماشین‌آلات" },
  { value: "site_overhead", label: "سربار پروژه" },
  { value: "tax_payment", label: "پرداخت مالیات" },
  { value: "advance_payment", label: "پیش‌پرداخت" },
  { value: "guarantee_payment", label: "ضمانت‌نامه" },
  { value: "other_expense", label: "سایر هزینه‌ها" },
] as const;

export function categoryLabel(category: string, txType: TxType) {
  const list = txType === "in" ? INFLOW_CATEGORIES : OUTFLOW_CATEGORIES;
  return list.find((c) => c.value === category)?.label ?? category;
}

export interface CashTransactionRow {
  id: string;
  tx_date: string;
  tx_type: TxType;
  category: string;
  category_label: string;
  amount: string;
  amount_display: string;
  description: string;
  counterparty: string;
  document_ref: string;
  is_forecast: boolean;
  due_date: string | null;
  actual_date: string | null;
  source: "ipc" | "direct";
}

export interface CashFlowSummary {
  total_inflow: number;
  total_outflow: number;
  net_balance: number;
  by_category: Record<string, number>;
}

export interface CashFlowListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: CashTransactionRow[];
  summary: CashFlowSummary;
}

export interface MonthlyCashFlowRow {
  month: string;
  inflow: number;
  outflow: number;
  net: number;
  cumulative_balance: number;
}

export interface ForecastRow {
  month: string;
  expected_inflow: number;
  expected_outflow: number;
  confidence_pct: number | null;
  notes: string;
  actual_inflow: number | null;
  actual_outflow: number | null;
  actual_net: number | null;
}

export interface GapRow {
  month: string;
  expected_inflow: number;
  expected_outflow: number;
  net: number;
  cumulative_balance: number;
  gap_amount: number;
  is_cumulative_negative: boolean;
}

export interface ReceivablesSummary {
  receivables: { total_approved_unpaid: number; overdue: number } | null;
  payables: { total_approved_unpaid: number; overdue: number } | null;
  note?: string;
}

export function formatFaAmount(value: number | string | null | undefined): string {
  const n = Number(value ?? 0);
  if (Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("fa-IR").format(Math.round(n));
}

export function fetchCashFlowList(
  projectId: string,
  params: Record<string, string | undefined> = {},
) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v) qs.set(k, v);
  }
  const q = qs.toString();
  return apiJson<CashFlowListResponse>(`${base(projectId)}/${q ? `?${q}` : ""}`);
}

export function createCashTransaction(
  projectId: string,
  body: Record<string, unknown>,
) {
  return apiJson<CashTransactionRow>(`${base(projectId)}/transactions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateCashTransaction(
  projectId: string,
  id: string,
  body: Record<string, unknown>,
) {
  return apiJson<CashTransactionRow>(`${base(projectId)}/transactions/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteCashTransaction(projectId: string, id: string) {
  return apiJson<void>(`${base(projectId)}/transactions/${id}/`, { method: "DELETE" });
}

export function fetchMonthlyCashFlow(
  projectId: string,
  params: { date_from?: string; date_to?: string } = {},
) {
  const qs = new URLSearchParams();
  if (params.date_from) qs.set("date_from", params.date_from);
  if (params.date_to) qs.set("date_to", params.date_to);
  const q = qs.toString();
  return apiJson<{ results: MonthlyCashFlowRow[] }>(
    `${base(projectId)}/monthly/${q ? `?${q}` : ""}`,
  );
}

export function fetchForecast(projectId: string) {
  return apiJson<{ results: ForecastRow[] }>(`${base(projectId)}/forecast/`);
}

export function upsertForecast(
  projectId: string,
  month: string,
  body: Partial<Pick<ForecastRow, "expected_inflow" | "expected_outflow" | "confidence_pct" | "notes">>,
) {
  return apiJson<ForecastRow>(`${base(projectId)}/forecast/${month}/`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function fetchGapAnalysis(projectId: string) {
  return apiJson<{ results: GapRow[] }>(`${base(projectId)}/gap-analysis/`);
}

export function fetchReceivables(projectId: string) {
  return apiJson<ReceivablesSummary>(`${base(projectId)}/receivables/`);
}

export interface ProjectionMonth {
  month: string;
  projected_inflow: number;
  projected_outflow: number;
  net_need: number;
  inflow_status: "registered" | "unregistered";
  outflow_status: string;
}

export interface ProjectionResponse {
  series: "projected";
  months: ProjectionMonth[];
  actual_months: Array<{
    month: string;
    actual_inflow: number;
    actual_outflow: number;
    net: number;
  }>;
  manual_forecast_months: Array<{
    month: string;
    expected_inflow: number;
    expected_outflow: number;
    net: number;
  }>;
}

export interface SuggestedNeedResponse {
  period_start: string;
  period_end: string;
  due_commitments: number;
  essential_costs: number;
  certain_planned_receipts: number;
  suggested_net_need: number;
}

export interface PriorityScore {
  urgency: number;
  return_score: number;
  recovery_speed: number;
  risk: number;
  composite: number;
  notes: string;
}

export interface LiquidityCycle {
  id: string;
  name: string;
  period_start: string;
  period_end: string;
  available_liquidity: string;
  currency: string;
  status: string;
}

export interface ProposalResponse {
  id: string;
  lines: Array<{
    project_id: string;
    suggested_amount: number;
    rank: number;
    composite_snapshot: number;
    need_snapshot: number;
  }>;
  message: string | null;
  warnings: { incomplete_score_projects: string[] };
}

export interface PortfolioReport {
  projects: Array<{
    project_id: string;
    project_name: string;
    projected_inflow: number;
    projected_outflow: number;
    net_need: number;
    suggested_net_need: number;
    composite: number | null;
    inflow_status: string;
  }>;
  allocations: Array<{
    cycle_id: string;
    decision_id: string;
    project_id: string;
    amount: number;
    owner_id: string;
    rationale: string;
  }>;
  totals: {
    projected_inflow: number;
    projected_outflow: number;
    net_need: number;
    allocated: number;
  };
}

export function fetchProjection(projectId: string, from: string, to: string) {
  const qs = new URLSearchParams({ from, to });
  return apiJson<ProjectionResponse>(`${base(projectId)}/projection/?${qs}`);
}

export function fetchSuggestedNeed(projectId: string, from: string, to: string) {
  const qs = new URLSearchParams({ from, to });
  return apiJson<SuggestedNeedResponse>(`${base(projectId)}/suggested-need/?${qs}`);
}

export function fetchPriorityScore(projectId: string) {
  return apiJson<PriorityScore>(`${base(projectId)}/priority-score/`);
}

export function putPriorityScore(projectId: string, body: Omit<PriorityScore, "composite">) {
  return apiJson<PriorityScore>(`${base(projectId)}/priority-score/`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function createLiquidityCycle(body: {
  name: string;
  period_start: string;
  period_end: string;
  available_liquidity: number | string;
  currency?: string;
}) {
  return apiJson<LiquidityCycle>(`/v1/cash-flow/portfolio/cycles/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function listLiquidityCycles() {
  return apiJson<{ results: LiquidityCycle[] }>(`/v1/cash-flow/portfolio/cycles/`);
}

export function proposeAllocation(cycleId: string) {
  return apiJson<ProposalResponse>(`/v1/cash-flow/portfolio/cycles/${cycleId}/propose/`, {
    method: "POST",
  });
}

export function createAllocationDecision(
  cycleId: string,
  body: {
    owner_id: string;
    rationale: string;
    acknowledge_overlap?: boolean;
    lines: Array<{
      project_id: string;
      amount: number;
      period_start: string;
      period_end: string;
      schedule_impact?: string;
      cost_impact?: string;
    }>;
  },
) {
  return apiJson(`/v1/cash-flow/portfolio/cycles/${cycleId}/decisions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function saveAllocationSimulation(
  cycleId: string,
  body: { name: string; lines: Array<{ project_id: string; amount: number }> },
) {
  return apiJson<{ id: string; name: string }>(
    `/v1/cash-flow/portfolio/cycles/${cycleId}/simulations/`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function compareAllocationSimulation(cycleId: string, simId: string) {
  return apiJson<{
    diffs: Array<{
      project_id: string;
      simulation_amount: number;
      proposal_amount: number;
      diff: number;
    }>;
  }>(`/v1/cash-flow/portfolio/cycles/${cycleId}/simulations/${simId}/compare/`);
}

export function fetchPortfolioCashReport(from: string, to: string, cycleId?: string) {
  const qs = new URLSearchParams({ from, to });
  if (cycleId) qs.set("cycle_id", cycleId);
  return apiJson<PortfolioReport>(`/v1/cash-flow/portfolio/report/?${qs}`);
}

/** Format month ISO as YYYY-MM for forecast PUT */
export function monthIsoToKey(iso: string) {
  return iso.slice(0, 7);
}

/** Billions label for chart axis */
export function formatBillions(value: number) {
  const b = value / 1_000_000_000;
  if (b >= 1) return `${b.toFixed(1)}B`;
  const m = value / 1_000_000;
  if (m >= 1) return `${m.toFixed(0)}M`;
  return formatFaAmount(value);
}
