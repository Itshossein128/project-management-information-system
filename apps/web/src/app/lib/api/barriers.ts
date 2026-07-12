import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

export type BarrierCategory =
  | "equipment_failure"
  | "payment_delay"
  | "design_change"
  | "weather"
  | "subcontractor"
  | "safety"
  | "other";

export type BarrierStatus = "open" | "in_progress" | "resolved";

export interface BarrierLog {
  id: string;
  log_date: string;
  description: string;
  category: BarrierCategory | "";
  category_label: string;
  impact_on_schedule: boolean;
  impact_on_cost: boolean;
  status: BarrierStatus;
  status_label: string;
  resolved_date: string | null;
  corrective_action: string;
  responsible_user: string | null;
  responsible_user_name: string;
}

export interface PaginatedBarriers {
  count: number;
  results: BarrierLog[];
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/barriers`;

export function fetchBarriers(
  projectId: string,
  params: Record<string, string | boolean | number | undefined> = {},
) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") search.set(k, String(v));
  }
  const qs = search.toString();
  return apiJson<PaginatedBarriers>(`${base(projectId)}/${qs ? `?${qs}` : ""}`);
}

export function createBarrier(projectId: string, body: Partial<BarrierLog>) {
  return apiJson<BarrierLog>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateBarrier(projectId: string, id: string, body: Partial<BarrierLog>) {
  return apiJson<BarrierLog>(`${base(projectId)}/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteBarrier(projectId: string, id: string) {
  return apiJson<void>(`${base(projectId)}/${id}/`, { method: "DELETE" });
}

export const CATEGORY_META: Record<
  BarrierCategory,
  { label: string; className: string }
> = {
  equipment_failure: { label: "خرابی تجهیزات", className: "bg-red-100 text-red-800" },
  payment_delay: { label: "تأخیر پرداخت", className: "bg-amber-100 text-amber-800" },
  design_change: { label: "تغییر طراحی", className: "bg-purple-100 text-purple-800" },
  weather: { label: "شرایط جوی", className: "bg-blue-100 text-blue-800" },
  subcontractor: { label: "پیمانکار", className: "bg-orange-100 text-orange-800" },
  safety: { label: "ایمنی", className: "bg-red-200 text-red-900" },
  other: { label: "سایر", className: "bg-gray-100 text-gray-800" },
};

export const STATUS_META: Record<BarrierStatus, { label: string; variant: "danger" | "warning" | "success" }> = {
  open: { label: "باز", variant: "danger" },
  in_progress: { label: "در حال پیگیری", variant: "warning" },
  resolved: { label: "رفع شده", variant: "success" },
};
