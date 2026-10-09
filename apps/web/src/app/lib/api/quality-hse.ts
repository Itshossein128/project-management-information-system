import { PATHS } from "@/app/routeVars";
import { apiJson } from "@/app/lib/api-client";

const projectBase = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export interface Inspection {
  id: string;
  wbs: string;
  responsible_user: string;
  inspection_date: string;
  stage: string;
  result: string;
  description: string;
}

export interface Nonconformity {
  id: string;
  inspection: string | null;
  wbs: string | null;
  description: string;
  status: string;
  raised_date: string;
}

export interface CorrectiveAction {
  id: string;
  nonconformity: string;
  description: string;
  responsible_user: string | null;
  due_date: string | null;
  status: string;
}

export interface HseEvent {
  id: string;
  kind: "incident" | "near_miss";
  event_date: string;
  description: string;
  wbs: string | null;
  status: string;
}

export interface WorkPermit {
  id: string;
  permit_date: string;
  permit_type: string;
  description: string;
  status: string;
}

export interface SafetyTraining {
  id: string;
  training_date: string;
  topic: string;
  description: string;
}

export interface PeriodReport {
  project_id: string;
  date_from: string;
  date_to: string;
  inspections: unknown[];
  nonconformities: unknown[];
  corrective_actions: unknown[];
  incidents: unknown[];
  near_misses: unknown[];
  work_permits: unknown[];
  trainings: unknown[];
  counts: Record<string, number>;
}

function listUrl(projectId: string, path: string, params: Record<string, string | undefined> = {}) {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v) search.set(k, v);
  }
  const qs = search.toString();
  return `${projectBase(projectId)}/${path}/${qs ? `?${qs}` : ""}`;
}

export function createInspection(projectId: string, body: Partial<Inspection>) {
  return apiJson<Inspection>(`${projectBase(projectId)}/inspections/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchInspections(projectId: string) {
  return apiJson<{ count: number; results: Inspection[] }>(listUrl(projectId, "inspections"));
}

export function createNonconformity(projectId: string, body: Partial<Nonconformity>) {
  return apiJson<Nonconformity>(`${projectBase(projectId)}/nonconformities/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createCorrectiveAction(projectId: string, body: Partial<CorrectiveAction>) {
  return apiJson<CorrectiveAction>(`${projectBase(projectId)}/corrective-actions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createHseEvent(projectId: string, body: Partial<HseEvent>) {
  return apiJson<HseEvent>(`${projectBase(projectId)}/hse-events/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createWorkPermit(projectId: string, body: Partial<WorkPermit>) {
  return apiJson<WorkPermit>(`${projectBase(projectId)}/work-permits/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function createSafetyTraining(projectId: string, body: Partial<SafetyTraining>) {
  return apiJson<SafetyTraining>(`${projectBase(projectId)}/safety-trainings/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchQualitySafetyReport(
  projectId: string,
  dateFrom: string,
  dateTo: string,
) {
  return apiJson<PeriodReport>(
    listUrl(projectId, "quality-safety/report", {
      date_from: dateFrom,
      date_to: dateTo,
    }),
  );
}
