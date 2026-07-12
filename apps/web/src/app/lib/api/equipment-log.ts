import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

export interface EquipmentLog {
  id: string;
  log_date: string;
  equipment_name: string;
  shift: string;
  status: string;
  ownership_type: string;
  work_start: string | null;
  work_end: string | null;
  repair_hours: string;
  productive_hours: string | null;
  warning?: string;
}

export interface EquipmentSummaryRow {
  date: string;
  equipment_name: string;
  total_units: number;
  active: number;
  standby: number;
  broken: number;
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/equipment-log`;

export function fetchEquipmentLogs(projectId: string, params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<{ count: number; results: EquipmentLog[] }>(`${base(projectId)}/${qs ? `?${qs}` : ""}`);
}

export function fetchEquipmentSummary(projectId: string, date?: string) {
  const qs = date ? `?date=${encodeURIComponent(date)}` : "";
  return apiJson<EquipmentSummaryRow[]>(`${base(projectId)}/summary/${qs}`);
}

export function createEquipmentLog(projectId: string, body: Partial<EquipmentLog>) {
  return apiJson<EquipmentLog>(`${base(projectId)}/`, { method: "POST", body: JSON.stringify(body) });
}

export function deleteEquipmentLog(projectId: string, id: string) {
  return apiJson(`${base(projectId)}/${id}/`, { method: "DELETE" });
}
