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
