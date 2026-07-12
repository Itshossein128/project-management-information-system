import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import type { ListResponse } from "@/app/lib/api-types";

export interface ProjectListItem {
  project_id: string;
  project_code: string;
  project_name: string;
  employer: string;
  status: string;
  start_date: string | null;
  planned_finish_date: string | null;
  contract_amount: string | null;
  member_count: number;
}

export interface ProjectDetail extends ProjectListItem {
  contractor: string;
  consultant: string;
  project_manager: string | null;
  location: string;
  contract_type: string;
  cut_off_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  project_code: string;
  project_name: string;
  employer: string;
  contractor?: string;
  consultant?: string;
  contract_type?: string;
  location?: string;
  start_date: string;
  planned_finish_date?: string;
  contract_amount?: string;
}

export function fetchProjects() {
  return apiJson<ListResponse<ProjectListItem>>(`/${PATHS.API_PROJECTS}/`);
}

export function fetchProject(projectId: string) {
  return apiJson<ProjectDetail>(`/${PATHS.API_PROJECTS}/${projectId}/`);
}

export function createProject(payload: CreateProjectPayload) {
  return apiJson<ProjectDetail>(`/${PATHS.API_PROJECTS}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProject(projectId: string, payload: Partial<CreateProjectPayload>) {
  return apiJson<ProjectDetail>(`/${PATHS.API_PROJECTS}/${projectId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
