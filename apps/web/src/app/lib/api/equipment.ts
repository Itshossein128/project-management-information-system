import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface EquipmentRegistryItem {
  id: string;
  equipment_code: string;
  equipment_name: string;
  equipment_type: string;
  ownership_type: string;
  plate_number: string;
  default_hourly_rate: number | null;
  is_active: boolean;
}

export interface EquipmentUtilizationRow {
  equipment_name: string;
  equipment_code: string;
  productive_hours: number;
  idle_hours: number;
  utilization_rate: number | null;
  total_cost: number;
  log_count: number;
  active_count: number;
  standby_count: number;
  broken_count: number;
}

export interface EquipmentUtilizationSummary {
  equipment_count: number;
  avg_utilization_rate: number | null;
  total_productive_hours: number;
  total_idle_hours: number;
  total_cost: number;
  active_logs: number;
  standby_logs: number;
  broken_logs: number;
}

export function fetchEquipmentRegistry(projectId: string, activeOnly = true) {
  const qs = activeOnly ? "?active_only=true" : "";
  return apiJson<EquipmentRegistryItem[] | { results: EquipmentRegistryItem[] }>(
    `${base(projectId)}/equipment/${qs}`,
  );
}

export function createEquipment(
  projectId: string,
  body: Partial<EquipmentRegistryItem> & { equipment_code: string; equipment_name: string },
) {
  return apiJson<EquipmentRegistryItem>(`${base(projectId)}/equipment/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateEquipment(projectId: string, id: string, body: Partial<EquipmentRegistryItem>) {
  return apiJson<EquipmentRegistryItem>(`${base(projectId)}/equipment/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function fetchEquipmentUtilization(
  projectId: string,
  params: { date_from?: string; date_to?: string; equipment_name?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  if (params.equipment_name) search.set("equipment_name", params.equipment_name);
  const qs = search.toString();
  return apiJson<EquipmentUtilizationRow[]>(
    `${base(projectId)}/equipment-utilization/${qs ? `?${qs}` : ""}`,
  );
}

export function fetchEquipmentUtilizationSummary(
  projectId: string,
  params: { date_from?: string; date_to?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.date_from) search.set("date_from", params.date_from);
  if (params.date_to) search.set("date_to", params.date_to);
  const qs = search.toString();
  return apiJson<EquipmentUtilizationSummary>(
    `${base(projectId)}/equipment-utilization/summary/${qs ? `?${qs}` : ""}`,
  );
}
