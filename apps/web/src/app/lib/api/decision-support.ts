import { PATHS } from "@/app/routeVars";
import { apiFetch, apiJson } from "@/app/lib/api-client";

export type DecisionMethod = "saw" | "topsis" | "ahp" | "dematel" | "ism";

export const DECISION_METHODS: DecisionMethod[] = ["saw", "topsis", "ahp", "dematel", "ism"];

export type DecisionCase = {
  id: string;
  title: string;
  selected_methods: DecisionMethod[];
  criteria: string[];
  alternatives: string[];
  weights: number[];
  types: string[];
  performance_matrix: (number | null)[][];
  ahp_matrix: unknown[];
  dematel_matrix: unknown[];
  ism_matrix: unknown[];
  criteria_count?: number;
  alternatives_count?: number;
  created_at?: string;
  updated_at?: string;
};

export type DecisionCaseSummary = {
  id: string;
  title: string;
  selected_methods: DecisionMethod[];
  criteria_count: number;
  alternatives_count: number;
  updated_at: string;
};

export type DecisionRunSummary = {
  id: string;
  method: DecisionMethod;
  extracted_at: string;
  extracted_by: string;
  extracted_by_name?: string;
  result: { status?: string; engine?: null };
};

export type DecisionRun = DecisionRunSummary & {
  input_snapshot: Record<string, unknown>;
};

export class DecisionSupportRequestError extends Error {
  payload: unknown;
  constructor(message: string, payload: unknown) {
    super(message);
    this.name = "DecisionSupportRequestError";
    this.payload = payload;
  }
}

function base(projectId: string) {
  return `/${PATHS.API_PROJECTS}/${projectId}/decision-cases`;
}

async function jsonOrThrow<T>(path: string, options: RequestInit): Promise<T> {
  const res = await apiFetch(path, options);
  const raw = await res.text();
  let data: unknown = {};
  if (raw) {
    try {
      data = JSON.parse(raw);
    } catch {
      data = {};
    }
  }
  if (!res.ok) {
    const errObj = data as { error?: { message?: string } | string };
    const message =
      typeof errObj.error === "object" && errObj.error?.message
        ? errObj.error.message
        : typeof errObj.error === "string"
          ? errObj.error
          : res.statusText || "Request failed";
    throw new DecisionSupportRequestError(message, data);
  }
  return data as T;
}

export function listDecisionCases(projectId: string) {
  return apiJson<{ count: number; results: DecisionCaseSummary[] }>(`${base(projectId)}/`);
}

export function getDecisionCase(projectId: string, caseId: string) {
  return apiJson<DecisionCase>(`${base(projectId)}/${caseId}/`);
}

export function createDecisionCase(
  projectId: string,
  body: Partial<DecisionCase> & { title: string },
) {
  return jsonOrThrow<DecisionCase>(`${base(projectId)}/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function patchDecisionCase(projectId: string, caseId: string, body: Partial<DecisionCase>) {
  return jsonOrThrow<DecisionCase>(`${base(projectId)}/${caseId}/`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function listDecisionRuns(projectId: string, caseId: string) {
  return apiJson<{ count: number; results: DecisionRunSummary[] }>(
    `${base(projectId)}/${caseId}/runs/`,
  );
}

export function getDecisionRun(projectId: string, caseId: string, runId: string) {
  return apiJson<DecisionRun>(`${base(projectId)}/${caseId}/runs/${runId}/`);
}

export function createDecisionRun(projectId: string, caseId: string, method: DecisionMethod) {
  return jsonOrThrow<DecisionRun>(`${base(projectId)}/${caseId}/runs/`, {
    method: "POST",
    body: JSON.stringify({ method }),
  });
}
