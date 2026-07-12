import { apiFormData, apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";

export interface MspPreviewWBSNode {
  wbs_code: string;
  wbs_name: string;
  depth: number;
  is_summary: boolean;
  activities: { activity_code: string; activity_name: string; duration_days: number | null }[];
  children: MspPreviewWBSNode[];
}

export interface MspPreviewResult {
  wbs_tree: MspPreviewWBSNode[];
  activities: {
    activity_code: string;
    activity_name: string;
    outline_number: string;
    duration_days: number | null;
  }[];
  warnings: string[];
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
    warnings: string[];
  };
  error?: string;
}

function mspBase(projectId: string) {
  return `/${PATHS.API_PROJECTS}/${projectId}/import/msp`;
}

export function previewMspImport(projectId: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiFormData<MspPreviewResult>(`${mspBase(projectId)}/preview/`, form);
}

export function startMspImport(projectId: string, file: File, replace: boolean) {
  const form = new FormData();
  form.append("file", file);
  form.append("replace", replace ? "true" : "false");
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

export function startP6Import(projectId: string, file: File, replace: boolean) {
  const form = new FormData();
  form.append("file", file);
  form.append("replace", replace ? "true" : "false");
  return apiFormData<MspImportStartResult>(`${p6Base(projectId)}/`, form);
}

export function fetchP6ImportStatus(projectId: string, taskId: string) {
  return apiJson<MspImportStatusResult>(
    `${p6Base(projectId)}/status/${taskId}/`,
  );
}

export function isP6File(file: File): boolean {
  return file.name.toLowerCase().endsWith(".xer");
}
