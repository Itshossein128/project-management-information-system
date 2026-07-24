import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";
import type { MaterialRequest } from "@/app/lib/api/materials";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/material-requests`;

export const REQUEST_STATUS_LABELS: Record<string, string> = {
  pending: "در انتظار تأیید",
  approved: "تأیید شده",
  ordered: "سفارش‌گذاری شده",
  delivered: "تحویل شده",
  cancelled: "لغو شده",
};

export interface PurchaseOrder {
  id: string;
  po_number: number;
  supplier: string;
  supplier_name: string;
  order_date: string;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  ordered_qty: number;
  unit_price: number | null;
  notes: string;
}

export type ProcurementRequest = MaterialRequest & {
  activity?: string | null;
  activity_name?: string;
  purchase_order?: PurchaseOrder | null;
};

export function fetchProcurementRequests(projectId: string, status?: string) {
  const qs = status ? `?status=${status}` : "";
  return apiJson<ProcurementRequest[]>(`${base(projectId)}${qs}`);
}

export function createProcurementRequest(
  projectId: string,
  body: {
    material: string;
    requested_qty: number;
    activity?: string;
    required_by_date?: string;
    notes?: string;
  },
) {
  return apiJson<ProcurementRequest>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function approveProcurementRequest(projectId: string, id: string) {
  return apiJson<ProcurementRequest>(`${base(projectId)}/${id}/approve/`, { method: "POST" });
}

export function placeProcurementOrder(
  projectId: string,
  id: string,
  body: { supplier: string; order_date?: string; expected_delivery_date?: string; unit_price?: number },
) {
  return apiJson<ProcurementRequest>(`${base(projectId)}/${id}/place-order/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function deliverProcurementRequest(
  projectId: string,
  id: string,
  body: { actual_delivery_date?: string; document_ref?: string } = {},
) {
  return apiJson<ProcurementRequest>(`${base(projectId)}/${id}/deliver/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function cancelProcurementRequest(projectId: string, id: string) {
  return apiJson<ProcurementRequest>(`${base(projectId)}/${id}/cancel/`, { method: "POST" });
}
