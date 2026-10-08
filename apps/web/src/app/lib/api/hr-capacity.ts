import { PATHS } from "@/app/routeVars";
import { apiFetch, apiJson } from "@/app/lib/api-client";

const base = (projectId: string) => `/${PATHS.API_PROJECTS}/${projectId}`;

export type PersonDossier = {
  id: string;
  full_name: string;
  email: string | null;
  mobile: string | null;
  status: string;
  is_active: boolean;
  organization: string;
  skills: string[];
  qualifications: string[];
  org_unit_id: string | null;
  org_unit_name: string | null;
  supervisor_id: string | null;
  supervisor_name: string | null;
  default_capacity_percent: string;
};

export type ResourceAllocation = {
  id: string;
  person_id: string;
  wbs_id: string | null;
  activity_id: string | null;
  start_date: string;
  end_date: string;
  role: string;
  capacity_percent: string;
  capacity_hours: string | null;
  work_location: string;
  supervisor_id: string | null;
  status: string;
  has_capacity_exception: boolean;
  capacity_exception_id: string | null;
};

export type CapacityException = {
  id: string;
  person_id: string;
  allocation_id: string | null;
  start_date: string;
  end_date: string;
  reason: string;
  status: string;
  requested_capacity_percent: string;
  decision_notes: string;
};

export type CapacityConflict = {
  code: string;
  available: string;
  committed: string;
  requested: string;
  overlapping_allocation_ids: string[];
};

export type CapacityPreview = {
  available: string;
  committed: string;
  requested: string;
  would_conflict: boolean;
  overlapping_allocation_ids: string[];
};

export type LaborCostEstimate = {
  amount: string | null;
  currency: string | null;
  rate_amount?: string | null;
  hours: string;
  warning: string | null;
};

export function fetchPersonDossier(projectId: string, userId: string) {
  return apiJson<PersonDossier>(`${base(projectId)}/people/${userId}/dossier/`);
}

export function updatePersonDossier(
  projectId: string,
  userId: string,
  body: Partial<{
    skills: string[];
    qualifications: string[];
    org_unit_id: string | null;
    supervisor_id: string | null;
    status: string;
    default_capacity_percent: string;
  }>,
) {
  return apiJson<PersonDossier>(`${base(projectId)}/people/${userId}/dossier/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function fetchResourceAllocations(projectId: string) {
  return apiJson<{ results: ResourceAllocation[] } | ResourceAllocation[]>(
    `${base(projectId)}/resource-allocations/`,
  );
}

export class CapacityConflictError extends Error {
  readonly conflict: CapacityConflict;

  constructor(conflict: CapacityConflict) {
    super(conflict.code || "capacity_conflict");
    this.name = "CapacityConflictError";
    this.conflict = conflict;
  }
}

export async function createResourceAllocation(
  projectId: string,
  body: Record<string, unknown>,
) {
  const res = await apiFetch(`${base(projectId)}/resource-allocations/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  const raw = await res.text();
  let data: Record<string, unknown> = {};
  if (raw) {
    try {
      data = JSON.parse(raw) as Record<string, unknown>;
    } catch {
      data = {};
    }
  }
  if (!res.ok) {
    const err = data.error as
      | { code?: string; message?: string; details?: Record<string, unknown> }
      | undefined;
    if (res.status === 409 && err?.code === "capacity_conflict") {
      const details = (err.details ?? {}) as Record<string, unknown>;
      throw new CapacityConflictError({
        code: "capacity_conflict",
        available: String(details.available ?? ""),
        committed: String(details.committed ?? ""),
        requested: String(details.requested ?? ""),
        overlapping_allocation_ids: Array.isArray(details.overlapping_allocation_ids)
          ? (details.overlapping_allocation_ids as string[])
          : [],
      });
    }
    throw new Error(err?.message || raw || res.statusText || "Request failed");
  }
  return data as unknown as ResourceAllocation;
}

export function deleteResourceAllocation(projectId: string, id: string) {
  return apiJson<void>(`${base(projectId)}/resource-allocations/${id}/`, {
    method: "DELETE",
  });
}

export function fetchCapacityPreview(
  projectId: string,
  params: {
    person_id: string;
    from: string;
    to: string;
    capacity_percent: string;
  },
) {
  const qs = new URLSearchParams(params).toString();
  return apiJson<CapacityPreview>(
    `${base(projectId)}/resource-allocations/capacity-preview/?${qs}`,
  );
}

export function fetchCapacityExceptions(projectId: string) {
  return apiJson<{ results: CapacityException[] } | CapacityException[]>(
    `${base(projectId)}/capacity-exceptions/`,
  );
}

export function createCapacityException(
  projectId: string,
  body: Record<string, unknown>,
) {
  return apiJson<CapacityException>(`${base(projectId)}/capacity-exceptions/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function submitCapacityException(projectId: string, id: string) {
  return apiJson<CapacityException>(
    `${base(projectId)}/capacity-exceptions/${id}/submit/`,
    { method: "POST" },
  );
}

export function approveCapacityException(
  projectId: string,
  id: string,
  decisionNotes = "",
) {
  return apiJson<CapacityException>(
    `${base(projectId)}/capacity-exceptions/${id}/approve/`,
    {
      method: "POST",
      body: JSON.stringify({ decision_notes: decisionNotes }),
    },
  );
}

export function rejectCapacityException(
  projectId: string,
  id: string,
  decisionNotes = "",
) {
  return apiJson<CapacityException>(
    `${base(projectId)}/capacity-exceptions/${id}/reject/`,
    {
      method: "POST",
      body: JSON.stringify({ decision_notes: decisionNotes }),
    },
  );
}

export function estimateLaborCost(
  projectId: string,
  body: { person_id: string; approved_hours: string; as_of?: string },
) {
  return apiJson<LaborCostEstimate>(`${base(projectId)}/labor-cost-estimate/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function listResults<T>(data: { results: T[] } | T[] | undefined): T[] {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  return data.results ?? [];
}
