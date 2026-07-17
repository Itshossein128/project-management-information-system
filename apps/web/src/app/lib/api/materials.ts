import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface MaterialBalanceRow {
  material_id: string;
  material_code: string;
  material_name: string;
  unit: string;
  discipline: string;
  location: string;
  block_type: string;
  estimated_total_qty: number | null;
  total_requested: number;
  total_received: number;
  total_issued: number;
  current_balance: number;
  min_stock_level: number | null;
  is_low_stock: boolean;
  last_transaction_date: string | null;
}

export interface Material {
  id: string;
  material_code: string;
  material_name: string;
  unit: string;
  unit_name: string;
  category: string;
  discipline: string;
  location: string;
  block_type: string;
  estimated_total_qty: number | null;
  qty_per_block: number | null;
  min_stock_level: number | null;
}

export interface MaterialRequest {
  id: string;
  material: string;
  material_name: string;
  request_number: number;
  requested_qty: number;
  unit: string;
  request_date: string | null;
  required_by_date: string | null;
  status: string;
  notes: string;
}

export interface InventoryTransaction {
  id: string;
  material: string;
  material_name: string;
  tx_date: string;
  tx_type: string;
  quantity: number;
  unit_cost: number | null;
  block_ref: string;
  document_ref: string;
  supplier: string | null;
  activity: string | null;
  daily_report: string | null;
  notes: string;
}

export function fetchMaterialBalance(
  projectId: string,
  params: {
    discipline?: string;
    location?: string;
    block_type?: string;
    low_stock?: boolean;
  } = {},
) {
  const search = new URLSearchParams();
  if (params.discipline) search.set("discipline", params.discipline);
  if (params.location) search.set("location", params.location);
  if (params.block_type) search.set("block_type", params.block_type);
  if (params.low_stock) search.set("low_stock", "true");
  const qs = search.toString();
  return apiJson<MaterialBalanceRow[]>(
    `${base(projectId)}/material-balance/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchMaterialBalanceDetail(projectId: string, materialId: string) {
  return apiJson<
    MaterialBalanceRow & { requests: MaterialRequest[]; transactions: InventoryTransaction[] }
  >(`${base(projectId)}/material-balance/${materialId}/`);
}

export function fetchMaterials(projectId: string) {
  return apiJson<Material[]>(`${base(projectId)}/materials/`);
}

export function fetchMaterialRequests(projectId: string) {
  return apiJson<MaterialRequest[]>(`${base(projectId)}/material-requests/`);
}

export function createMaterialRequest(
  projectId: string,
  body: {
    material: string;
    requested_qty: number;
    unit?: string;
    request_date?: string;
    required_by_date?: string;
    status?: string;
    notes?: string;
  },
) {
  return apiJson<MaterialRequest>(`${base(projectId)}/material-requests/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchInventoryTransactions(
  projectId: string,
  params: { material?: string; page?: number } = {},
) {
  const search = new URLSearchParams();
  if (params.material) search.set("material", params.material);
  if (params.page) search.set("page", String(params.page));
  const qs = search.toString();
  return apiJson<InventoryTransaction[] | { results: InventoryTransaction[] }>(
    `${base(projectId)}/inventory-transactions/${qs ? `?${qs}` : ""}`,
  );
}

export function createInventoryTransaction(
  projectId: string,
  body: {
    material: string;
    tx_date: string;
    tx_type: string;
    quantity: number;
    unit_cost?: number;
    block_ref?: string;
    document_ref?: string;
    supplier?: string;
    activity?: string;
    notes?: string;
  },
) {
  return apiJson<InventoryTransaction>(`${base(projectId)}/inventory-transactions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface MaterialConsumptionRow {
  material_id: string;
  material_code: string;
  material_name: string;
  estimated_total_qty: number | null;
  total_received: number;
  total_issued: number;
  total_waste: number;
  consumption_pct: number | null;
  waste_pct: number | null;
}

export interface RunningBalancePoint {
  date: string;
  transaction_type: string;
  qty: number;
  running_balance: number;
}

export function fetchMaterialConsumption(
  projectId: string,
  params: { material_id?: string; activity_id?: string; date_from?: string; date_to?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.material_id) search.set("material_id", params.material_id);
  if (params.activity_id) search.set("activity_id", params.activity_id);
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  const qs = search.toString();
  return apiJson<{ materials: MaterialConsumptionRow[]; activities: unknown[] }>(
    `${base(projectId)}/material-balance/consumption/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchRunningBalance(projectId: string, materialId: string) {
  return apiJson<RunningBalancePoint[]>(
    `${base(projectId)}/inventory-transactions/balance/?material_id=${materialId}`,
  );
}
