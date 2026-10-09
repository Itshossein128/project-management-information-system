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
  version?: string | null;
  level?: string;
  wbs: string | null;
  activity: string | null;
  cbs?: string | null;
  contract?: string | null;
  wbs_code: string | null;
  wbs_name: string | null;
  activity_code: string | null;
  activity_name: string | null;
  cost_category: CostCategory;
  budget_amount: number;
  budget_amount_display: string;
  notes: string;
}

export type BudgetVersionKind = "initial" | "approved" | "revised" | "final_forecast";
export type BudgetVersionStatus = "draft" | "submitted" | "approved" | "rejected";

export interface BudgetVersion {
  id: string;
  kind: BudgetVersionKind;
  status: BudgetVersionStatus;
  version_number: number;
  name: string;
  currency: string;
  notes: string;
  is_control: boolean;
  line_count: number;
  total_amount: number;
  submitted_at?: string | null;
  approved_at?: string | null;
  rejection_reason?: string;
}

export type BudgetChangeRequestStatus =
  | "draft"
  | "submitted"
  | "approved"
  | "rejected"
  | "cancelled";

export interface BudgetChangeRequest {
  id: string;
  base_version: string;
  resulting_version: string | null;
  reason: string;
  amount_delta: string | number;
  project_impact: string;
  affected_lines: Record<string, unknown>[];
  status: BudgetChangeRequestStatus;
  requested_at: string;
  decision_notes: string;
}

export interface RemainingHeading {
  key: string;
  level: string;
  wbs: string | null;
  cbs: string | null;
  contract: string | null;
  cost_category: string;
  approved: number;
  committed: number;
  consumed: number;
  remaining: number;
  overrun: boolean;
  cbs_missing_warning: boolean;
}

