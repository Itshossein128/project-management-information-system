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
  equipment_failure: { label: "خرابی تجهیزات", className: "bg-danger-100 text-danger-800" },
  payment_delay: { label: "تأخیر پرداخت", className: "bg-warning-100 text-warning-800" },
  design_change: { label: "تغییر طراحی", className: "bg-purple-100 text-purple-800" },
  weather: { label: "شرایط جوی", className: "bg-info-100 text-info-800" },
  subcontractor: { label: "پیمانکار", className: "bg-safety-100 text-safety-800" },
  safety: { label: "ایمنی", className: "bg-danger-200 text-danger-900" },
  other: { label: "سایر", className: "bg-neutral-100 text-neutral-800" },
};

export const STATUS_META: Record<BarrierStatus, { label: string; variant: "danger" | "warning" | "success" }> = {
  open: { label: "باز", variant: "danger" },
  in_progress: { label: "در حال پیگیری", variant: "warning" },
  resolved: { label: "رفع شده", variant: "success" },
};
