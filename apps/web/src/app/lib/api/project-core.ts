import { apiJson } from "@/app/lib/api-client";
import { PATHS } from "@/app/routeVars";
import type { ListResponse } from "@/app/lib/api-types";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export type CapabilityMode = "required" | "optional" | "disabled";

export interface ProjectCapability {
  capability_key: string;
  enabled: boolean;
  mode?: CapabilityMode;
  updated_at?: string;
  updated_by?: string | null;
}

export interface FiscalPeriodLock {
  id: string;
  period_start: string;
  period_end: string;
  reason: string;
  is_active?: boolean;
  closed_at?: string;
}

export interface CreateFiscalLockPayload {
  period_start: string;
  period_end: string;
  reason: string;
}

async function asList<T>(path: string): Promise<T[]> {
  const data = await apiJson<ListResponse<T> | T[]>(path);
  return Array.isArray(data) ? data : (data.results ?? []);
}

export function listCapabilities(projectId: string) {
  return asList<ProjectCapability>(`${base(projectId)}/capabilities/`);
}

export function updateCapability(
  projectId: string,
  capabilityKey: string,
  payload: Partial<Pick<ProjectCapability, "enabled" | "mode">>,
) {
  return apiJson<ProjectCapability>(
    `${base(projectId)}/capabilities/${capabilityKey}/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export function listFiscalLocks(projectId: string) {
  return asList<FiscalPeriodLock>(`${base(projectId)}/fiscal-period-locks/`);
}

export function createFiscalLock(
  projectId: string,
  payload: CreateFiscalLockPayload,
) {
  return apiJson<FiscalPeriodLock>(`${base(projectId)}/fiscal-period-locks/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