export interface RemainingResponse {
  version_id: string | null;
  project_ceiling: number;
  headings: RemainingHeading[];
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
  params: {
    wbs_id?: string;
    activity_id?: string;
    cost_category?: string;
    version_id?: string;
  } = {},
) {
  const search = new URLSearchParams();
  if (params.wbs_id) search.set("wbs_id", params.wbs_id);
  if (params.activity_id) search.set("activity_id", params.activity_id);
  if (params.cost_category) search.set("cost_category", params.cost_category);
  if (params.version_id) search.set("version_id", params.version_id);
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
  versionId?: string | null,
) {
  const body =
    versionId != null
      ? { version_id: versionId, items }
      : items;
  return apiJson<{
    saved: number;
    version_id?: string;
    summary: BudgetListResponse["summary"];
    warning?: string;
  }>(`${base(projectId)}/budgets/bulk/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchBudgetVersions(projectId: string) {
  return apiJson<BudgetVersion[]>(`${base(projectId)}/budget-versions/`);
}

export function createBudgetVersion(
  projectId: string,
  body: { kind: "initial" | "revised" | "final_forecast"; name?: string; currency?: string },
) {
  return apiJson<BudgetVersion>(`${base(projectId)}/budget-versions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function submitBudgetVersion(projectId: string, versionId: string) {
  return apiJson<BudgetVersion>(`${base(projectId)}/budget-versions/${versionId}/submit/`, {
    method: "POST",
    body: "{}",
  });
}

export function approveBudgetVersion(
  projectId: string,
  versionId: string,
  promoteToControl = false,
) {
  return apiJson<BudgetVersion>(`${base(projectId)}/budget-versions/${versionId}/approve/`, {
    method: "POST",
    body: JSON.stringify({ promote_to_control: promoteToControl }),
  });
}

export function rejectBudgetVersion(projectId: string, versionId: string, reason = "") {
  return apiJson<BudgetVersion>(`${base(projectId)}/budget-versions/${versionId}/reject/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export type BudgetLineLevel =
  | "project"
  | "phase"
  | "contract"
  | "wbs"
  | "cbs"
  | "activity";

export function createBudgetVersionLine(
  projectId: string,
  versionId: string,
  body: {
    level: BudgetLineLevel;
    cost_category: CostCategory;
    budget_amount: number | string;
    wbs?: string | null;
    activity?: string | null;
    cbs?: string | null;
    contract?: string | null;
    period_start?: string | null;
    period_end?: string | null;
    notes?: string;
  },
) {
  return apiJson<BudgetRow>(`${base(projectId)}/budget-versions/${versionId}/lines/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface BudgetCompareResponse {
  left_id: string;
  right_id: string;
  fx_rate: number;
  diffs: {
    key: string;
    left_amount: number;
    right_amount: number;
    right_amount_converted: number;
    delta: number;
  }[];
}

export function compareBudgetVersions(
  projectId: string,
  left: string,
  right: string,
  fxRate?: string | number,
) {
  const search = new URLSearchParams({ left, right });
  if (fxRate != null && fxRate !== "") search.set("fx_rate", String(fxRate));
  return apiJson<BudgetCompareResponse>(
    `${base(projectId)}/budget-versions/compare/?${search.toString()}`,
  );
}

export function fetchBudgetChangeRequests(projectId: string) {
  return apiJson<BudgetChangeRequest[]>(`${base(projectId)}/budget-change-requests/`);
}

export function createBudgetChangeRequest(
  projectId: string,
  body: {
    reason: string;
    project_impact: string;
    amount_delta?: number | string;
    affected_lines: Record<string, unknown>[];
  },
) {
  return apiJson<BudgetChangeRequest>(`${base(projectId)}/budget-change-requests/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function submitBudgetChangeRequest(projectId: string, id: string) {
  return apiJson<BudgetChangeRequest>(
    `${base(projectId)}/budget-change-requests/${id}/submit/`,
    { method: "POST", body: "{}" },
  );
}

export function approveBudgetChangeRequest(projectId: string, id: string, notes = "") {
  return apiJson<BudgetChangeRequest>(
    `${base(projectId)}/budget-change-requests/${id}/approve/`,
    { method: "POST", body: JSON.stringify({ decision_notes: notes }) },
  );
}

export function rejectBudgetChangeRequest(projectId: string, id: string, notes = "") {
  return apiJson<BudgetChangeRequest>(
    `${base(projectId)}/budget-change-requests/${id}/reject/`,
    { method: "POST", body: JSON.stringify({ decision_notes: notes }) },
  );
}

export function fetchBudgetRemaining(projectId: string, versionId?: string) {
  const qs = versionId ? `?version_id=${versionId}` : "";
  return apiJson<RemainingResponse>(`${base(projectId)}/budgets/remaining/${qs}`);
}

export function postBudgetTransfer(
  projectId: string,
  body: { from_line_id: string; to_line_id: string; amount: number | string; note?: string },
) {
  return apiJson<{ transfer: { id: string }; from_line: BudgetRow; to_line: BudgetRow }>(
    `${base(projectId)}/budgets/transfers/`,
    { method: "POST", body: JSON.stringify(body) },
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
    corrective?: boolean;
    correction_reason?: string;
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

export async function fetchCostPools(projectId: string) {
  const data = await apiJson<CostPool[] | { results: CostPool[] }>(
    `${base(projectId)}/cost-pools/`,
  );
  return Array.isArray(data) ? data : (data.results ?? []);
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

export type AutoAllocateMethod = "by_budget_weight" | "by_quantity" | "by_hours";

export const AUTO_ALLOCATE_METHODS: { value: AutoAllocateMethod; label: string }[] = [
  { value: "by_budget_weight", label: "بر اساس وزن بودجه" },
  { value: "by_quantity", label: "بر اساس مقدار" },
  { value: "by_hours", label: "بر اساس ساعت" },
];

export function autoAllocateCostPool(
  projectId: string,
  poolId: string,
  body: { method?: AutoAllocateMethod; activity_ids?: string[] } = {},
) {
  return apiJson<{
    pool: CostPool;
    allocations: { activity_id: string; amount: number; allocation_method?: string }[];
  }>(`${base(projectId)}/cost-pools/${poolId}/auto-allocate/`, {
    method: "POST",
    body: JSON.stringify({
      method: body.method ?? "by_budget_weight",
      ...(body.activity_ids?.length ? { activity_ids: body.activity_ids } : {}),
    }),
  });
}

export async function fetchSuppliers(projectId: string) {
  const data = await apiJson<Supplier[] | { results: Supplier[] }>(
    `${base(projectId)}/suppliers/`,
  );
  return Array.isArray(data) ? data : (data.results ?? []);
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
