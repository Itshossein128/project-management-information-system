import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

export interface WBSNode {
  wbs_id: string;
  wbs_code: string;
  wbs_name: string;
  weight_physical: string | null;
  weight_financial: string | null;
  description?: string;
  depth: number;
  children: WBSNode[];
  warnings?: string[];
}

export interface WBSFlatNode {
  wbs_id: string;
  wbs_code: string;
  wbs_name: string;
  depth: number;
  weight_physical: string | null;
  weight_financial: string | null;
}

export function fetchWBSTree(projectId: string) {
  return apiJson<WBSNode[]>(`/${PATHS.API_PROJECTS}/${projectId}/wbs/`);
}

export function fetchWBSFlat(projectId: string) {
  return apiJson<WBSFlatNode[]>(`/${PATHS.API_PROJECTS}/${projectId}/wbs/flat/`);
}

export function createWBSNode(
  projectId: string,
  payload: {
    parent_id?: string | null;
    wbs_code: string;
    wbs_name: string;
    weight_physical?: number | null;
    weight_financial?: number | null;
    description?: string;
  },
) {
  return apiJson<WBSNode>(`/${PATHS.API_PROJECTS}/${projectId}/wbs/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateWBSNode(
  projectId: string,
  wbsId: string,
  payload: Partial<{
    wbs_name: string;
    weight_physical: number | null;
    weight_financial: number | null;
    description: string;
  }>,
) {
  return apiJson<WBSNode>(`/${PATHS.API_PROJECTS}/${projectId}/wbs/${wbsId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteWBSNode(projectId: string, wbsId: string) {
  return apiJson<void>(`/${PATHS.API_PROJECTS}/${projectId}/wbs/${wbsId}/`, {
    method: "DELETE",
  });
}
