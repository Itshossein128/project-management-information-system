import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

export interface LaborCampRecord {
  id: string;
  report_date: string;
  connex_number: string;
  subcontractor_name: string;
  total_residents: number;
  present_count: number;
  on_leave_count: number;
  capacity: number;
  empty_capacity: number;
  warning?: string;
}

export interface LaborCampGroup {
  date: string;
  records: LaborCampRecord[];
  totals: {
    total_residents: number;
    present: number;
    on_leave: number;
    capacity: number;
    empty: number;
  };
}

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}/labor-camp`;

export function fetchLaborCampGroups(projectId: string) {
  return apiJson<LaborCampGroup[]>(`${base(projectId)}/?grouped=true`);
}

export function createLaborCampBatch(projectId: string, records: Partial<LaborCampRecord>[]) {
  return apiJson(`${base(projectId)}/`, { method: "POST", body: JSON.stringify(records) });
}

export function deleteLaborCamp(projectId: string, id: string) {
  return apiJson(`${base(projectId)}/${id}/`, { method: "DELETE" });
}
