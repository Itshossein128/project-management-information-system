import { apiFormData, apiJson } from "@/app/lib/api-client";

export type ProjectType =
  | "residential"
  | "road"
  | "commercial"
  | "industrial"
  | "epc"
  | "other";

export interface ProjectTemplateListItem {
  template_id: string;
  template_name: string;
  description: string;
  project_type: ProjectType;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  wbs_node_count: number;
}

export interface ProjectTemplateWBSNode {
  id: string;
  wbs_code: string;
  wbs_name: string;
  weight_physical: string | null;
  level: number;
  order: number;
  children: ProjectTemplateWBSNode[];
  activities: {
    activity_code: string;
    activity_name: string;
    unit: string;
    duration_days: number | null;
    weight: string | null;
  }[];
}

export interface ProjectTemplateDetail extends ProjectTemplateListItem {
  wbs_tree: ProjectTemplateWBSNode[];
  roles: string[];
}

export interface ApplyTemplateResult {
  wbs_nodes_created: number;
  activities_created: number;
  roles_added: number;
}

export const projectTypeLabels: Record<ProjectType, string> = {
  residential: "مسکونی",
  road: "راهسازی",
  commercial: "اداری/تجاری",
  industrial: "صنعتی",
  epc: "EPC",
  other: "سایر",
};

export function fetchProjectTemplates(params?: {
  project_type?: string;
  is_system?: boolean;
}) {
  const qs = new URLSearchParams();
  if (params?.project_type) qs.set("project_type", params.project_type);
  if (params?.is_system != null) qs.set("is_system", String(params.is_system));
  const query = qs.toString();
  return apiJson<ProjectTemplateListItem[]>(
    `/v1/project-templates/${query ? `?${query}` : ""}`,
  );
}

export function fetchProjectTemplate(templateId: string) {
  return apiJson<ProjectTemplateDetail>(`/v1/project-templates/${templateId}/`);
}

export function createProjectTemplate(payload: {
  template_name: string;
  description?: string;
  project_type: ProjectType;
}) {
  return apiJson<ProjectTemplateDetail>("/v1/project-templates/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteProjectTemplate(templateId: string) {
  return apiJson<void>(`/v1/project-templates/${templateId}/`, {
    method: "DELETE",
  });
}

export function applyProjectTemplate(
  templateId: string,
  projectId: string,
  force = false,
) {
  const qs = force ? "?force=true" : "";
  return apiJson<ApplyTemplateResult>(
    `/v1/project-templates/${templateId}/apply/${projectId}/${qs}`,
    { method: "POST" },
  );
}

export function saveProjectAsTemplate(
  projectId: string,
  payload: {
    template_name: string;
    description?: string;
    project_type: ProjectType;
  },
) {
  return apiJson<ProjectTemplateDetail>(
    `/v1/projects/${projectId}/save-as-template/`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}
