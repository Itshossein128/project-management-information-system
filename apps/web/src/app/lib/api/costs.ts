import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export type CostCategory =
  | "labor"
  | "material"
  | "equipment"
  | "subcontract"
  | "site_overhead"
  | "hq_overhead"
  | "transport"
  | "other";

export const COST_CATEGORIES: { value: CostCategory; label: string }[] = [
  { value: "labor", label: "نیروی کار" },
  { value: "material", label: "مصالح" },
  { value: "equipment", label: "ماشین‌آلات" },
  { value: "subcontract", label: "پیمانکاران جزء" },
  { value: "site_overhead", label: "سربار پروژه" },
  { value: "hq_overhead", label: "سربار مرکزی" },
  { value: "transport", label: "حمل‌ونقل" },
  { value: "other", label: "سایر" },
];

export function costCategoryLabel(cat: string) {
  return COST_CATEGORIES.find((c) => c.value === cat)?.label ?? cat;
}

export interface BudgetRow {
  id: string;
  wbs: string | null;
  activity: string | null;
  wbs_code: string | null;
  wbs_name: string | null;
  activity_code: string | null;
  activity_name: string | null;
  cost_category: CostCategory;
  budget_amount: number;
  budget_amount_display: string;
  notes: string;
}

export interface BudgetListResponse {
  results: BudgetRow[];
  summary: { total_bac: number; by_category: Record<string, number> };
  warning?: string;
}

export interface ActualCostRow {
  id: string;
  activity: string | null;
  wbs: string | null;
  wbs_code: string | null;
  activity_code: string | null;
  cost_date: string;
  cost_category: CostCategory;
  amount: number;
  amount_display: string;
  description: string;
  invoice_number: string;
  supplier: string | null;
  supplier_name: string | null;
  cost_type: string;
  confidence_level: string;
  allocation_method: string;
  cost_pool: string | null;
  daily_report: string | null;
  is_auto_created: boolean;
}

export interface ActualCostListResponse {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: ActualCostRow[];
  meta: { total_actual: number; by_category: Record<string, number> };
}

export interface VarianceRow {
  budget: number;
  actual: number;
  variance: number;
  consumption_pct: number | null;
  wbs_id?: string | null;
  wbs_code?: string | null;
  wbs_name?: string | null;
  activity_id?: string | null;
  activity_code?: string | null;
  activity_name?: string | null;
  cost_category?: string;
}

export interface VarianceResponse {
  group_by: string;
  as_of: string;
  results: VarianceRow[];
}

export interface CostSummary {
  total_budget: number;
  total_actual: number;
  total_committed: number;
  budget_consumption_pct: number | null;
  by_category: Record<string, { budget: number; actual: number }>;
  by_wbs: VarianceRow[];
  cost_trend: { month: string; actual: number; cumulative: number }[];
}

export interface CostPool {
  id: string;
  pool_name: string;
  cost_category: CostCategory;
  total_amount: number | null;
  total_amount_display: string;
  allocated_amount: number;
  remaining: number;
  status: string;
  data_source: string;
  confidence_level: string;
}

export interface Supplier {
  id: string;
  project: string | null;
  supplier_name: string;
  supplier_code: string;
  contact_person: string;
  phone: string;
  email: string;
  address: string;
}

export function fetchBudgets(
  projectId: string,
  params: { wbs_id?: string; activity_id?: string; cost_category?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.wbs_id) search.set("wbs_id", params.wbs_id);
  if (params.activity_id) search.set("activity_id", params.activity_id);
  if (params.cost_category) search.set("cost_category", params.cost_category);
  const qs = search.toString();
  return apiJson<BudgetListResponse>(`${base(projectId)}/budgets/${qs ? `?${qs}` : ""}`);
}

export function postBudgetsBulk(
  projectId: string,
  items: {
    wbs?: string | null;
    activity?: string | null;
    cost_category: CostCategory;
    budget_amount: number;
    notes?: string;
  }[],
) {
  return apiJson<{ saved: number; summary: BudgetListResponse["summary"]; warning?: string }>(
    `${base(projectId)}/budgets/bulk/`,
    { method: "POST", body: JSON.stringify(items) },
  );
}

export function fetchActualCosts(
  projectId: string,
  params: {
    activity_id?: string;
    wbs_id?: string;
    cost_category?: string;
    cost_type?: string;
    supplier_id?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
  } = {},
) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v != null && v !== "") search.set(k, String(v));
  }
  const qs = search.toString();
  return apiJson<ActualCostListResponse>(`${base(projectId)}/costs/${qs ? `?${qs}` : ""}`);
}

export function createActualCost(
  projectId: string,
  body: {
    activity?: string | null;
    wbs?: string | null;
    cost_date: string;
    cost_category: CostCategory;
    amount: number;
    description?: string;
    invoice_number?: string;
    supplier?: string | null;
    cost_type?: string;
    confidence_level?: string;
  },
) {
  return apiJson<ActualCostRow>(`${base(projectId)}/costs/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchVariance(
  projectId: string,
  params: { group_by?: "wbs" | "category" | "activity"; as_of?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.group_by) search.set("group_by", params.group_by);
  if (params.as_of) search.set("as_of", params.as_of);
  const qs = search.toString();
  return apiJson<VarianceResponse>(`${base(projectId)}/costs/variance/${qs ? `?${qs}` : ""}`);
}

export function fetchCostSummary(projectId: string, asOf?: string) {
  const qs = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  return apiJson<CostSummary>(`${base(projectId)}/costs/summary/${qs}`);
}

export function fetchCostPools(projectId: string) {
  return apiJson<CostPool[]>(`${base(projectId)}/cost-pools/`);
}

export function createCostPool(
  projectId: string,
  body: {
    pool_name: string;
    cost_category?: CostCategory;
    total_amount?: number;
    data_source?: string;
    confidence_level?: string;
  },
) {
  return apiJson<CostPool>(`${base(projectId)}/cost-pools/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function allocateCostPool(
  projectId: string,
  poolId: string,
  items: {
    activity_id: string;
    amount: number;
    allocation_method?: string;
    confidence_level?: string;
  }[],
) {
  return apiJson<CostPool>(`${base(projectId)}/cost-pools/${poolId}/allocate/`, {
    method: "POST",
    body: JSON.stringify(items),
  });
}

export function fetchSuppliers(projectId: string) {
  return apiJson<Supplier[]>(`${base(projectId)}/suppliers/`);
}

export function fetchGlobalSuppliers(q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiJson<Supplier[]>(`/v1/suppliers/${qs}`);
}

export const formatFaAmount = (n: number) =>
  new Intl.NumberFormat("fa-IR", { maximumFractionDigits: 0 }).format(n);

export function parseFaAmount(input: string): number {
  const normalized = input
    .replace(/[۰-۹]/g, (d) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(d)))
    .replace(/[,٬]/g, "")
    .trim();
  const n = Number(normalized);
  return Number.isFinite(n) ? n : 0;
}
