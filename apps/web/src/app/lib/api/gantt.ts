import { PATHS } from "@/app/routeVars";
import { apiBlob, apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface GanttTask {
  id: string;
  name: string;
  start: string | null;
  end: string | null;
  progress: number;
  dependencies: string;
  wbs_code: string;
  is_critical: boolean;
  baseline_start: string | null;
  baseline_end: string | null;
  status: string;
  responsible: string;
  activity_id: string;
}

export interface GanttBaseline {
  id: string;
  name: string;
  is_current: boolean;
}

export interface GanttData {
  tasks: GanttTask[];
  baseline_name: string;
  baselines?: GanttBaseline[];
  project_start: string | null;
  project_end: string | null;
}

export function fetchGantt(projectId: string, baselineId?: string) {
  const qs = baselineId ? `?baseline_id=${baselineId}` : "";
  return apiJson<GanttData>(`${base(projectId)}/gantt/${qs}`);
}

export function downloadGanttPdf(projectId: string, baselineId?: string) {
  const qs = baselineId ? `?baseline_id=${baselineId}` : "";
  return apiBlob(`${base(projectId)}/gantt/pdf/${qs}`);
}
