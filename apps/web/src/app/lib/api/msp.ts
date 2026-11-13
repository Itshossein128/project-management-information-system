import { apiFormData, apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import {
  isMspFamilyFile,
  isP6File,
  isScheduleImportFile,
} from "@/app/lib/api/msp-file-utils";

export { isMspFamilyFile, isP6File, isScheduleImportFile };

export interface MspPreviewWBSNode {
  wbs_code: string;
  wbs_name: string;
  depth: number;
  is_summary: boolean;
  activities: { activity_code: string; activity_name: string; duration_days: number | null }[];
  children: MspPreviewWBSNode[];
}

export interface ImportCounts {
  created_packages: number;
  created_activities: number;
  created_links: number;
  omitted_count: number;
  warned_count: number;
  rows_read: number;
  relationships_kept: number;
  duplicate_count: number;
  rows_omitted: number;
}

export interface ReplacementProjection {
  blocked: string | null;
  wbs_nodes_removed: number;
  activities_removed: number;
  relations_removed: number;
}

export interface MspPreviewResult {
  wbs_tree: MspPreviewWBSNode[];
  recognized_kind?: "mpp" | "xml" | "xer";
  activities: {
    activity_code: string;
    activity_name: string;
    outline_number: string;
    duration_days: number | null;
  }[];
  warnings: string[];
  warning_items?: { code: string; row: string }[];
  blocking?: { code: string; row: string }[];
  counts?: ImportCounts;
  counts_if_replaced?: ImportCounts;
  replacement?: ReplacementProjection;
}

export interface MspImportStartResult {
  task_id: string;
  status: string;
}

export type MspImportJobStatus = "pending" | "running" | "done" | "failed" | "queued";

export interface MspImportStatusResult {
  status: MspImportJobStatus;
  progress_pct: number;
  result?: {
    wbs_nodes_created: number;
    activities_created: number;
    relations_created: number;
    relationships_kept?: number;
    rows_read?: number;
    duplicate_count?: number;
    rows_omitted?: number;
    wbs_nodes_removed?: number;
    activities_removed?: number;
    relations_removed?: number;
    warnings: string[];
    warning_items?: { code: string; row: string }[];
    nothing_changed?: boolean;
  };
  error?: string;
  error_code?: string;
  blocking?: { code: string; row: string }[];
}

function mspBase(projectId: string) {
  return `/${PATHS.API_PROJECTS}/${projectId}/import/msp`;
}

export function previewMspImport(projectId: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiFormData<MspPreviewResult>(`${mspBase(projectId)}/preview/`, form);
}

export function startMspImport(
  projectId: string,
  file: File,
  replace: boolean,
  options?: { intent?: "new" | "retry"; retryOf?: string },
) {
  const form = new FormData();
  form.append("file", file);
  form.append("replace", replace ? "true" : "false");
  form.append("intent", options?.intent ?? "new");
  if (options?.intent === "retry" && options.retryOf) form.append("retry_of", options.retryOf);
  return apiFormData<MspImportStartResult>(`${mspBase(projectId)}/`, form);
}

export function fetchMspImportStatus(projectId: string, taskId: string) {
  return apiJson<MspImportStatusResult>(
    `${mspBase(projectId)}/status/${taskId}/`,
  );
}

function p6Base(projectId: string) {
  return `/${PATHS.API_PROJECTS}/${projectId}/import/p6`;
}

export function previewP6Import(projectId: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiFormData<MspPreviewResult>(`${p6Base(projectId)}/preview/`, form);
}

export function startP6Import(
  projectId: string,
  file: File,
  replace: boolean,
  options?: { intent?: "new" | "retry"; retryOf?: string },
) {
  const form = new FormData();
  form.append("file", file);
  form.append("replace", replace ? "true" : "false");
  form.append("intent", options?.intent ?? "new");
  if (options?.intent === "retry" && options.retryOf) form.append("retry_of", options.retryOf);
  return apiFormData<MspImportStartResult>(`${p6Base(projectId)}/`, form);
}

export function fetchP6ImportStatus(projectId: string, taskId: string) {
  return apiJson<MspImportStatusResult>(
    `${p6Base(projectId)}/status/${taskId}/`,
  );
}

