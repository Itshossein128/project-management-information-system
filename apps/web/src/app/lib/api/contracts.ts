import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface ContractRow {
  id: string;
  contract_number: string;
  contract_type: string;
  counterparty: string;
  original_amount: number | null;
  adjusted_amount: number | null;
  effective_amount: number;
  status: string;
  total_ipc_count: number;
  paid_ipc_count: number;
  total_billed: number;
  total_paid: number;
  guarantee_expiry_alert: boolean;
}

export interface ContractDetail extends ContractRow {
  start_date: string | null;
  finish_date: string | null;
  advance_payment_pct: number;
  retention_pct: number;
  insurance_pct: number;
  tax_pct: number;
  performance_guarantee_amount: number | null;
  performance_guarantee_expiry: string | null;
  advance_guarantee_amount: number | null;
  advance_guarantee_expiry: string | null;
  file_url: string;
  notes: string;
  items: ContractItemRow[];
  change_orders: ChangeOrderRow[];
}

export interface ContractItemRow {
  id: string;
  activity: string | null;
  boq_code: string;
  description: string;
  unit: string | null;
  unit_name: string;
  unit_price: number;
  quantity: number;
  total_amount: number;
}

export interface ChangeOrderRow {
  id: string;
  change_number: number;
  description: string;
  amount_change: number;
  status: string;
}

export interface IPCRow {
  id: string;
  ipc_number: number;
  contract: string;
  contract_number: string;
  period_start: string | null;
  period_end: string | null;
  gross_amount: number;
  net_amount: number | null;
  status: string;
  days_overdue: number | null;
}

export interface IPCDetail extends IPCRow {
  items: Array<{
    id: string;
    description: string;
    unit: string;
    unit_price: number;
    qty_previous: number;
    qty_current: number;
    qty_cumulative: number;
    amount_current: number;
    amount_cumulative: number;
  }>;
  deductions: Array<{ id: string; deduction_type: string; amount: number; description: string }>;
  deductions_total: number;
  net_amount_computed: number;
  notes: string;
  rejection_reason: string;
}

export const CONTRACT_TYPE_LABELS: Record<string, string> = {
  main: "اصلی",
  subcontract: "پیمانکار فرعی",
  purchase: "خرید",
  equipment_rental: "اجاره ماشین‌آلات",
};

export const IPC_STATUS_LABELS: Record<string, string> = {
  draft: "پیش‌نویس",
  submitted: "ارسال‌شده",
  under_review: "در حال بررسی",
  approved: "تأییدشده",
  paid: "پرداخت‌شده",
};

export function fetchContracts(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: ContractRow[] }>(`${base(projectId)}/contracts/${qs ? `?${qs}` : ""}`);
}

export function fetchContract(projectId: string, id: string) {
  return apiJson<ContractDetail>(`${base(projectId)}/contracts/${id}/`);
}

export function createContract(projectId: string, body: Record<string, unknown>) {
  return apiJson<ContractDetail>(`${base(projectId)}/contracts/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateContract(projectId: string, id: string, body: Record<string, unknown>) {
  return apiJson<ContractDetail>(`${base(projectId)}/contracts/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function bulkContractItems(projectId: string, contractId: string, items: unknown[]) {
  return apiJson<ContractItemRow[]>(`${base(projectId)}/contracts/${contractId}/items/`, {
    method: "POST",
    body: JSON.stringify(items),
  });
}

export function fetchIPCs(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ results: IPCRow[] }>(`${base(projectId)}/ipcs/${qs ? `?${qs}` : ""}`);
}

export function fetchIPC(projectId: string, id: string) {
  return apiJson<IPCDetail>(`${base(projectId)}/ipcs/${id}/`);
}

export function createIPC(projectId: string, body: Record<string, unknown>) {
  return apiJson<IPCDetail>(`${base(projectId)}/ipcs/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function populateIPC(projectId: string, id: string) {
  return apiJson<IPCDetail>(`${base(projectId)}/ipcs/${id}/populate/`, { method: "POST" });
}

export function submitIPC(projectId: string, id: string) {
  return apiJson<IPCDetail>(`${base(projectId)}/ipcs/${id}/submit/`, { method: "POST" });
}

export function approveIPC(projectId: string, id: string) {
  return apiJson<IPCDetail>(`${base(projectId)}/ipcs/${id}/approve/`, { method: "POST" });
}

export function payIPC(projectId: string, id: string) {
  return apiJson<IPCDetail>(`${base(projectId)}/ipcs/${id}/pay/`, { method: "POST" });
}

export function formatFaAmount(value: number | null | undefined) {
  return new Intl.NumberFormat("fa-IR").format(Math.round(Number(value ?? 0)));
}
